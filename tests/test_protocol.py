"""PROTOCOL + Linus card schema the desks actually read."""

from __future__ import annotations

import unittest
from pathlib import Path


class TestProtocolDoc(unittest.TestCase):
    def test_matrix_headings(self):
        text = Path("docs/program/PROTOCOL.md").read_text(encoding="utf-8")
        for needle in (
            "## Handoffs",
            "## Parallel",
            "## Spawn packet",
            "duration_s",
            "ec_rate",
            "recover_banks",
            "live_sortie",
            "Verena",
            "Communications",
            "docs/press/",
        ):
            self.assertIn(needle, text)

    def test_charter_points_at_protocol(self):
        text = Path("docs/program/CHARTER.md").read_text(encoding="utf-8")
        self.assertIn("docs/program/PROTOCOL.md", text)
        self.assertIn("Os is the founder", text)


class TestLinusCardSchema(unittest.TestCase):
    def test_pad_card_has_budget_fields(self):
        text = Path("docs/missions/jebediah/science.md").read_text(encoding="utf-8")
        self.assertIn("recover_banks:", text)
        self.assertIn("duration_s:", text)
        self.assertIn("ec_rate:", text)
        self.assertIn("mysteryGoo", text)
        self.assertIn("temperatureScan", text)
        self.assertIn("GooExperiment", text)


class TestPressDesk(unittest.TestCase):
    def test_verena_files(self):
        self.assertTrue(Path("docs/crew/verena.md").is_file())
        self.assertTrue(Path(".grok/agents/verena.md").is_file())
        self.assertTrue(Path("docs/press/INDEX.md").is_file())
        self.assertTrue(Path("docs/press/pad-goo.md").is_file())

    def test_readme_portrait(self):
        text = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("docs/press/", text)
        self.assertIn("letsgrok", text)
        self.assertIn("Os", text)
        self.assertIn("Verena", text)
        self.assertIn("python main.py world", text)
