"""RA comms dump: TL table + LIVE/SILENT ground from fixture ConfigCache."""

from __future__ import annotations

import unittest

from comms_catalog import load_comms_catalog, scan_comms_cache
from science_scan import format_comms
from tests.test_world import FIXTURE
from world import load_world

_LECTURE = "TL2 (survivability) MaxDataRate=64 bps on every ModuleRealAntenna"


class TestFixtureComms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = load_world(ksp_root=FIXTURE, save="letsgrok")
        cls.text = format_comms(cls.world)

    def test_dump_has_tl_live_and_silent(self):
        text = self.text
        self.assertIn("# after Harmony clamp, the live Cape path (kRPC RateToHome).", text)
        self.assertNotIn("64 bps on every ModuleRealAntenna", text)
        self.assertIn("owned comms TL = 0", text)
        self.assertIn("minRelayTL = 0", text)
        self.assertIn("rate_bps", text)
        self.assertRegex(text, r"(?m)^0\s+\S+\s+4\s+LIVE")
        self.assertRegex(text, r"(?m)^2\s+survivability\s+64")
        self.assertIn("survivability", text)
        self.assertIn("US - Cape Canaveral", text)
        self.assertIn("Silent Station", text)
        self.assertRegex(text, r"Cape Canaveral\s+.*\s+LIVE")
        self.assertRegex(text, r"Silent Station\s+.*\s+SILENT")
        self.assertIn("# craft: part tech lock gain D band HD samp", text)
        self.assertIn("# ground: name lat lon band gain_dBi Tx_dBm need_TL LIVE|SILENT", text)
        self.assertNotIn(_LECTURE, text)
        self.assertNotIn("Mercury", text)
        self.assertNotIn("dump hour", text.lower())

    def test_ground_live_before_silent(self):
        lines = [
            ln
            for ln in self.text.splitlines()
            if ln.endswith(" LIVE") or ln.endswith(" SILENT")
        ]
        ground = [ln for ln in lines if "Cape" in ln or "Silent" in ln]
        self.assertGreaterEqual(len(ground), 2)
        lives = [i for i, ln in enumerate(ground) if ln.endswith(" LIVE")]
        silents = [i for i, ln in enumerate(ground) if ln.endswith(" SILENT")]
        self.assertTrue(lives)
        self.assertTrue(silents)
        self.assertLess(max(lives), min(silents))

    def test_scan_alone_owned_zero(self):
        cat = scan_comms_cache(FIXTURE / "GameData" / "ModuleManager.ConfigCache")
        cat_u = load_comms_catalog(self.world)
        self.assertEqual(cat_u.owned_tl, 0)
        self.assertEqual(len(cat.tech_levels), 2)
        self.assertEqual({tl.level for tl in cat.tech_levels}, {0, 2})
        self.assertEqual(cat.upgrades.get("commsTL2"), "survivability")
        names = {row.name for row in cat_u.stations}
        self.assertIn("US - Cape Canaveral", names)
        self.assertIn("Silent Station", names)
        by_name = {row.name: row for row in cat_u.stations}
        self.assertTrue(by_name["US - Cape Canaveral"].live)
        self.assertFalse(by_name["Silent Station"].live)
        self.assertEqual(by_name["Silent Station"].need_tl, 3)
