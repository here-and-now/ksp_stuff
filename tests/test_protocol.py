"""PROTOCOL + Linus card schema the desks actually read."""

from __future__ import annotations

import re
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
            "live_run",
            "docs/missions/<id>/logs/",
            "Verena",
            "Communications",
            "docs/press/",
            "python main.py screenshot",
            "## Return (this job)",
            "feedback.md",
            "F-NNN",
            "improve:",
            "desk.md",
            "Practice",
            "protocol fly",
        ):
            self.assertIn(needle, text)
        self.assertNotIn("L-NNN", text)

    def test_charter_points_at_protocol(self):
        text = Path("docs/program/CHARTER.md").read_text(encoding="utf-8")
        self.assertIn("docs/program/PROTOCOL.md", text)
        self.assertIn("Os is the founder", text)
        self.assertIn("Recursive self-improvement", text)
        self.assertTrue(Path("docs/program/improve/README.md").is_file())
        self.assertTrue(Path("docs/archive/letsgrok-2026-08-21/improve/I-001.md").is_file())
        for path in Path(".grok/agents").glob("*.md"):
            body = path.read_text(encoding="utf-8")
            self.assertIn("agents_md: false", body, path.name)
        mortimer = Path(".grok/agents/mortimer.md").read_text(encoding="utf-8")
        self.assertIn("tickets:", mortimer)
        self.assertNotIn("need_builder", mortimer)
        self.assertTrue(Path("docs/program/GLOSSARY.md").is_file())
        self.assertTrue(Path("docs/missions/jebediah/logs").is_dir())
        self.assertFalse(Path("docs/missions/jebediah/sorties").is_dir())


class TestLinusCardSchema(unittest.TestCase):
    def test_pad_card_has_budget_fields(self):
        proto = Path("docs/program/PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("duration_s", proto)
        self.assertIn("ec_rate", proto)
        text = Path("docs/missions/jebediah/science.md").read_text(encoding="utf-8")
        self.assertIn("recover_banks:", text)


def _md_image_targets(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    out: list[str] = []
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        raw = m.group(1).strip().split()[0]
        if raw:
            out.append(raw)
    return out


class TestPressDesk(unittest.TestCase):
    def test_verena_files(self):
        self.assertTrue(Path("docs/crew/verena.md").is_file())
        self.assertTrue(Path(".grok/agents/verena.md").is_file())
        self.assertTrue(Path("docs/press/INDEX.md").is_file())
        self.assertTrue(Path("docs/press/pad-goo.md").is_file())
        self.assertTrue(Path("docs/press/forest-for-the-trees.md").is_file())

    def test_readme_portrait(self):
        text = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("docs/press/", text)
        self.assertIn("letsgrok", text)
        self.assertIn("Os", text)
        self.assertIn("Verena", text)
        self.assertIn("python main.py world", text)
        heads = re.findall(r"^## .+", text, flags=re.M)
        self.assertTrue(heads)
        self.assertEqual(heads[-1], "## Agent checkout")
        hist = text.index("## History (so far)")
        checkout = text.index("## Agent checkout")
        self.assertGreater(checkout, hist)
        self.assertIn("python main.py world", text[checkout:])
        self.assertIn("python main.py tech", text[checkout:])

    def test_press_images_resolve(self):
        files = [Path("README.md"), *sorted(Path("docs/press").glob("*.md"))]
        missing: list[str] = []
        for path in files:
            for raw in _md_image_targets(path):
                if raw.startswith("http://") or raw.startswith("https://"):
                    continue
                dest = (path.parent / raw).resolve()
                if not dest.is_file():
                    missing.append(f"{path}: {raw}")
        self.assertEqual(missing, [])

    def test_forest_tale_from_disk(self):
        tale = Path("docs/press/forest-for-the-trees.md").read_text(encoding="utf-8")
        for needle in (
            "chute",
            "shear",
            "girder",
            "Forest",
            "latitude",
            "longitude",
            "trees",
            "Ad astra",
            "sci",
        ):
            self.assertIn(needle, tale)
        self.assertTrue(
            "2026-08-23T11-11-21Z-hop" in tale
            or "2026-08-23T10-47-12Z-hop" in tale
        )
        lessons = Path("docs/lessons.md").read_text(encoding="utf-8")
        self.assertIn("latitude", lessons)
        self.assertIn("Forest is 270", lessons)

    def test_index_leads_with_science_gained(self):
        index = Path("docs/press/INDEX.md").read_text(encoding="utf-8")
        self.assertIn("13.26 sci → 16.47 sci", index)
        self.assertIn("5.67 sci → 7.77 sci", index)
        self.assertNotIn("16.47 sci → 1.47 sci", index)
        self.assertNotIn("16.47 → **1.47**", index)

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
        self.assertIn("status: accepted", Path("docs/program/feedback/F-005.md").read_text())
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

    def test_lessons_use_run_headings(self):
        text = Path("docs/lessons.md").read_text(encoding="utf-8")
        self.assertNotIn("L-NNN", text)
        self.assertIn("## ", text)
