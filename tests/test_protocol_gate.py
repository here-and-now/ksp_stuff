"""Fly gate and return parse — files, not chat."""

from __future__ import annotations

import unittest
from pathlib import Path

from desk import DeskSit, F013
from unittest.mock import patch

from protocol import FlyGate, _bound_ids, fly_gate, format_gate, parse_return
from phases import NAMES


def _sit(**kwargs) -> DeskSit:
    base = dict(
        lock="free",
        hangar="none",
        active_vessel="none",
        seat="jebediah",
        sci=2.4,
        sci_delta="2.4000",
        unlocked="start",
        capable="yes",
        craft="kspstuff-hop-hammer-pbc",
        card=("temperatureScan",),
        last_command="hop",
        last_exit="0",
        last_abort="",
        review="none",
        note_tech="",
        f013=(
            F013(
                eid="temperatureScan",
                instrument="sensorThermometer",
                tech="start",
                unlocked="yes",
                on_craft="yes",
                host="none",
            ),
        ),
        stack=("sensorThermometer",),
        vessels=(),
        leftover_science=(),
        stack_dump="",
        mods=("FAR",),
    )
    base.update(kwargs)
    return DeskSit(**base)


_FLYING = (
    "## Flying\n"
    "- experiment: temperatureScan\n"
    "  situation: FlyingLow\n"
)


class TestParseReturn(unittest.TestCase):
    def test_gene_missing_go(self):
        result = parse_return("phase: hop\nrecommended: python main.py hop\n", "gene")
        self.assertIn("go", result.missing)

    def test_gene_ok(self):
        text = (
            "go: yes\n"
            "recommended: python main.py hop\n"
            "phase: hop\n"
            "f013: temperatureScan unlocked=yes on_craft=yes\n"
        )
        result = parse_return(text, "gene")
        self.assertEqual(result.missing, ())
        self.assertEqual(result.fields["go"], "yes")

    def test_gene_cli_aliases_recommended(self):
        text = (
            "go: yes\n"
            "cli: python main.py hop\n"
            "phase: hop\n"
            "f013: temperatureScan unlocked=yes on_craft=yes\n"
        )
        result = parse_return(text, "gene")
        self.assertEqual(result.missing, ())
        self.assertEqual(result.fields["recommended"], "python main.py hop")

    def test_gene_without_need_keys_ok(self):
        text = (
            "go: wait\n"
            "cli: none\n"
            "phase: hop\n"
            "f013: none\n"
        )
        result = parse_return(text, "gene")
        self.assertEqual(result.missing, ())
        self.assertNotIn("need_stack", result.fields)

    def test_linus_without_card_ok(self):
        result = parse_return(
            "science: tickets\nf013: temperatureScan start yes yes\n",
            "linus",
        )
        self.assertEqual(result.missing, ())

    def test_linus_missing_science_or_f013(self):
        self.assertIn("science", parse_return("f013: x\n", "linus").missing)
        self.assertIn("f013", parse_return("science: tickets\n", "linus").missing)


class TestFlyGate(unittest.TestCase):
    def setUp(self):
        self._ticket = patch("protocol.seated_fly_ticket", return_value=None)
        self._ticket.start()
        self.addCleanup(self._ticket.stop)
        self._ids = patch("tickets.science_ids_for", return_value=())
        self._ids.start()
        self.addCleanup(self._ids.stop)

    def test_missing_go_is_wait(self):
        gate = fly_gate(sit=_sit(), plan={"phase": "hop"}, science_text=_FLYING)
        self.assertEqual(gate.fly, "wait")
        self.assertIn("go", gate.reason)

    def test_capable_no_is_wait(self):
        gate = fly_gate(
            sit=_sit(capable="no"),
            plan={"go": "yes", "phase": "hop", "recommended": "python main.py hop"},
            science_text=_FLYING,
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("capable", gate.reason)

    def test_recover_leftover_is_wait(self):
        gate = fly_gate(
            sit=_sit(hangar="recover flea sit=FLYING"),
            plan={"go": "yes", "phase": "hop"},
            science_text=_FLYING,
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("leftover", gate.reason)

    def test_leftover_n_is_wait(self):
        gate = fly_gate(
            sit=_sit(hangar="none", vessels=("kspstuff-hop-flea-pbc",)),
            plan={"go": "yes", "phase": "hop", "recommended": "python main.py hop"},
            science_text=_FLYING,
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("leftover", gate.reason)

    def test_empty_card_is_wait(self):
        gate = fly_gate(
            sit=_sit(card=(), f013=(F013("", "none", "none", "n/a", "no", "none"),)),
            plan={"go": "yes", "phase": "hop", "recommended": "python main.py hop"},
            science_text="# no experiments\n",
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("card", gate.reason)

    def test_locked_instrument_is_wait(self):
        row = F013(
            eid="geigerCounter",
            instrument="kerbalism-geigercounter",
            tech="survivability",
            unlocked="no",
            on_craft="no",
            host="none",
        )
        gate = fly_gate(
            sit=_sit(f013=(row,), card=("geigerCounter",)),
            plan={"go": "yes", "phase": "pad", "recommended": "python main.py pad"},
            science_text="## Pad\n- experiment: geigerCounter\n  situation: SrfLanded\n",
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("f013", gate.reason)

    def test_yes_when_signed_and_bound(self):
        gate = fly_gate(
            sit=_sit(),
            plan={
                "go": "yes",
                "phase": "hop",
                "recommended": "python main.py hop",
            },
            science_text=_FLYING,
        )
        self.assertEqual(gate.fly, "yes")
        self.assertEqual(gate.cli, "python main.py hop")
        text = format_gate(gate)
        self.assertIn("fly: yes", text)

    def test_phase_leftover_cli(self):
        gate = fly_gate(
            sit=_sit(hangar="phase flea sit=PRELAUNCH", capable="no"),
            plan={"go": "yes", "phase": "hop"},
            science_text=_FLYING,
        )
        self.assertEqual(gate.fly, "yes")
        self.assertEqual(gate.cli, "python main.py phase hop")

    def test_ticket_wins_over_plan(self):
        ticket = {
            "go": "yes",
            "type": "fly",
            "status": "ready",
            "payload": {
                "cli": "python main.py hop",
                "campaign": "uncrewed",
                "phase": "hop",
            },
        }
        gate = fly_gate(
            sit=_sit(),
            plan={
                "go": "wait",
                "phase": "pad",
                "recommended": "python main.py pad",
            },
            science_text=_FLYING,
            ticket=ticket,
        )
        self.assertEqual(gate.fly, "yes")
        self.assertEqual(gate.cli, "python main.py hop")
        self.assertEqual(gate.campaign, "uncrewed")
        text = format_gate(gate)
        self.assertIn("campaign: uncrewed", text)

    def test_no_ticket_falls_back_to_plan(self):
        gate = fly_gate(
            sit=_sit(),
            plan={
                "go": "yes",
                "phase": "hop",
                "recommended": "python main.py hop",
                "campaign": "none",
            },
            science_text=_FLYING,
            ticket=None,
        )
        self.assertEqual(gate.fly, "yes")
        self.assertEqual(gate.cli, "python main.py hop")

    def test_ticket_science_ids_skip_card(self):
        ticket = {
            "go": "yes",
            "payload": {
                "cli": "python main.py hop",
                "phase": "hop",
                "science_ids": ("temperatureScan",),
            },
        }
        gate = fly_gate(
            sit=_sit(),
            plan={"go": "wait", "recommended": "python main.py pad"},
            science_text="# no experiments\n",
            ticket=ticket,
        )
        self.assertEqual(gate.fly, "yes")

    def test_fly_science_ids_union_bound(self):
        ticket = {
            "go": "yes",
            "payload": {
                "cli": "python main.py hop",
                "phase": "hop",
                "science_ids": ("temperatureScan",),
            },
        }
        with patch(
            "tickets.science_ids_for",
            return_value=("kerbalism_TELEMETRY", "mysteryGoo"),
        ):
            ids = _bound_ids(ticket, _sit(), "hop", "# no experiments\n")
        self.assertEqual(
            ids,
            ("kerbalism_TELEMETRY", "mysteryGoo", "temperatureScan"),
        )

    def test_names_match_blocks(self):
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        for name in NAMES:
            self.assertIn(f"| {name} ", blocks)
        # table rows that are phases
        rows = []
        for line in blocks.splitlines():
            if line.startswith("| ") and not line.startswith("| Phase"):
                col = line.split("|")[1].strip()
                if col and col != "---":
                    rows.append(col)
        self.assertEqual(tuple(rows), NAMES)
