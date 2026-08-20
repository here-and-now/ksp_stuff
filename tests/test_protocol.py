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
            "python main.py screenshot",
            "need_retro",
            "feedback.md",
            "F-NNN",
        ):
            self.assertIn(needle, text)
        self.assertNotIn("L-NNN", text)

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

    def test_goo_shot_preserved(self):
        from screenshot import PRESERVE, resolve_dest

        self.assertIn("first-mystery-goo.png", PRESERVE)
        goo = Path("screenshots/first-mystery-goo.png")
        self.assertTrue(goo.is_file())
        with self.assertRaises(Exception):
            resolve_dest(name="first-mystery-goo")


class TestFeedbackBoard(unittest.TestCase):
    def test_index_and_items(self):
        index = Path("docs/program/feedback.md").read_text(encoding="utf-8")
        for n in ("F-001", "F-002", "F-003", "F-004", "F-005"):
            self.assertIn(n, index)
            body = Path(f"docs/program/feedback/{n}.md").read_text(encoding="utf-8")
            self.assertRegex(body, r"status: (open|accepted|discussed|wont)")
        self.assertIn("status: open", Path("docs/program/feedback/F-005.md").read_text())
        self.assertIn("ec_rate", Path("docs/missions/jebediah/science.md").read_text())

    def test_notes_per_desk(self):
        for slug in (
            "gene",
            "gus",
            "linus",
            "lars",
            "jebediah",
            "verena",
            "mortimer",
        ):
            self.assertTrue(Path(f"docs/program/feedback/notes/{slug}.md").is_file())

    def test_lessons_use_sortie_headings(self):
        text = Path("docs/lessons.md").read_text(encoding="utf-8")
        self.assertNotIn("L-NNN", text)
        self.assertIn("## 1101Z —", text)
        self.assertIn("## 1204Z —", text)
