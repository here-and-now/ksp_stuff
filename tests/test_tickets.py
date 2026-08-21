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

    def test_leftover_hangar_line(self):
        act = ops.next_actions(
            desk={"hangar": "phase t7 sit=LANDED"},
            locked=False,
        )
        self.assertEqual(act["hire"][0]["desk"], "jebediah")
        self.assertIn("leftover", act["hire"][0]["why"])
