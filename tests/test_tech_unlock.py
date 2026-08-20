"""tech-unlock catalog: disk check + kRPC spend. No GameData, no save edit."""

from __future__ import annotations

import argparse
import unittest
from pathlib import Path
from unittest.mock import patch

from telem import MissionAbort
from world import load_world

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "world"


class _Krpc:
    class GameScene:
        research_and_development = "research_and_development"
        space_center = "space_center"
        flight = "flight"

    def __init__(self, scene="space_center"):
        self.game_scene = scene


class _Conn:
    def __init__(self, scene="space_center"):
        self.krpc = _Krpc(scene)
        self.space_center = None
        self._types = type("T", (), {"string_type": "s"})()
        self.invokes: list[tuple[str, str, list]] = []

    def _invoke(self, svc, proc, args, names, types, ret):
        raise RuntimeError(f'Procedure "{proc}" not found, in service "{svc}"')


class _SC:
    def __init__(self, science=8.9, unlock=None):
        self.science = science
        self.saved: list[str] = []
        self._unlock = unlock

    def unlock_tech(self, node_id):
        if self._unlock is False:
            raise RuntimeError("nope")
        self.science -= 5
        self.last = node_id

    def save(self, name):
        self.saved.append(name)


class _Session:
    def __init__(self, sc=None, scene="space_center"):
        self.space_center = sc or _SC()
        self.conn = _Conn(scene)
        self.conn.space_center = self.space_center

    def require_connected(self):
        return None


class TestCatalog(unittest.TestCase):
    def test_in_names_and_blocks(self):
        from phases import NAMES, UNCREWED

        self.assertIn("tech-unlock", NAMES)
        self.assertIn("tech-unlock", UNCREWED)
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertIn("tech-unlock", blocks)
        self.assertIn("tech-unlock", Path("tech_unlock.py").read_text(encoding="utf-8"))

    def test_source_is_not_a_godfile(self):
        text = Path("tech_unlock.py").read_text(encoding="utf-8")
        self.assertNotIn("from watch", text)
        self.assertNotIn("GameData/", text)
        self.assertNotIn("write_text", text)
        self.assertNotIn("Path(", text)
        self.assertIn("research_and_development", text)
        self.assertIn("UnlockTech", text)

    def test_resolve_node(self):
        from tech_unlock import resolve_node

        self.assertEqual(resolve_node("engineering101"), "engineering101")
        with patch("tech_unlock.plan_node", return_value=""):
            with self.assertRaises(MissionAbort) as ctx:
                resolve_node(None)
        self.assertIn("needs a node", str(ctx.exception))
        with patch("tech_unlock.plan_node", return_value="engineering101"):
            self.assertEqual(resolve_node(None), "engineering101")


class TestDiskBuy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = load_world(ksp_root=FIXTURE, save="letsgrok")

    def test_unknown(self):
        from tech_unlock import assert_can_buy

        with self.assertRaises(MissionAbort) as ctx:
            assert_can_buy(self.world, "engineering101")
        self.assertIn("unknown node", str(ctx.exception))

    def test_already_start(self):
        from tech_unlock import assert_can_buy

        node = assert_can_buy(self.world, "start")
        self.assertEqual(node.id, "start")
        self.assertIn("start", self.world.research.unlocked)

    def test_parent_locked(self):
        from tech_unlock import assert_can_buy

        with self.assertRaises(MissionAbort) as ctx:
            assert_can_buy(self.world, "simpleCommandModules")
        self.assertIn("parent", str(ctx.exception))
        self.assertIn("enhancedSurvivability", str(ctx.exception))

    def test_basic_rocketry_payable_on_tree(self):
        from tech_unlock import assert_can_buy

        node = assert_can_buy(self.world, "basicRocketry")
        self.assertEqual(node.cost, 5)
        self.assertNotIn("basicRocketry", self.world.research.unlocked)


class TestSpend(unittest.TestCase):
    def test_attr_unlock_spends(self):
        from tech_unlock import spend

        session = _Session(_SC(science=8.9))
        spend(session, "engineering101")
        self.assertAlmostEqual(session.space_center.science, 3.9)
        self.assertEqual(session.space_center.last, "engineering101")

    def test_no_rpc_aborts_without_writing_save(self):
        from tech_unlock import persist, spend

        class Bare:
            science = 8.9
            saved: list[str] = []

            def save(self, name):
                self.saved.append(name)

        sc = Bare()
        sc.saved = []
        session = _Session(sc)
        with self.assertRaises(MissionAbort) as ctx:
            spend(session, "engineering101")
        self.assertIn("no UnlockTech", str(ctx.exception))
        self.assertIn("GameData", str(ctx.exception))
        self.assertEqual(sc.science, 8.9)
        persist(session)
        self.assertEqual(sc.saved, ["persistent"])


class TestRunPhase(unittest.TestCase):
    def test_skip_already_unlocked(self):
        from tech_unlock import run_phase

        logs: list[str] = []
        session = _Session()
        world = load_world(ksp_root=FIXTURE, save="letsgrok")
        with patch("tech_unlock.load_world", return_value=world):
            result = run_phase(session, node="start", on_log=logs.append)
        self.assertEqual(result, "tech-unlock skip start")
        self.assertTrue(any("skip already start" in x for x in logs))

    def test_poor_aborts(self):
        from tech_unlock import run_phase

        session = _Session(_SC(science=1.0))
        world = load_world(ksp_root=FIXTURE, save="letsgrok")
        with patch("tech_unlock.load_world", return_value=world):
            with self.assertRaises(MissionAbort) as ctx:
                run_phase(session, node="basicRocketry")
        self.assertIn("science 1.00 < cost 5", str(ctx.exception))

    def test_buy_basic_rocketry(self):
        from tech_unlock import run_phase

        session = _Session(_SC(science=8.9))
        world = load_world(ksp_root=FIXTURE, save="letsgrok")
        logs: list[str] = []
        with patch("tech_unlock.load_world", return_value=world):
            with patch("tech_unlock.go_research"):
                with patch("tech_unlock.go_space_center"):
                    result = run_phase(
                        session, node="basicRocketry", on_log=logs.append
                    )
        self.assertEqual(result, "tech-unlock basicRocketry")
        self.assertAlmostEqual(session.space_center.science, 3.9)
        self.assertEqual(session.space_center.saved, ["persistent"])
        self.assertTrue(any("bought basicRocketry" in x for x in logs))

    def test_cmd_phase_skips_seat(self):
        from main import cmd_phase

        session = _Session()
        args = argparse.Namespace(name="tech-unlock", timeout=0.0)
        with patch("missions.assert_seated") as seated:
            with patch("tech_unlock.run_phase", return_value="tech-unlock skip start"):
                code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 0)
