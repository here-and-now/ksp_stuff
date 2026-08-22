"""Ticket bus and Hank dispatch. No kRPC."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ops
import tickets


def _tmp_board():
    d = Path(tempfile.mkdtemp())
    return {
        "TICKET_DIR": d,
        "BOARD": d / "board.jsonl",
        "HEAD": d / "head.json",
        "PRINT": d / "BOARD.md",
        "FINGERPRINTS": d / "fingerprints.json",
    }


class TestTickets(unittest.TestCase):
    def setUp(self):
        self.paths = _tmp_board()
        self.patches = [
            patch.object(tickets, k, v) for k, v in self.paths.items()
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_open_list_assign_close(self):
        t = tickets.open_ticket(
            type="science",
            title="FlyingHigh Forest TELEMETRY leftover",
            reporter="Linus Grokman, Director of Research",
            severity="S3",
            priority="P1",
            fingerprint="flyinghigh-forest-telem",
        )
        self.assertEqual(t["id"], "T-001")
        self.assertEqual(t["desk"], "linus")
        self.assertEqual(t["status"], "inbox")
        rows = tickets.list_tickets()
        self.assertEqual(len(rows), 1)
        t2 = tickets.patch_ticket(
            "T-001",
            {"desk": "linus", "status": "assigned"},
            who="hank",
        )
        self.assertEqual(t2["status"], "assigned")
        t3 = tickets.patch_ticket("T-001", {"status": "done"}, who="linus")
        self.assertEqual(t3["status"], "done")
        self.assertEqual(tickets.list_tickets(), [])

    def test_fly_fields_go_either_or(self):
        t = {
            "go": "yes",
            "payload": {"go": "", "cli": "python main.py hop", "recommended": "other"},
        }
        ff = tickets.fly_fields(t)
        self.assertEqual(ff["go"], "yes")
        self.assertEqual(ff["cli"], "python main.py hop")
        t2 = {"payload": {"go": "yes", "recommended": "python main.py pad"}}
        self.assertEqual(tickets.fly_fields(t2)["go"], "yes")
        self.assertEqual(tickets.fly_fields(t2)["cli"], "python main.py pad")
        self.assertEqual(tickets.fly_fields(None)["go"], "")

    def test_seated_fly_ticket_missing_head(self):
        self.assertIsNone(tickets.seated_fly_ticket())

    def test_seated_fly_ticket_prefers_go_yes(self):
        tickets.open_ticket(
            type="fly", title="wait hop", reporter="Hank", desk="gene"
        )
        t2 = tickets.open_ticket(
            type="fly", title="go hop", reporter="Hank", desk="gene"
        )
        tickets.patch_ticket(
            t2["id"], {"go": "yes", "status": "ready"}, who="gene"
        )
        got = tickets.seated_fly_ticket()
        self.assertIsNotNone(got)
        self.assertEqual(got["id"], t2["id"])

    def test_patch_fly_payload_keeps_go(self):
        t = tickets.open_ticket(
            type="fly", title="hop", reporter="Hank", desk="gene"
        )
        tickets.patch_ticket(t["id"], {"go": "yes"}, who="gene")
        tickets.patch_fly_payload(
            t["id"],
            {"cli": "python main.py hop", "campaign": "uncrewed"},
            who="hank",
        )
        cur = tickets.show_ticket(t["id"])
        self.assertEqual(cur["go"], "yes")
        self.assertEqual(cur["payload"]["cli"], "python main.py hop")
        self.assertEqual(cur["payload"]["campaign"], "uncrewed")

    def test_only_gene_stamps_go(self):
        tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
        )
        with self.assertRaises(tickets.TicketError):
            tickets.patch_ticket("T-001", {"go": "yes"}, who="hank")
        t = tickets.patch_ticket("T-001", {"go": "yes"}, who="gene")
        self.assertEqual(t["go"], "yes")

    def test_rsi_opens_at_three(self):
        for i in range(3):
            tickets.open_ticket(
                type="control",
                title=f"ec=0 splash {i}",
                reporter="Jebediah",
                fingerprint="ec=0-after-loft",
            )
        rsi = tickets.maybe_open_rsi("ec=0-after-loft")
        self.assertIsNotNone(rsi)
        self.assertEqual(rsi["type"], "rsi")
        self.assertEqual(rsi["priority"], "P1")
        again = tickets.maybe_open_rsi("ec=0-after-loft")
        self.assertIsNone(again)

    def test_batch_ids(self):
        tickets.open_ticket(type="vehicle", title="a", reporter="Gus")
        tickets.open_ticket(type="vehicle", title="b", reporter="Gus")
        rows = tickets.list_tickets(desk="gus")
        self.assertEqual([r["id"] for r in rows], ["T-001", "T-002"])


class TestOpsNext(unittest.TestCase):
    def setUp(self):
        self.paths = _tmp_board()
        self.patches = [
            patch.object(tickets, k, v) for k, v in self.paths.items()
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_pad_occupancy_beats_ground(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
            severity="S2",
            priority="P0",
        )
        tickets.patch_ticket(t["id"], {"go": "yes", "status": "ready"}, who="gene")
        tickets.patch_ticket(
            t["id"],
            {"payload": {"go": "yes", "cli": "python main.py hop-splash"}},
            who="hank",
        )
        tickets.open_ticket(type="vehicle", title="next stack", reporter="Gus")
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        self.assertEqual(act["hire"][0]["desk"], "jebediah")
        self.assertEqual(act["hire"][0]["cli"], "python main.py hop-splash")
        desks = [h["desk"] for h in act["hire"]]
        self.assertIn("gus", desks)

    def test_lock_live_no_commander(self):
        tickets.open_ticket(type="science", title="backlog", reporter="Linus")
        act = ops.next_actions(desk={"hangar": "none"}, locked=True)
        desks = [h["desk"] for h in act["hire"]]
        self.assertNotIn("jebediah", desks)
        self.assertNotIn("gene", desks)
        self.assertIn("linus", desks)

    def test_fly_without_go_hires_gene_once(self):
        tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
        )
        tickets.open_ticket(type="vehicle", title="t7", reporter="Gus")
        tickets.open_ticket(type="science", title="goo", reporter="Linus")
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        desks = [h["desk"] for h in act["hire"]]
        self.assertEqual(desks[0], "gene")
        self.assertEqual(desks.count("gene"), 1)
        self.assertIn("gus", desks)
        self.assertIn("linus", desks)

    def test_s1_recover_first(self):
        tickets.open_ticket(
            type="recover",
            title="Forest land",
            reporter="Hank",
            severity="S1",
            priority="P0",
            desk="jebediah",
        )
        tickets.patch_ticket("T-001", {"status": "ready"}, who="hank")
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        self.assertEqual(act["hire"][0]["desk"], "jebediah")
        self.assertIn("S1 recover", act["hire"][0]["why"])

    def test_fly_gate_wait_without_go(self):
        tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
        )
        g = ops.fly_gate(desk={"hangar": "none"}, locked=False)
        self.assertEqual(g["fly"], "wait")

    def test_fly_gate_yes_with_go(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
        )
        tickets.patch_ticket(
            t["id"],
            {"go": "yes", "status": "ready", "payload": {"go": "yes", "cli": "python main.py hop-splash"}},
            who="gene",
        )
        g = ops.fly_gate(desk={"hangar": "none"}, locked=False)
        self.assertEqual(g["fly"], "yes")
        self.assertEqual(g["cli"], "python main.py hop-splash")

    def test_leftover_hangar_line(self):
        act = ops.next_actions(
            desk={"hangar": "phase t7 sit=LANDED"},
            locked=False,
        )
        self.assertEqual(act["hire"][0]["desk"], "jebediah")
        self.assertIn("leftover", act["hire"][0]["why"])


class TestPacketAndReasoning(unittest.TestCase):
    def setUp(self):
        self.paths = _tmp_board()
        self.patches = [
            patch.object(tickets, k, v) for k, v in self.paths.items()
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_reasoning_never_xhigh_mortimer_always_high(self):
        t = tickets.open_ticket(
            type="ops",
            title="hygiene",
            reporter="Hank",
            severity="S4",
            priority="P3",
            desk="hank",
        )
        self.assertIn(tickets.reasoning_for(t), tickets.REASONING)
        self.assertNotEqual(tickets.reasoning_for(t), "xhigh")
        t["desk"] = "mortimer"
        self.assertEqual(tickets.reasoning_for(t), "high")
        s1 = tickets.open_ticket(
            type="recover",
            title="wreck",
            reporter="Hank",
            severity="S1",
            priority="P0",
            desk="jebediah",
        )
        self.assertEqual(tickets.reasoning_for(s1), "high")
        self.assertEqual(tickets.reasoning_for(s1, "mortimer"), "high")

    def test_skim_omits_jsonl_deep_includes_it(self):
        t = tickets.open_ticket(
            type="control",
            title="relight on descent",
            reporter="Jebediah",
            severity="S2",
            priority="P1",
            desk="lars",
            payload={"live_run": "2026-08-21T21-14-09Z-hop-splash"},
        )
        tickets.patch_ticket(
            t["id"],
            {
                "evidence": [
                    "docs/missions/jebediah/logs/2026-08-21T21-14-09Z-hop-splash.jsonl"
                ]
            },
            who="hank",
        )
        skim = tickets.format_packet(t["id"], deep=False)
        deep = tickets.format_packet(t["id"], deep=True)
        self.assertIn("docs/program/desk.md", skim)
        self.assertNotIn(".jsonl", skim)
        self.assertIn("packet T-001 --deep", skim)
        self.assertIn(".jsonl", deep)
        self.assertIn("reasoning: high", skim)
        self.assertNotIn("xhigh", skim)
        self.assertNotIn("xhigh", deep)

    def test_from_need_stack_is_control_ticket(self):
        t = tickets.from_need(
            "need_stack",
            title="hop-splash dwell",
            reporter="Gene Grokman, Flight Director",
        )
        self.assertEqual(t["type"], "control")
        self.assertEqual(t["desk"], "lars")
        self.assertEqual(t["id"], "T-001")

    def test_cmd_packet_entry_point(self):
        from contextlib import redirect_stdout
        from io import StringIO

        t = tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
            severity="S2",
            priority="P0",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            rc = tickets.cmd_tickets(["packet", t["id"]])
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("ticket: T-001", out)
        self.assertIn("docs/program/desk.md", out)
        self.assertNotIn(".jsonl", out)
        self.assertIn("--deep", out)

    def test_ops_hire_has_reasoning_and_packet(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
            severity="S2",
            priority="P0",
        )
        tickets.patch_ticket(
            t["id"],
            {
                "go": "yes",
                "status": "ready",
                "payload": {"go": "yes", "cli": "python main.py hop-splash"},
            },
            who="gene",
        )
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        hire = act["hire"][0]
        self.assertEqual(hire["desk"], "jebediah")
        self.assertIn(hire["reasoning"], tickets.REASONING)
        self.assertNotEqual(hire["reasoning"], "xhigh")
        self.assertIn("tickets packet", hire["packet"])
        text = ops.format_next(act)
        self.assertIn("reasoning=", text)
        self.assertIn("packet:", text)
        self.assertNotIn("xhigh", text)

    def test_category_and_tags_on_open(self):
        t = tickets.open_ticket(
            type="control",
            title="hard splash 233 m/s",
            reporter="Hank",
            category="bug",
            tags=["Hard Splash", "east-t3"],
            desk="lars",
        )
        self.assertEqual(t["category"], "bug")
        self.assertEqual(t["tags"], ["hard-splash", "east-t3"])
        rows = tickets.list_tickets(category="bug", tag="hard-splash")
        self.assertEqual([r["id"] for r in rows], [t["id"]])

    def test_science_ids_from_ticket_payload(self):
        tickets.open_ticket(
            type="science",
            title="splash goo",
            reporter="Linus",
            payload={
                "experiment_id": "mysteryGoo",
                "situation": "SrfSplashed",
                "part": "GooExperiment",
            },
        )
        tickets.open_ticket(
            type="science",
            title="flying thermo",
            reporter="Linus",
            payload={
                "experiment_id": "temperatureScan",
                "situation": "FlyingLow",
            },
        )
        self.assertEqual(
            tickets.science_ids_for(situation="splash"),
            ("mysteryGoo",),
        )
        self.assertEqual(
            tickets.science_ids_for(situation="flying"),
            ("temperatureScan",),
        )
        tickets.open_ticket(
            type="science",
            title="splash telem first",
            reporter="Linus",
            payload={
                "experiment_id": "kerbalism_TELEMETRY",
                "situation": "SrfSplashed",
                "seq": 0,
            },
        )
        self.assertEqual(
            tickets.science_ids_for(situation="splash"),
            ("kerbalism_TELEMETRY", "mysteryGoo"),
        )

    def test_attach_run_landing_on_skim_not_jsonl(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-to-water",
            reporter="Hank",
            desk="gene",
            severity="S2",
            priority="P0",
        )
        path = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "telem"
            / "hard-splash.jsonl"
        )
        tickets.attach_run(t["id"], path, who="hank")
        skim = tickets.format_packet(t["id"], deep=False)
        deep = tickets.format_packet(t["id"], deep=True)
        self.assertIn("landing: catastrophic", skim)
        self.assertIn("category: flight", skim)
        self.assertIn("docs/program/tickets/BRIEF.md", skim)
        self.assertNotIn("hard-splash.jsonl", skim)
        self.assertIn("hard-splash.jsonl", deep)
        self.assertIn("catastrophic", tickets.format_inbox("gene"))

    def test_attach_run_preserves_top_level_go(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-to-water",
            reporter="Hank",
            desk="gene",
            payload={"cli": "python main.py hop-to-water", "go": ""},
        )
        tickets.patch_ticket(t["id"], {"go": "yes"}, who="gene")
        path = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "telem"
            / "hard-splash.jsonl"
        )
        tickets.attach_run(t["id"], path, who="hank")
        cur = tickets.show_ticket(t["id"])
        self.assertEqual(cur["go"], "yes")
        self.assertEqual(
            (cur.get("payload") or {}).get("cli"),
            "python main.py hop-to-water",
        )

    def test_cmd_inbox_and_landing(self):
        from contextlib import redirect_stdout
        from io import StringIO

        t = tickets.open_ticket(
            type="control",
            title="heading 301",
            reporter="Jebediah",
            desk="lars",
            tags=["heading-090"],
        )
        buf = StringIO()
        with redirect_stdout(buf):
            rc = tickets.cmd_tickets(["inbox", "--desk", "lars"])
        self.assertEqual(rc, 0)
        self.assertIn(t["id"], buf.getvalue())
        path = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "telem"
            / "hard-splash.jsonl"
        )
        buf2 = StringIO()
        with redirect_stdout(buf2):
            rc2 = tickets.cmd_tickets(["landing", str(path)])
        self.assertEqual(rc2, 0)
        self.assertIn("catastrophic", buf2.getvalue())
