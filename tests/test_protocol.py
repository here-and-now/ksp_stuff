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
        self.assertTrue(
            Path("docs/archive/2026-08-23-md-cutover/program/improve/README.md").is_file()
        )
        self.assertTrue(Path("docs/archive/letsgrok-2026-08-21/improve/I-001.md").is_file())
        self.assertFalse(Path("docs/program/improve/README.md").is_file())
        for path in Path(".grok/agents").glob("*.md"):
            body = path.read_text(encoding="utf-8")
            self.assertIn("agents_md: false", body, path.name)
        mortimer = Path(".grok/agents/mortimer.md").read_text(encoding="utf-8")
        self.assertIn("tickets:", mortimer)
        self.assertNotIn("need_builder", mortimer)
        self.assertTrue(Path("docs/program/GLOSSARY.md").is_file())
        self.assertTrue(Path("docs/missions/uncrewed/logs").is_dir())
        self.assertFalse(Path("docs/missions/jebediah/sorties").is_dir())


class TestLinusCardSchema(unittest.TestCase):
    def test_pad_card_has_budget_fields(self):
        proto = Path("docs/program/PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("duration_s", proto)
        self.assertIn("ec_rate", proto)
        text = Path("docs/missions/jebediah/science.md").read_text(encoding="utf-8")
        self.assertIn("recover_banks:", text)


def _md_image_targets(path: Path) -> list[str]:
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
    out: list[str] = []
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        raw = m.group(1).strip().split()[0]
        if raw:
            out.append(raw)
    for m in re.finditer(r'<img\s[^>]*src="([^"]+)"', text, flags=re.I):
        raw = m.group(1).strip()
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
        self.assertTrue(Path("docs/crew/katherine.md").is_file())
        self.assertTrue(Path(".grok/agents/katherine.md").is_file())
        self.assertIn("katherine", Path("tickets.py").read_text(encoding="utf-8"))
        self.assertTrue(Path("docs/crew/eleanor.md").is_file())
        self.assertTrue(Path(".grok/agents/eleanor.md").is_file())
        self.assertIn("eleanor", Path("tickets.py").read_text(encoding="utf-8"))
        self.assertFalse(Path("docs/crew/otto.md").is_file())
        self.assertFalse(Path("docs/crew/iris.md").is_file())

    def test_readme_portrait(self):
        text = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("docs/press/", text)
        self.assertIn("letsgrok", text)
        self.assertIn("Os", text)
        self.assertIn("Verena", text)
        self.assertIn("Katherine", text)
        self.assertIn("python main.py world", text)
        heads = re.findall(r"^## .+", text, flags=re.M)
        self.assertTrue(heads)
        self.assertEqual(heads[-1], "## Agent checkout")
        what = text.index("## What this is")
        hist = text.index("## History (so far)")
        world = text.index("## The world")
        checkout = text.index("## Agent checkout")
        self.assertLess(what, hist)
        self.assertLess(hist, world)
        self.assertGreater(checkout, hist)
        self.assertIn("python main.py world", text[checkout:])
        self.assertIn("python main.py tech", text[checkout:])
        self.assertIn("screenshots/house-loop.png", text)
        self.assertNotIn("```mermaid", text)
        self.assertNotIn("readme-banner", text)

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
            "sci",
        ):
            self.assertIn(needle, tale)
        self.assertTrue(
            "2026-08-23T11-11-21Z-hop" in tale
            or "2026-08-23T10-47-12Z-hop" in tale
        )

    def test_index_leads_with_science_gained(self):
        index = Path("docs/press/INDEX.md").read_text(encoding="utf-8")
        self.assertIn("| Date | Story | Sci | Shot |", index)
        self.assertIn("13.26 → 16.47", index)
        self.assertIn("5.67 → 7.77", index)
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
        parked = Path("docs/archive/2026-08-23-md-cutover/program")
        index = (parked / "feedback.md").read_text(encoding="utf-8")
        for n in ("F-001", "F-002", "F-003", "F-004", "F-005"):
            self.assertIn(n, index)
            body = (parked / "feedback" / f"{n}.md").read_text(encoding="utf-8")
            self.assertRegex(body, r"status: (open|accepted|discussed|wont)")
        self.assertIn(
            "status: accepted",
            (parked / "feedback" / "F-005.md").read_text(encoding="utf-8"),
        )
        self.assertIn("ec_rate", Path("docs/missions/jebediah/science.md").read_text())
        self.assertFalse(Path("docs/program/feedback.md").is_file())

    def test_notes_per_desk(self):
        notes = Path(
            "docs/archive/2026-08-23-md-cutover/program/feedback/notes"
        )
        for slug in (
            "gene",
            "gus",
            "linus",
            "lars",
            "jebediah",
            "verena",
            "mortimer",
        ):
            self.assertTrue((notes / f"{slug}.md").is_file())
