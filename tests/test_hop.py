"""No-KSP gates for hop / science (L-041)."""

from __future__ import annotations

import unittest

from phases import NAMES, OffPlan, check_expect
from science import EVA_EXPERIMENTS, HOP_EXPERIMENTS, experiment_name, run_ready
from watch import FlightState


class _Exp:
    def __init__(self, name, **kw):
        self.name = name
        self.title = name
        self.biome = kw.get("biome", "LaunchPad")
        self.available = kw.get("available", True)
        self.has_data = kw.get("has_data", False)
        self.inoperable = kw.get("inoperable", False)
        self.rerunnable = kw.get("rerunnable", name == "crewReport")
        self.ran = False
        self.part = type("P", (), {"name": "mk1pod.v2", "modules": []})()

    def run(self):
        if self.has_data:
            raise RuntimeError("Experiment already contains data")
        self.ran = True
        self.has_data = True


class _Vessel:
    def __init__(self, exps):
        self.parts = type("Parts", (), {"experiments": exps})()


class TestHopName(unittest.TestCase):
    def test_in_catalog(self):
        self.assertIn("hop", NAMES)

    def test_ascent_is_sounding(self):
        from hop import hop_ascent_config, hop_target_apo

        self.assertGreaterEqual(hop_target_apo(), 8_000.0)
        self.assertLessEqual(hop_target_apo(), 25_000.0)
        cfg = hop_ascent_config()
        self.assertFalse(cfg.circularize)
        self.assertLess(cfg.target_altitude, 80_000.0)


class TestScience(unittest.TestCase):
    def test_skip_eva(self):
        self.assertIn("evaReport", EVA_EXPERIMENTS)
        eva = _Exp("evaReport", available=True)
        crew = _Exp("crewReport", available=True)
        goo = _Exp("mysteryGoo", available=True, rerunnable=False)
        ran = run_ready(_Vessel([eva, crew, goo]), names=HOP_EXPERIMENTS)
        self.assertEqual(ran, ["crewReport", "mysteryGoo"])
        self.assertFalse(eva.ran)
        self.assertTrue(crew.ran)
        self.assertTrue(goo.ran)

    def test_keep_goo_no_rerun(self):
        goo = _Exp("mysteryGoo", available=True, has_data=True, rerunnable=False)
        ran = run_ready(_Vessel([goo]), names=HOP_EXPERIMENTS)
        self.assertEqual(ran, [])
        self.assertFalse(goo.ran)

    def test_name(self):
        self.assertEqual(experiment_name(_Exp("crewReport")), "crewReport")


class TestHopExpect(unittest.TestCase):
    def test_skip_peri(self):
        st = FlightState(body="Earth", peri=0.0, apo=12_000.0)
        check_expect(st, skip_peri=True)

    def test_apo_still_checked(self):
        st = FlightState(body="Earth", peri=0.0, apo=900_000.0)
        with self.assertRaises(OffPlan):
            check_expect(st, skip_peri=True)


if __name__ == "__main__":
    unittest.main()
