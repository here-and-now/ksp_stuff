"""Disk world desk. No kRPC. Fixtures under tests/fixtures/world/."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from catalog import cfg_name, craft_name, load_catalog, scan_config_cache
from hangar import DEFAULT_SAVE, RSS_KSP, STEAM_KSP, discover_hangar, discover_ksp
from world import (
    craft_part_names,
    filter_parts,
    format_parts,
    format_stack,
    format_tech,
    format_world,
    load_world,
    parse_research,
    parse_tech_tree,
    unlocked_parts,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "world"
RSS_CACHE = Path.home() / "Games" / "KSP-rss" / "GameData" / "ModuleManager.ConfigCache"


class TestNames(unittest.TestCase):
    def test_round_trip(self):
        self.assertEqual(cfg_name("probeCoreSphere.v2"), "probeCoreSphere_v2")
        self.assertEqual(craft_name("probeCoreSphere_v2"), "probeCoreSphere.v2")


class TestFixtureWorld(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = load_world(ksp_root=FIXTURE, save="letsgrok")

    def test_mode_and_home(self):
        w = self.world
        self.assertEqual(w.save, "letsgrok")
        self.assertEqual(w.mode, "SCIENCE_SANDBOX")
        self.assertEqual(w.home_hint, "Earth")
        self.assertEqual(w.research.science, 0.0)
        self.assertEqual(w.research.unlocked, ("start",))

    def test_tree(self):
        tree = self.world.tree
        self.assertIn("start", tree)
        self.assertEqual(tree["basicRocketry"].cost, 5)
        self.assertEqual(tree["basicRocketry"].parents, ("start",))
        self.assertEqual(tree["simpleCommandModules"].cost, 90)

    def test_catalog_start_not_mk1(self):
        cat = self.world.catalog
        stay = cat.get("probeCoreSphere_v2")
        self.assertIsNotNone(stay)
        assert stay is not None
        self.assertEqual(stay.tech, "start")
        self.assertIn("Experiment", stay.modules)
        self.assertIn("kerbalism_TELEMETRY", stay.experiments)
        goo = cat.experiments.get("mysteryGoo")
        self.assertIsNotNone(goo)
        assert goo is not None
        self.assertEqual(goo.sample_amount, 1)
        self.assertGreater(goo.data_rate or 0, 0.5)
        mk1 = cat.get("mk1pod_v2")
        self.assertIsNotNone(mk1)
        assert mk1 is not None
        self.assertEqual(mk1.tech, "simpleCommandModules")
        srb = cat.get("proceduralSRBRealFuels")
        self.assertIsNotNone(srb)
        assert srb is not None
        self.assertTrue(srb.procedural)
        self.assertIn("SolidFuel", srb.resources)

    def test_unlocked_omits_mk1(self):
        names = {p.name for p in unlocked_parts(self.world)}
        self.assertIn("probeCoreSphere_v2", names)
        self.assertIn("GooExperiment", names)
        self.assertIn("proceduralSRBRealFuels", names)
        self.assertNotIn("mk1pod_v2", names)

    def test_search_and_module(self):
        goo = filter_parts(self.world, search="goo")
        self.assertEqual([p.name for p in goo], ["GooExperiment"])
        exp = filter_parts(self.world, unlocked=True, module="Experiment")
        self.assertTrue({p.name for p in exp} >= {"probeCoreSphere_v2", "GooExperiment"})

    def test_parts_text_does_not_call_stayputnik_a_geiger(self):
        stay = filter_parts(self.world, unlocked=True, search="stayputnik")
        text = format_parts(self.world, stay)
        self.assertIn("probeCoreSphere_v2", text)
        self.assertNotIn("exp=", text)
        self.assertIn("hosted experiments", text)
        self.assertIn("hosted_on=", text)
        stay_part = self.world.catalog.get("probeCoreSphere_v2")
        assert stay_part is not None
        if stay_part.experiments:
            self.assertIn(stay_part.experiments[0], text)

    def test_search_hosted_experiment_is_not_a_part(self):
        stay = self.world.catalog.get("probeCoreSphere_v2")
        self.assertIsNotNone(stay)
        assert stay is not None
        eid = stay.experiments[0]
        text = format_parts(self.world, [], search=eid, unlocked=True)
        self.assertIn("hosted_on=", text)
        self.assertIn(eid, text)
        self.assertIn("probeCoreSphere_v2", text)

    def test_stack_from_craft_md(self):
        md = (
            "craft: kspstuff-pad-pbc\n"
            "parts:\n"
            "  - probeCoreSphere_v2\n"
            "  - GooExperiment\n"
            "  - sensorThermometer\n"
            "notes: ignore\n"
        )
        names = craft_part_names(md)
        self.assertEqual(
            names,
            ["probeCoreSphere_v2", "GooExperiment", "sensorThermometer"],
        )
        text = format_stack(self.world, names, label="pad")
        self.assertIn("probeCoreSphere_v2", text)
        self.assertIn("GooExperiment", text)
        visible, _, hosted = text.partition("hosted")
        self.assertNotIn("kerbalism-geigercounter", visible)
        stay = self.world.catalog.get("probeCoreSphere_v2")
        assert stay is not None
        if stay.experiments:
            self.assertIn("hosted_on=", text)
            self.assertTrue(any(e in text for e in stay.experiments))

    def test_tech_start_text(self):
        text = format_tech(self.world, "start")
        self.assertIn("unlocked: yes", text)
        self.assertIn("probeCoreSphere_v2", text)
        self.assertNotIn("mk1pod_v2", text)

    def test_world_text(self):
        text = format_world(self.world)
        self.assertIn("save: letsgrok", text)
        self.assertIn("mode: SCIENCE_SANDBOX", text)
        self.assertIn("home: Earth", text)
        self.assertIn("unlocked: start", text)

    def test_save_part_dots(self):
        start_parts = self.world.research.parts_by_node["start"]
        self.assertIn("probeCoreSphere_v2", start_parts)


class TestDiscover(unittest.TestCase):
    def test_env_wins(self):
        old = os.environ.get("KSPSTUFF_KSP")
        try:
            os.environ["KSPSTUFF_KSP"] = str(FIXTURE)
            self.assertEqual(discover_ksp(), FIXTURE)
            hangar = discover_hangar()
            self.assertIsNotNone(hangar)
            assert hangar is not None
            self.assertEqual(hangar.save, DEFAULT_SAVE)
            self.assertEqual(hangar.ksp_root, FIXTURE)
        finally:
            if old is None:
                os.environ.pop("KSPSTUFF_KSP", None)
            else:
                os.environ["KSPSTUFF_KSP"] = old

    def test_rss_preferred_over_steam(self):
        old = os.environ.pop("KSPSTUFF_KSP", None)
        try:
            if not (RSS_KSP / "GameData" / "RealSolarSystem").is_dir():
                self.skipTest("no RSS GameData")
            root = discover_ksp()
            self.assertEqual(root, RSS_KSP)
            self.assertNotEqual(root, STEAM_KSP)
            hangar = discover_hangar()
            assert hangar is not None
            self.assertEqual(hangar.save, DEFAULT_SAVE)
        finally:
            if old is not None:
                os.environ["KSPSTUFF_KSP"] = old

    def test_explicit_save(self):
        old_k = os.environ.get("KSPSTUFF_KSP")
        old_s = os.environ.get("KSPSTUFF_SAVE")
        try:
            os.environ["KSPSTUFF_KSP"] = str(FIXTURE)
            os.environ["KSPSTUFF_SAVE"] = "letsgrok"
            hangar = discover_hangar()
            assert hangar is not None
            self.assertEqual(hangar.save, "letsgrok")
        finally:
            for key, old in (("KSPSTUFF_KSP", old_k), ("KSPSTUFF_SAVE", old_s)):
                if old is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old


class TestParsers(unittest.TestCase):
    def test_tree_file(self):
        path = FIXTURE / "GameData/HideEmptyTechTreeNodes/Resources/HETTN.TechTree"
        tree = parse_tech_tree(path)
        self.assertEqual(set(tree), {"start", "basicRocketry", "simpleCommandModules"})

    def test_research_block(self):
        text = (FIXTURE / "saves/letsgrok/persistent.sfs").read_text(encoding="utf-8")
        rnd = parse_research(text)
        self.assertEqual(rnd.science, 0.0)
        self.assertEqual(rnd.unlocked, ("start",))

    def test_cache_scan_alone(self):
        cat = scan_config_cache(FIXTURE / "GameData/ModuleManager.ConfigCache")
        self.assertEqual(len(cat.parts), 4)
        self.assertTrue(cat.get("GooExperiment").experiments == ("mysteryGoo",))


@unittest.skipUnless(RSS_CACHE.is_file(), "no ~/Games/KSP-rss ConfigCache")
class TestLiveRss(unittest.TestCase):
    def test_start_has_stayputnik_not_mk1(self):
        root = RSS_CACHE.parents[1]
        cat = load_catalog(root)
        self.assertGreater(len(cat.parts), 800)
        stay = cat.get("probeCoreSphere_v2")
        self.assertIsNotNone(stay)
        assert stay is not None
        self.assertEqual(stay.tech, "start")
        mk1 = cat.get("mk1pod_v2")
        self.assertIsNotNone(mk1)
        assert mk1 is not None
        self.assertNotEqual(mk1.tech, "start")
        goo = cat.experiments.get("mysteryGoo")
        self.assertIsNotNone(goo)
        assert goo is not None
        # GooExperiment 0.18, not Large_Crewed_Lab 0.9 (last-wins was wrong).
        self.assertAlmostEqual(goo.ec_rate or 0.0, 0.18, places=2)
