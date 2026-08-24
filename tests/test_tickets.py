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
        self.assertEqual(tickets.fly_fields(None)["learn"], "")
        t3 = {"payload": {"learn": "heading never 090", "campaign": "none"}}
        self.assertEqual(tickets.fly_fields(t3)["learn"], "heading never 090")
        self.assertFalse(tickets.needs_learn(t3))
        self.assertTrue(tickets.needs_learn({"payload": {"campaign": "none"}}))
        self.assertFalse(
            tickets.needs_learn({"payload": {"campaign": "uncrewed"}})
        )

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
        tickets.stamp_learn(t["id"], "envelope heading 300", who="gene")
        cur = tickets.show_ticket(t["id"])
        self.assertEqual(cur["go"], "yes")
        self.assertEqual(cur["payload"]["learn"], "envelope heading 300")
        self.assertEqual(tickets.fly_fields(cur)["learn"], "envelope heading 300")

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
        rsi_rows = [t for t in tickets.list_tickets() if t.get("type") == "rsi"]
        self.assertEqual(len(rsi_rows), 1)
        rsi = rsi_rows[0]
        self.assertEqual(rsi["priority"], "P1")
        self.assertEqual(rsi["desk"], "mortimer")
        tickets.open_ticket(
            type="control",
            title="ec=0 splash again",
            reporter="Jebediah",
            fingerprint="ec=0-after-loft",
        )
        rsi_rows = [t for t in tickets.list_tickets() if t.get("type") == "rsi"]
        self.assertEqual(len(rsi_rows), 1)
        self.assertIsNone(tickets.maybe_open_rsi("ec=0-after-loft"))

    def test_rsi_software_desk_wernher(self):
        for i in range(3):
            tickets.open_ticket(
                type="systems",
                title=f"leftover vs krpc {i}",
                reporter="Wernher",
                fingerprint="desk-leftover-vs-krpc",
                rsi_loop="software",
            )
        rsi_rows = [t for t in tickets.list_tickets() if t.get("type") == "rsi"]
        self.assertEqual(len(rsi_rows), 1)
        self.assertEqual(rsi_rows[0]["desk"], "wernher")
        self.assertEqual(rsi_rows[0]["rsi_loop"], "software")

    def test_rsi_long_abort_fingerprint_ignored(self):
        novel = "suicide leftover LF MET 179.7 then splash catastrophic impact 124 m/s " * 2
        self.assertGreater(len(novel), 80)
        self.assertEqual(tickets.normalize_fingerprint(novel), "")
        with self.assertRaises(tickets.TicketError) as ctx:
            tickets.open_ticket(
                type="control",
                title="splash novel",
                reporter="Jebediah",
                fingerprint=novel,
            )
        self.assertIn("fingerprint required", str(ctx.exception))
        self.assertIn("reuse (count):", str(ctx.exception))
        for i in range(3):
            tickets.open_ticket(
                type="vehicle",
                title=f"splash novel {i}",
                reporter="Gus",
                fingerprint=novel,
            )
        rsi_rows = [t for t in tickets.list_tickets() if t.get("type") == "rsi"]
        self.assertEqual(rsi_rows, [])

    def test_batch_ids(self):
        tickets.open_ticket(type="vehicle", title="a", reporter="Gus")
        tickets.open_ticket(type="vehicle", title="b", reporter="Gus")
        rows = tickets.list_tickets(desk="gus")
        self.assertEqual([r["id"] for r in rows], ["T-001", "T-002"])

    def test_control_empty_fingerprint_refused(self):
        with self.assertRaises(tickets.TicketError) as ctx:
            tickets.open_ticket(
                type="control", title="heading 299", reporter="Lars"
            )
        msg = str(ctx.exception)
        self.assertIn("fingerprint required for control", msg)
        self.assertIn("copy: --fingerprint", msg)
        with self.assertRaises(tickets.TicketError):
            tickets.open_ticket(
                type="ops",
                title="house friction",
                reporter="Hank",
                tags=["feedback"],
            )
        t = tickets.open_ticket(
            type="ops",
            title="ask gus",
            reporter="Linus",
            tags=["ask"],
        )
        self.assertEqual(t["fingerprint"], "")
        twin = tickets.open_ticket(
            type="control",
            title="old lesson",
            reporter="Lars",
            tags=["legacy-twin", "lesson"],
            fingerprint="",
        )
        self.assertEqual(twin["fingerprint"], "")

    def test_fingerprint_alias_and_novels(self):
        self.assertEqual(tickets.normalize_fingerprint("hop-081"), "")
        self.assertEqual(
            tickets.normalize_fingerprint("2026-08-23-heading-stuck"), ""
        )
        self.assertEqual(tickets.normalize_fingerprint("22-33-35Z-shear"), "")
        self.assertEqual(
            tickets.normalize_fingerprint("flyinghigh-lid-18km-hop"),
            "flyinghigh-lid-18km-hop",
        )
        first = tickets.open_ticket(
            type="control",
            title="flyinghigh lid",
            reporter="Lars",
            fingerprint="flyinghigh-lid",
        )
        self.assertEqual(first["fingerprint"], "flyinghigh-lid")
        second = tickets.open_ticket(
            type="control",
            title="flyinghigh lid 18km",
            reporter="Lars",
            fingerprint="flyinghigh-lid-18km-hop",
        )
        self.assertEqual(second["fingerprint"], "flyinghigh-lid")
        self.assertEqual(tickets.fingerprint_count("flyinghigh-lid"), 2)
        self.assertEqual(tickets.fingerprint_count("flyinghigh-lid-18km-hop"), 0)
        inland = tickets.open_ticket(
            type="control",
            title="inland heading 299",
            reporter="Lars",
            fingerprint="heading-299-inland",
        )
        self.assertEqual(inland["fingerprint"], "heading-299-inland")
        self.assertNotEqual(inland["fingerprint"], "heading-never-090")
        tickets.open_ticket(
            type="control",
            title="flyinghigh lid again",
            reporter="Lars",
            fingerprint="flyinghigh-lid-retry",
        )
        rsi_rows = [t for t in tickets.list_tickets() if t.get("type") == "rsi"]
        self.assertEqual(len(rsi_rows), 1)
        self.assertEqual(rsi_rows[0]["fingerprint"], "flyinghigh-lid")

    def test_patch_add_fp_increments(self):
        t = tickets.open_ticket(type="vehicle", title="ghost", reporter="Gus")
        self.assertEqual(t["fingerprint"], "")
        self.assertEqual(tickets.fingerprint_count("desk-leftover-vs-krpc"), 0)
        tickets.patch_ticket(
            t["id"], {"fingerprint": "desk-leftover-vs-krpc"}, who="hank"
        )
        self.assertEqual(tickets.fingerprint_count("desk-leftover-vs-krpc"), 1)
        tickets.patch_ticket(t["id"], {"title": "ghost 2"}, who="hank")
        self.assertEqual(tickets.fingerprint_count("desk-leftover-vs-krpc"), 1)

    def test_feedback_appends_and_close_refuses_empty(self):
        from contextlib import redirect_stdout
        from io import StringIO

        self.assertEqual(len(tickets.TYPES), 11)
        hire = tickets.open_ticket(
            type="systems",
            title="kernel door",
            reporter="Mortimer",
            desk="wernher",
            fingerprint="feedback-return",
        )
        with self.assertRaises(tickets.TicketError) as ctx:
            tickets.close_ticket(hire["id"], who="wernher")
        self.assertIn("empty findings", str(ctx.exception))
        with self.assertRaises(tickets.TicketError) as empty_claim:
            tickets.add_feedback(hire["id"], claim="", who="wernher")
        self.assertIn("claim required", str(empty_claim.exception))
        with self.assertRaises(tickets.TicketError) as real_no_ev:
            tickets.add_feedback(
                hire["id"],
                claim="confirm leftover",
                real=True,
                who="wernher",
            )
        self.assertIn("--real requires --evidence", str(real_no_ev.exception))
        own = tickets.add_feedback(
            hire["id"],
            claim="I could write fewer tests",
            who="wernher",
        )
        rows = tickets.finding_rows(own)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["claim"], "I could write fewer tests")
        self.assertEqual(rows[0]["owner"], "none")
        self.assertEqual(rows[0]["evidence"], "")
        self.assertFalse(rows[0]["real"])
        self.assertEqual(rows[0]["who"], "wernher")
        self.assertNotIn("good", rows[0])
        self.assertNotIn("self", rows[0])
        self.assertNotIn("them", rows[0])
        req = tickets.add_feedback(
            hire["id"],
            claim="leftover abort should live in physics_warp",
            evidence="hop.py:892",
            owner="lars leftover abort",
            who="wernher",
        )
        self.assertEqual(len(tickets.finding_rows(req)), 2)
        last = tickets.last_feedback(req)
        assert last is not None
        self.assertEqual(last["owner"], "lars")
        self.assertEqual(tickets.them_desk(str(last.get("owner") or "")), "lars")
        ops_rows = [t for t in tickets.list_tickets() if t.get("type") == "ops"]
        self.assertEqual(ops_rows, [])
        with self.assertRaises(SystemExit):
            tickets.cmd_tickets(
                [
                    "feedback",
                    hire["id"],
                    "--good",
                    "CLI append",
                    "--self",
                    "close after three rows",
                    "--them",
                    "none",
                    "--who",
                    "wernher",
                ]
            )
        buf = StringIO()
        with redirect_stdout(buf):
            rc = tickets.cmd_tickets(
                [
                    "feedback",
                    hire["id"],
                    "--claim",
                    "CLI append",
                    "--who",
                    "wernher",
                ]
            )
        self.assertEqual(rc, 0)
        self.assertIn("feedback", buf.getvalue())
        stored = tickets.show_ticket(hire["id"])
        claims = [r["claim"] for r in tickets.finding_rows(stored)]
        self.assertIn("CLI append", claims)
        skim = tickets.format_packet(hire["id"], deep=False)
        self.assertIn("finding:", skim)
        self.assertIn("CLI append", skim)
        self.assertIn("I could write fewer tests", skim)
        self.assertIn(f'tickets feedback {hire["id"]} --claim "…"', skim)
        self.assertNotIn("good=", skim)
        nag = tickets.inbox_for("wernher", feedback=True)
        self.assertFalse(any(r["id"] == hire["id"] for r in nag))
        addressed = tickets.inbox_for("lars", feedback=True)
        self.assertEqual([r["id"] for r in addressed], [hire["id"]])
        tickets.add_feedback(
            hire["id"],
            claim="keep flying",
            owner="none",
            who="wernher",
        )
        addressed = tickets.inbox_for("lars", feedback=True)
        self.assertEqual([r["id"] for r in addressed], [hire["id"]])
        buf2 = StringIO()
        with redirect_stdout(buf2):
            rc2 = tickets.cmd_tickets(
                ["close", hire["id"], "--why", "kernel door", "--who", "wernher"]
            )
        self.assertEqual(rc2, 0)
        self.assertIn("done", buf2.getvalue())

    def test_legacy_trio_reads_as_finding(self):
        hire = tickets.open_ticket(
            type="systems",
            title="legacy door",
            reporter="Mortimer",
            desk="wernher",
            fingerprint="feedback-return",
        )
        tickets.patch_ticket(
            hire["id"],
            {
                "payload": {
                    "feedback": [
                        {
                            "who": "mortimer",
                            "good": "packet skim",
                            "self": "T-375 restored Return keys",
                            "them": "wernher land tickets feedback",
                            "at": "2026-08-24T00:00:00Z",
                        }
                    ]
                }
            },
            who="hank",
        )
        rows = tickets.finding_rows(tickets.show_ticket(hire["id"]))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["claim"], "T-375 restored Return keys")
        self.assertEqual(rows[0]["owner"], "wernher")
        self.assertEqual(rows[0]["evidence"], "")
        self.assertFalse(rows[0]["real"])
        self.assertEqual(rows[0]["who"], "mortimer")

    def test_close_harvests_why_when_findings_empty(self):
        hire = tickets.open_ticket(
            type="control",
            title="lid ifs",
            reporter="Lars",
            desk="lars",
            fingerprint="flyinghigh-lid",
        )
        closed = tickets.close_ticket(
            hire["id"], why="kernel door from close_why", who="lars"
        )
        self.assertEqual(closed["status"], "done")
        self.assertEqual(closed.get("close_why"), "kernel door from close_why")
        rows = tickets.finding_rows(closed)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["claim"], "kernel door from close_why")
        self.assertEqual(rows[0]["who"], "lars")

    def test_feedback_real_needs_evidence_via_cli(self):
        from contextlib import redirect_stdout
        from io import StringIO

        hire = tickets.open_ticket(
            type="systems",
            title="confirm leftover",
            reporter="Wernher",
            desk="wernher",
            fingerprint="control-blocks",
        )
        rc_bad = tickets.cmd_tickets(
            [
                "feedback",
                hire["id"],
                "--claim",
                "confirm leftover_wreck still hop.py:892",
                "--who",
                "wernher",
                "--real",
            ]
        )
        self.assertEqual(rc_bad, 1)
        self.assertEqual(tickets.finding_rows(tickets.show_ticket(hire["id"])), [])
        buf = StringIO()
        with redirect_stdout(buf):
            rc = tickets.cmd_tickets(
                [
                    "feedback",
                    hire["id"],
                    "--claim",
                    "confirm leftover_wreck still hop.py:892",
                    "--evidence",
                    "hop.py:892",
                    "--who",
                    "wernher",
                    "--real",
                ]
            )
        self.assertEqual(rc, 0)
        last = tickets.last_feedback(tickets.show_ticket(hire["id"]))
        assert last is not None
        self.assertTrue(last["real"])
        self.assertEqual(last["evidence"], "hop.py:892")
        skim = tickets.format_packet(hire["id"], deep=False)
        self.assertIn(" real", skim)

    def test_inbox_feedback_nags_owned_missing(self):
        t = tickets.open_ticket(
            type="systems",
            title="extract blocks",
            reporter="Mortimer",
            desk="wernher",
            fingerprint="control-blocks",
        )
        rows = tickets.inbox_for("wernher", feedback=True)
        self.assertEqual([r["id"] for r in rows], [t["id"]])
        text = tickets.format_inbox("wernher", feedback=True)
        self.assertIn("inbox wernher feedback:", text)
        self.assertIn(t["id"], text)


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
        text = ops.format_next(act)
        self.assertIn("rsi:", text)
        self.assertIn("writer: hop-pid", text)
        self.assertIn("commander: jebediah", text)

    def test_uncrewed_parent_starts_hop_no_commander_hire(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            severity="S2",
            priority="P0",
        )
        tickets.patch_ticket(t["id"], {"go": "yes", "status": "ready"}, who="gene")
        tickets.patch_ticket(
            t["id"],
            {
                "payload": {
                    "go": "yes",
                    "cli": "python main.py hop",
                    "campaign": "uncrewed",
                }
            },
            who="hank",
        )
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        self.assertEqual(act["hire"][0]["desk"], "hank")
        self.assertEqual(act["hire"][0]["cli"], "python main.py hop")
        self.assertEqual(act.get("commander"), "none")
        self.assertEqual(act.get("writer"), "hop-pid")
        self.assertNotIn("jebediah", [h["desk"] for h in act["hire"]])
        text = ops.format_next(act)
        self.assertIn("commander: none", text)
        self.assertIn("writer: hop-pid", text)
        self.assertEqual(tickets.commander_for(campaign="uncrewed"), "none")
        self.assertEqual(tickets.commander_for(campaign="none"), "jebediah")
        self.assertIn("katherine", tickets.DESKS)

    def test_fly_ready_hires_katherine_only_with_inbox(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            payload={"go": "yes", "cli": "python main.py hop", "campaign": "uncrewed"},
        )
        tickets.patch_ticket(t["id"], {"go": "yes", "status": "ready"}, who="gene")
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        self.assertNotIn("katherine", [h["desk"] for h in act["hire"]])
        tickets.open_ticket(
            type="ops",
            title="Flight Dynamics: burnout vs FAR",
            reporter="Mortimer",
            desk="katherine",
            tags=["dynamics"],
        )
        act2 = ops.next_actions(desk={"hangar": "none"}, locked=False)
        self.assertIn("katherine", [h["desk"] for h in act2["hire"]])

    def test_fly_ready_hires_mortimer_on_rsi(self):
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
        rsi = tickets.open_ticket(
            type="rsi",
            title="RSI heading-never-090 x3",
            reporter="Hank",
            desk="mortimer",
            fingerprint="heading-never-090",
            rsi_loop="ops",
        )
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        desks = [h["desk"] for h in act["hire"]]
        self.assertEqual(desks[0], "jebediah")
        self.assertIn("mortimer", desks)
        mort = next(h for h in act["hire"] if h["desk"] == "mortimer")
        self.assertIn(rsi["id"], mort["tickets"])
        text = ops.format_next(act)
        self.assertIn("rsi: " + rsi["id"], text)
        live = ops.next_actions(desk={"hangar": "none"}, locked=True)
        self.assertNotIn("mortimer", [h["desk"] for h in live["hire"]])
        self.assertNotIn("jebediah", [h["desk"] for h in live["hire"]])

    def test_unbound_science_not_in_linus_hire_or_bind(self):
        tickets.open_ticket(
            type="science",
            title="FlyingLow@Water thermo",
            reporter="Linus",
            tags=["unbound"],
            payload={"experiment_id": "temperatureScan", "situation": "FlyingLow"},
        )
        tickets.open_ticket(
            type="science",
            title="Grasslands FlyingLow thermo",
            reporter="Linus",
            tags=["bound"],
            payload={
                "experiment_id": "temperatureScan",
                "situation": "FlyingLow",
                "bound": "yes",
            },
        )
        self.assertEqual(
            tickets.science_ids_for(situation="flying"),
            ("temperatureScan",),
        )
        t = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            payload={"cli": "python main.py hop"},
        )
        tickets.patch_ticket(t["id"], {"go": "yes", "status": "ready"}, who="gene")
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        linus = next(h for h in act["hire"] if h["desk"] == "linus")
        titles = [tickets.show_ticket(i)["title"] for i in linus["tickets"]]
        self.assertTrue(any("Grasslands" in x for x in titles))
        self.assertFalse(any("Water" in x for x in titles))

    def test_inbox_includes_ask_payload_to(self):
        tickets.open_ticket(
            type="ops",
            title="need a stiffer hang",
            reporter="Linus",
            desk="linus",
            tags=["ask"],
            payload={"to": "gus"},
        )
        rows = tickets.inbox_for("gus")
        self.assertEqual([r["title"] for r in rows], ["need a stiffer hang"])
        self.assertTrue(tickets.inbox_for("linus"))

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

    def test_needing_go_batches_systems(self):
        tickets.open_ticket(
            type="fly", title="hop-splash", reporter="Hank", desk="gene"
        )
        tickets.open_ticket(
            type="systems",
            title="packet skim",
            reporter="Wernher",
            desk="wernher",
            fingerprint="packet-skim",
        )
        tickets.open_ticket(type="vehicle", title="t7", reporter="Gus")
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        desks = [h["desk"] for h in act["hire"]]
        self.assertEqual(desks[0], "gene")
        self.assertIn("wernher", desks)
        self.assertIn("gus", desks)
        self.assertNotIn("jebediah", desks)
        self.assertIsNone(act["fly_ready"])

    def test_fly_ready_not_stolen_by_learn(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
            payload={"campaign": "none", "cli": "python main.py hop-splash"},
        )
        tickets.patch_ticket(
            t["id"],
            {"go": "yes", "status": "ready"},
            who="gene",
        )
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        desks = [h["desk"] for h in act["hire"]]
        self.assertEqual(desks[0], "jebediah")
        self.assertNotIn("gene", desks)
        self.assertEqual(act["fly_ready"], t["id"])

    def test_campaign_stop_hires_gene_for_learn(self):
        tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
            payload={"campaign": "none", "cli": "python main.py hop-splash"},
        )
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        hire = act["hire"][0]
        self.assertEqual(hire["desk"], "gene")
        self.assertIn("Learn", hire["why"])
        self.assertIsNone(act["fly_ready"])

    def test_uncrewed_missing_go_is_stamp_not_learn(self):
        tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
            payload={"campaign": "uncrewed"},
        )
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        self.assertEqual(act["hire"][0]["desk"], "gene")
        self.assertEqual(act["hire"][0]["why"], "fly ticket needs go stamp")

    def test_lock_live_hires_wernher_not_gene(self):
        tickets.open_ticket(
            type="systems",
            title="desk leftover",
            reporter="Wernher",
            fingerprint="desk-leftover-vs-krpc",
        )
        act = ops.next_actions(desk={"hangar": "none"}, locked=True)
        desks = [h["desk"] for h in act["hire"]]
        self.assertIn("wernher", desks)
        self.assertNotIn("gene", desks)
        self.assertNotIn("jebediah", desks)

    def test_s1_recover_first(self):
        tickets.open_ticket(
            type="recover",
            title="Forest land",
            reporter="Hank",
            severity="S1",
            priority="P0",
            desk="hank",
        )
        tickets.patch_ticket("T-001", {"status": "ready"}, who="hank")
        act = ops.next_actions(desk={"hangar": "none"}, locked=False)
        self.assertEqual(act["hire"][0]["desk"], "hank")
        self.assertIn("S1 recover", act["hire"][0]["why"])
        self.assertEqual(
            act["hire"][0]["cli"],
            "python main.py recover-probe --recover",
        )
        self.assertEqual(act["ksc"], "leftover")
        self.assertIn("recover-probe", act["call"])

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
        self.assertEqual(act["hire"][0]["desk"], "hank")
        self.assertIn("leftover", act["hire"][0]["why"])
        self.assertEqual(
            act["hire"][0]["cli"],
            "python main.py recover-probe --recover",
        )
        self.assertEqual(act["ksc"], "leftover")
        text = ops.format_next(act)
        self.assertIn("ksc: leftover", text)
        self.assertIn("call: python main.py recover-probe --recover", text)

    def test_leftover_n_hires_hank_not_commander(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-splash",
            reporter="Hank",
            desk="gene",
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
        act = ops.next_actions(
            desk={"hangar": "none", "leftover": "1"},
            locked=False,
        )
        self.assertEqual(act["hire"][0]["desk"], "hank")
        self.assertIsNone(act["fly_ready"])
        self.assertIn("recover-probe", act["hire"][0]["cli"])

    def test_leftover_recover_hangar_uses_space_center_call(self):
        act = ops.next_actions(
            desk={"hangar": "recover flea sit=FLYING"},
            locked=False,
        )
        self.assertEqual(act["hire"][0]["desk"], "hank")
        self.assertEqual(
            act["hire"][0]["cli"],
            "python main.py recover-probe --space-center",
        )


    def test_parse_desk_leftover_comment(self):
        d = ops.parse_desk("hangar: none\n# leftover vessels n=2\n")
        self.assertEqual(d["leftover"], "2")
        self.assertEqual(ops.leftover_n(d), 2)


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

    def test_reasoning_desk_floors_never_xhigh(self):
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
        self.assertEqual(tickets.reasoning_for(s1, "wernher"), "high")
        self.assertEqual(tickets.reasoning_for(s1, "lars"), "high")
        self.assertEqual(tickets.reasoning_for(s1, "walt"), "low")
        gene = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            severity="S2",
            priority="P0",
        )
        self.assertEqual(tickets.reasoning_for(gene), "medium")
        gene["severity"] = "S1"
        self.assertEqual(tickets.reasoning_for(gene), "high")
        lars = tickets.open_ticket(
            type="control",
            title="heading",
            reporter="Hank",
            desk="lars",
            severity="S2",
            priority="P0",
            fingerprint="heading-hold",
        )
        self.assertEqual(tickets.reasoning_for(lars), "medium")
        rsi = tickets.open_ticket(
            type="rsi",
            title="RSI stem",
            reporter="Hank",
            desk="mortimer",
            fingerprint="heading-never-090",
        )
        self.assertEqual(tickets.reasoning_for(rsi), "high")

    def test_skim_omits_jsonl_deep_includes_it(self):
        t = tickets.open_ticket(
            type="control",
            title="relight on descent",
            reporter="Jebediah",
            severity="S2",
            priority="P1",
            desk="lars",
            fingerprint="relight-on-descent",
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
        self.assertIn("docs/program/tickets/BRIEF.md", skim)
        self.assertNotIn("BOARD.md", skim)
        self.assertIn("inbox:", skim)
        self.assertNotIn(".jsonl", skim)
        self.assertIn("packet T-001 --deep", skim)
        self.assertNotRegex(deep, r"(?m)^  - .+\.jsonl")
        self.assertIn("python main.py telem", deep)
        self.assertIn(".jsonl", deep)
        self.assertNotIn('"kind": "state"', deep)
        self.assertNotIn("kind=state", skim)
        self.assertIn("reasoning: medium", skim)
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
        self.assertNotIn("BOARD.md", out)
        self.assertNotIn(".jsonl", out)
        self.assertIn("--deep", out)
        self.assertIn("reasoning: medium", out)

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
        self.assertNotIn("--deep", hire["packet"])
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
            fingerprint="hard-splash-east-t3",
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

    def test_fly_science_ids_union_bound_not_shadow(self):
        tickets.open_ticket(
            type="science",
            title="flying telem",
            reporter="Linus",
            payload={
                "experiment_id": "kerbalism_TELEMETRY",
                "situation": "FlyingLow",
                "seq": 2,
            },
        )
        tickets.open_ticket(
            type="science",
            title="flying goo",
            reporter="Linus",
            payload={
                "experiment_id": "mysteryGoo",
                "situation": "FlyingLow",
                "seq": 3,
            },
        )
        fly = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            payload={"science_ids": ["temperatureScan"]},
        )
        self.assertEqual(
            tickets.card_science_ids(situation="flying", ticket=fly),
            ("kerbalism_TELEMETRY", "mysteryGoo", "temperatureScan"),
        )
        self.assertEqual(
            tickets.union_science_ids(
                ("kerbalism_TELEMETRY", "mysteryGoo"),
                ("temperatureScan",),
            ),
            ("kerbalism_TELEMETRY", "mysteryGoo", "temperatureScan"),
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
        self.assertIn("horiz=", skim)
        self.assertIn("pitch=", skim)
        self.assertIn("category: flight", skim)
        self.assertIn("docs/program/tickets/BRIEF.md", skim)
        self.assertNotIn("BOARD.md", skim)
        self.assertNotIn("hard-splash.jsonl", skim)
        self.assertIn("hard-splash.jsonl", deep)
        self.assertIn("python main.py telem", deep)
        self.assertNotRegex(deep, r"(?m)^  - .+\.jsonl")
        self.assertIn("eyes:", skim)
        self.assertIn("last:", skim)
        self.assertNotIn('"kind": "state"', skim)
        self.assertNotIn("kind=state", skim)
        self.assertIn("catastrophic", tickets.format_inbox("gene"))
        self.assertIn("S2 P0", tickets.format_list(tickets.list_tickets()))
        self.assertNotIn("S2P0", tickets.format_list(tickets.list_tickets()))
        self.assertIn("S2 P0", tickets.format_packet("T-001", deep=False))
        self.assertNotIn("S2P0", tickets.format_packet("T-001", deep=False))


class TestHouseDump(unittest.TestCase):
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

    def test_science_dump_catalog_vs_bound(self):
        from house_dump import format_science_dump, format_seated_science, render_plan

        unbound = tickets.open_ticket(
            type="science",
            title="FlyingLow@Water thermo",
            reporter="Linus",
            tags=["unbound"],
            payload={"experiment_id": "temperatureScan", "situation": "FlyingLow@Water"},
        )
        bound = tickets.open_ticket(
            type="science",
            title="Grasslands FlyingLow thermo",
            reporter="Linus",
            tags=["bound"],
            payload={
                "experiment_id": "temperatureScan",
                "situation": "FlyingLow",
                "biome": "Grasslands",
                "bound": "yes",
                "recover_banks": "yes",
            },
        )
        desk = {"sci": "7.7748", "craft": "proc-stiff", "unlocked": "start", "leftover": "0"}
        text = format_science_dump(desk=desk)
        work, shelf = text.split("## Catalog", 1)
        self.assertIn(bound["id"], work)
        self.assertNotIn(unbound["id"], work)
        self.assertIn(unbound["id"], shelf)
        self.assertNotIn("east-t3", text.lower())
        seated = format_seated_science(desk=desk)
        self.assertIn("recover_banks: yes", seated)
        self.assertNotIn("east-t3", seated.lower())
        tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            payload={"go": "yes", "cli": "python main.py hop", "campaign": "uncrewed", "phase": "hop"},
        )
        tickets.patch_ticket("T-003", {"go": "yes"}, who="gene")
        tmp = Path(tempfile.mkdtemp()) / "plan.md"
        tmp.write_text(
            "phase: hop\ngo: wait\nrecommended: python main.py hop-to-water\nhop_apo: 18000\n",
            encoding="utf-8",
        )
        out = render_plan(tmp)
        self.assertNotIn("recommended:", out)
        self.assertIn("cli: python main.py hop", out)
        self.assertIn("hop_apo: 18000", out)


class TestMigrateSecondBus(unittest.TestCase):
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

    def test_idempotent_and_no_i013_duplicate(self):
        first = tickets.seed_legacy()
        self.assertTrue(first)
        titles = [t["title"] for t in tickets.load_head()["tickets"].values()]
        self.assertEqual(sum(1 for t in titles if "I-013" in t), 1)
        self.assertEqual(sum(1 for t in titles if "I-017" in t), 1)
        self.assertTrue(any("I-012" in t for t in titles))
        self.assertTrue(any("F-014" in t for t in titles))
        self.assertTrue(any("F-007" in t for t in titles))
        again = tickets.seed_legacy()
        self.assertEqual(again, [])
        titles2 = [t["title"] for t in tickets.load_head()["tickets"].values()]
        self.assertEqual(sum(1 for t in titles2 if "I-013" in t), 1)
        self.assertEqual(sum(1 for t in titles2 if "I-012" in t), 1)
        self.assertEqual(tickets.TYPES, (
            "fly",
            "science",
            "vehicle",
            "control",
            "systems",
            "org",
            "rsi",
            "ctt",
            "recover",
            "press",
            "ops",
        ))

    def test_skim_omits_parked_dispatch(self):
        from docs_inventory import FORBIDDEN_DISPATCH, packet_read_paths, skim_mentions_forbidden

        t = tickets.open_ticket(
            type="systems",
            title="F-014 load persistent autosaves RAM first",
            reporter="Mortimer",
            desk="wernher",
            fingerprint="f-014",
        )
        skim = tickets.format_packet(t["id"], deep=False)
        for path in packet_read_paths(skim):
            self.assertEqual(skim_mentions_forbidden(path), [])
        for needle in FORBIDDEN_DISPATCH:
            self.assertNotIn(needle, skim)


class TestLiveDocsInventory(unittest.TestCase):
    """Drive the real docs/ tree and live board — not a mocked inventory."""

    def test_every_docs_file_one_class(self):
        from docs_inventory import DOC_CLASSES, classified_map

        mapping = classified_map()
        self.assertGreater(len(mapping), 100)
        for rel, cls in mapping.items():
            self.assertIn(cls, DOC_CLASSES, rel)
        self.assertEqual(mapping["docs/program/CHARTER.md"], "live_kernel")
        self.assertEqual(mapping["docs/program/PROTOCOL.md"], "live_kernel")
        self.assertEqual(mapping["docs/program/OPS.md"], "live_kernel")
        self.assertEqual(mapping["docs/program/tickets/BRIEF.md"], "live_kernel")
        self.assertEqual(mapping["docs/missions/jebediah/plan.md"], "live_kernel")
        self.assertEqual(mapping["docs/missions/jebediah/science.md"], "live_kernel")
        self.assertEqual(mapping["docs/program/tickets/board.jsonl"], "live_kernel")
        leftover = [r for r, c in mapping.items() if c == "leftover_migrated"]
        self.assertTrue(any("I-012.md" in r for r in leftover))
        self.assertTrue(any("F-014.md" in r for r in leftover))
        parked = [r for r, c in mapping.items() if c == "parked_archive"]
        self.assertTrue(any(r.startswith("docs/archive/") for r in parked))
        self.assertFalse(Path("docs/program/improve/README.md").is_file())
        self.assertFalse(Path("docs/crew/niche/gene.md").is_file())

    def test_live_trio_rows_read_as_findings(self):
        self.assertEqual(len(tickets.TYPES), 11)
        for tid in ("T-375", "T-378", "T-379"):
            t = tickets.show_ticket(tid)
            rows = tickets.finding_rows(t)
            self.assertTrue(rows, tid)
            for row in rows:
                self.assertTrue(row.get("claim"), tid)
                self.assertIn(row.get("owner"), set(tickets.DESKS) | {"none"})
                self.assertFalse(row.get("real"))
                self.assertEqual(row.get("evidence"), "")

    def test_twins_on_live_board(self):
        from docs_inventory import if_tokens, twin_title_hits

        head = tickets.load_head()
        titles = [t.get("title") or "" for t in (head.get("tickets") or {}).values()]
        for token in if_tokens():
            self.assertGreaterEqual(
                twin_title_hits(titles, token),
                1,
                f"missing twin for {token}",
            )
            if token in {"I-013", "I-017", "I-018", "I-019"}:
                self.assertEqual(twin_title_hits(titles, token), 1, token)

    def test_spawn_read_omits_parked_dispatch(self):
        from docs_inventory import FORBIDDEN_DISPATCH, packet_read_paths, skim_mentions_forbidden

        for path in (
            Path("AGENTS.md"),
            Path("docs/program/tickets/BRIEF.md"),
        ):
            text = path.read_text(encoding="utf-8")
            for needle in FORBIDDEN_DISPATCH:
                self.assertNotIn(needle, text, path.as_posix())
        rows = tickets.list_tickets()
        twin = next(
            (t for t in rows if "F-014" in (t.get("title") or "")),
            rows[0] if rows else None,
        )
        self.assertIsNotNone(twin)
        skim = tickets.format_packet(twin["id"], deep=False)
        self.assertEqual(skim_mentions_forbidden(skim), [])
        for p in packet_read_paths(skim):
            self.assertEqual(skim_mentions_forbidden(p), [])
            self.assertFalse(p.startswith("docs/archive/"))
            self.assertFalse(p.startswith("docs/crew/niche/"))
            self.assertFalse(p.startswith("docs/program/improve/"))


class TestPacketAttachAndInbox(unittest.TestCase):
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
            fingerprint="heading-301",
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
        self.assertIn("eyes:", buf2.getvalue())
        self.assertNotIn('"kind": "state"', buf2.getvalue())

    def test_packet_prints_learn(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop-to-water",
            reporter="Hank",
            desk="gene",
            payload={"cli": "python main.py hop-to-water", "campaign": "none"},
        )
        tickets.stamp_learn(t["id"], "heading never 090", who="gene")
        skim = tickets.format_packet(t["id"], deep=False)
        self.assertIn("learn: heading never 090", skim)
        self.assertNotIn("BOARD.md", skim)

    def test_attach_run_stamps_learn_and_sci_unchanged_bump(self):
        t = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            payload={"cli": "python main.py hop", "campaign": "uncrewed"},
        )
        env = {
            "landing": "soft",
            "impact_ms": 5,
            "heading": 299,
            "horiz": 0,
            "pitch": 90,
            "sit": "landed",
            "apo_max": 1611,
            "biome": "Shores",
            "recoverable": True,
            "sci_run": 0,
            "sci_bank": 8.77,
        }
        path = Path(tempfile.mkdtemp()) / "a.jsonl"
        path.write_text("{}\n", encoding="utf-8")
        with patch("tape.envelope", return_value=env):
            tickets.attach_run(t["id"], path, who="wernher")
        cur = tickets.show_ticket(t["id"])
        learn = (cur.get("payload") or {}).get("learn") or ""
        self.assertIn("landing: soft", learn)
        self.assertIn("apo=1611", learn)
        self.assertIn("biome=Shores", learn)
        self.assertIn("rec=yes", learn)
        self.assertIn("sci=run=0", learn)
        self.assertIn("bank=8.77", learn)
        self.assertEqual(tickets.fingerprint_count(tickets.SCI_UNCHANGED_FP), 1)
        self.assertFalse(tickets.needs_learn(cur))
        skim = tickets.format_packet(t["id"], deep=False)
        self.assertIn("learn:", skim)
        self.assertIn("rec=yes", skim)
        harvested = tickets.finding_rows(cur)
        self.assertEqual(len(harvested), 1)
        self.assertEqual(harvested[0]["who"], "hank")
        self.assertEqual(harvested[0]["claim"], learn)
        self.assertEqual(harvested[0]["evidence"], str(path))
        self.assertIn(f'tickets feedback {t["id"]} --claim "…"', skim)
        with patch("tape.envelope", return_value=env):
            tickets.attach_run(t["id"], path, who="hank")
        self.assertEqual(tickets.fingerprint_count(tickets.SCI_UNCHANGED_FP), 1)
        self.assertEqual(len(tickets.finding_rows(tickets.show_ticket(t["id"]))), 1)
        path2 = Path(tempfile.mkdtemp()) / "b.jsonl"
        path2.write_text("{}\n", encoding="utf-8")
        with patch("tape.envelope", return_value=env):
            tickets.attach_run(t["id"], path2, who="hank")
        self.assertEqual(tickets.fingerprint_count(tickets.SCI_UNCHANGED_FP), 2)
        self.assertEqual(len(tickets.finding_rows(tickets.show_ticket(t["id"]))), 1)
        wreck = {
            **env,
            "landing": "catastrophic",
            "recoverable": False,
        }
        path3 = Path(tempfile.mkdtemp()) / "c.jsonl"
        path3.write_text("{}\n", encoding="utf-8")
        fly2 = tickets.open_ticket(
            type="fly",
            title="hop wreck",
            reporter="Hank",
            desk="gene",
            payload={"campaign": "uncrewed"},
        )
        with patch("tape.envelope", return_value=wreck):
            tickets.attach_run(fly2["id"], path3, who="hank")
        self.assertEqual(tickets.fingerprint_count(tickets.SCI_UNCHANGED_FP), 2)
        rsi = [x for x in tickets.list_tickets() if x.get("type") == "rsi"]
        self.assertEqual(rsi, [])
        waste = (tickets.show_ticket(t["id"]).get("payload") or {}).get("waste")
        self.assertIsInstance(waste, dict)
        self.assertIn("bind", waste)
        wreck_pl = tickets.show_ticket(fly2["id"]).get("payload") or {}
        self.assertNotIn("waste", wreck_pl)
        self.assertFalse(tickets.waste_blocks_refly(tickets.show_ticket(fly2["id"])))

    def test_waste_blocks_refly_until_bind_or_hang_changes(self):
        forest = tickets.open_ticket(
            type="science",
            title="Forest landed thermo",
            reporter="Linus",
            payload={
                "experiment_id": "temperatureScan",
                "situation": "SrfLanded@Forest",
                "biome": "Forest",
                "bound": "yes",
                "craft": "kspstuff-hop-valiant-proc-stiff-pbc",
            },
        )
        landing = {
            "landing": "soft",
            "sit": "landed",
            "biome": "Shores",
            "recoverable": True,
            "sci_run": 0,
            "sci_bank": 8.77,
        }
        snap = tickets.bind_snapshot(craft="kspstuff-hop-valiant-proc-stiff-pbc")
        fly = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            payload={
                "cli": "python main.py hop",
                "campaign": "uncrewed",
                "phase": "hop",
                "landing": landing,
                "waste": snap,
            },
        )
        tickets.patch_ticket(fly["id"], {"go": "yes", "status": "ready"}, who="gene")
        cur = tickets.show_ticket(fly["id"])
        self.assertTrue(
            tickets.waste_blocks_refly(
                cur, craft="kspstuff-hop-valiant-proc-stiff-pbc"
            )
        )
        self.assertFalse(tickets.needs_learn(cur))
        self.assertFalse(tickets.bind_matches_envelope(landing))
        tickets.patch_ticket(
            forest["id"],
            {
                "payload": {
                    **(tickets.show_ticket(forest["id"]).get("payload") or {}),
                    "situation": "SrfLanded@Shores",
                    "biome": "Shores",
                }
            },
            who="linus",
        )
        self.assertTrue(tickets.bind_matches_envelope(landing))
        self.assertFalse(
            tickets.waste_blocks_refly(
                tickets.show_ticket(fly["id"]),
                craft="kspstuff-hop-valiant-proc-stiff-pbc",
            )
        )

    def test_waste_blocks_refly_hang_changed_does_not_idle(self):
        tickets.open_ticket(
            type="science",
            title="Forest landed thermo",
            reporter="Linus",
            payload={
                "experiment_id": "temperatureScan",
                "situation": "SrfLanded@Forest",
                "biome": "Forest",
                "bound": "yes",
                "craft": "old-hang",
            },
        )
        landing = {
            "sit": "landed",
            "biome": "Shores",
            "recoverable": True,
            "sci_run": 0,
        }
        fly = {
            "go": "yes",
            "payload": {
                "campaign": "uncrewed",
                "landing": landing,
                "waste": {
                    "bind": [
                        {
                            "id": "T-001",
                            "eid": "temperatureScan",
                            "situation": "SrfLanded@Forest",
                            "biome": "Forest",
                        }
                    ],
                    "craft": "old-hang",
                },
            },
        }
        self.assertTrue(tickets.waste_blocks_refly(fly, craft="old-hang"))
        self.assertFalse(tickets.waste_blocks_refly(fly, craft="new-hang"))
        run1 = {**landing, "sci_run": 1}
        fly_run = {"payload": {"campaign": "uncrewed", "landing": run1, "waste": fly["payload"]["waste"]}}
        self.assertFalse(tickets.waste_blocks_refly(fly_run, craft="old-hang"))
        self.assertFalse(tickets.needs_learn(fly_run))

    def test_waste_blocks_refly_wreck_rec_no_does_not_block(self):
        tickets.open_ticket(
            type="science",
            title="FlyingHigh goo",
            reporter="Linus",
            payload={
                "experiment_id": "mysteryGoo",
                "situation": "FlyingHigh",
                "biome": "global",
                "bound": "yes",
                "craft": "t7-chute-pbc",
            },
        )
        wreck = {
            "landing": "catastrophic",
            "sit": "landed",
            "biome": "Shores",
            "apo_max": 917,
            "recoverable": False,
            "sci_run": 0,
            "sci_bank": 9.47,
        }
        living = {**wreck, "recoverable": True, "landing": "soft", "sit": "flying"}
        snap = tickets.bind_snapshot(craft="t7-chute-pbc")
        self.assertFalse(
            tickets.waste_blocks_refly(
                {"payload": {"landing": wreck, "waste": snap}},
                craft="t7-chute-pbc",
            )
        )
        self.assertTrue(
            tickets.waste_blocks_refly(
                {"payload": {"landing": living, "waste": snap}},
                craft="t7-chute-pbc",
            )
        )

    def test_waste_blocks_refly_flyinghigh_short_hop_cannot_pay(self):
        tickets.open_ticket(
            type="science",
            title="FlyingHigh goo",
            reporter="Linus",
            payload={
                "experiment_id": "mysteryGoo",
                "situation": "FlyingHigh",
                "biome": "global",
                "bound": "yes",
                "craft": "t7-chute-pbc",
            },
        )
        landing = {
            "landing": "catastrophic",
            "sit": "flying",
            "biome": "Shores",
            "apo_max": 2574,
            "recoverable": False,
            "sci_run": 0,
            "sci_bank": 9.47,
        }
        self.assertFalse(tickets.bind_matches_envelope(landing))
        snap = tickets.bind_snapshot(craft="t7-chute-pbc")
        fly = {"payload": {"landing": landing, "waste": snap}}
        self.assertFalse(tickets.waste_blocks_refly(fly, craft="t7-chute-pbc"))
        living = {**landing, "recoverable": True, "landing": "soft"}
        self.assertTrue(
            tickets.waste_blocks_refly(
                {"payload": {"landing": living, "waste": snap}},
                craft="t7-chute-pbc",
            )
        )
        high = {**landing, "apo_max": 60_000, "recoverable": True}
        self.assertTrue(tickets.bind_matches_envelope(high))
        self.assertFalse(
            tickets.waste_blocks_refly(
                {"payload": {"landing": high, "waste": snap}},
                craft="t7-chute-pbc",
            )
        )
        run1 = {**landing, "sci_run": 1}
        self.assertFalse(
            tickets.waste_blocks_refly(
                {"payload": {"landing": run1, "waste": snap}},
                craft="t7-chute-pbc",
            )
        )

    def test_bind_matches_envelope_flyinglow_pays_short_hop(self):
        tickets.open_ticket(
            type="science",
            title="FlyingLow Shores thermo",
            reporter="Linus",
            payload={
                "experiment_id": "temperatureScan",
                "situation": "FlyingLow@Shores",
                "biome": "Shores",
                "bound": "yes",
            },
        )
        landing = {
            "sit": "flying",
            "biome": "Shores",
            "apo_max": 2574,
            "recoverable": False,
            "sci_run": 0,
        }
        self.assertTrue(tickets.bind_matches_envelope(landing))
        self.assertFalse(
            tickets.waste_blocks_refly(
                {"payload": {"landing": landing, "waste": tickets.bind_snapshot()}},
                craft="",
            )
        )

    def test_ops_fly_gate_waste_mismatch_wait(self):
        tickets.open_ticket(
            type="science",
            title="Forest landed thermo",
            reporter="Linus",
            payload={
                "experiment_id": "temperatureScan",
                "situation": "SrfLanded@Forest",
                "biome": "Forest",
                "bound": "yes",
                "craft": "kspstuff-hop-valiant-proc-stiff-pbc",
            },
        )
        t = tickets.open_ticket(
            type="fly",
            title="hop",
            reporter="Hank",
            desk="gene",
            payload={
                "cli": "python main.py hop",
                "campaign": "uncrewed",
                "phase": "hop",
                "landing": {
                    "recoverable": True,
                    "sci_run": 0,
                    "sit": "landed",
                    "biome": "Shores",
                },
                "waste": tickets.bind_snapshot(
                    craft="kspstuff-hop-valiant-proc-stiff-pbc"
                ),
            },
        )
        tickets.patch_ticket(
            t["id"], {"go": "yes", "status": "ready"}, who="gene"
        )
        g = ops.fly_gate(
            desk={
                "hangar": "none",
                "craft": "kspstuff-hop-valiant-proc-stiff-pbc",
            },
            locked=False,
        )
        self.assertEqual(g["fly"], "wait")
        self.assertIn("sci-unchanged-recovered", g["reason"])
        self.assertFalse(tickets.needs_learn(tickets.show_ticket(t["id"])))
        g2 = ops.fly_gate(
            desk={"hangar": "none", "craft": "new-hang"},
            locked=False,
        )
        self.assertEqual(g2["fly"], "yes")


class TestReviewLearn(unittest.TestCase):
    def test_hop_learn_has_envelope_not_placeholder(self):
        import shutil
        from review import write_review

        src = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "telem"
            / "hard-splash.jsonl"
        )
        dest = Path(tempfile.mkdtemp()) / "hop-to-water.jsonl"
        shutil.copy(src, dest)
        text = write_review(
            dest,
            command="hop-to-water",
            exit_code=2,
            abort="ABORT",
            campaign="none",
        ).read_text(encoding="utf-8")
        self.assertNotIn("_Gene fills this", text)
        learn = text.split("## Learn", 1)[1]
        self.assertIn("heading", learn)
        self.assertIn("horiz max", learn)
        self.assertIn("pitch", learn)
        self.assertIn("payload.learn", learn)

    def test_ksc_learn_is_hygiene(self):
        import shutil
        from review import write_review

        src = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "telem"
            / "hard-splash.jsonl"
        )
        dest = Path(tempfile.mkdtemp()) / "ksc.jsonl"
        shutil.copy(src, dest)
        text = write_review(
            dest, command="ksc", exit_code=0, abort=None
        ).read_text(encoding="utf-8")
        self.assertNotIn("_Gene fills this", text)
        learn = text.split("## Learn", 1)[1]
        self.assertIn("hygiene ksc", learn)

    def test_uncrewed_learn_skips_gene_nag(self):
        import shutil
        from review import learn_block, write_review

        src = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "telem"
            / "hard-splash.jsonl"
        )
        dest = Path(tempfile.mkdtemp()) / "hop.jsonl"
        shutil.copy(src, dest)
        text = write_review(
            dest, command="hop", exit_code=2, abort=None, campaign="uncrewed"
        ).read_text(encoding="utf-8")
        learn = text.split("## Learn", 1)[1]
        self.assertNotIn("payload.learn", learn)
        self.assertNotIn("Stamp", learn)
        block = "\n".join(
            learn_block(
                "hop",
                0,
                None,
                {
                    "heading_first": 299,
                    "heading_last": 34,
                    "horiz_max": 5,
                    "pitch_first": 90,
                    "pitch_last": -9,
                },
                campaign="uncrewed",
            )
        )
        self.assertNotIn("Stamp payload.learn", block)
        crewed = "\n".join(
            learn_block(
                "hop",
                0,
                None,
                {"heading_first": 90, "heading_last": 90},
                campaign="none",
            )
        )
        self.assertIn("Stamp payload.learn", crewed)
