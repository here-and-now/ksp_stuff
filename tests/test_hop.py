"""No-KSP gates for hop: light, flying card, recover when down."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from hop import (
    CRAFT,
    HOP_TO_WATER_ABORT,
    hop_craft_name,
    hop_craft_path,
    hop_science_ids,
    hop_target_apo,
    install_and_launch,
    run_hop,
    run_hop_to_water,
    run_on_vessel,
    run_phase,
)
from phases import OffPlan, check_expect
from card import HOP_EXPERIMENTS, NO_BOUND_CARD, card_experiment_ids, card_flying_ids
from telem import MissionAbort


def _fast_clock():
    t = [0.0]

    def now():
        return t[0]

    def sleep(dt):
        t[0] += dt if dt else 0.01

    return now, sleep, t


class _Mod:
    def __init__(self, name, eid, events=None, broken=False):
        self.name = name
        self.fields = {"experiment_id": eid, "broken": broken}
        self.events = list(events or ["Start Experiment"])
        self.triggered: list[str] = []

    def trigger_event(self, name):
        self.triggered.append(name)

    def get_field(self, key):
        return self.fields[key]


class _Part:
    def __init__(self, name, modules):
        self.name = name
        self.modules = modules


class _Parts:
    def __init__(self, parts):
        self.all = parts

    @property
    def experiments(self):
        raise AssertionError("must not use vessel.parts.experiments")


class _Control:
    def __init__(self):
        self.throttle = 0.0
        self.sas = False
        self.staged = 0

    def activate_next_stage(self):
        self.staged += 1


class _Body:
    name = "Earth"
    has_atmosphere = True
    atmosphere_depth = 140_000.0


class _Res:
    def __init__(self, ec=10.0, fuel=5.0):
        self.ec = float(ec)
        self.fuel = float(fuel)

    def amount(self, n):
        return {"ElectricCharge": self.ec, "SolidFuel": self.fuel}.get(n, 0.0)


class _Flight:
    def __init__(self, vessel):
        self._vessel = vessel
        self.dynamic_pressure = 0.0
        self.surface_altitude = 80.0

    @property
    def mean_altitude(self):
        return self._vessel._alt

    @property
    def speed(self):
        return self._vessel._speed


class _Orbit:
    def __init__(self, apo=80.0, peri=-500_000.0):
        self.body = _Body()
        self.periapsis_altitude = peri
        self.apoapsis_altitude = apo
        self.eccentricity = 0.99
        self.semi_major_axis = 6.4e6
        self.time_to_periapsis = 0.0
        self.time_to_apoapsis = 1.0


class _Vessel:
    def __init__(self, modules, *, recoverable=False, sit="pre_launch", ec=10.0):
        self.name = "probe"
        self.situation = sit
        self.recoverable = recoverable
        self.recovered = False
        self.control = _Control()
        self.resources = _Res(ec=ec)
        self.thrust = 0.0
        self.parts = _Parts([_Part("GooExperiment", modules)])
        self.orbit = _Orbit()
        self._alt = 80.0
        self._speed = 0.0
        self._flight = _Flight(self)

    def flight(self):
        return self._flight

    def recover(self):
        if not self.recoverable:
            raise RuntimeError("not recoverable")
        self.recovered = True


class _Session:
    def __init__(self, vessel):
        self.active_vessel = vessel
        vessels = [vessel] if vessel is not None else []
        self.space_center = type(
            "SC",
            (),
            {
                "rails_warp_factor": 0,
                "physics_warp_factor": 0,
                "vessels": vessels,
            },
        )()

    def add_stream(self, func, obj, name):
        class _S:
            def __call__(self_inner):
                return func(obj, name)

            def remove(self_inner):
                pass

        return _S()


class _Uplink:
    def __init__(self, verb: str):
        self.verb = verb


class TestHopCatalog(unittest.TestCase):
    def test_in_names(self):
        from phases import NAMES

        self.assertIn("hop", NAMES)
        self.assertIn("splash", NAMES)
        self.assertIn("hop-to-water", NAMES)
        self.assertEqual(HOP_EXPERIMENTS, ("kerbalism_TELEMETRY", "temperatureScan"))
        self.assertEqual(CRAFT, "kspstuff-hop-flea-pbc")
        self.assertTrue(hop_craft_path("kspstuff-hop-flea-pbc").is_file())
        self.assertTrue(hop_craft_path("kspstuff-hop-hammer-pbc").is_file())
        from session import SessionError

        with patch(
            "missions.hangar_craft_name",
            return_value="kspstuff-hop-hammer-pbc",
        ):
            self.assertEqual(hop_craft_name(), "kspstuff-hop-hammer-pbc")
        with patch(
            "missions.hangar_craft_name",
            side_effect=SessionError("VAB capable=no — no Hangar (L-039)"),
        ):
            with self.assertRaises(SessionError):
                hop_craft_name()

    def test_source_is_not_a_godfile(self):
        text = Path("hop.py").read_text(encoding="utf-8")
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertNotIn("from watch", text)
        self.assertNotIn("import watch", text)
        self.assertNotIn("from launch", text)
        self.assertNotIn("parts.experiments", text)
        self.assertNotIn("run_ready", text)
        self.assertNotIn("pad_pbc", text)
        self.assertNotIn("parachute", text.lower())
        self.assertIn(
            "from hangar import discover_hangar, game_scene, go_flight, go_space_center",
            text,
        )
        self.assertIn("kspstuff-hop-hammer-pbc", text)
        self.assertIn("uncrewed", blocks.lower())
        self.assertIn("kspstuff-hop-hammer-pbc", blocks)

    def test_apo_clamp(self):
        with patch("phases._kv", return_value={"hop_apo": "15000"}):
            self.assertEqual(hop_target_apo(), 15_000.0)
        with patch("phases._kv", return_value={"hop_apo": "18000"}):
            self.assertEqual(hop_target_apo(), 18_000.0)
        with patch("phases._kv", return_value={"hop_apo": "40000"}):
            self.assertEqual(hop_target_apo(), 18_000.0)
        with patch("phases._kv", return_value={"hop_apo": "1000"}):
            self.assertEqual(hop_target_apo(), 8_000.0)


class TestCardIds(unittest.TestCase):
    def test_parse(self):
        text = (
            "- experiment: kerbalism_TELEMETRY\n"
            "  situation: FlyingLow\n"
            "- experiment: temperatureScan\n"
        )
        self.assertEqual(
            card_experiment_ids(text),
            ("kerbalism_TELEMETRY", "temperatureScan"),
        )

    def test_empty_is_empty(self):
        self.assertEqual(card_experiment_ids(""), ())

    def test_flying_skips_splash_goo(self):
        text = (
            "## Flying\n"
            "- experiment: kerbalism_TELEMETRY\n"
            "  situation: FlyingLow\n"
            "- experiment: temperatureScan\n"
            "  situation: FlyingLow\n"
            "## Splash\n"
            "- experiment: mysteryGoo\n"
            "  situation: SrfSplashed\n"
        )
        self.assertEqual(
            card_flying_ids(text),
            ("kerbalism_TELEMETRY", "temperatureScan"),
        )
        self.assertNotIn("mysteryGoo", card_flying_ids(text))

    def test_fixture_card_is_flying_not_splash_goo(self):
        path = Path("tests/fixtures/cards/hop-flying.md")
        with patch("missions.seated_science_path", return_value=path):
            ids = hop_science_ids()
        self.assertIn("temperatureScan", ids)
        self.assertNotIn("mysteryGoo", ids)
        self.assertNotIn("geigerCounter", ids)

    def test_empty_card_aborts(self):
        empty = Path("tests/fixtures/cards/empty.md")
        with patch("missions.seated_science_path", return_value=empty):
            with self.assertRaises(MissionAbort) as ctx:
                hop_science_ids()
        self.assertIn(NO_BOUND_CARD, str(ctx.exception))


class TestHopExpect(unittest.TestCase):
    def test_skip_peri(self):
        state = type(
            "S",
            (),
            {"body": "Earth", "peri": -6_000_000.0, "apo": 15_000.0},
        )()
        with patch(
            "phases._kv",
            return_value={
                "expect_body": "Earth",
                "expect_peri_min": "0",
                "expect_apo_max": "20000",
            },
        ):
            check_expect(state, skip_peri=True)
            with self.assertRaises(OffPlan):
                check_expect(state, skip_peri=False)

    def test_apo_still_checked(self):
        state = type(
            "S",
            (),
            {"body": "Earth", "peri": -6_000_000.0, "apo": 40_000.0},
        )()
        with patch(
            "phases._kv",
            return_value={
                "expect_body": "Earth",
                "expect_peri_min": "-500000",
                "expect_apo_max": "18000",
            },
        ):
            with self.assertRaises(OffPlan):
                check_expect(state, skip_peri=True)
            check_expect(state, skip_peri=True, skip_apo=True)


class TestHopSequence(unittest.TestCase):
    def test_light_science_after_airborne_then_recover(self):
        mod = _Mod("Experiment", "mysteryGoo")
        sits: list[str] = []

        def trigger_event(name):
            sits.append(vessel.situation)
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        mod.trigger_event = trigger_event
        vessel = _Vessel([mod], recoverable=False)
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["flying"])

    def test_fresh_hangar_starts_flying_card(self):
        """New Flea that lights: leftover-HD skip must not fire."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        thermo = _Mod("Experiment", "temperatureScan")
        drive = _Mod("HardDrive", "")
        drive.fields = {"Data": "empty"}
        vessel = _Vessel([tel], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel, drive]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and tel.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertTrue(any("kerbalism_TELEMETRY" in line for line in logs))
        self.assertFalse(any("keep HD" in line for line in logs))

    def test_does_not_recover_on_pad_without_flight(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=True, sit="pre_launch")
        now, sleep, t = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=3.0,
                pulse=1.0,
            )
        self.assertIn("timeout", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(mod.triggered, [])

    def test_empty_tanks_are_expected(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=False, sit="flying")
        vessel._alt = 5_000.0
        vessel._speed = 40.0
        vessel.resources.fuel = 0.0
        vessel.orbit.apoapsis_altitude = 14_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertEqual(vessel.control.staged, 0)

    def test_ec_zero_recovers_without_down(self):
        """Airborne EC=0 with HD: recover on first recoverable, even if flying."""
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="flying", ec=0.0)
        vessel._alt = 5_000.0
        vessel._speed = 80.0
        vessel.orbit.apoapsis_altitude = 14_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertEqual(vessel.situation, "flying")

    def test_ec_zero_timeout_waits_then_recovers(self):
        """Do not timeout-dump a dead airborne probe; recover when down."""
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="flying", ec=0.0)
        vessel._alt = 4_000.0
        vessel._speed = 40.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            if t[0] >= 4.0 and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            now=now,
            sleep=nap,
            timeout=2.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertGreaterEqual(t[0], 4.0)

    def test_ec_zero_empty_pad_aborts(self):
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=0.0)
        now, sleep, _t = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                now=now,
                sleep=sleep,
                timeout=5.0,
                pulse=1.0,
            )
        self.assertIn("ec=0", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_ec_zero_down_not_recoverable_aborts(self):
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="flying", ec=0.0)
        vessel._alt = 3_000.0
        vessel.orbit.apoapsis_altitude = 10_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = False
            t[0] += dt if dt else 0.01

        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                now=now,
                sleep=nap,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_wreck_waits_recoverable(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=False, sit="flying")
        vessel._alt = 8_000.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.situation == "flying" and mod.triggered:
                vessel.situation = "wrecked"
                vessel.recoverable = False
            elif vessel.situation == "wrecked":
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_apo_overshoot_offplan(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 10_000.0
        vessel.orbit.apoapsis_altitude = 55_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        with self.assertRaises(OffPlan) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=5.0,
                pulse=1.0,
            )
        self.assertIn("apo", str(ctx.exception))
        self.assertIn("FlyingLow", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_hammer_18km_overshoot_is_not_offplan(self):
        """SRB cannot hold. 18.8 km is still FlyingLow (< 50 km)."""
        from hop import FLYING_LOW_M

        self.assertGreater(FLYING_LOW_M, 18_858.0)
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 4_800.0
                vessel.orbit.apoapsis_altitude = 18_858.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_no_science_aborts(self):
        """Modules present but none start — empty card still aborts."""
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 2_000.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        now, sleep, _t = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                now=now,
                sleep=sleep,
                timeout=5.0,
                pulse=1.0,
            )
        self.assertIn("no science", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(mod.triggered, [])

    def test_leftover_no_modules_recovers(self):
        """Dead leftover: Experiment gone. Recover HD. Do not light."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=True)
        vessel._alt = 73.0
        vessel._speed = 10.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
            now=now,
            sleep=sleep,
            timeout=5.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)

    def test_leftover_hd_skips_fresh_start(self):
        """HardDrive already has files — do not Toggle the leftover card."""
        exp = _Mod("Experiment", "kerbalism_TELEMETRY")
        drive = _Mod("HardDrive", "")
        drive.fields = {"Data": "Telemetry Report 0.11 Mb"}
        vessel = _Vessel([exp], sit="flying", ec=0.0, recoverable=True)
        vessel.parts = _Parts(
            [_Part("probeCoreSphere.v2", [exp, drive])]
        )
        vessel._alt = 73.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
            now=now,
            sleep=sleep,
            timeout=5.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(exp.triggered, [])
        self.assertEqual(vessel.control.staged, 0)

    def test_leftover_no_modules_waits_recoverable(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel._alt = 73.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            if t[0] >= 3.0:
                vessel.recoverable = True

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
            now=now,
            sleep=nap,
            timeout=2.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertGreaterEqual(t[0], 3.0)

    def test_falling_probe_waits_while_met_moves(self):
        """Live fall: MET moving. Do not dismiss Flight Results yet."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 70.0
        vessel._alt = 400.0
        vessel.orbit.apoapsis_altitude = 800.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            vessel.met += dt if dt else 0.01
            vessel._alt = max(80.0, vessel._alt - 40.0)
            if t[0] >= 8.0:
                vessel.recoverable = True

        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=nap,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        scene.assert_not_called()
        self.assertGreaterEqual(t[0], 8.0)
        self.assertEqual(vessel.control.staged, 0)

    def test_frozen_wreck_dismisses_flight_results(self):
        """Paused Flight Results: MET stuck, recoverable never true."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel._speed = 127.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        now, sleep, t = _fast_clock()
        session = _Session(vessel)

        def dismiss(sess, **_kwargs):
            sess.active_vessel = None

        logs: list[str] = []
        with patch("hop.go_space_center", side_effect=dismiss) as scene:
            result = run_on_vessel(
                session,
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                on_log=logs.append,
                now=now,
                sleep=sleep,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        scene.assert_called()
        self.assertIn("recovered", logs)
        self.assertGreaterEqual(t[0], 5.0)
        self.assertLess(t[0], 20.0)

    def test_frozen_wreck_recovers_hop_debris(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        debris = _Vessel([], sit="landed", ec=0.0, recoverable=True)
        debris.name = CRAFT + " Debris"
        debris.met = 75.56
        session = _Session(vessel)
        session.space_center.vessels = [vessel, debris]
        now, sleep, _t = _fast_clock()
        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                session,
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=sleep,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(debris.recovered)
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        scene.assert_called()

    def test_gone_vessel_finishes_hd(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel._alt = 72.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        session = _Session(vessel)
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            session.active_vessel = None

        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                session,
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        scene.assert_called()
        self.assertEqual(vessel.control.staged, 0)

    def test_frozen_wreck_abort_if_dismiss_fails(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        now, sleep, _t = _fast_clock()
        with patch("hop.go_space_center", side_effect=RuntimeError("scene")):
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)

    def test_skip_peri_on_ballistic(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 4_000.0
        vessel.orbit.apoapsis_altitude = 14_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch(
            "phases._kv",
            return_value={
                "hop_apo": "15000",
                "expect_body": "Earth",
                "expect_peri_min": "0",
                "expect_apo_max": "20000",
            },
        ):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")

    def test_science_uplink_does_not_toggle_twice(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 3_000.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.take", return_value=_Uplink("science")):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_cut_throttle_at_hop_apo(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 5_000.0
        vessel.orbit.apoapsis_altitude = 16_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            self.assertEqual(vessel.control.throttle, 0.0)
            vessel.situation = "landed"
            vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("phases._kv", return_value={"hop_apo": "15000"}):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_no_vessel_hangars(self):
        session = _Session(None)  # type: ignore[arg-type]
        session.active_vessel = None
        with patch("hop.run_hop", return_value="recovered") as hop:
            result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()

    def test_pad_motor_hangars_instead_of_lighting(self):
        vessel = _Vessel([])
        vessel.name = "kspstuff-pad-pbc"
        session = _Session(vessel)
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_pulses_write_state_jsonl(self):
        """Each Telem.read lands alt/apo/peri/sit/MET/EC/fuel on the seated jsonl."""
        import flightlog

        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 7.0
        vessel._alt = 2123.0
        vessel.orbit.apoapsis_altitude = 11562.0
        vessel.orbit.periapsis_altitude = -6_362_500.0
        now, sleep, t = _fast_clock()
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        old = (
            flightlog._path,
            flightlog._t0,
            flightlog._count,
            flightlog._last_write,
            flightlog._last_flags,
        )
        flightlog._path = tmp
        flightlog._t0 = time.monotonic()
        flightlog._count = 0
        flightlog._last_write = 0.0
        flightlog._last_flags = None

        def nap(dt):
            t[0] += dt if dt else 0.01
            vessel.met += dt if dt else 0.01
            vessel._alt = max(80.0, vessel._alt - 200.0)
            if t[0] >= 3.0:
                vessel.recoverable = True

        try:
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=nap,
                timeout=2.0,
                pulse=1.0,
            )
        finally:
            (
                flightlog._path,
                flightlog._t0,
                flightlog._count,
                flightlog._last_write,
                flightlog._last_flags,
            ) = old
        self.assertEqual(result, "recovered")
        rows = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        states = [row for row in rows if row.get("kind") == "state"]
        self.assertGreaterEqual(len(states), 3)
        first = states[0]
        self.assertEqual(first["situation"], "flying")
        self.assertAlmostEqual(first["alt"], 2123.0)
        self.assertAlmostEqual(first["apo"], 11562.0)
        self.assertAlmostEqual(first["peri"], -6_362_500.0)
        self.assertAlmostEqual(first["met"], 7.0)
        self.assertEqual(first["ec"], 0.0)
        self.assertEqual(first["fuel"], 5.0)
        alts = [row["alt"] for row in states]
        self.assertGreater(max(alts), min(alts))

    def test_already_launched_hop_skips_hangar(self):
        vessel = _Vessel([])
        vessel.name = CRAFT
        session = _Session(vessel)
        with patch("hop.run_hop") as hop:
            with patch("hop.run_on_vessel", return_value="recovered") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        run.assert_called_once()

    def test_spacecenter_leftover_enters_flight_not_hangar(self):
        """KSC overview + leftover Flea: enter Flight. Do not Hangar."""
        vessel = _Vessel([], sit="pre_launch")
        vessel.name = CRAFT
        session = _Session(vessel)
        entered: list[object] = []

        def fake_flight(sess, v=None, **_kwargs):
            entered.append(v or sess.active_vessel)

        with patch("hop.game_scene", return_value="space_center"):
            with patch("hop.go_flight", side_effect=fake_flight) as gf:
                with patch("hop.run_hop") as hop:
                    with patch(
                        "hop.run_on_vessel", return_value="recovered"
                    ) as run:
                        result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        gf.assert_called()
        self.assertIs(entered[0], vessel)
        run.assert_called_once()
        self.assertIs(run.call_args[0][1], vessel)

    def test_tracking_leftover_enters_flight_when_active_none(self):
        leftover = _Vessel([], sit="pre_launch")
        leftover.name = CRAFT
        session = _Session(None)  # type: ignore[arg-type]
        session.active_vessel = None
        session.space_center.vessels = [leftover]
        with patch("hop.game_scene", return_value="space_center"):
            with patch("hop.go_flight") as gf:
                with patch("hop.run_hop") as hop:
                    with patch(
                        "hop.run_on_vessel", return_value="recovered"
                    ) as run:
                        result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        gf.assert_called()
        self.assertIs(gf.call_args[0][1], leftover)
        self.assertIs(run.call_args[0][1], leftover)


class TestPhaseHopUncrewed(unittest.TestCase):
    def test_cmd_phase_skips_seat(self):
        from main import cmd_phase

        session = _Session(_Vessel([], recoverable=True))
        args = argparse.Namespace(name="hop", timeout=0.0)
        with patch("missions.assert_seated") as seated:
            with patch("hop.run_phase", return_value="recovered"):
                code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 0)

    def test_cmd_hop_skips_seat(self):
        from main import cmd_hop

        session = _Session(_Vessel([], recoverable=True))
        args = argparse.Namespace(timeout=0.0)
        with patch("missions.assert_seated") as seated:
            with patch("hop.run_hop", return_value="recovered"):
                code = cmd_hop(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 0)


class _FakeHangar:
    def __init__(self, root: Path):
        self.root = root
        self.calls: list[dict] = []

    def ships(self, facility: str = "VAB") -> Path:
        path = self.root / facility
        path.mkdir(parents=True, exist_ok=True)
        return path

    def launch(self, session, name, *, recover=True, uncrewed=False, **_kwargs):
        self.calls.append(
            {"name": name, "uncrewed": uncrewed, "recover": recover}
        )
        session.active_vessel = _Vessel([], sit="pre_launch")
        session.active_vessel.name = name


class TestInstallSigned(unittest.TestCase):
    def test_copies_named_file(self):
        from hangar import install_signed

        src = hop_craft_path("kspstuff-hop-hammer-pbc")
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            install_signed(
                session,
                "kspstuff-hop-hammer-pbc",
                hangar=fake,
                src=src,
            )
            dest = fake.ships("VAB") / "kspstuff-hop-hammer-pbc.craft"
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.read_bytes(), src.read_bytes())


class TestHopHangar(unittest.TestCase):
    def test_copies_hammer_not_flea_or_pad(self):
        src = hop_craft_path("kspstuff-hop-hammer-pbc").read_bytes()
        self.assertIn(b"solidBooster", src)
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            with patch("hop.discover_hangar", return_value=fake):
                with patch("hop.hop_craft_name", return_value="kspstuff-hop-hammer-pbc"):
                    install_and_launch(session)
            dest = fake.ships("VAB") / "kspstuff-hop-hammer-pbc.craft"
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.read_bytes(), src)
            text = dest.read_text(encoding="utf-8")
            self.assertNotIn("kspstuff-pad-pbc", text)
            self.assertNotIn("kspstuff-hop-flea-pbc", text)
            self.assertNotIn("kerbalism-geigercounter", text)
            self.assertEqual(fake.calls[0]["name"], "kspstuff-hop-hammer-pbc")
            self.assertTrue(fake.calls[0]["uncrewed"])
            self.assertEqual(session.active_vessel.name, "kspstuff-hop-hammer-pbc")

    def test_refuses_pad_and_geiger_names(self):
        session = _Session(None)  # type: ignore[arg-type]
        for bad in ("kspstuff-pad-pbc", "kspstuff-geiger-pbc"):
            with patch("hop.hop_craft_name", return_value=bad):
                with self.assertRaises(MissionAbort) as ctx:
                    install_and_launch(session)
            self.assertIn("refused", str(ctx.exception))
            self.assertIn(bad, str(ctx.exception))

    def test_missing_ksp_aborts(self):
        session = _Session(None)  # type: ignore[arg-type]
        with patch("hop.hop_craft_name", return_value="kspstuff-hop-hammer-pbc"):
            with patch("hop.discover_hangar", return_value=None):
                with self.assertRaises(MissionAbort) as ctx:
                    install_and_launch(session)
        self.assertIn("KSP", str(ctx.exception))

    def test_run_hop_hangars_then_lights(self):
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            with patch("hop.discover_hangar", return_value=fake):
                with patch("hop.hop_craft_name", return_value="kspstuff-hop-hammer-pbc"):
                    with patch("hop.hop_science_ids", return_value=("temperatureScan",)):
                        with patch("hop.time.sleep"):
                            with patch("hop.run_on_vessel", return_value="recovered") as run:
                                result = run_hop(session)
            self.assertEqual(result, "recovered")
            self.assertEqual(fake.calls[0]["name"], "kspstuff-hop-hammer-pbc")
            self.assertTrue(fake.calls[0]["uncrewed"])
            run.assert_called_once()
            self.assertIs(run.call_args[0][1], session.active_vessel)


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
            },
        )()

    @property
    def game_scene(self):
        return self._scene

    @game_scene.setter
    def game_scene(self, val):
        self._scene = val if hasattr(val, "name") else _Scene(str(val))


class _StuckKrpc(_Krpc):
    @property
    def game_scene(self):
        return self._scene

    @game_scene.setter
    def game_scene(self, val):
        return


class _FlightSession:
    def __init__(self, vessel, scene="space_center", stuck=False):
        self.active_vessel = vessel
        krpc = _StuckKrpc(scene) if stuck else _Krpc(scene)
        sc = type("SC", (), {"active_vessel": vessel})()
        self.space_center = sc
        self.conn = type("C", (), {"krpc": krpc, "space_center": sc})()
        self.switch_settle_s = 0.0

    def require_connected(self):
        return None

    def switch_to(self, vessel, settle=None):
        self.active_vessel = vessel
        if not isinstance(self.conn.krpc, _StuckKrpc):
            self.conn.krpc.game_scene = self.conn.krpc.GameScene.flight


class TestGoFlight(unittest.TestCase):
    def test_enters_flight_from_space_center(self):
        from hangar import go_flight

        vessel = _Vessel([])
        vessel.name = CRAFT
        session = _FlightSession(vessel, scene="space_center")
        with patch("hangar.time.sleep"):
            go_flight(session, vessel, timeout=2.0)
        self.assertEqual(session.conn.krpc.game_scene.name, "flight")

    def test_already_flight_is_noop(self):
        from hangar import go_flight

        vessel = _Vessel([])
        session = _FlightSession(vessel, scene="flight")
        with patch("hangar.time.sleep") as nap:
            go_flight(session, vessel)
        nap.assert_not_called()

    def test_timeout_if_scene_stuck(self):
        from hangar import go_flight
        from session import SessionError

        vessel = _Vessel([])
        vessel.name = CRAFT
        session = _FlightSession(vessel, scene="space_center", stuck=True)
        with patch("hangar.time.sleep"):
            with patch("hangar.time.monotonic", side_effect=[0.0, 1.0, 1.0]):
                with self.assertRaises(SessionError) as ctx:
                    go_flight(session, vessel, timeout=0.01)
        self.assertIn("flight", str(ctx.exception))
        self.assertIn(CRAFT, str(ctx.exception))


class TestLoadSave(unittest.TestCase):
    def test_load_persistent_not_quicksave(self):
        from hangar import load_save
        from session import SessionError

        sc = type("SC", (), {})()
        sc.load = lambda name: setattr(sc, "loaded", name)
        session = type("S", (), {"space_center": sc})()
        self.assertEqual(load_save(session, "rd-engineering101"), "load rd-engineering101")
        self.assertEqual(sc.loaded, "rd-engineering101")
        with self.assertRaises(SessionError):
            load_save(session, "quicksave")
        with self.assertRaises(SessionError):
            load_save(session, "persistent")


class TestWaitVesselReady(unittest.TestCase):
    def test_ready_when_parts_and_flight(self):
        from hangar import wait_vessel_ready

        vessel = _Vessel([])
        session = _FlightSession(vessel, scene="flight")
        with patch("hangar.time.sleep") as nap:
            msg = wait_vessel_ready(session, vessel, timeout=1.0)
        nap.assert_not_called()
        self.assertIn("hangar ready", msg)
        self.assertIn("parts=", msg)

    def test_timeout_if_parts_empty(self):
        from hangar import wait_vessel_ready
        from session import SessionError

        vessel = _Vessel([])
        vessel.parts = _Parts([])
        session = _FlightSession(vessel, scene="flight")
        with patch("hangar.time.sleep"):
            with patch("hangar.time.monotonic", side_effect=[0.0, 0.2, 2.0]):
                with self.assertRaises(SessionError) as ctx:
                    wait_vessel_ready(session, vessel, timeout=1.0)
        self.assertIn("vessel ready", str(ctx.exception))


class TestHopToWater(unittest.TestCase):
    def test_refuses_without_hangar(self):
        session = _Session(None)  # type: ignore[arg-type]
        with patch("hop.install_and_launch") as hangar:
            with self.assertRaises(MissionAbort) as ctx:
                run_hop_to_water(session)
        hangar.assert_not_called()
        self.assertEqual(str(ctx.exception), HOP_TO_WATER_ABORT)
        self.assertIn("no torque", str(ctx.exception))
        self.assertIn("Shores", str(ctx.exception))

    def test_cmd_phase_skips_seat_and_aborts(self):
        from main import cmd_phase

        session = _Session(_Vessel([]))
        args = argparse.Namespace(name="hop-to-water", timeout=0.0)
        with patch("missions.assert_seated") as seated:
            code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 2)

    def test_blocks_name(self):
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertIn("hop-to-water", blocks)
        self.assertIn("Refused", blocks)
