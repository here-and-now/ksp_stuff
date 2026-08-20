"""Unittest must not clobber live last-flight / sorties."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from flightlog import live_records


class TestLiveRecords(unittest.TestCase):
    def test_false_under_unittest(self):
        self.assertFalse(live_records())

    def test_env_off(self):
        old = os.environ.get("KSPSTUFF_HANDOFF")
        try:
            os.environ["KSPSTUFF_HANDOFF"] = "off"
            self.assertFalse(live_records())
        finally:
            if old is None:
                os.environ.pop("KSPSTUFF_HANDOFF", None)
            else:
                os.environ["KSPSTUFF_HANDOFF"] = old

    def test_write_handoff_does_not_touch_disk(self):
        from main import write_handoff

        path = Path("docs/last-flight.md")
        before = path.read_text(encoding="utf-8") if path.is_file() else None
        write_handoff(command="pad", exit_code=0)
        after = path.read_text(encoding="utf-8") if path.is_file() else None
        self.assertEqual(before, after)
