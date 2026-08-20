"""Unittest must not clobber live last-flight / sorties."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from datetime import datetime, timezone

from flightlog import earth_stamp, format_kerbal_clock, live_records


class TestStamps(unittest.TestCase):
    def test_earth_stamp_has_seconds_not_radio_zulu(self):
        now = datetime(2026, 8, 20, 12, 35, 42, tzinfo=timezone.utc)
        stamp = earth_stamp(now)
        self.assertEqual(stamp, "2026-08-20T12-35-42Z")
        self.assertNotEqual(stamp, "2026-08-20T1235Z")
        self.assertIn("-35-42Z", stamp)

    def test_kerbal_ut_days_hms(self):
        # 1 day + 2h + 3m + 4s
        text = format_kerbal_clock(86400 + 2 * 3600 + 3 * 60 + 4)
        self.assertEqual(text, "1d 02:03:04 UT")
        met = format_kerbal_clock(740, label="MET")
        self.assertEqual(met, "MET 0d 00:12:20")


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
