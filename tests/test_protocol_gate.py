"""Fly gate and return parse — files, not chat."""

from __future__ import annotations

import unittest
from pathlib import Path

from desk import DeskSit, F013
from protocol import FlyGate, fly_gate, format_gate, parse_return
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


class TestFlyGate(unittest.TestCase):
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
