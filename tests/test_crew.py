"""Portrait kv stops at Log; append_log is not the voice file."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from crew import Person, _parse_kv, append_log, slug_for


class TestCrew(unittest.TestCase):
    def test_parse_kv_stops_at_log(self):
        text = (
            "duty: ceo\n"
            "energy_cap: 1.25\n"
            "## Notes\n"
            "go: wait leftover\n"
        )
        kv = _parse_kv(text)
        self.assertEqual(kv["duty"], "ceo")
        self.assertEqual(kv["energy_cap"], "1.25")
        self.assertNotIn("go", kv)

    def test_append_log_writes_crew_log_dir(self):
        with TemporaryDirectory() as tmp:
            log_dir = Path(tmp) / "log"
            person = Person(
                slug="gene",
                name="Gene Grokman",
                duty="fdo",
                kerbal=None,
                path=Path(tmp) / "gene.md",
                body="",
            )
            with patch("crew.CREW_LOG_DIR", log_dir):
                append_log(person, "Learn: leftover recover")
            dest = log_dir / "gene.md"
            self.assertTrue(dest.is_file())
            self.assertIn("leftover recover", dest.read_text(encoding="utf-8"))

    def test_katherine_slug(self):
        self.assertEqual(slug_for("Katherine Grokman"), "katherine")
        self.assertEqual(slug_for("Katherine Kerman"), "katherine")


if __name__ == "__main__":
    unittest.main()
