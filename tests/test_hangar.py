"""Hangar Close until KSC; Flight Results is not a green light."""

from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import hangar as hangar_mod
from ra_align import align_live
from hangar import (
    Hangar,
    _abort_preflight_hang,
    dismiss_flight_results,
    go_ksc,
    go_space_center,
    hold_prelaunch,
    install_signed,
    ksc_ready,
    leftover_ship,
    leftover_will_land,
    overlay_painted,
    load_save,
    name_is_refused,
    walk_home,
)
from session import ConnectionSettings, SessionError


def _craft(name="wreck", *, recoverable=False, typ="ship", sit="landed", id=None):
    attrs = {
        "name": name,
        "recoverable": recoverable,
        "type": type("T", (), {"name": typ})(),
        "situation": type("S", (), {"name": sit})(),
    }
    if id is not None:
        attrs["id"] = id
    return type("V", (), attrs)()


class _Scene:
    def __init__(self, name):
        self.name = name


class _Krpc:
    def __init__(self, scene="space_center", sc=None):
        self._scene = _Scene(scene)
        self._sc = sc
        self.GameScene = type(
            "GS",
            (),
            {
                "space_center": _Scene("space_center"),
                "flight": _Scene("flight"),
                "tracking_station": _Scene("tracking_station"),
            },
        )()

    @property
    def game_scene(self):
        return self._scene

    @game_scene.setter
    def game_scene(self, val):
        new = val if hasattr(val, "name") else _Scene(str(val))
        old = self._scene.name
        if self._sc is not None:
            self._sc.order.append(("game_scene", getattr(new, "name", str(new))))
        self._scene = new
        if (
            self._sc is not None
            and old == "flight"
            and getattr(new, "name", "") != "flight"
        ):
            # Leaving Flight without persist loads last SaveGame (launch UT).
            self._sc.ut = float(self._sc.last_save_ut)


class _SC:
    def __init__(self, *, revert=False, vessels=(), ut=1000.0, launch_ut=None):
        self._revert = revert
        self.closes = 0
        self.reverts = 0
        self.vessels = list(vessels)
        self.saves: list[str] = []
        self.loads: list[str] = []
        self.order: list[tuple[str, str]] = []
        self.ut = float(ut)
        self.last_save_ut = float(ut if launch_ut is None else launch_ut)
        self.save_error: Exception | None = None

    def can_revert_to_launch(self):
        return bool(self._revert)

    def revert_to_launch(self):
        self.reverts += 1
        raise AssertionError("never revert_to_launch")

    def load_space_center(self):
        self.closes += 1
        self._revert = False

    def save(self, name):
        slug = str(name or "")
        if slug.lower() in {"leftover-ksc", "leftover_ksc"}:
            raise AssertionError("never leftover-ksc save")
        self.order.append(("save", slug))
        if self.save_error is not None:
            raise self.save_error
        self.saves.append(slug)
        self.last_save_ut = float(self.ut)

    def load(self, name):
        slug = str(name or "")
        if slug.lower() == "persistent":
            raise AssertionError("never load persistent (F-014)")
        self.loads.append(slug)
        self._revert = False


class _Session:
    def __init__(
        self,
        scene="space_center",
        *,
        revert=False,
        vessels=(),
        ut=1000.0,
        launch_ut=None,
    ):
        if launch_ut is None and scene == "flight":
            launch_ut = float(ut) - 240.0
        self.space_center = _SC(
            revert=revert, vessels=vessels, ut=ut, launch_ut=launch_ut
        )
        self.settings = ConnectionSettings()
        krpc = _Krpc(scene, sc=self.space_center)
        self.conn = type(
            "C",
            (),
            {"krpc": krpc, "space_center": self.space_center},
        )()

    def require_connected(self):
        return None


class TestKscReady(unittest.TestCase):
    def test_tracking_empty_is_not_ksc(self):
        session = _Session(scene="tracking_station", vessels=())
        ok, why = ksc_ready(session)
        self.assertFalse(ok)
        self.assertIn("tracking", why)

    def test_empty_ksc_stale_can_revert_is_ready(self):
        session = _Session(scene="space_center", revert=True, vessels=())
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")
        self.assertFalse(overlay_painted(session))

    def test_leftover_ship_is_not_ready(self):
        session = _Session(
            scene="space_center", revert=False, vessels=(_craft("hop-wreck"),)
        )
        ok, why = ksc_ready(session)
        self.assertFalse(ok)
        self.assertIn("leftover ships", why)

    def test_asteroid_is_not_leftover_ship(self):
        rock = _craft("Ast. XRL-564", typ="spaceobject")
        self.assertFalse(leftover_ship(rock))
        session = _Session(scene="space_center", revert=False, vessels=(rock,))
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")

    def test_sub_orbital_will_land_orbiting_will_not(self):
        self.assertTrue(leftover_will_land(_craft("t7-pbc", sit="sub_orbital")))
        self.assertFalse(leftover_will_land(_craft("t7-pbc", sit="orbiting")))

    def test_unrecoverable_guid_is_not_leftover_ship(self):
        wreck = _craft("t7-pbc", sit="sub_orbital", id="guid-crash-ui")
        self.assertTrue(leftover_ship(wreck))
        hangar_mod._UNRECOVERABLE.add("guid-crash-ui")
        try:
            self.assertFalse(leftover_ship(wreck))
            session = _Session(scene="space_center", revert=False, vessels=(wreck,))
            ok, why = ksc_ready(session)
            self.assertTrue(ok)
            self.assertEqual(why, "ksc")
        finally:
            hangar_mod._UNRECOVERABLE.discard("guid-crash-ui")

    def test_unrecoverable_guid_survives_fresh_process(self):
        wreck = _craft("t7-pbc", sit="sub_orbital", id="guid-disk")
        path = Path(tempfile.mkdtemp()) / "unrecoverable.last"
        hangar_mod._UNRECOVERABLE.clear()
        with patch("hangar.UNRECOVERABLE_LAST", path):
            hangar_mod.remember_unrecoverable(wreck)
            hangar_mod._UNRECOVERABLE.clear()
            self.assertFalse(leftover_ship(wreck))
            self.assertIn("guid-disk", path.read_text(encoding="utf-8"))
            session = _Session(scene="space_center", revert=False, vessels=(wreck,))
            ok, why = ksc_ready(session)
            self.assertTrue(ok)
            self.assertEqual(why, "ksc")

    def test_dead_guid_is_not_leftover_ship(self):
        class _Dead:
            @property
            def name(self):
                raise RuntimeError("No such vessel")

        self.assertFalse(leftover_ship(_Dead()))
        session = _Session(scene="space_center", revert=False, vessels=(_Dead(),))
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")

    def test_leftover_ship_with_can_revert_is_not_ready(self):
        session = _Session(
            scene="space_center", revert=True, vessels=(_craft("hop-wreck"),)
        )
        ok, why = ksc_ready(session)
        self.assertFalse(ok)
        self.assertIn("leftover ships", why)
        self.assertTrue(overlay_painted(session))

    def test_ksc_clean(self):
        session = _Session(scene="space_center", revert=False)
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")

    def test_airborne_leftover_is_not_hangar_veto(self):
        wreck = _craft("t7-pbc", sit="sub_orbital")
        session = _Session(scene="space_center", vessels=(wreck,))
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")


class TestRaAlign(unittest.TestCase):
    def test_align_live_noop_without_service(self):
        session = _Session(scene="space_center")
        self.assertFalse(align_live(session, world=None))


class TestGoSpaceCenter(unittest.TestCase):
    def test_close_does_not_load_space_center(self):
        session = _Session(scene="space_center", revert=True)
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0)
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")

    def test_tracking_closes_to_ksc(self):
        session = _Session(scene="tracking_station", revert=False)
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0)
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")
        self.assertEqual(session.space_center.reverts, 0)
        ok, _ = ksc_ready(session)
        self.assertTrue(ok)

    def test_crash_close_does_not_reload_save(self):
        session = _Session(scene="space_center", revert=False)
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0, reload_save=False)
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.reverts, 0)

    def test_never_calls_revert(self):
        session = _Session(scene="space_center", revert=True)
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0)
        self.assertEqual(session.space_center.reverts, 0)

    def test_overlay_close_not_leftover_ksc(self):
        wreck = _craft("wreck")
        session = _Session(scene="space_center", revert=True, vessels=(wreck,))
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.reverts, 0)

    def test_stuck_results_do_not_reload_loop(self):
        wreck = _craft("wreck")
        session = _Session(scene="space_center", revert=True, vessels=(wreck,))
        n = {"n": 0}

        def stuck() -> None:
            n["n"] += 1

        session.space_center.load_space_center = stuck  # type: ignore[method-assign]
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0)
        self.assertEqual(n["n"], 0)
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.space_center.saves, [])

    def test_close_from_flight_saves_before_scene(self):
        session = _Session(scene="flight", ut=1200.0, launch_ut=900.0)
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0)
        self.assertEqual(session.space_center.saves, ["persistent"])
        self.assertEqual(
            session.space_center.order,
            [
                ("save", "persistent"),
                ("game_scene", "tracking_station"),
                ("game_scene", "space_center"),
            ],
        )
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.space_center.ut, 1200.0)
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")

    def test_close_from_flight_save_fail_stays_flight(self):
        session = _Session(scene="flight", ut=1200.0, launch_ut=900.0)
        session.space_center.save_error = RuntimeError("SaveGame NRE")
        with patch("hangar.time.sleep"):
            with self.assertRaises(SessionError) as ctx:
                go_space_center(session, timeout=5.0)
        self.assertIn("save RAM", str(ctx.exception))
        self.assertEqual(session.conn.krpc.game_scene.name, "flight")
        self.assertEqual(session.space_center.ut, 1200.0)
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.saves, [])
        self.assertNotIn(
            ("game_scene", "space_center"), session.space_center.order
        )
        self.assertNotIn(
            ("game_scene", "tracking_station"), session.space_center.order
        )

    def test_close_from_flight_rewind_is_failure(self):
        session = _Session(scene="flight", ut=1200.0, launch_ut=900.0)
        with patch("hangar.time.sleep"):
            with patch("hangar._persist_ram"):
                with self.assertRaises(SessionError) as ctx:
                    go_space_center(session, timeout=5.0)
        self.assertIn("rewound", str(ctx.exception).lower())
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertLess(session.space_center.ut, 1200.0 - 0.5)


class TestDismissFlightResults(unittest.TestCase):
    def test_overlay_close_not_save_load(self):
        session = _Session(scene="space_center", revert=True, vessels=())
        with patch("hangar.time.sleep"):
            dismiss_flight_results(session)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")

    def test_clean_ksc_does_not_save(self):
        session = _Session(scene="space_center", revert=False)
        with patch("hangar.time.sleep"):
            dismiss_flight_results(session)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)


class TestHangarLaunchGate(unittest.TestCase):
    def test_no_launch_vessel_if_leftover_ship(self):
        wreck = _craft("wreck")
        session = _Session(scene="tracking_station", revert=False, vessels=(wreck,))
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")
        with patch("hangar.time.sleep"):
            with patch("hangar.go_flight"):
                with patch.object(hangar, "_launch_watched") as launch:
                    with self.assertRaises(SessionError) as ctx:
                        hangar.launch(
                            session, "kspstuff-hop-valiant-east-pbc", uncrewed=True
                        )
        self.assertIn("Hangar waits", str(ctx.exception))
        launch.assert_not_called()
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])

    def test_launch_after_walk_home_recover(self):
        wreck = _craft("wreck", recoverable=True)
        session = _Session(scene="space_center", revert=False, vessels=[wreck])

        def _recover() -> None:
            session.space_center.vessels = [
                v for v in session.space_center.vessels if v is not wreck
            ]

        wreck.recover = _recover  # type: ignore[method-assign]
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")
        with patch("hangar.time.sleep"):
            with patch("hangar.go_flight"):
                with patch("hangar.clear_launch_site", return_value=0):
                    with patch.object(hangar, "_launch_watched") as launch:
                        with patch("hangar.run_physics"):
                            with patch("hangar.wait_vessel_ready"):
                                hangar.launch(
                                    session,
                                    "kspstuff-hop-valiant-east-pbc",
                                    uncrewed=True,
                                )
        launch.assert_called_once()
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)

    def test_go_ksc_overlay_does_not_named_load(self):
        session = _Session(scene="space_center", revert=True, vessels=())
        with patch("hangar.time.sleep"):
            with patch("hangar.OVERLAY_LAST", Path(tempfile.mkdtemp()) / "overlay.last"):
                out = go_ksc(session)
        self.assertEqual(out, "ksc")
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)

    def test_load_save_refuses_leftover_ksc(self):
        session = _Session()
        with self.assertRaises(SessionError) as ctx:
            load_save(session, "leftover-ksc")
        self.assertIn("leftover-ksc", str(ctx.exception))
        self.assertEqual(session.space_center.loads, [])

    def test_walk_home_recovers_then_close(self):
        wreck = _craft("hop-wreck", recoverable=True)
        session = _Session(scene="space_center", revert=False, vessels=[wreck])

        def _recover() -> None:
            session.space_center.vessels = [
                v for v in session.space_center.vessels if v is not wreck
            ]

        wreck.recover = _recover  # type: ignore[method-assign]
        with patch("hangar.time.sleep"):
            with patch("hangar.go_flight"):
                n = walk_home(session)
        self.assertEqual(n, 1)
        self.assertEqual(session.space_center.vessels, [])
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")

    def test_walk_home_ksc_air_leftover_no_go_flight(self):
        wreck = _craft("t7-pbc", recoverable=False, sit="sub_orbital")
        session = _Session(scene="space_center", revert=False, vessels=[wreck])
        with patch("hangar.time.sleep"):
            with patch("hangar.go_flight") as gf:
                n = walk_home(session)
        self.assertEqual(n, 0)
        gf.assert_not_called()
        self.assertEqual(session.space_center.vessels, [wreck])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")

    def test_walk_home_crash_ui_guid_not_pad_occupancy(self):
        wreck = _craft(
            "t7-pbc", recoverable=False, sit="landed", id="guid-crash-ui"
        )
        session = _Session(scene="space_center", revert=False, vessels=[wreck])

        def _recover() -> None:
            raise RuntimeError("not recoverable")

        wreck.recover = _recover  # type: ignore[method-assign]
        hangar_mod._UNRECOVERABLE.discard("guid-crash-ui")
        path = Path(tempfile.mkdtemp()) / "unrecoverable.last"
        try:
            with patch("hangar.UNRECOVERABLE_LAST", path):
                with patch("hangar.time.sleep"):
                    with patch("hangar.go_flight") as gf:
                        n = walk_home(session)
                self.assertEqual(n, 0)
                gf.assert_not_called()
                hangar_mod._UNRECOVERABLE.clear()
                wreck.situation = type("S", (), {"name": "sub_orbital"})()
                self.assertFalse(leftover_ship(wreck))
                ok, why = ksc_ready(session)
                self.assertTrue(ok)
                self.assertEqual(why, "ksc")
            self.assertEqual(session.space_center.reverts, 0)
            self.assertEqual(session.space_center.saves, [])
        finally:
            hangar_mod._UNRECOVERABLE.discard("guid-crash-ui")

    def test_walk_home_close_when_sub_orbital_still_not_recoverable(self):
        wreck = _craft("t7-pbc", recoverable=False, sit="sub_orbital")
        session = _Session(scene="space_center", revert=False, vessels=[wreck])
        with patch("hangar.time.sleep"):
            with patch("hangar.go_flight") as gf:
                with patch("hangar._wait_leftover_land", return_value=False):
                    n = walk_home(session)
        self.assertEqual(n, 0)
        gf.assert_not_called()
        self.assertEqual(session.space_center.vessels, [wreck])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")
        ok, _ = ksc_ready(session)
        self.assertTrue(ok)

    def test_walk_home_waits_sub_orbital_land_then_recover(self):
        wreck = _craft("t7-pbc", recoverable=False, sit="sub_orbital")
        session = _Session(scene="flight", revert=False, vessels=[wreck])

        def _land(_session, vessel, **_kwargs):
            vessel.recoverable = True
            vessel.situation = type("S", (), {"name": "landed"})()
            return True

        def _recover() -> None:
            session.space_center.vessels = []

        wreck.recover = _recover  # type: ignore[method-assign]
        with patch("hangar.time.sleep"):
            with patch("hangar.go_flight") as gf:
                with patch("hangar._wait_leftover_land", side_effect=_land) as wait:
                    n = walk_home(session)
        self.assertEqual(n, 1)
        gf.assert_not_called()
        wait.assert_called()
        self.assertEqual(session.space_center.vessels, [])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.space_center.saves, ["persistent"])
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")
        self.assertTrue(leftover_will_land(wreck))

    def test_walk_home_waits_gone_when_recover_already_in_flight(self):
        wreck = _craft("t7-pbc", recoverable=False, sit="splashed")
        session = _Session(scene="flight", revert=False, vessels=[wreck])

        def _gone(_session, name, **_kwargs):
            session.space_center.vessels = []
            return True

        with patch("hangar.time.sleep"):
            with patch("hangar.go_flight") as gf:
                with patch("hangar._wait_recovered", side_effect=_gone):
                    n = walk_home(session)
        self.assertEqual(n, 1)
        gf.assert_not_called()
        self.assertEqual(session.space_center.vessels, [])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertEqual(session.space_center.saves, ["persistent"])
        self.assertEqual(
            session.space_center.order,
            [
                ("save", "persistent"),
                ("game_scene", "tracking_station"),
                ("game_scene", "space_center"),
            ],
        )
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.conn.krpc.game_scene.name, "space_center")

    def test_launch_after_ksc_clean(self):
        session = _Session(scene="space_center", revert=False)
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")
        with patch("hangar.time.sleep"):
            with patch("hangar.clear_launch_site", return_value=0):
                with patch.object(hangar, "_launch_watched") as launch:
                    with patch("hangar.run_physics"):
                        with patch("hangar.wait_vessel_ready"):
                            hangar.launch(
                                session,
                                "kspstuff-hop-valiant-east-pbc",
                                uncrewed=True,
                            )
        launch.assert_called_once()
        self.assertEqual(session.space_center.reverts, 0)

    def test_hangar_does_not_launch_on_rewound_clock(self):
        session = _Session(scene="flight", ut=1200.0, launch_ut=900.0)
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")
        with patch("hangar.time.sleep"):
            with patch("hangar._persist_ram"):
                with patch.object(hangar, "_launch_watched") as launch:
                    with self.assertRaises(SessionError) as ctx:
                        hangar.launch(
                            session,
                            "kspstuff-hop-valiant-east-pbc",
                            uncrewed=True,
                        )
        self.assertIn("Hangar waits", str(ctx.exception))
        self.assertIn("rewound", str(ctx.exception).lower())
        launch.assert_not_called()
        self.assertEqual(session.space_center.closes, 0)
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)

    def test_hung_launch_does_not_rpc_poisoned_session(self):
        session = _Session(scene="space_center", revert=False)
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")
        hung = SessionError("launch_vessel hung on pre-flight (dialog?)")
        with patch("hangar.time.sleep"):
            with patch("hangar.go_space_center") as go:
                with patch("hangar.clear_launch_site", return_value=0):
                    with patch.object(hangar, "_launch_watched", side_effect=hung):
                        with patch("hangar._abort_preflight_hang") as abort:
                            with self.assertRaises(SessionError) as ctx:
                                hangar.launch(
                                    session,
                                    "kspstuff-hop-valiant-proc-tank-pbc",
                                    uncrewed=True,
                                )
        self.assertIn("session poisoned", str(ctx.exception))
        self.assertEqual(go.call_count, 1)
        abort.assert_not_called()

    def test_launch_watched_timeout_raises_without_long_join(self):
        session = _Session(scene="space_center", revert=False)
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")
        joins: list[float | None] = []

        class _Alive:
            def __init__(self, *args, **kwargs):
                pass

            def start(self):
                return None

            def join(self, timeout=None):
                joins.append(timeout)

            def is_alive(self):
                return True

        with patch("hangar.threading.Thread", return_value=_Alive()):
            with patch("hangar._abort_preflight_hang") as abort:
                with self.assertRaises(SessionError) as ctx:
                    hangar._launch_watched(
                        session,
                        "VAB",
                        "kspstuff-hop-valiant-proc-tank-pbc",
                        "LaunchPad",
                        [],
                        True,
                        timeout=0.05,
                    )
        self.assertIn("hung on pre-flight", str(ctx.exception))
        abort.assert_called_once()
        self.assertTrue(joins)
        self.assertLessEqual(max(t or 0.0 for t in joins), 2.0)

    def test_flight_scene_does_not_abort_to_ksc(self):
        session = _Session(scene="flight", revert=False)
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")

        class _Alive:
            def __init__(self, *args, **kwargs):
                pass

            def start(self):
                return None

            def join(self, timeout=None):
                return None

            def is_alive(self):
                return True

        with patch("hangar.threading.Thread", return_value=_Alive()):
            with patch("hangar._abort_preflight_hang") as abort:
                with self.assertRaises(SessionError) as ctx:
                    hangar._launch_watched(
                        session,
                        "VAB",
                        "kspstuff-hop-valiant-proc-tank-pbc",
                        "LaunchPad",
                        [],
                        True,
                        timeout=0.05,
                        flight_grace=0.05,
                    )
        self.assertIn("Flight scene", str(ctx.exception))
        abort.assert_not_called()

    def test_abort_client_times_out(self):
        def hang_connect(**_kwargs):
            time.sleep(30)
            raise AssertionError("connect should have been abandoned")

        fake = type("K", (), {"connect": staticmethod(hang_connect)})()
        with patch.dict("sys.modules", {"krpc": fake}):
            t0 = time.monotonic()
            _abort_preflight_hang(ConnectionSettings(), timeout=0.2)
            self.assertLess(time.monotonic() - t0, 2.0)


_REFUSE = ("kspstuff-pad-pbc", "kspstuff-geiger-pbc")


class _FakeHangar:
    def __init__(self, root: Path):
        self.root = root
        self.calls: list[str] = []

    def ships(self, facility: str = "VAB") -> Path:
        path = self.root / facility
        path.mkdir(parents=True, exist_ok=True)
        return path

    def launch(self, session, name, *, recover=True, uncrewed=False, **_kwargs):
        self.calls.append(name)
        control = type("C", (), {"throttle": 1.0, "activate_next_stage": lambda self: (_ for _ in ()).throw(AssertionError("light"))})()
        session.active_vessel = type(
            "V",
            (),
            {"name": name, "situation": "pre_launch", "control": control},
        )()


class TestHangarRefuse(unittest.TestCase):
    def test_refuse_is_exact_basename_not_substring(self):
        self.assertEqual(
            name_is_refused("kspstuff-geiger-pbc", _REFUSE),
            "kspstuff-geiger-pbc",
        )
        self.assertEqual(
            name_is_refused("kspstuff-pad-pbc", _REFUSE),
            "kspstuff-pad-pbc",
        )
        self.assertIsNone(name_is_refused("kspstuff-hop-flea-geiger-pbc", _REFUSE))
        self.assertIsNone(name_is_refused("kspstuff-hop-geiger-pbc-plus", _REFUSE))
        self.assertIsNone(name_is_refused("kspstuff-hop-flea-pbc", _REFUSE))

    def test_install_signed_allows_hop_name_containing_geiger_pbc(self):
        session = _Session()
        session.active_vessel = None
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            src = Path(raw) / "src.craft"
            src.write_text("ship", encoding="utf-8")
            name = "kspstuff-hop-flea-geiger-pbc"
            out = install_signed(
                session, name, hangar=fake, refuse=_REFUSE, src=src
            )
            self.assertEqual(out, name)
            self.assertEqual(fake.calls, [name])
            dest = fake.ships("VAB") / f"{name}.craft"
            self.assertTrue(dest.is_file())

    def test_install_signed_refuses_exact_geiger_pbc(self):
        session = _Session()
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            src = Path(raw) / "src.craft"
            src.write_text("ship", encoding="utf-8")
            with self.assertRaises(SessionError) as ctx:
                install_signed(
                    session,
                    "kspstuff-geiger-pbc",
                    hangar=fake,
                    refuse=_REFUSE,
                    src=src,
                )
        self.assertIn("refused", str(ctx.exception))
        self.assertIn("kspstuff-geiger-pbc", str(ctx.exception))
        self.assertEqual(fake.calls, [])

    def test_hold_prelaunch_throttle_zero_no_light(self):
        session = _Session()
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            root = Path(raw)
            (root / "kspstuff-hop-valiant-t7-wheel-pbc.craft").write_text(
                "ship", encoding="utf-8"
            )
            with patch("hangar.REPO_CRAFTS", root):
                msg = hold_prelaunch(
                    session,
                    hangar=fake,
                    name="kspstuff-hop-valiant-t7-wheel-pbc",
                )
        self.assertIn("pre_launch", msg)
        self.assertIn("throttle=0", msg)
        self.assertEqual(fake.calls, ["kspstuff-hop-valiant-t7-wheel-pbc"])
        self.assertEqual(session.active_vessel.control.throttle, 0.0)

    def test_hold_prelaunch_accepts_enum_sit_and_skips_second_launch(self):
        session = _Session()
        control = type("C", (), {"throttle": 0.4})()
        session.active_vessel = type(
            "V",
            (),
            {
                "name": "kspstuff-hop-valiant-t7-wheel-pbc",
                "situation": "VesselSituation.pre_launch",
                "control": control,
            },
        )()
        fake = _FakeHangar(Path("/tmp"))
        msg = hold_prelaunch(
            session,
            hangar=fake,
            name="kspstuff-hop-valiant-t7-wheel-pbc",
        )
        self.assertEqual(fake.calls, [])
        self.assertIn("pre_launch", msg)
        self.assertEqual(control.throttle, 0.0)

    def test_launch_skips_vessel_when_occupancy(self):
        session = _Session(scene="flight")
        control = type("C", (), {"throttle": 1.0})()
        session.active_vessel = type("V", (), {"control": control})()
        with patch("hangar.seated_prelaunch_occupancy", return_value=True):
            Hangar(Path("/tmp"), save="kspstuff").launch(
                session, "kspstuff-hop-valiant-t7-wheel-pbc", uncrewed=True
            )
        self.assertEqual(control.throttle, 0.0)


if __name__ == "__main__":
    unittest.main()
