"""Open-science scan. Fixture world, no live gym."""

from __future__ import annotations

import unittest

from science_scan import _sit_key, format_science_scan
from tests.test_world import FIXTURE
from world import load_world


class TestSitKey(unittest.TestCase):
    def test_tags(self):
        self.assertEqual(_sit_key("Surface@Biomes"), "surface")
        self.assertEqual(_sit_key("FlyingLow"), "flyinglow")
        self.assertEqual(_sit_key("FlyingHigh"), "flyinghigh")
        self.assertEqual(_sit_key("Space@VirtualBiomes"), "space")


class TestFixtureScan(unittest.TestCase):
    def test_scan_runs_on_fixture(self):
        world = load_world(ksp_root=FIXTURE)
        text = format_science_scan(world)
        self.assertIn("# open science", text)
        self.assertIn("unlocked experiments", text)
        self.assertIn("live experiment defs", text)

    def test_sit_key_space_split(self):
        self.assertEqual(_sit_key("InSpaceLow"), "inspacelow")
        self.assertEqual(_sit_key("InSpaceHigh@Biomes"), "inspacehigh")
