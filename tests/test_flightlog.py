"""Unittest must not clobber live last-flight / logs."""

from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from datetime import datetime, timezone

from flightlog import (
    cmd_ship,
    earth_stamp,
    envelope_from_snapshot,
    format_kerbal_clock,
    format_ship,
    live_records,
    parse_as_of,
    parse_ship,
    publish_hangar_radio,
    ship_stale,
)


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

    def test_false_under_pytest_env(self):
        if not os.environ.get("PYTEST_CURRENT_TEST"):
            self.skipTest("pytest runner")
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

    def test_close_synthesizes_landing_when_still_flying(self):
        import flightlog
        from telem import Snapshot

        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        old = (
            flightlog._path,
            flightlog._t0,
            flightlog._count,
            flightlog._last_write,
            flightlog._last_flags,
            flightlog._last_state,
            flightlog._wrote_landing,
        )
        flightlog._path = tmp
        flightlog._t0 = time.monotonic()
        flightlog._count = 0
        flightlog._last_write = 0.0
        flightlog._last_flags = None
        flightlog._last_state = None
        flightlog._wrote_landing = False
        try:
            flightlog.record(
                Snapshot(
                    situation="flying",
                    alt=52.0,
                    v_vert=-154.0,
                    speed=154.0,
                    horiz=19.0,
                    heading=299.0,
                    pitch=90.0,
                ),
                tag="flight",
                force=True,
            )
            flightlog._emit_landing_if_missing()
            flightlog.event("end", "samples=1")
        finally:
            (
                flightlog._path,
                flightlog._t0,
                flightlog._count,
                flightlog._last_write,
                flightlog._last_flags,
                flightlog._last_state,
                flightlog._wrote_landing,
            ) = old
        rows = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        kinds = [r["kind"] for r in rows]
        self.assertIn("state", kinds)
        self.assertIn("landing", kinds)
        self.assertIn("end", kinds)
        self.assertGreater(kinds.index("landing"), kinds.index("state"))
        land = next(r for r in rows if r.get("kind") == "landing")
        self.assertTrue(land.get("synthesized"))

    def test_close_synthesizes_landed_on_silk_flying(self):
        import flightlog
        from telem import Snapshot

        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        old = (
            flightlog._path,
            flightlog._t0,
            flightlog._count,
            flightlog._last_write,
            flightlog._last_flags,
            flightlog._last_state,
            flightlog._wrote_landing,
        )
        flightlog._path = tmp
        flightlog._t0 = time.monotonic()
        flightlog._count = 0
        flightlog._last_write = 0.0
        flightlog._last_flags = None
        flightlog._last_state = None
        flightlog._wrote_landing = False
        try:
            flightlog.record(
                Snapshot(
                    situation="flying",
                    alt=62.0,
                    v_vert=-5.0,
                    speed=5.0,
                    horiz=0.01,
                    heading=299.0,
                    pitch=90.0,
                    biome="Forest",
                    chute="deployed",
                    recoverable=False,
                ),
                tag="flight",
                force=True,
            )
            flightlog._emit_landing_if_missing()
        finally:
            (
                flightlog._path,
                flightlog._t0,
                flightlog._count,
                flightlog._last_write,
                flightlog._last_flags,
                flightlog._last_state,
                flightlog._wrote_landing,
            ) = old
        landing = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("kind") == "landing"
        ]
        self.assertEqual(landing[0]["sit"], "landed")
        self.assertEqual(landing[0]["landing"], "soft")


_SNAPSHOT_BLOB = (
    "Snapshot(scene='?', vessel='kspstuff-hop-flea-pbc', body='Earth', "
    "situation='flying', alt=1523.0, peri=-6362500.0, apo=11562.0, ecc=0.99, "
    "q=0.0, atm_depth=140000.0, in_atmo=True, wreck=False, throttle=1.0, "
    "thrust=0.0, speed=0.0, horiz=nan, v_vert=nan, g=nan, landing='', "
    "heading=nan, pitch=nan, aoa=nan, biome='', met=10.0, ec=0.0, fuel=5.0, "
    "lf=5.0, broken=None, stage=None, hz=20.0, "
    "resources={'ElectricCharge': 0.0, 'SolidFuel': 5.0}, flags=('ec=0',))\n"
    "as_of: 2026-08-22T23:46Z\n"
)


class TestShipEnvelope(unittest.TestCase):
    def test_parses_snapshot_blob_without_resources(self):
        env = parse_ship(_SNAPSHOT_BLOB)
        text = format_ship(env)
        self.assertIn("heading: ?", text)
        self.assertIn("wreck: no", text)
        self.assertIn("ec: 0", text)
        self.assertIn("alt: 1523", text)
        self.assertIn("as_of: 2026-08-22T23:46Z", text)
        self.assertIn("sit: flying", text)
        self.assertIn("flags: ec=0", text)
        self.assertNotIn("Snapshot(", text)
        self.assertNotIn("resources", text)
        self.assertNotIn("ElectricCharge", text)
        self.assertLess(len(text), 400)

    def test_parses_kv_envelope(self):
        env = parse_ship(
            "heading: 299\nwreck: no\nec: 12\nalt: 400\nas_of: 2026-08-23T00:01Z\n"
        )
        text = format_ship(env)
        self.assertIn("heading: 299", text)
        self.assertIn("wreck: no", text)
        self.assertIn("ec: 12", text)
        self.assertIn("alt: 400", text)

    def test_cmd_ship_from_disk(self):
        from contextlib import redirect_stdout
        from io import StringIO

        path = Path(tempfile.mkdtemp()) / "ship.md"
        path.write_text(_SNAPSHOT_BLOB, encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            rc = cmd_ship(path)
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("wreck: no", out)
        self.assertIn("alt: 1523", out)
        self.assertIn("as_of:", out)
        self.assertNotIn("Snapshot(", out)

    def test_cmd_ship_missing(self):
        from contextlib import redirect_stdout
        from io import StringIO

        buf = StringIO()
        with redirect_stdout(buf):
            rc = cmd_ship(Path(tempfile.mkdtemp()) / "missing.md")
        self.assertEqual(rc, 0)
        self.assertIn("ship: none", buf.getvalue())

    def test_publish_writes_envelope_not_repr(self):
        import flightlog
        from telem import Snapshot
        from unittest.mock import patch

        dest = Path(tempfile.mkdtemp()) / "ship.md"
        snap = Snapshot(
            vessel="kspstuff-hop-valiant-chute-stiff-pbc",
            situation="flying",
            heading=298.97,
            wreck=False,
            ec=80.0,
            alt=19197.0,
            mass=1677.0,
            parts_n=9,
            root="probeCoreOcto.v2",
            flags=("atmosphere alt=19197 peri=-1 atm=140000", "shear"),
        )
        with (
            patch.object(flightlog, "live_records", return_value=True),
            patch.object(flightlog, "SHIP", dest),
            patch.object(flightlog, "_flight", "jebediah"),
        ):
            flightlog._publish_ship(snap, "flight")
        text = dest.read_text(encoding="utf-8")
        self.assertIn("heading: 299", text)
        self.assertIn("wreck: no", text)
        self.assertIn("ec: 80", text)
        self.assertIn("alt: 19197", text)
        self.assertIn("as_of:", text)
        self.assertIn("flight: jebediah", text)
        self.assertIn("mass: 1677", text)
        self.assertIn("parts_n: 9", text)
        self.assertIn("root: probeCoreOcto.v2", text)
        self.assertIn("shear", text)
        self.assertNotIn("Snapshot(", text)

    def test_envelope_from_snapshot_keys(self):
        from telem import Snapshot

        env = envelope_from_snapshot(
            Snapshot(heading=90.0, wreck=True, ec=0.0, alt=74.0),
            as_of="2026-08-23T00:00Z",
        )
        self.assertTrue(env["wreck"])
        self.assertEqual(env["heading"], 90.0)
        text = format_ship(env)
        self.assertIn("wreck: yes", text)
        self.assertIn("heading: 90", text)

    def test_format_ship_link_no(self):
        from telem import Snapshot

        env = envelope_from_snapshot(
            Snapshot(
                heading=90.0,
                wreck=False,
                link=False,
                snr=0.0,
                via="KSC",
                alt=400.0,
            ),
            as_of="2026-08-24T00:00Z",
        )
        self.assertIs(env["link"], False)
        text = format_ship(env)
        self.assertIn("link: no", text)
        self.assertIn("via: KSC", text)
        self.assertIn("snr: 0", text)
        yes = format_ship(
            envelope_from_snapshot(
                Snapshot(link=True, wreck=False), as_of="2026-08-24T00:00Z"
            )
        )
        self.assertIn("link: yes", yes)
        none = format_ship(
            envelope_from_snapshot(
                Snapshot(link=None, wreck=False), as_of="2026-08-24T00:00Z"
            )
        )
        self.assertNotIn("link:", none)

    def test_ship_carries_where(self):
        from telem import Snapshot

        env = envelope_from_snapshot(
            Snapshot(
                heading=299.0,
                wreck=False,
                ec=80.0,
                alt=400.0,
                lat=28.608389,
                lon=-80.604333,
                downrange=0.12,
                biome="Shores",
            ),
            as_of="2026-08-23T12:00Z",
        )
        text = format_ship(env)
        self.assertIn("lat: 28.6084", text)
        self.assertIn("lon: -80.6043", text)
        self.assertIn("downrange: 0.12", text)
        self.assertIn("biome: Shores", text)

    def test_ship_stale_when_as_of_predates_lock(self):
        lock = Path(tempfile.mkdtemp()) / "flight.lock"
        lock.write_text("pid=1\ncommand=hop\n", encoding="utf-8")
        env = {"as_of": "2026-08-23T00:13Z"}
        self.assertTrue(ship_stale(env, lock_path=lock))
        env2 = {
            "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        }
        self.assertFalse(ship_stale(env2, lock_path=lock))
        self.assertFalse(ship_stale(env, lock_path=lock.parent / "missing.lock"))
        self.assertEqual(
            parse_as_of("2026-08-23T00:13Z"),
            datetime(2026, 8, 23, 0, 13, tzinfo=timezone.utc),
        )

    def test_publish_hangar_radio_is_ksc_not_last_hop(self):
        import flightlog

        dest = Path(tempfile.mkdtemp()) / "ship.md"
        with (
            patch.object(flightlog, "live_records", return_value=True),
            patch.object(flightlog, "SHIP", dest),
            patch.object(flightlog, "_flight", "jebediah"),
        ):
            publish_hangar_radio(
                vessel="kspstuff-hop-valiant-proc-tank-pbc", why="preflight"
            )
        text = dest.read_text(encoding="utf-8")
        self.assertIn("sit: ksc", text)
        self.assertIn("flags: preflight", text)
        self.assertIn("as_of:", text)
        self.assertIn("wreck: no", text)
        self.assertNotIn("sit: landed", text)
