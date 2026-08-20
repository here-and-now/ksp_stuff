"""cmd_phase pad: uncrewed probe, no seat, no heartbeat after recover."""

from __future__ import annotations

import argparse
import unittest
from unittest.mock import patch

from main import cmd_phase


class _Body:
    name = "Earth"
    has_atmosphere = True
    atmosphere_depth = 140_000.0


class _Control:
    throttle = 0.0

    def activate_next_stage(self):
        pass


class _ExpMod:
    def __init__(self):
        self.name = "Experiment"
        self.fields = {
            "experiment_id": "geigerCounter",
            "broken": False,
            "Has Data": True,
            "status": "Done",
        }
        self.events = ["Start Experiment"]
        self.triggered: list[str] = []

    def trigger_event(self, name):
        self.triggered.append(name)

    def get_field(self, key):
        return self.fields[key]


class _Vessel:
    def __init__(self, session):
        self.name = "probe"
        self.situation = "pre_launch"
        self.recoverable = True
        self.recovered = False
        self.crew = []
        self.control = _Control()
        self.resources = type(
            "R", (), {"amount": lambda self, n: {"ElectricCharge": 10.0, "SolidFuel": 5}.get(n, 0)}
        )()
        self.thrust = 0.0
        core = type("Part", (), {"name": "probeCoreSphere.v2", "modules": [_ExpMod()]})()
        self.parts = type("P", (), {"all": [core]})()
        self.orbit = type(
            "O",
            (),
            {
                "body": _Body(),
                "periapsis_altitude": -500_000.0,
                "apoapsis_altitude": 80.0,
                "eccentricity": 0.99,
                "semi_major_axis": 6.4e6,
                "time_to_periapsis": 0.0,
                "time_to_apoapsis": 1.0,
            },
        )()
        self._session = session

    def flight(self):
        return type(
            "F",
            (),
            {
                "mean_altitude": 80.0,
                "dynamic_pressure": 0.0,
                "surface_altitude": 80.0,
                "speed": 0.0,
            },
        )()

    def recover(self):
        self.recovered = True
        self._session.active_vessel = None


class _Session:
    def __init__(self):
        self.active_vessel = None
        self.space_center = type("SC", (), {"vessels": []})()
        v = _Vessel(self)
        self.active_vessel = v
        self.space_center.vessels = [v]

    def add_stream(self, func, obj, name):
        class _S:
            def __call__(self_inner):
                return func(obj, name)

            def remove(self_inner):
                pass

        return _S()


class TestUnknownPhase(unittest.TestCase):
    def test_names_pad_and_hop(self):
        from phases import NAMES

        self.assertEqual(
            NAMES, ("pad", "hop", "splash", "hop-to-water", "tech-unlock")
        )

    def test_need_stack_message(self):
        from phases import run
        from telem import MissionAbort

        with self.assertRaises(MissionAbort) as ctx:
            run("mun", None)  # type: ignore[arg-type]
        self.assertIn("need_stack", str(ctx.exception))
        self.assertIn("blocks.md", str(ctx.exception))


class TestPhasePad(unittest.TestCase):
    def test_uncrewed_recover_skips_seat_and_heartbeat(self):
        session = _Session()
        args = argparse.Namespace(name="pad", timeout=0.0, keep_debris=False)
        # assert_seated would SESSION (crew=[] vs Jeb). heartbeat after
        # recover would MissionAbort (no vessel). Skip both → 0.
        with patch("pad.time.sleep"):
            code = cmd_phase(session, args)
        self.assertEqual(code, 0)
        self.assertIsNone(session.active_vessel)
