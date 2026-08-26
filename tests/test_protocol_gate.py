"""Fly gate and return parse — files, not chat."""

from __future__ import annotations

import unittest
from dataclasses import fields as dc_fields
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
    names = {f.name for f in dc_fields(DeskSit)}
    if "note_tech" in names:
        base.setdefault("note_tech", "")
    base.update(kwargs)
    return DeskSit(**{k: v for k, v in base.items() if k in names})


_FLYING = (
    "## Flying\n"
    "- experiment: temperatureScan\n"
    "  situation: FlyingLow\n"
)


def _fly_ticket(*, cli="python main.py hop", phase="hop", campaign="none", **extra):
    payload = {"cli": cli, "campaign": campaign, "phase": phase}
    payload.update(extra)
    return {
        "go": "yes",
        "type": "fly",
        "status": "ready",
        "payload": payload,
    }


class TestParseReturn(unittest.TestCase):
    def test_gene_missing_go(self):
        result = parse_return("phase: hop\nrecommended: python main.py hop\n", "gene")
        self.assertIn("go", result.missing)

    def test_gene_ok(self):
        text = (
            "go: yes\n"
            "cli: python main.py hop\n"
            "phase: hop\n"
            "f013: temperatureScan unlocked=yes on_craft=yes\n"
        )
        result = parse_return(text, "gene")
        self.assertEqual(result.missing, ())
        self.assertEqual(result.fields["go"], "yes")

    def test_gene_cli_does_not_require_recommended(self):
        text = (
            "go: yes\n"
            "cli: python main.py hop\n"
            "phase: hop\n"
            "f013: temperatureScan unlocked=yes on_craft=yes\n"
        )
        result = parse_return(text, "gene")
        self.assertEqual(result.missing, ())
        self.assertNotIn("recommended", result.missing)
        self.assertNotIn("lesson", result.missing)
        self.assertNotIn("ask", result.missing)

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

    def test_lars_and_katherine_drop_lesson_ask(self):
        lars = parse_return("stack: ok\nf013: none\n", "lars")
        self.assertEqual(lars.missing, ())
        self.assertNotIn("lesson", lars.missing)
        kath = parse_return("model: tape\ntickets: none\n", "katherine")
        self.assertEqual(kath.missing, ())
        self.assertNotIn("ask", kath.missing)


class TestFlyGate(unittest.TestCase):
    def setUp(self):
        self._ticket = patch("protocol.seated_fly_ticket", return_value=None)
        self._ticket.start()
        self.addCleanup(self._ticket.stop)
        self._ids = patch("tickets.science_ids_for", return_value=())
        self._ids.start()
        self.addCleanup(self._ids.stop)

    def test_missing_go_is_wait(self):
        gate = fly_gate(
            sit=_sit(),
            plan={"phase": "hop", "go": "yes"},
            science_text=_FLYING,
            ticket={"go": "", "payload": {"phase": "hop", "cli": "python main.py hop"}},
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("go", gate.reason)

    def test_capable_no_is_wait(self):
        gate = fly_gate(
            sit=_sit(capable="no"),
            plan={"go": "wait", "phase": "hop"},
            science_text=_FLYING,
            ticket=_fly_ticket(),
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("capable", gate.reason)

    def test_recover_leftover_is_wait(self):
        gate = fly_gate(
            sit=_sit(hangar="recover flea sit=FLYING"),
            plan={"go": "wait", "phase": "hop"},
            science_text=_FLYING,
            ticket=_fly_ticket(cli=""),
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("leftover", gate.reason)

    def test_leftover_n_is_wait(self):
        gate = fly_gate(
            sit=_sit(hangar="none", vessels=("kspstuff-hop-flea-pbc",)),
            plan={"go": "wait", "phase": "hop"},
            science_text=_FLYING,
            ticket=_fly_ticket(),
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("leftover", gate.reason)

    def test_occupancy_prelaunch_is_fly(self):
        gate = fly_gate(
            sit=_sit(
                hangar="occupancy kspstuff-hop-hammer-pbc",
                craft="kspstuff-hop-hammer-pbc",
                vessels=("kspstuff-hop-hammer-pbc",),
            ),
            plan={"go": "wait", "phase": "hop"},
            science_text=_FLYING,
            ticket=_fly_ticket(),
        )
        self.assertEqual(gate.fly, "yes")

    def test_empty_card_is_wait(self):
        gate = fly_gate(
            sit=_sit(card=(), f013=(F013("", "none", "none", "n/a", "no", "none"),)),
            plan={"go": "wait", "phase": "hop"},
            science_text="# no experiments\n",
            ticket=_fly_ticket(),
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
            plan={"go": "wait", "phase": "pad"},
            science_text="## Pad\n- experiment: geigerCounter\n  situation: SrfLanded\n",
            ticket=_fly_ticket(cli="python main.py pad", phase="pad"),
        )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("f013", gate.reason)

    def test_yes_when_signed_and_bound(self):
        gate = fly_gate(
            sit=_sit(),
            plan={"go": "wait", "phase": "hop"},
            science_text=_FLYING,
            ticket=_fly_ticket(),
        )
        self.assertEqual(gate.fly, "yes")
        self.assertEqual(gate.cli, "python main.py hop")
        text = format_gate(gate)
        self.assertIn("fly: yes", text)

    def _waste_ticket(self, **landing):
        env = {
            "recoverable": True,
            "sci_run": 0,
            "sit": "landed",
            "biome": "Shores",
        }
        env.update(landing)
        return {
            "go": "yes",
            "payload": {
                "cli": "python main.py hop",
                "campaign": "uncrewed",
                "phase": "hop",
                "landing": env,
            },
        }

    def test_waste_mismatch_is_wait(self):
        with patch("protocol.waste_blocks_refly", return_value=True):
            gate = fly_gate(
                sit=_sit(),
                plan={"go": "wait", "phase": "hop"},
                science_text=_FLYING,
                ticket=self._waste_ticket(),
            )
        self.assertEqual(gate.fly, "wait")
        self.assertIn("sci-unchanged-recovered", gate.reason)
        self.assertIn("cannot pay", gate.reason)
        self.assertEqual(gate.commander, "none")

    def test_waste_match_or_changed_is_yes(self):
        with patch("protocol.waste_blocks_refly", return_value=False):
            gate = fly_gate(
                sit=_sit(),
                plan={"go": "wait", "phase": "hop"},
                science_text=_FLYING,
                ticket=self._waste_ticket(sit="splashed", biome="Forest"),
            )
        self.assertEqual(gate.fly, "yes")
        self.assertEqual(gate.commander, "none")

    def test_living_sci_run_1_is_yes(self):
        gate = fly_gate(
            sit=_sit(),
            plan={"go": "wait", "phase": "hop"},
            science_text=_FLYING,
            ticket=self._waste_ticket(sci_run=1, sit="splashed", biome="Forest"),
        )
        self.assertEqual(gate.fly, "yes")

    def test_phase_leftover_cli(self):
        gate = fly_gate(
            sit=_sit(hangar="phase flea sit=PRELAUNCH", capable="no"),
            plan={"go": "wait", "phase": "hop"},
            science_text=_FLYING,
            ticket=_fly_ticket(cli="", phase="hop"),
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
        self.assertEqual(gate.commander, "none")
        self.assertEqual(gate.writer, "hop-pid")
        text = format_gate(gate)
        self.assertIn("campaign: uncrewed", text)
        self.assertIn("commander: none", text)
        self.assertIn("writer: hop-pid", text)

    def test_missing_ticket_is_wait(self):
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
        self.assertEqual(gate.fly, "wait")
        self.assertIn("ticket", gate.reason)
        self.assertEqual(gate.commander, "none")

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
