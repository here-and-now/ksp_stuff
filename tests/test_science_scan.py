"""Open-science scan. Live ConfigCache if present."""

from __future__ import annotations

import unittest

from science_scan import _sit_key, format_science_scan, unlocked_experiment_ids
from world import load_world


class TestSitKey(unittest.TestCase):
    def test_tags(self):
        self.assertEqual(_sit_key("Surface@Biomes"), "surface")
        self.assertEqual(_sit_key("FlyingLow"), "flyinglow")
        self.assertEqual(_sit_key("FlyingHigh"), "flyinghigh")
        self.assertEqual(_sit_key("Space@VirtualBiomes"), "space")


class TestLiveScan(unittest.TestCase):
    def test_geiger_situations_and_scan(self):
        world = load_world()
        cfg = world.catalog.experiments.get("geigerCounter")
        self.assertIsNotNone(cfg)
        assert cfg is not None
        self.assertTrue(any("FlyingLow" in s for s in cfg.situations))
        self.assertIn("geigerCounter", unlocked_experiment_ids(world))
        text = format_science_scan(world)
        self.assertIn("geigerCounter", text)
        self.assertIn("FlyingLow", text)
