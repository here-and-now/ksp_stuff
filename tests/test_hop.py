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
    FLYING_HIGH_M,
    FLYING_LOW_M,
    HOP_TO_WATER_ABORT,
    WATER_CRAFT,
    WATER_HEADING_DEG,
    WATER_PITCH_DEG,
    WATER_PITCH_FROM_UP,
    WATER_PITCH_SLEW_DPS,
    WATER_PITCH_UP,
    WATER_SLEW_THROTTLE,
    hop_craft_name,
    hop_craft_path,
    hop_offplan_apo,
    hop_science_alt,
    hop_science_ids,
    hop_target_apo,
    install_and_launch,
    leftover_wreck_before_light,
    _wait_vessel_gone,
    run_hop,
    run_hop_to_water,
    run_on_vessel,
    run_phase,
    water_can_steer,
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


class _Autopilot:
    def __init__(self):
        self.engaged = False
        self.target_pitch = 0.0
        self.target_heading = 0.0
        self.target_roll = 0.0

    def engage(self):
        self.engaged = True

    def disengage(self):
        self.engaged = False


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


class _DeadVessel:
    """kRPC active_vessel proxy whose GUID is already gone."""

    def __init__(self, guid="fbacb1ed-301a-4b89-b2ff-19b3483f6fd8"):
        self._guid = guid

    @property
    def name(self):
        raise ValueError(f"No such vessel {self._guid}")


class _Vessel:
    def __init__(self, modules, *, recoverable=False, sit="pre_launch", ec=10.0):
        self.name = "probe"
        self.situation = sit
        self.recoverable = recoverable
        self.recovered = False
        self.control = _Control()
        self.auto_pilot = _Autopilot()
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
        gs = type(
            "GS",
            (),
            {
                "tracking_station": "tracking_station",
                "space_center": "space_center",
                "flight": "flight",
            },
        )()
        krpc = type("K", (), {"GameScene": gs, "game_scene": "flight"})()
        self.conn = type("C", (), {"krpc": krpc})()

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
        self.assertIn("run_physics", text)
        self.assertIn("go_space_center", text)
        self.assertIn("from hangar import", text)
        self.assertIn("kspstuff-hop-hammer-pbc", text)
        self.assertIn("uncrewed", blocks.lower())
        self.assertIn("kspstuff-hop-hammer-pbc", blocks)

    def test_apo_clamp(self):
        with patch("hop.hop_wants_flying_high", return_value=False):
            with patch("phases._kv", return_value={"hop_apo": "15000"}):
                self.assertEqual(hop_target_apo(), 15_000.0)
            with patch("phases._kv", return_value={"hop_apo": "18000"}):
                self.assertEqual(hop_target_apo(), 18_000.0)
            with patch("phases._kv", return_value={"hop_apo": "40000"}):
                self.assertEqual(hop_target_apo(), 18_000.0)
            with patch("phases._kv", return_value={"hop_apo": "1000"}):
                self.assertEqual(hop_target_apo(), 8_000.0)
        with patch("hop.hop_wants_flying_high", return_value=False):
            self.assertEqual(hop_science_alt(), 0.0)

    def test_apo_unclamp_flyinghigh(self):
        with patch("hop.hop_wants_flying_high", return_value=True):
            self.assertEqual(hop_offplan_apo(), FLYING_HIGH_M)
            self.assertEqual(hop_science_alt(), FLYING_LOW_M)
            with patch("phases._kv", return_value={"hop_apo": "80000"}):
                self.assertEqual(hop_target_apo(), 80_000.0)
            with patch("phases._kv", return_value={"hop_apo": "40000"}):
                self.assertEqual(hop_target_apo(), 40_000.0)
            with patch("phases._kv", return_value={"hop_apo": "200000"}):
                self.assertEqual(hop_target_apo(), FLYING_HIGH_M)
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
    def setUp(self):
        # Live seated card may be FlyingHigh; sequence stubs fly at 2 km.
        self._fh = patch("hop.hop_wants_flying_high", return_value=False)
        self._fh.start()
        self.addCleanup(self._fh.stop)

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
        with patch("hop.hop_wants_flying_high", return_value=False):
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

    def test_flyinghigh_80km_is_not_offplan(self):
        """Valiant loft 80 km is FlyingHigh, under Space 140 km."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 55_000.0
                vessel.orbit.apoapsis_altitude = 80_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "80000"}):
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
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_flyinghigh_toggle_only_at_50km(self):
        """Bound FlyingHigh: do not Toggle at T+1 FlyingLow (~100 m)."""
        from hop import FLYING_LOW_M

        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()
        alts: list[float] = []
        logs: list[str] = []

        def trigger_event(name):
            alts.append(vessel._alt)
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        mod.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 100.0
                vessel.orbit.apoapsis_altitude = 80_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and vessel._alt < FLYING_LOW_M:
                vessel._alt = 50_400.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "splashed"
                vessel._alt = -0.3
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "80000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertEqual(alts, [50_400.0])
        self.assertTrue(any("science wait FlyingHigh" in line for line in logs))
        self.assertGreaterEqual(min(alts), FLYING_LOW_M)

    def test_flyinghigh_never_lid_does_not_toggle_crumbs(self):
        """Down below 50 km with a FlyingHigh card: abort, no FlyingLow Toggle."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 100.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("FlyingHigh lid", str(ctx.exception))
        self.assertEqual(mod.triggered, [])

    def test_flyinghigh_space_is_offplan(self):
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 80_000.0
        vessel.orbit.apoapsis_altitude = 150_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        with patch("hop.hop_wants_flying_high", return_value=True):
            with self.assertRaises(OffPlan) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=sleep,
                    timeout=5.0,
                    pulse=1.0,
                )
        self.assertIn("apo", str(ctx.exception))
        self.assertIn("Space", str(ctx.exception))
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

    def test_frozen_wreck_unpause_then_recover(self):
        """Living recover: unpause frozen MET, then recover() — not dismiss."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 65.8
        vessel._alt = 74.0
        vessel._speed = 127.0
        vessel.orbit.apoapsis_altitude = 315.0
        vessel.orbit.periapsis_altitude = -6_362_000.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def unpause(_session):
            vessel.recoverable = True

        with patch("hop.run_physics", side_effect=unpause) as physics:
            with patch("hop.go_space_center") as scene:
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        physics.assert_called()
        scene.assert_not_called()
        self.assertIn("hop unpause", logs)
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertGreaterEqual(t[0], 5.0)

    def test_frozen_wreck_dismiss_without_recover_aborts(self):
        """Catastrophic flying recoverable=no: Space Center, abort, no wait landed."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel._speed = 0.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        now, sleep, t = _fast_clock()
        session = _Session(vessel)

        def dismiss(sess, **_kwargs):
            sess.active_vessel = None

        logs: list[str] = []
        with patch("hop.go_space_center", side_effect=dismiss) as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    session,
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        scene.assert_not_called()
        self.assertIn("hop unpause", logs)
        self.assertTrue(any("hop crash ui sit=flying recoverable=no" in line for line in logs))
        self.assertTrue(
            any("tracking (not pad reload)" in line for line in logs)
        )
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertNotIn("hop wait landed recoverable=yes", logs)
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertFalse(any(line.startswith("recovered") for line in logs))
        self.assertLess(t[0], 15.0)

    def test_lithobrake_q0_flying_is_down_now(self):
        """Lit hop, MET-still + q=0: unpause once; recover if sit=landed."""
        mod = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=9.9)
        vessel.name = CRAFT
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("kerbalism-geigercounter", [mod])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        order: list[str] = []

        def recover():
            order.append("recover")
            if vessel.situation not in ("landed", "splashed") and not vessel.recoverable:
                raise RuntimeError("not recoverable")
            vessel.recovered = True

        vessel.recover = recover

        def nap(dt):
            t[0] += dt if dt else 0.01
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 1_200.0
                vessel.orbit.apoapsis_altitude = 7_500.0
                vessel.orbit.periapsis_altitude = -6_362_000.0
                vessel.met = 10.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel._alt = 75.0
                vessel._speed = 0.0
                vessel._flight.dynamic_pressure = 0.0
                vessel.orbit.apoapsis_altitude = 327.0
                vessel.met = 65.0
                vessel.resources.ec = 9.9

        def unpause(_session):
            vessel.situation = "landed"
            vessel._alt = 78.0
            vessel.recoverable = True

        with patch("hop.run_physics", side_effect=unpause) as physics:
            with patch("hop.go_space_center") as scene:
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        physics.assert_called()
        self.assertIn("recover", order)
        self.assertIn("hop unpause", logs)
        self.assertTrue(any("recovered sit=landed" in line for line in logs))
        self.assertGreaterEqual(t[0], 5.0)
        self.assertLess(t[0], 25.0)
        self.assertEqual(vessel.situation, "landed")

    def test_lithobrake_q0_unpause_recovers_flying(self):
        """Living recover after MET-still q=0: recover() before dismiss."""
        mod = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=9.9)
        vessel.name = CRAFT
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("kerbalism-geigercounter", [mod])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            t[0] += dt if dt else 0.01
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 1_200.0
                vessel.orbit.apoapsis_altitude = 7_500.0
                vessel.orbit.periapsis_altitude = -6_362_000.0
                vessel.met = 10.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel._alt = 75.0
                vessel._speed = 0.0
                vessel._flight.dynamic_pressure = 0.0
                vessel.orbit.apoapsis_altitude = 327.0
                vessel.met = 65.0

        def unpause(_session):
            vessel.recoverable = True

        with patch("hop.run_physics", side_effect=unpause) as physics:
            with patch("hop.go_space_center") as scene:
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        physics.assert_called()
        scene.assert_not_called()
        self.assertIn("hop unpause", logs)
        self.assertTrue(any("sit=flying recoverable=yes" in line for line in logs))
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertGreaterEqual(t[0], 5.0)
        self.assertLess(t[0], 20.0)

    def test_dismiss_prelaunch_is_not_hop_hd(self):
        """11-09-13Z: do not dismiss flying recoverable=no; pre_launch is not HD."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 65.8
        vessel._alt = 75.0
        vessel._speed = 0.0
        vessel.orbit.apoapsis_altitude = 307.0
        vessel.orbit.periapsis_altitude = -6_362_000.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        session = _Session(vessel)

        def dismiss(*_a, **_k):
            vessel.situation = "pre_launch"
            vessel.recoverable = True

        with patch("hop.go_space_center", side_effect=dismiss) as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    session,
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        self.assertIn("hop crash ui tracking (not pad reload)", logs)
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertFalse(any(line.startswith("recovered") for line in logs))
        self.assertLess(t[0], 15.0)

    def test_low_flying_recovers_in_flight(self):
        """~199 m flying: recover() while still Flight, before lithobrake."""
        mod = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=9.9)
        vessel.name = CRAFT
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("kerbalism-geigercounter", [mod])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        order: list[str] = []

        def recover():
            order.append("recover")
            vessel.recovered = True

        vessel.recover = recover

        def nap(dt):
            t[0] += dt if dt else 0.01
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 1_200.0
                vessel.orbit.apoapsis_altitude = 7_500.0
                vessel.orbit.periapsis_altitude = -6_362_000.0
                vessel.met = 10.0
            elif vessel.situation == "flying" and mod.triggered and not vessel.recovered:
                vessel._alt = 199.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 2_800.0
                vessel.orbit.apoapsis_altitude = 430.0
                vessel.met = 64.0
                vessel.recoverable = True

        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("geigerCounter",),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        scene.assert_not_called()
        self.assertIn("recover", order)
        self.assertTrue(any("recovered sit=flying" in line for line in logs))
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertLess(t[0], 15.0)

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
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    session,
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("no vessel", str(ctx.exception))
        scene.assert_not_called()
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)

    def test_frozen_wreck_abort_if_dismiss_fails(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        now, sleep, t = _fast_clock()
        with patch("hop.go_space_center", side_effect=RuntimeError("scene")) as scene:
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
        scene.assert_not_called()
        self.assertEqual(vessel.control.staged, 0)
        self.assertLess(t[0], 15.0)

    def test_crash_ui_frozen_landed_not_recoverable_dismisses(self):
        """13-58-18Z: sit=landed recoverable=no MET frozen — Close, no unpause."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 400.0
        vessel._alt = 2_000.0
        vessel._speed = 80.0
        vessel._flight.dynamic_pressure = 32_700.0
        vessel.orbit.apoapsis_altitude = 90_000.0
        vessel.orbit.periapsis_altitude = -6_361_632.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        landed = [False]

        def nap(dt):
            t[0] += dt if dt else 0.01
            if t[0] >= 2.0 and not landed[0]:
                landed[0] = True
                vessel.situation = "landed"
                vessel._alt = 32.95
                vessel._speed = 0.0
                vessel._flight.dynamic_pressure = 0.0
                vessel.met = 407.46
            elif not landed[0]:
                vessel.met += dt if dt else 0.01

        with patch("hop.go_space_center") as scene:
            with patch("hop.run_physics") as physics:
                with self.assertRaises(MissionAbort) as ctx:
                    run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=("geigerCounter",),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=30.0,
                        pulse=1.0,
                    )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        physics.assert_called()
        self.assertTrue(
            any(
                "hop crash ui sit=landed recoverable=no" in line
                and "met=407.46" in line
                and "alt=33.0" in line
                for line in logs
            )
        )
        self.assertIn("hop crash ui tracking (not pad reload)", logs)
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertIn("hop unpause", logs)
        self.assertNotIn("hop paused wreck", logs)
        self.assertNotIn("hop finish wreck", logs)
        self.assertFalse(any(line.startswith("recovered") for line in logs))
        self.assertLess(t[0], 15.0)
        self.assertGreaterEqual(t[0], 6.0)

    def test_crash_ui_frozen_flying_dismisses_now(self):
        """12-04-13Z: frozen flying q=0 alt~74 is crash UI, not wait landed."""
        vessel = _Vessel([], sit="flying", ec=9.9, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 67.62
        vessel._alt = 74.03
        vessel._speed = 0.0
        vessel._flight.dynamic_pressure = 0.0
        vessel.orbit.apoapsis_altitude = 292.0
        vessel.orbit.periapsis_altitude = -6_362_935.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        with patch("hop.go_space_center") as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        self.assertTrue(
            any(
                "hop crash ui sit=flying recoverable=no" in line
                and "met=67.62" in line
                and "alt=74.0" in line
                and "q=0" in line
                for line in logs
            )
        )
        self.assertIn("hop crash ui tracking (not pad reload)", logs)
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertNotIn("hop wait landed recoverable=yes", logs)
        self.assertLess(t[0], 15.0)
        self.assertGreaterEqual(t[0], 5.0)

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
        with patch("hop.hop_match_name", return_value=CRAFT):
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

        with patch("hop.hop_match_name", return_value=CRAFT):
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
        with patch("hop.hop_match_name", return_value=CRAFT):
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

    def test_dead_active_guid_scans_pool(self):
        """Dead kRPC GUID is not leftover. Living tracking Flea enters Flight."""
        leftover = _Vessel([], sit="pre_launch")
        leftover.name = CRAFT
        dead = _DeadVessel()
        session = _Session(dead)
        session.space_center.vessels = [dead, leftover]
        with patch("hop.hop_match_name", return_value=CRAFT):
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

    def test_dead_active_empty_pool_hangars(self):
        """Tracking empty: dead GUID is not leftover. Hangar."""
        dead = _DeadVessel()
        session = _Session(dead)
        session.space_center.vessels = [dead]
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_flying_debris_is_not_leftover(self):
        """Live pool Debris FLYING is not leftover. Hangar (I-017)."""
        ghost = _Vessel([], sit="flying")
        ghost.name = f"{CRAFT} Debris"
        session = _Session(ghost)
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_dead_guid_plus_flying_debris_hangars(self):
        """Ghost FLYING debris in the pool is not leftover. Hangar."""
        dead = _DeadVessel()
        ghost = _Vessel([], sit="flying")
        ghost.name = f"{CRAFT} Debris"
        session = _Session(dead)
        session.space_center.vessels = [dead, ghost]
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_unmatched_flea_recovers_without_light(self):
        """PRELAUNCH Flea vs seated Valiant: recover, do not light, then Hangar."""
        flea = _Vessel([], sit="pre_launch", recoverable=True)
        flea.name = CRAFT
        session = _Session(flea)
        logs: list[str] = []
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-valiant-pbc"
        ):
            with patch("hop.run_hop", return_value="recovered") as hop:
                with patch("hop.run_on_vessel") as run:
                    result = run_phase(session, on_log=logs.append)
        self.assertEqual(result, "recovered")
        self.assertTrue(flea.recovered)
        self.assertEqual(flea.control.staged, 0)
        hop.assert_called_once()
        run.assert_not_called()
        self.assertTrue(any("unmatched" in line for line in logs))
        self.assertTrue(any("do not light" in line for line in logs))

    def test_unmatched_flea_not_recoverable_does_not_hangar(self):
        flea = _Vessel([], sit="pre_launch", recoverable=False)
        flea.name = CRAFT
        session = _Session(flea)
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-valiant-pbc"
        ):
            with patch("hop.run_hop") as hop:
                with patch("hop.run_on_vessel") as run:
                    with self.assertRaises(MissionAbort) as ctx:
                        run_phase(session)
        self.assertIn("unmatched leftover not recoverable", str(ctx.exception))
        self.assertFalse(flea.recovered)
        self.assertEqual(flea.control.staged, 0)
        hop.assert_not_called()
        run.assert_not_called()

    def test_cli_hop_recovers_unmatched_before_hangar(self):
        flea = _Vessel([], sit="pre_launch", recoverable=True)
        flea.name = CRAFT
        session = _Session(flea)
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-valiant-pbc"
        ):
            with patch("hop.hop_science_ids", return_value=("temperatureScan",)):
                with patch("hop.install_and_launch") as hangar:
                    with patch("hop.wait_vessel_ready", return_value="ready"):
                        with patch(
                            "hop.run_on_vessel", return_value="recovered"
                        ) as run:
                            result = run_hop(session)
        self.assertEqual(result, "recovered")
        self.assertTrue(flea.recovered)
        self.assertEqual(flea.control.staged, 0)
        hangar.assert_called_once()
        run.assert_called_once()

    def test_hop_name_with_geiger_pbc_is_leftover_not_pad(self):
        """Substring geiger-pbc is not the pad motor (I-013)."""
        vessel = _Vessel([])
        vessel.name = "kspstuff-hop-flea-geiger-pbc"
        session = _Session(vessel)
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-flea-geiger-pbc"
        ):
            with patch("hop.run_hop") as hop:
                with patch("hop.run_on_vessel", return_value="recovered") as run:
                    result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        run.assert_called_once()


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

    def test_allows_hop_name_containing_geiger_pbc(self):
        """Refuse exact pad/geiger names, not substring geiger-pbc (I-013)."""
        session = _Session(None)  # type: ignore[arg-type]
        session.active_vessel = None
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            with patch(
                "hop.hop_craft_name", return_value="kspstuff-hop-flea-geiger-pbc"
            ):
                with patch("hop.discover_hangar", return_value=fake):
                    with patch("hangar.install_signed", return_value="ok") as inst:
                        install_and_launch(session)
        inst.assert_called_once()
        self.assertEqual(inst.call_args.args[1], "kspstuff-hop-flea-geiger-pbc")

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
    def test_flea_refuses_without_hangar(self):
        session = _Session(None)  # type: ignore[arg-type]
        with patch("hop.hop_craft_name", return_value=CRAFT):
            with patch("hop.install_and_launch") as hangar:
                with self.assertRaises(MissionAbort) as ctx:
                    run_hop_to_water(session)
        hangar.assert_not_called()
        self.assertEqual(str(ctx.exception), HOP_TO_WATER_ABORT)
        self.assertIn("no torque", str(ctx.exception))
        self.assertIn("Shores", str(ctx.exception))

    def test_steer_gate(self):
        self.assertFalse(water_can_steer(CRAFT))
        self.assertFalse(water_can_steer("kspstuff-hop-hammer-pbc"))
        self.assertTrue(water_can_steer(WATER_CRAFT))
        self.assertTrue(water_can_steer("kspstuff-hop-valiant-t7-pbc"))
        self.assertEqual(WATER_PITCH_FROM_UP, 25.0)
        self.assertEqual(WATER_PITCH_UP, 90.0)
        self.assertEqual(WATER_PITCH_DEG, 65.0)
        self.assertEqual(WATER_PITCH_SLEW_DPS, 10.0)
        self.assertEqual(WATER_SLEW_THROTTLE, 0.4)
        self.assertEqual(WATER_HEADING_DEG, 90.0)
        self.assertTrue(hop_craft_path(WATER_CRAFT).is_file())

    def test_valiant_hangars(self):
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            with patch("hop.discover_hangar", return_value=fake):
                with patch("hop.hop_craft_name", return_value=WATER_CRAFT):
                    with patch(
                        "hop.hop_to_water_science",
                        return_value=(("temperatureScan",), ("mysteryGoo",)),
                    ):
                        with patch("hop.time.sleep"):
                            with patch(
                                "hop.run_on_vessel", return_value="recovered"
                            ) as run:
                                result = run_hop_to_water(session)
            self.assertEqual(result, "recovered")
            self.assertEqual(fake.calls[0]["name"], WATER_CRAFT)
            run.assert_called_once()
            kwargs = run.call_args.kwargs
            self.assertTrue(kwargs.get("wait_water"))
            self.assertEqual(kwargs.get("splash_ids"), ("mysteryGoo",))
            self.assertEqual(kwargs.get("science_ids"), ("temperatureScan",))

    def test_cmd_phase_skips_seat_and_aborts_flea(self):
        from main import cmd_phase

        session = _Session(_Vessel([]))
        args = argparse.Namespace(name="hop-to-water", timeout=0.0)
        with patch("hop.hop_craft_name", return_value=CRAFT):
            with patch("missions.assert_seated") as seated:
                code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 2)

    def test_blocks_name(self):
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertIn("hop-to-water", blocks)
        self.assertIn("25", blocks)
        self.assertIn("valiant-east-pbc", blocks)
        self.assertIn("Flea still", blocks)
        self.assertIn("do not light", blocks)
        self.assertIn("PRELAUNCH is a lie", blocks)
        self.assertIn("through burnout", blocks)
        self.assertIn("after left_pad", blocks)
        self.assertIn("0.4", blocks)
        self.assertIn("16-11-58Z", blocks)

    def test_pitch_east_waits_splash(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        flying_recovered: list[bool] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "flying":
                flying_recovered.append(vessel.recovered)
                if tel.triggered:
                    vessel.recoverable = True
                if t[0] >= 5.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(flying_recovered)
        self.assertFalse(any(flying_recovered))
        self.assertEqual(vessel.auto_pilot.target_pitch, WATER_PITCH_DEG)
        self.assertEqual(vessel.auto_pilot.target_heading, WATER_HEADING_DEG)
        self.assertFalse(vessel.auto_pilot.engaged)
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(goo.triggered, ["Start Experiment"])
        self.assertTrue(
            any(
                f"{WATER_PITCH_FROM_UP:g}" in line and "east" in line
                for line in logs
            )
        )

    def test_holds_ap_east_through_burnout(self):
        """15-26-18Z: do not disengage AP at fuel=0 while still flying."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        dry_engaged: list[bool] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "flying":
                if vessel.resources.fuel <= 0:
                    dry_engaged.append(vessel.auto_pilot.engaged)
                if vessel.resources.fuel > 0 and t[0] >= 2.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                elif vessel.resources.fuel <= 0 and t[0] >= 4.0:
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(dry_engaged)
        self.assertTrue(all(dry_engaged))
        self.assertFalse(vessel.auto_pilot.engaged)
        self.assertTrue(
            any("hold east through burnout" in line for line in logs)
        )

    def test_slew_east_after_pad_low_throttle(self):
        """16-11-58Z: do not slam AP 65 at light TWR 5 (bare stack shears)."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        pad_pitch: list[float] = []
        pad_engaged: list[bool] = []
        air_pitch: list[float] = []
        air_throt: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                pad_pitch.append(vessel.auto_pilot.target_pitch)
                pad_engaged.append(vessel.auto_pilot.engaged)
                vessel.situation = "landed"
                vessel._alt = 40.0
                vessel._speed = 20.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "landed":
                pad_pitch.append(vessel.auto_pilot.target_pitch)
                pad_engaged.append(vessel.auto_pilot.engaged)
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
            elif vessel.situation == "flying":
                air_pitch.append(vessel.auto_pilot.target_pitch)
                air_throt.append(vessel.control.throttle)
                if tel.triggered:
                    vessel.recoverable = True
                if t[0] >= 6.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(pad_pitch)
        self.assertTrue(all(p != WATER_PITCH_DEG for p in pad_pitch))
        self.assertTrue(all(not e for e in pad_engaged))
        self.assertTrue(air_pitch)
        self.assertLess(air_pitch[0], WATER_PITCH_UP)
        self.assertGreater(air_pitch[0], WATER_PITCH_DEG)
        self.assertTrue(any(abs(th - WATER_SLEW_THROTTLE) < 1e-6 for th in air_throt))
        self.assertEqual(vessel.auto_pilot.target_pitch, WATER_PITCH_DEG)
        self.assertTrue(any("slew" in line and "after pad" in line for line in logs))

    def test_landed_aborts_not_splashed(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([tel], recoverable=True, sit="pre_launch")
        vessel.name = WATER_CRAFT
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
            elif vessel.situation == "flying" and tel.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                splash_ids=("mysteryGoo",),
                wait_water=True,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertIn("not splashed", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_pad_landed_after_light_is_not_shores(self):
        """14-45-33Z: KSP sit=landed on pad hop-off is not a Shores miss."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "landed"
                vessel._alt = 97.0
                vessel._speed = 49.2
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
                vessel.thrust = 89_000.0
            elif vessel.situation == "landed":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
            elif vessel.situation == "flying":
                if tel.triggered:
                    vessel.recoverable = True
                if t[0] >= 3.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertGreaterEqual(vessel.control.staged, 1)
        self.assertTrue(any("pitch" in line and "east" in line for line in logs))
        self.assertFalse(any("not splashed" in line for line in logs))

    def test_leftover_wreck_fuel0_does_not_light_or_science(self):
        """14-52-25Z: leftover flying MET 13.8 fuel=0 is crash UI, not a pad."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([tel, thermo], sit="flying", ec=9.3, recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.met = 13.8
        vessel._alt = 83.2
        vessel._speed = 0.0
        vessel.thrust = 0.0
        vessel.resources.fuel = 0.0
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        with patch("hop.go_space_center") as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan", "kerbalism_TELEMETRY"),
                    splash_ids=("mysteryGoo",),
                    wait_water=True,
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(tel.triggered, [])
        self.assertEqual(thermo.triggered, [])
        scene.assert_not_called()
        self.assertTrue(any("do not light" in line for line in logs))
        self.assertTrue(
            any("sit=flying" in line and "fuel=0.0" in line for line in logs)
        )
        self.assertNotIn("hop airborne", logs)
        self.assertFalse(any(line.startswith("science ") for line in logs))
        self.assertIn("hop crash ui tracking (not pad reload)", logs)
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertLess(t[0], 5.0)

    def test_leftover_wreck_recoverable_recovers_without_science(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([tel], sit="flying", ec=9.3, recoverable=True)
        vessel.name = WATER_CRAFT
        vessel.met = 13.8
        vessel._alt = 83.2
        vessel._speed = 0.0
        vessel.resources.fuel = 0.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=sleep,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(tel.triggered, [])
        self.assertTrue(any("do not light" in line for line in logs))
        self.assertLess(t[0], 2.0)

    def test_hop_to_water_leftover_wreck_does_not_hangar(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([tel], sit="flying", ec=9.3, recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.met = 13.8
        vessel._alt = 83.2
        vessel._speed = 0.0
        vessel.resources.fuel = 0.0
        session = _Session(vessel)
        with patch("hop.hop_craft_name", return_value=WATER_CRAFT):
            with patch("hop.hop_match_name", return_value=WATER_CRAFT):
                with patch(
                    "hop.hop_to_water_science",
                    return_value=(("kerbalism_TELEMETRY",), ("mysteryGoo",)),
                ):
                    with patch("hop.install_and_launch") as hangar:
                        with patch("hop.go_space_center"):
                            with patch("hop.time.sleep"):
                                with self.assertRaises(MissionAbort) as ctx:
                                    run_hop_to_water(session)
        self.assertIn("not recoverable", str(ctx.exception))
        hangar.assert_not_called()
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(tel.triggered, [])

    def test_leftover_wreck_predicate_dry_flying(self):
        snap = type(
            "S",
            (),
            {
                "situation": "flying",
                "fuel": 0.0,
                "q": 0.0,
                "speed": 0.0,
            },
        )()
        vessel = _Vessel([], sit="flying", recoverable=False)
        self.assertTrue(leftover_wreck_before_light(snap, vessel))
        snap.fuel = 5.0
        self.assertFalse(leftover_wreck_before_light(snap, vessel))
        snap.fuel = 0.0
        snap.speed = 80.0
        snap.q = 1200.0
        self.assertFalse(leftover_wreck_before_light(snap, vessel))
        pad = type("S", (), {"situation": "pre_launch", "fuel": 0.0, "q": 0.0, "speed": 0.0})()
        self.assertTrue(leftover_wreck_before_light(pad, vessel))
        pad.fuel = 5.0
        self.assertFalse(leftover_wreck_before_light(pad, vessel))


class TestWaitVesselGone(unittest.TestCase):
    def test_returns_when_pool_empty(self):
        session = type(
            "S", (), {"space_center": type("C", (), {"vessels": []})()}
        )()
        vessel = _Vessel([], sit="pre_launch", recoverable=True)
        logs: list[str] = []
        with patch("hop._vessel_live", return_value=False):
            with patch("hop._pool", return_value=[]):
                _wait_vessel_gone(session, vessel, logs.append, timeout=1.0)
        self.assertTrue(any("gone" in line for line in logs))
