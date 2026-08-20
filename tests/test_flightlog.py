"""Unittest must not clobber live last-flight / logs."""

from __future__ import annotations

import json
import os
import tempfile
import time
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


class TestRecordEnvelope(unittest.TestCase):
    def test_state_rows_envelope_hop(self):
        import flightlog
        from review import summarize
        from telem import Snapshot

        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        old = (
            flightlog._path,
            flightlog._t0,
            flightlog._count,
            flightlog._last_write,
            flightlog._last_flags,
        )
        flightlog._path = tmp
        flightlog._t0 = time.monotonic()
        flightlog._count = 0
        flightlog._last_write = 0.0
        flightlog._last_flags = None
        try:
            flightlog.record(
                Snapshot(
                    body="Earth",
                    situation="flying",
                    alt=2123.0,
                    peri=-6_362_500.0,
                    apo=11562.0,
                    met=7.0,
                    ec=0.0,
                    fuel=3.5,
                    lf=3.5,
                    flags=("ec=0",),
                ),
                tag="flight",
                ut=62610.0,
                force=True,
            )
            flightlog.record(
                Snapshot(
                    body="Earth",
                    situation="flying",
                    alt=400.0,
                    peri=-7_000_000.0,
                    apo=810.0,
                    met=75.0,
                    ec=0.0,
                    fuel=0.0,
                    lf=0.0,
                    flags=("ec=0",),
                ),
                tag="flight",
                ut=62678.0,
                force=True,
            )
        finally:
            (
                flightlog._path,
                flightlog._t0,
                flightlog._count,
                flightlog._last_write,
                flightlog._last_flags,
            ) = old
        rows = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        stats = summarize(rows)
        self.assertEqual(stats["samples"], 2)
        self.assertEqual(stats["alt_min"], 400.0)
        self.assertEqual(stats["apo_max"], 11562.0)
        self.assertEqual(stats["met_max"], 75.0)
        self.assertEqual(stats["ec_min"], 0.0)
        self.assertEqual(stats["fuel_min"], 0.0)
        self.assertEqual(stats["fuel_start"], 3.5)
        self.assertIn("ec=0", stats["flag_counts"])
        self.assertIn("met=7.0", stats["first"])
        self.assertIn("fuel=0.0", stats["last"])
