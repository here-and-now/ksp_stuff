"""Pad-RF sit: hop_factory_pad is the named helper. Not the house."""

from __future__ import annotations

import unittest
from pathlib import Path

from hop_factory_pad import _pad_hold, _pad_light, _pad_rf_snap, _rf_pad_sit
from telem import MissionAbort


class _Control:
    def __init__(self):
        self.throttle = 0.0
        self.sas = False
        self.staged = 0

    def activate_next_stage(self):
        self.staged += 1


class _Engine:
    """kRPC Engine: re-enabling independent zeros Current Throttle."""

    def __init__(self):
        self._independent = False
        self._throttle = 0.0
        self.independent_sets = 0

    @property
    def independent_throttle(self):
        return self._independent

    @independent_throttle.setter
    def independent_throttle(self, value):
        self.independent_sets += 1
        value = bool(value)
        if value:
            self._throttle = 0.0
        self._independent = value

    @property
    def throttle(self):
        return self._throttle

    @throttle.setter
    def throttle(self, value):
        if self._independent:
            self._throttle = float(value)


class _Parts:
    def __init__(self):
        self.engines: list = []


class _Vessel:
    def __init__(self):
        self.control = _Control()
        self.parts = _Parts()


class _ColdEngine:
    def __init__(self):
        self._throttle = 0.0

    @property
    def independent_throttle(self):
        return False

    @independent_throttle.setter
    def independent_throttle(self, value):
        return

    @property
    def throttle(self):
        return self._throttle

    @throttle.setter
    def throttle(self, value):
        return


class _CurrentMod:
    """kRPC Module: independentThrottlePercentage is the ignition command."""

    def __init__(self, engine: "_CurrentThrottleEngine"):
        self._engine = engine

    def get_field_by_id(self, key: str):
        if key != "independentThrottlePercentage":
            raise ValueError(key)
        return self._engine.pct

    def set_field_float_by_id(self, key: str, value: float):
        if key != "independentThrottlePercentage":
            raise ValueError(key)
        self._engine.pct = float(value)


class _CurrentPart:
    def __init__(self, engine: "_CurrentThrottleEngine"):
        self.modules = [_CurrentMod(engine)]


class _CurrentThrottleEngine:
    """kRPC 0.6: Engine.throttle GET is currentThrottle (0 until lit)."""

    def __init__(self):
        self._independent = False
        self.pct = 0.0
        self.independent_sets = 0
        self.part = _CurrentPart(self)

    @property
    def independent_throttle(self):
        return self._independent

    @independent_throttle.setter
    def independent_throttle(self, value):
        self.independent_sets += 1
        value = bool(value)
        if value:
            self.pct = 0.0
        self._independent = value

    @property
    def throttle(self):
        return 0.0

    @throttle.setter
    def throttle(self, value):
        if self._independent:
            self.pct = float(value) * 100.0


class _RfMod:
    """Live ModuleEnginesRF: ignitions remaining + independent setpoint."""

    def __init__(self, engine: "_RfEngine"):
        self.name = "ModuleEnginesRF"
        self._engine = engine

    def get_field_by_id(self, key: str):
        if key == "independentThrottlePercentage":
            return self._engine.pct
        if key == "ignitions":
            return self._engine.ignitions
        if key == "currentThrottle":
            return self._engine.actual
        raise ValueError(key)

    def set_field_float_by_id(self, key: str, value: float):
        if key != "independentThrottlePercentage":
            raise ValueError(key)
        self._engine.pct = float(value)


class _RfPart:
    def __init__(self, engine: "_RfEngine"):
        self.modules = [_RfMod(engine)]


class _RfEngine(_CurrentThrottleEngine):
    """Valiant 1-start: cfg ignitions=1. Stage may spend it."""

    def __init__(self):
        self.ignitions = 1
        self.actual = 0.0
        super().__init__()
        self.part = _RfPart(self)


class TestHopFactoryPad(unittest.TestCase):
    def test_pad_module_is_the_rf_sit(self):
        factory = Path("hop_factory.py").read_text(encoding="utf-8")
        pad = Path("hop_factory_pad.py").read_text(encoding="utf-8")
        self.assertIn("from hop_factory_pad import", factory)
        self.assertNotIn("def _pad_light", factory)
        self.assertNotIn("def _pad_hold", factory)
        self.assertIn("def _pad_light", pad)
        self.assertIn("def _pad_hold", pad)
        self.assertIn("def _apply_pad_throttle", pad)
        self.assertIn("def _pad_engines", pad)
        self.assertIn("def _engine_throttle", pad)
        self.assertIn("def _engine_setpoint", pad)
        self.assertIn("def _pad_engine_live", pad)
        self.assertIn("def _release_pad_throttle", pad)
        self.assertIn("def _pad_thrusting", pad)
        self.assertIn("def _pad_rf_snap", pad)
        self.assertIn("def _rf_pad_sit", pad)
        self.assertIn("def _abort_rf_light", pad)
        self.assertNotIn("wait_water", factory)
        self.assertNotIn("wait_splash", factory)

    def test_pad_light_does_not_stage_on_krpc_throttle_alone(self):
        vessel = _Vessel()
        vessel.parts.engines = [_ColdEngine()]
        vessel.control.throttle = 1.0
        snap = type("S", (), {"link": True, "situation": "pre_launch"})()
        logs: list[str] = []
        self.assertFalse(_pad_light(vessel, logs.append, snap, deaf=False))
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(logs, [])

    def test_pad_light_stages_when_engine_throttle_live(self):
        vessel = _Vessel()
        engine = _Engine()
        vessel.parts.engines = [engine]
        snap = type("S", (), {"link": True, "situation": "pre_launch"})()
        logs: list[str] = []
        self.assertFalse(_pad_light(vessel, logs.append, snap, deaf=False))
        self.assertEqual(vessel.control.staged, 0)
        self.assertTrue(engine.independent_throttle)
        self.assertGreater(engine.throttle, 0.05)
        self.assertEqual(engine.independent_sets, 1)
        self.assertTrue(_pad_light(vessel, logs.append, snap, deaf=False))
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(engine.independent_sets, 1)
        self.assertGreater(engine.throttle, 0.05)
        self.assertTrue(any("hop light" in line for line in logs))

    def test_pad_light_does_not_stage_on_independent_with_throttle_zero(self):
        """rf-ignition-ullage: 21-57-33Z independent True Current Throttle 0."""
        vessel = _Vessel()
        engine = _Engine()
        engine.independent_throttle = True
        self.assertEqual(engine.throttle, 0.0)
        vessel.parts.engines = [engine]
        snap = type("S", (), {"link": True, "situation": "pre_launch"})()
        logs: list[str] = []
        self.assertFalse(_pad_light(vessel, logs.append, snap, deaf=False))
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(logs, [])
        self.assertGreater(engine.throttle, 0.05)
        self.assertEqual(engine.independent_sets, 1)

    def test_pad_light_stages_on_setpoint_when_current_throttle_zero(self):
        """rf-ignition-ullage: kRPC Engine.throttle GET is 0 until lit."""
        vessel = _Vessel()
        engine = _CurrentThrottleEngine()
        vessel.parts.engines = [engine]
        snap = type("S", (), {"link": True, "situation": "pre_launch"})()
        logs: list[str] = []
        self.assertFalse(_pad_light(vessel, logs.append, snap, deaf=False))
        self.assertEqual(vessel.control.staged, 0)
        self.assertTrue(engine.independent_throttle)
        self.assertEqual(engine.throttle, 0.0)
        self.assertGreater(engine.pct, 5.0)
        self.assertEqual(engine.independent_sets, 1)
        self.assertTrue(_pad_light(vessel, logs.append, snap, deaf=False))
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(engine.independent_sets, 1)
        self.assertEqual(engine.throttle, 0.0)
        self.assertTrue(any("hop light" in line for line in logs))
        lit = " ".join(logs)
        self.assertIn("currentThrottle=0.00", lit)
        self.assertIn("setpoint=1.00", lit)
        self.assertIn("ignitions=?", lit)

    def test_pad_light_aborts_rf_after_confirmed_light(self):
        """rf-ignition-ullage: hop light is the product. Do not loft."""
        vessel = _Vessel()
        engine = _RfEngine()
        vessel.parts.engines = [engine]
        vessel.recoverable = True
        vessel.recovered = 0

        def recover():
            vessel.recovered += 1

        vessel.recover = recover
        snap = type("S", (), {"link": True, "situation": "pre_launch"})()
        logs: list[str] = []
        self.assertFalse(_pad_light(vessel, logs.append, snap, deaf=False))
        self.assertEqual(vessel.control.staged, 0)
        self.assertTrue(_rf_pad_sit(vessel))
        rf = _pad_rf_snap(vessel)
        self.assertEqual(rf["ignitions"], 1)
        self.assertGreater(float(rf["setpoint"]), 0.05)
        self.assertEqual(rf["currentThrottle"], 0.0)

        def stage():
            engine.ignitions = 0
            vessel.control.staged += 1

        vessel.control.activate_next_stage = stage
        with self.assertRaises(MissionAbort) as ctx:
            _pad_light(vessel, logs.append, snap, deaf=False)
        self.assertIn("rf-light-test", str(ctx.exception))
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(vessel.recovered, 1)
        self.assertEqual(vessel.control.throttle, 0.0)
        lit = " ".join(logs)
        self.assertIn("hop light", lit)
        self.assertIn("ignitions=1→0", lit)
        self.assertIn("setpoint=1.00", lit)
        self.assertIn("currentThrottle=0.00", lit)
        self.assertIn("hop abort rf-light-test", lit)

    def test_pad_hold_keeps_start_airborne_until_meco(self):
        """rf-ignition-ullage: thrusting hands stack to MainThrottle 1."""
        vessel = _Vessel()
        engine = _Engine()
        vessel.parts.engines = [engine]
        pad = type(
            "S",
            (),
            {"situation": "pre_launch", "met": 0.0, "link": True, "alt": 86.0},
        )()
        fly = type(
            "S",
            (),
            {"situation": "flying", "met": 0.3, "link": True, "alt": 200.0},
        )()
        self.assertTrue(
            _pad_hold(vessel, pad, lit=True, left_pad=False, deaf=False)
        )
        self.assertTrue(engine.independent_throttle)
        self.assertGreater(engine.throttle, 0.05)
        sets = engine.independent_sets
        self.assertTrue(
            _pad_hold(vessel, pad, lit=True, left_pad=False, deaf=False)
        )
        self.assertEqual(engine.independent_sets, sets)
        self.assertGreater(engine.throttle, 0.05)
        self.assertTrue(
            _pad_hold(vessel, fly, lit=True, left_pad=True, deaf=False)
        )
        self.assertEqual(vessel.control.throttle, 1.0)
        self.assertFalse(engine.independent_throttle)
        self.assertTrue(
            _pad_hold(vessel, fly, lit=True, left_pad=True, deaf=False)
        )
        self.assertFalse(engine.independent_throttle)
        self.assertEqual(vessel.control.throttle, 1.0)
        vessel.control.throttle = 0.0
        self.assertFalse(
            _pad_hold(vessel, fly, lit=True, left_pad=True, deaf=False)
        )
        self.assertFalse(engine.independent_throttle)

    def test_pad_hold_releases_independent_when_thrusting_on_pad(self):
        """rf-ignition-ullage: 20-36-06Z independent after light starves stack."""
        vessel = _Vessel()
        engine = _Engine()
        vessel.parts.engines = [engine]
        vessel.thrust = 89019.0
        vessel.available_thrust = 89766.0
        pad = type(
            "S",
            (),
            {
                "situation": "pre_launch",
                "met": 0.3,
                "link": True,
                "alt": 86.0,
                "thrust": 89019.0,
                "available_thrust": 89766.0,
            },
        )()
        self.assertTrue(
            _pad_hold(vessel, pad, lit=True, left_pad=False, deaf=False)
        )
        self.assertEqual(vessel.control.throttle, 1.0)
        self.assertFalse(engine.independent_throttle)

    def test_pad_hold_restokes_pad_throttle_drop(self):
        vessel = _Vessel()
        pad = type(
            "S",
            (),
            {"situation": "pre_launch", "met": 1.0, "link": True, "alt": 86.0},
        )()
        vessel.control.throttle = 0.0
        self.assertTrue(
            _pad_hold(vessel, pad, lit=True, left_pad=False, deaf=False)
        )
        self.assertEqual(vessel.control.throttle, 1.0)

    def test_pad_light_deaf_aborts(self):
        vessel = _Vessel()
        vessel.control.sas = True
        vessel.control.throttle = 0.4
        snap = type("S", (), {"link": False})()
        with self.assertRaises(MissionAbort) as ctx:
            _pad_light(vessel, None, snap, deaf=True)
        self.assertIn("no signal (pad)", str(ctx.exception))
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(vessel.control.throttle, 0.0)
