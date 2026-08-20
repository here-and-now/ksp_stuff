"""PBC Start craft text + RSS pad coordinates."""

from __future__ import annotations

import unittest
from pathlib import Path

from catalog import load_catalog
from craft import pad_pbc
from hangar import pad_ll
from sites import STOCK_PAD, default_pad_ll

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "world"


class TestPadCraft(unittest.TestCase):
    def test_craft_text(self):
        cat = load_catalog(FIXTURE)
        craft = pad_pbc(diameter=0.625, length=1.4, catalog=cat)
        text = craft.dumps()
        self.assertIn("probeCoreSphere.v2", text)
        self.assertTrue("GooExperiment" in text or "sensorThermometer" in text)
        self.assertIn("ProceduralShapeCylinder", text)
        self.assertRegex(text, r"diameter = 0\.625")
        self.assertRegex(text, r"length = 1\.4")
        self.assertNotIn("mk1pod", text.lower())
        self.assertNotIn("parachute", text.lower())
        names = [p.name for p in craft.parts]
        self.assertIn("probeCoreSphere_v2", names)
        self.assertIn("proceduralSRBRealFuels", names)
        self.assertIn("batteryPack", names)
        self.assertIn("SurfAntenna", names)


class TestPadSite(unittest.TestCase):
    def test_fixture_is_cape_not_stock_ksc(self):
        lat, lon = default_pad_ll(FIXTURE)
        self.assertAlmostEqual(lat, 28.608389, places=4)
        self.assertAlmostEqual(lon, -80.604333, places=4)
        self.assertNotAlmostEqual(lat, STOCK_PAD.latitude, places=2)
        self.assertNotAlmostEqual(lon, STOCK_PAD.longitude, places=2)

    def test_hangar_pad_ll_uses_rss_when_env_set(self):
        import os

        old = os.environ.get("KSPSTUFF_KSP")
        try:
            os.environ["KSPSTUFF_KSP"] = str(FIXTURE)
            lat, lon = pad_ll()
            self.assertGreater(lat, 20.0)
            self.assertLess(lon, -70.0)
            self.assertNotAlmostEqual(lat, -0.0972, places=2)
        finally:
            if old is None:
                os.environ.pop("KSPSTUFF_KSP", None)
            else:
                os.environ["KSPSTUFF_KSP"] = old
