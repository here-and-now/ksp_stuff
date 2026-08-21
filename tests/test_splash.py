"""No-KSP gates for splash: wait Water, goo dwell, recover HD."""

from __future__ import annotations

import argparse
import unittest
from pathlib import Path
from unittest.mock import patch

from science import SPLASH_EXPERIMENTS, card_flying_ids, card_splash_ids
from splash import run_on_vessel, run_phase, splash_science_ids
from telem import MissionAbort


def _fast_clock():
    t = [0.0]

    def now():
        return t[0]

    def sleep(dt):
        t[0] += dt if dt else 0.01

    return now, sleep, t


class _Mod:
    def __init__(self, name, eid, events=None):
        self.name = name
        self.fields = {"experiment_id": eid, "broken": False}
        self.events = list(events or ["Start Experiment"])
        self.triggered: list[str] = []

    def trigger_event(self, name):
        self.triggered.append(name)
        self.fields["status"] = "Running"

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
    def __init__(self, modules, *, recoverable=False, sit="flying", ec=10.0):
        self.name = "kspstuff-hop-flea-pbc"
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


class TestSplashCatalog(unittest.TestCase):
    def test_in_names(self):
        from phases import NAMES

        self.assertIn("splash", NAMES)
        self.assertEqual(SPLASH_EXPERIMENTS, ("mysteryGoo",))

    def test_source_is_not_a_godfile(self):
        text = Path("splash.py").read_text(encoding="utf-8")
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertNotIn("from watch", text)
        self.assertNotIn("import watch", text)
        self.assertNotIn("from launch", text)
        self.assertNotIn("hangar.launch", text)
        self.assertNotIn("parachute", text.lower())
        self.assertIn("Lars Grokman", blocks)

    def test_card_splash_skips_flying(self):
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
        self.assertEqual(card_splash_ids(text), ("mysteryGoo",))
        self.assertNotIn("mysteryGoo", card_flying_ids(text))
        self.assertNotIn("kerbalism_TELEMETRY", card_splash_ids(text))

    def test_live_card_splash_is_goo(self):
        ids = splash_science_ids()
        self.assertEqual(ids, ("mysteryGoo",))


class TestSplashSequence(unittest.TestCase):
    def test_already_splashed_starts_goo_and_recovers(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="splashed", recoverable=False)
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                mod.fields["status"] = "Done"
                mod.fields["Has Data"] = True
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
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertEqual(vessel.control.staged, 0)

    def test_flying_recoverable_waits_for_splash(self):
        """Hop would recover here. Splash must not."""
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying", recoverable=True)
        vessel._alt = 2_000.0
        vessel.orbit.apoapsis_altitude = 8_000.0
        now, sleep, t = _fast_clock()
        flying_recovered = []

        def nap(dt):
            if vessel.situation == "flying":
                flying_recovered.append(vessel.recovered)
                if t[0] >= 2.0:
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and mod.triggered:
                mod.fields["status"] = "Done"
                mod.fields["Has Data"] = True
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
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertTrue(flying_recovered)
        self.assertFalse(any(flying_recovered))
        self.assertEqual(vessel.control.staged, 0)

    def test_landed_aborts_not_splashed(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="landed", recoverable=True)
        now, sleep, _t = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=5.0,
                pulse=1.0,
            )
        self.assertIn("not splashed", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(mod.triggered, [])

    def test_no_vessel_does_not_hangar(self):
        session = _Session(None)  # type: ignore[arg-type]
        session.active_vessel = None
        session.space_center.vessels = []
        with patch("splash.run_on_vessel") as run:
            with self.assertRaises(MissionAbort) as ctx:
                run_phase(session)
        self.assertIn("hop leftover", str(ctx.exception))
        run.assert_not_called()

    def test_pad_motor_refused(self):
        vessel = _Vessel([], sit="splashed")
        vessel.name = "kspstuff-pad-pbc"
        with self.assertRaises(MissionAbort) as ctx:
            run_phase(_Session(vessel))
        self.assertIn("hop leftover", str(ctx.exception))


class TestSplashCli(unittest.TestCase):
    def test_cmd_splash_skips_seat(self):
        from main import cmd_splash

        session = _Session(_Vessel([], sit="splashed", recoverable=True))
        args = argparse.Namespace(timeout=0.0)
        with patch("missions.assert_seated") as seated:
            with patch("splash.run_splash", return_value="recovered"):
                code = cmd_splash(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 0)

    def test_cmd_phase_splash_skips_seat(self):
        from main import cmd_phase

        session = _Session(_Vessel([], sit="splashed", recoverable=True))
        args = argparse.Namespace(name="splash", timeout=0.0)
        with patch("missions.assert_seated") as seated:
            with patch("splash.run_phase", return_value="recovered"):
                code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 0)
