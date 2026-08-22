"""Hangar Close until KSC; Flight Results is not a green light."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hangar import (
    Hangar,
    dismiss_flight_results,
    go_space_center,
    install_signed,
    ksc_ready,
    name_is_refused,
)
from session import SessionError


class _Scene:
    def __init__(self, name):
        self.name = name


class _Krpc:
    def __init__(self, scene="space_center"):
        self._scene = _Scene(scene)
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
        self._scene = val if hasattr(val, "name") else _Scene(str(val))


class _SC:
    def __init__(self, *, revert=False, vessels=()):
        self._revert = revert
        self.closes = 0
        self.reverts = 0
        self.vessels = list(vessels)
        self.saves: list[str] = []
        self.loads: list[str] = []

    def can_revert_to_launch(self):
        return bool(self._revert)

    def revert_to_launch(self):
        self.reverts += 1
        raise AssertionError("never revert_to_launch")

    def load_space_center(self):
        self.closes += 1
        self._revert = False

    def save(self, name):
        self.saves.append(name)

    def load(self, name):
        self.loads.append(name)
        self._revert = False


class _Session:
    def __init__(self, scene="space_center", *, revert=False, vessels=()):
        self.space_center = _SC(revert=revert, vessels=vessels)
        self.conn = type(
            "C",
            (),
            {"krpc": _Krpc(scene), "space_center": self.space_center},
        )()

    def require_connected(self):
        return None


class TestKscReady(unittest.TestCase):
    def test_tracking_empty_is_not_ksc(self):
        session = _Session(scene="tracking_station", vessels=())
        ok, why = ksc_ready(session)
        self.assertFalse(ok)
        self.assertIn("tracking", why)

    def test_flight_results_can_revert_is_not_ksc(self):
        wreck = type("V", (), {"name": "wreck"})()
        session = _Session(scene="space_center", revert=True, vessels=(wreck,))
        ok, why = ksc_ready(session)
        self.assertFalse(ok)
        self.assertIn("flight results", why)

    def test_stale_can_revert_empty_ksc_is_ready(self):
        session = _Session(scene="space_center", revert=True, vessels=())
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")

    def test_ksc_clean(self):
        session = _Session(scene="space_center", revert=False)
        ok, why = ksc_ready(session)
        self.assertTrue(ok)
        self.assertEqual(why, "ksc")


class TestGoSpaceCenter(unittest.TestCase):
    def test_closes_until_can_revert_false(self):
        session = _Session(scene="space_center", revert=True)
        with patch("hangar.time.sleep"):
            go_space_center(session, timeout=5.0)
        self.assertGreaterEqual(session.space_center.closes, 1)
        self.assertEqual(session.space_center.reverts, 0)
        self.assertFalse(session.space_center.can_revert_to_launch())
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

    def test_timeout_if_results_stuck(self):
        wreck = type("V", (), {"name": "wreck"})()
        session = _Session(scene="space_center", revert=True, vessels=(wreck,))
        session.space_center.load_space_center = lambda: None  # type: ignore[method-assign]
        with patch("hangar.time.sleep"):
            with patch("hangar.time.monotonic", side_effect=[0.0, 0.0, 2.0]):
                with self.assertRaises(SessionError) as ctx:
                    go_space_center(session, timeout=0.01)
        self.assertIn("Flight Results", str(ctx.exception))
        self.assertEqual(session.space_center.reverts, 0)

    def test_stuck_results_do_not_reload_loop(self):
        wreck = type("V", (), {"name": "wreck"})()
        session = _Session(scene="space_center", revert=True, vessels=(wreck,))
        n = {"n": 0}

        def stuck() -> None:
            n["n"] += 1

        session.space_center.load_space_center = stuck  # type: ignore[method-assign]
        with patch("hangar.time.sleep"):
            with self.assertRaises(SessionError):
                go_space_center(session, timeout=5.0)
        self.assertLessEqual(n["n"], 1)
        self.assertEqual(session.space_center.reverts, 0)


class TestDismissFlightResults(unittest.TestCase):
    def test_overlay_save_load_not_revert(self):
        session = _Session(scene="space_center", revert=True, vessels=())
        with patch("hangar.time.sleep"):
            dismiss_flight_results(session)
        self.assertEqual(session.space_center.saves, ["leftover-ksc"])
        self.assertEqual(session.space_center.loads, ["leftover-ksc"])
        self.assertEqual(session.space_center.reverts, 0)
        self.assertFalse(session.space_center.can_revert_to_launch())

    def test_clean_ksc_does_not_save(self):
        session = _Session(scene="space_center", revert=False)
        with patch("hangar.time.sleep"):
            dismiss_flight_results(session)
        self.assertEqual(session.space_center.saves, [])
        self.assertEqual(session.space_center.loads, [])
        self.assertEqual(session.space_center.reverts, 0)


class TestHangarLaunchGate(unittest.TestCase):
    def test_no_launch_vessel_while_flight_results(self):
        wreck = type("V", (), {"name": "wreck"})()
        session = _Session(scene="tracking_station", revert=True, vessels=(wreck,))
        session.space_center.load_space_center = lambda: None  # type: ignore[method-assign]
        hangar = Hangar(ksp_root=Path("/tmp"), save="letsgrok")
        with patch("hangar.time.sleep"):
            with patch("hangar.time.monotonic", side_effect=[0.0, 0.0, 2.0]):
                with patch.object(hangar, "_launch_watched") as launch:
                    with self.assertRaises(SessionError) as ctx:
                        hangar.launch(session, "kspstuff-hop-valiant-east-pbc", uncrewed=True)
        self.assertIn("Hangar waits", str(ctx.exception))
        launch.assert_not_called()
        self.assertEqual(session.space_center.reverts, 0)

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
        session.active_vessel = type("V", (), {"name": name})()


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


if __name__ == "__main__":
    unittest.main()
