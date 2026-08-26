"""Telemetry snapshots, body-relative gates, emergency table identity."""

from __future__ import annotations

import json
import math
import tempfile
import time
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from emergencies import CALLABLES, Ctx, abort_pad, call, cut, hold, transmit
from tape import Tape, cmd_telem, envelope, format_envelope
from telem import (
    EventLog,
    Telem,
    classify_abort,
    classify_impact,
    comms_via,
    engine_dead,
    format_landing,
    format_snapshot,
    gates,
    in_atmosphere,
    landing_from_jsonl,
    pulse_s,
    read_snapshot,
    reliability_broken,
    Snapshot,
    stack_shear,
)
import uplink

ARCHIVE_LOGS = Path("docs/archive/2026-08-26-jebediah-logs")
LIVE_UNCREWED_LOGS = Path("docs/missions/uncrewed/logs")
LEGACY_JEB_LOGS = Path("docs/missions/jebediah/logs")


def _tape_log(name: str) -> Path:
    for root in (ARCHIVE_LOGS, LIVE_UNCREWED_LOGS, LEGACY_JEB_LOGS):
        path = root / name
        if path.is_file():
            return path
    return ARCHIVE_LOGS / name


def _bind_run_jsonl(test: unittest.TestCase, path: Path) -> None:
    import flightlog

    old = (
        flightlog._path,
        flightlog._t0,
        flightlog._count,
        flightlog._last_write,
        flightlog._last_flags,
        flightlog._command,
    )
    flightlog._path = path
    flightlog._t0 = time.monotonic()
    flightlog._count = 0
    flightlog._last_write = 0.0
    flightlog._last_flags = None
    flightlog._command = "test"

    def restore() -> None:
        (
            flightlog._path,
            flightlog._t0,
            flightlog._count,
            flightlog._last_write,
            flightlog._last_flags,
            flightlog._command,
        ) = old

    test.addCleanup(restore)


class _Body:
    def __init__(self, name="Earth", depth=140_000.0, has=True):
        self.name = name
        self.atmosphere_depth = depth
        self.has_atmosphere = has
        self.reference_frame = object()


class _Flight:
    def __init__(
        self,
        alt=100.0,
        q=0.0,
        surf=80.0,
        speed=0.0,
        heading=0.0,
        horiz=None,
        v_vert=0.0,
    ):
        self.mean_altitude = alt
        self.dynamic_pressure = q
        self.surface_altitude = surf
        self.speed = speed
        self.vertical_speed = v_vert
        self.heading = heading
        self.pitch = 90.0
        self.angle_of_attack = 0.0
        self.horizontal_speed = speed if horiz is None else horiz
        self.g_force = 1.0
        self.latitude = float("nan")
        self.longitude = float("nan")


class _Orbit:
    def __init__(self, body, peri=-500_000.0, apo=100.0, ecc=0.99):
        self.body = body
        self.periapsis_altitude = peri
        self.apoapsis_altitude = apo
        self.eccentricity = ecc
        self.semi_major_axis = 6.4e6
        self.time_to_periapsis = 0.0
        self.time_to_apoapsis = 100.0


class _Control:
    def __init__(self):
        self.throttle = 0.0
        self.staged = 0
        self.current_stage = 1

    def activate_next_stage(self):
        self.staged += 1


class _Resources:
    def __init__(self, amounts):
        self._a = dict(amounts)

    def amount(self, name):
        return self._a.get(name, 0.0)


class _Vessel:
    def __init__(self, *, alt=100.0, sit="pre_launch", ec=10.0, fuel=20.0, speed=0.0, depth=140_000.0):
        self.name = "probe"
        self.situation = sit
        self.recoverable = False
        self.recovered = False
        self.control = _Control()
        self.resources = _Resources({"ElectricCharge": ec, "SolidFuel": fuel})
        self.thrust = 0.0
        self.available_thrust = 0.0
        self.mass = 1000.0
        self.met = 0.0
        self.biome = "Shores"
        self._flight = _Flight(alt=alt, speed=speed, heading=90.0, horiz=speed)
        self.orbit = _Orbit(_Body(depth=depth), peri=-500_000.0, apo=alt)
        self.parts = type("P", (), {"all": []})()

    def flight(self, ref=None):
        return self._flight

    def recover(self):
        self.recovered = True


class _Session:
    def __init__(self, vessel=None):
        self.active_vessel = vessel
        self.stream_calls = []
        self.space_center = type("SC", (), {"rails_warp_factor": 1, "physics_warp_factor": 0})()

    def add_stream(self, func, obj, name):
        self.stream_calls.append((func, obj, name))

        class _S:
            def __init__(self, f, o, n):
                self._f, self._o, self._n = f, o, n

            def __call__(self):
                return self._f(self._o, self._n)

            def remove(self):
                pass

        return _S(func, obj, name)


class TestNoVessel(unittest.TestCase):
    def test_printable(self):
        snap = read_snapshot(_Session(None), scene="space_center")
        line = format_snapshot(snap)
        self.assertIn("vessel=none", line)
        self.assertIn("scene=space_center", line)
        self.assertEqual(gates(snap), [])


class TestAtmosphereGate(unittest.TestCase):
    def test_uses_body_depth(self):
        earth = _Body("Earth", depth=140_000.0)
        self.assertTrue(in_atmosphere(100_000.0, earth))
        self.assertFalse(in_atmosphere(150_000.0, earth))
        kerbin_like = _Body("X", depth=70_000.0)
        self.assertFalse(in_atmosphere(100_000.0, kerbin_like))

    def test_flying_in_atmo_emits_gate(self):
        vessel = _Vessel(alt=80_000.0, sit="flying", depth=140_000.0, speed=200.0, fuel=10)
        vessel.orbit.periapsis_altitude = 50_000.0
        vessel.orbit.apoapsis_altitude = 200_000.0
        session = _Session(vessel)
        log = EventLog()
        with Telem(session, events=log, scene="flight") as telem:
            snap = telem.read()
        self.assertTrue(snap.in_atmo)
        self.assertTrue(any(g.startswith("atmosphere") and "atm=140000" in g for g in gates(snap)))
        self.assertTrue(any(e["event"] == "snapshot" for e in log.events))
        self.assertTrue(any(e["event"] == "gate" for e in log.events))
        self.assertTrue(session.stream_calls)
        self.assertIs(session.stream_calls[0][0], getattr)

    def test_ec_zero_flying(self):
        vessel = _Vessel(alt=200_000.0, sit="flying", ec=0.0, fuel=10, speed=100.0, depth=140_000.0)
        vessel.orbit.periapsis_altitude = 180_000.0
        vessel.orbit.apoapsis_altitude = 220_000.0
        snap = read_snapshot(_Session(vessel))
        self.assertIn("ec=0", gates(snap))

    def test_ec_zero_on_pad(self):
        vessel = _Vessel(alt=80.0, sit="pre_launch", ec=0.0, fuel=10, speed=0.0)
        snap = read_snapshot(_Session(vessel))
        self.assertIn("ec=0", gates(snap))

    def test_empty_tanks_with_speed(self):
        vessel = _Vessel(alt=200_000.0, sit="flying", fuel=0.0, speed=50.0, depth=140_000.0, ec=5)
        vessel.orbit.periapsis_altitude = 180_000.0
        vessel.orbit.apoapsis_altitude = 220_000.0
        snap = read_snapshot(_Session(vessel))
        self.assertIn("empty tanks", gates(snap))

    def test_low_flying_q0_frozen_met_is_wreck(self):
        """Crash UI: MET-still + q=0 + low flying is wreck (jsonl lie otherwise)."""
        vessel = _Vessel(alt=74.0, sit="flying", speed=0.0, fuel=0.0)
        vessel.met = 67.62
        vessel._flight.dynamic_pressure = 0.0
        with Telem(_Session(vessel)) as telem:
            first = telem.read()
            second = telem.read()
        self.assertFalse(first.wreck)
        self.assertTrue(second.wreck)
        self.assertIn("wreck", gates(second))


class TestJsonl(unittest.TestCase):
    def test_writes_snapshot(self):
        tmp = Path(tempfile.mkdtemp()) / "events.jsonl"
        log = EventLog(tmp)
        read_snapshot(_Session(None), scene="space_center", events=log)
        text = tmp.read_text(encoding="utf-8")
        rec = json.loads(text.splitlines()[0])
        self.assertEqual(rec["event"], "snapshot")
        self.assertIsNone(rec["vessel"])

    def test_telem_read_writes_seated_state_row(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        tmp.write_text("", encoding="utf-8")
        _bind_run_jsonl(self, tmp)
        vessel = _Vessel(
            alt=2123.0, sit="flying", ec=0.0, fuel=3.5, speed=429.0
        )
        vessel.met = 7.0
        vessel.orbit.apoapsis_altitude = 11562.0
        vessel.orbit.periapsis_altitude = -6_362_500.0
        session = _Session(vessel)
        session.space_center.ut = 62610.0
        with Telem(session, scene="flight") as telem:
            snap = telem.read()
            telem.read()
        self.assertEqual(snap.situation, "flying")
        self.assertAlmostEqual(snap.met, 7.0)
        rows = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        states = [row for row in rows if row.get("kind") == "state"]
        self.assertEqual(len(states), 2)
        row = states[0]
        self.assertEqual(row["situation"], "flying")
        self.assertAlmostEqual(row["alt"], 2123.0)
        self.assertAlmostEqual(row["apo"], 11562.0)
        self.assertAlmostEqual(row["peri"], -6_362_500.0)
        self.assertAlmostEqual(row["met"], 7.0)
        self.assertEqual(row["ec"], 0.0)
        self.assertEqual(row["fuel"], 3.5)
        self.assertEqual(row["lf"], 3.5)
        self.assertAlmostEqual(row["speed"], 429.0)
        self.assertAlmostEqual(row["horiz"], 429.0)
        self.assertAlmostEqual(row["heading"], 90.0)
        self.assertAlmostEqual(row["pitch"], 90.0)
        self.assertAlmostEqual(row["aoa"], 0.0)
        self.assertEqual(row["biome"], "Shores")
        self.assertIn("ec=0", row.get("flags") or [])
        self.assertEqual(row["ut"], 62610.0)

    def test_vessel_frame_speed_zero_still_logs_horiz(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        tmp.write_text("", encoding="utf-8")
        _bind_run_jsonl(self, tmp)
        vessel = _Vessel(alt=500.0, sit="flying", speed=0.0)
        vessel._flight = _Flight(alt=500.0, speed=0.0, heading=90.0, horiz=44.0)
        session = _Session(vessel)
        with Telem(session, scene="flight") as telem:
            snap = telem.read()
        self.assertAlmostEqual(snap.horiz, 44.0)
        self.assertAlmostEqual(snap.heading, 90.0)
        self.assertAlmostEqual(snap.speed, 44.0)

    def test_empty_eventlog_does_not_skip_seated_jsonl(self):
        tmp = Path(tempfile.mkdtemp()) / "pad.jsonl"
        _bind_run_jsonl(self, tmp)
        vessel = _Vessel(alt=80.0, sit="pre_launch", ec=10.0, fuel=20.0)
        vessel.met = 0.0
        with Telem(_Session(vessel), events=EventLog()) as telem:
            telem.read()
        rows = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        states = [row for row in rows if row.get("kind") == "state"]
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0]["situation"], "pre_launch")
        self.assertAlmostEqual(states[0]["alt"], 80.0)


class TestEmergencies(unittest.TestCase):
    def test_same_table_as_uplink(self):
        self.assertIs(uplink.CALLABLES, CALLABLES)
        self.assertIs(uplink.CALLABLES["cut"], cut)
        self.assertIs(uplink.CALLABLES["hold"], hold)
        for name in (
            "hold",
            "cut",
            "no_warp",
            "stage",
            "recover",
            "science",
            "transmit",
            "abort_pad",
        ):
            self.assertIn(name, CALLABLES)
            self.assertIs(uplink.CALLABLES[name], CALLABLES[name])
        self.assertIs(uplink.CALLABLES["abort_pad"], abort_pad)
        self.assertIs(uplink.CALLABLES["transmit"], transmit)

    def test_transmit_fires_kerbalism_event_not_stock_or_toggle(self):
        class _Ev:
            def __init__(self, name, gui, active=True):
                self.name = name
                self.gui_name = gui
                self.active = active
                self.n = 0

            def trigger(self):
                self.n += 1

        class _Mod:
            def __init__(self):
                self.name = "Experiment"
                self.fields = {"experiment_id": "temperatureScan"}
                self.events = ["Start Experiment", "Toggle", "Dump", "Reset", "Transmit"]
                self.event_list = [
                    _Ev("ToggleEvent", "Toggle"),
                    _Ev("Dump", "Dump"),
                    _Ev("Reset", "Reset"),
                    _Ev("TransmitEvent", "Transmit"),
                ]
                self.triggered: list[str] = []

            def trigger_event(self, name):
                self.triggered.append(name)

        class _Parts:
            def __init__(self, part):
                self.all = [part]

            @property
            def experiments(self):
                raise AssertionError("must not use vessel.parts.experiments")

        mod = _Mod()
        part = type("P", (), {"name": "sensorThermometer", "modules": [mod]})()
        vessel = _Vessel(sit="flying")
        vessel.parts = _Parts(part)
        ctx = Ctx(
            session=_Session(vessel),
            vessel=vessel,
            events=EventLog(),
            science_ids=("temperatureScan",),
        )
        self.assertEqual(call("transmit", ctx), "transmit:temperatureScan")
        self.assertEqual(mod.event_list[3].n, 1)
        self.assertEqual(mod.event_list[0].n, 0)
        self.assertEqual(mod.event_list[1].n, 0)
        self.assertEqual(mod.event_list[2].n, 0)
        self.assertEqual(mod.triggered, [])
        self.assertTrue(any(e["event"] == "transmit" for e in ctx.events.events))

    def test_transmit_does_not_toggle_when_no_tx_event(self):
        class _Mod:
            def __init__(self):
                self.name = "Experiment"
                self.fields = {"experiment_id": "mysteryGoo"}
                self.events = ["Start Experiment", "Toggle"]
                self.triggered: list[str] = []

            def trigger_event(self, name):
                self.triggered.append(name)

        class _Parts:
            def __init__(self, part):
                self.all = [part]

            @property
            def experiments(self):
                raise AssertionError("must not use vessel.parts.experiments")

        mod = _Mod()
        part = type("P", (), {"name": "GooExperiment", "modules": [mod]})()
        vessel = _Vessel(sit="flying")
        vessel.parts = _Parts(part)
        ctx = Ctx(session=_Session(vessel), vessel=vessel, events=EventLog())
        self.assertEqual(call("transmit", ctx), "transmit")
        self.assertEqual(mod.triggered, [])

    def test_cut_and_hold(self):
        vessel = _Vessel()
        vessel.control.throttle = 1.0
        ctx = Ctx(session=_Session(vessel), vessel=vessel, events=EventLog())
        self.assertEqual(call("cut", ctx), "cut")
        self.assertEqual(vessel.control.throttle, 0.0)

        # Flying, peri > 0: hold matches freeze — cut throttle.
        vessel.control.throttle = 1.0
        vessel.orbit.body.has_atmosphere = True
        vessel.orbit.body.atmosphere_depth = 140_000.0
        vessel._flight.mean_altitude = 100_000.0
        vessel.orbit.periapsis_altitude = 80_000.0
        call("hold", ctx)
        self.assertEqual(vessel.control.throttle, 0.0)

        # In-atmo pad (peri underground, alt 80 m) is not lithobrake — cut.
        vessel.control.throttle = 1.0
        vessel._flight.mean_altitude = 80.0
        vessel.orbit.periapsis_altitude = -500_000.0
        call("hold", ctx)
        self.assertEqual(vessel.control.throttle, 0.0)

        # True lithobrake: airless, peri < 0, alt < 30 km — keep throttle 1.
        vessel.control.throttle = 1.0
        vessel.orbit.body.has_atmosphere = False
        vessel._flight.mean_altitude = 5_000.0
        vessel.orbit.periapsis_altitude = -1_000.0
        call("hold", ctx)
        self.assertEqual(vessel.control.throttle, 1.0)
        self.assertIn("lithobrake", ctx.notes)
        self.assertTrue(any(e["event"] == "call" for e in ctx.events.events))


class TestLandingTape(unittest.TestCase):
    def test_classify_impact_thresholds(self):
        self.assertEqual(classify_impact(5.0), "soft")
        self.assertEqual(classify_impact(20.0), "firm")
        self.assertEqual(classify_impact(60.0), "hard")
        self.assertEqual(classify_impact(233.0), "catastrophic")
        self.assertEqual(classify_impact(float("nan")), "")

    def test_pulse_s_bursts_near_surface(self):
        cruise = pulse_s(Snapshot(situation="flying", alt=40_000.0, v_vert=-50.0))
        near = pulse_s(Snapshot(situation="flying", alt=400.0, v_vert=-200.0))
        chute = pulse_s(Snapshot(situation="flying", alt=5_000.0, v_vert=-110.0))
        burn = pulse_s(
            Snapshot(situation="flying", alt=12_000.0, v_vert=400.0, throttle=1.0)
        )
        coast = pulse_s(
            Snapshot(situation="flying", alt=12_000.0, v_vert=50.0, throttle=0.0)
        )
        self.assertLess(near, cruise)
        self.assertAlmostEqual(near, 0.05)
        self.assertAlmostEqual(cruise, 0.2)
        self.assertAlmostEqual(chute, 0.05)
        self.assertAlmostEqual(burn, 0.05)
        self.assertAlmostEqual(coast, 0.2)

    def test_streams_vertical_speed(self):
        vessel = _Vessel(alt=400.0, sit="flying", speed=200.0)
        vessel._flight.vertical_speed = -180.0
        session = _Session(vessel)
        with Telem(session) as telem:
            snap = telem.read()
        self.assertAlmostEqual(snap.v_vert, -180.0)
        names = [c[2] for c in session.stream_calls]
        self.assertIn("vertical_speed", names)
        self.assertIn("latitude", names)
        self.assertIn("longitude", names)
        self.assertFalse(math.isfinite(snap.lat))
        self.assertFalse(math.isfinite(snap.downrange))

    def test_sit_change_emits_landing_event(self):
        vessel = _Vessel(alt=200.0, sit="flying", speed=233.0)
        vessel._flight.vertical_speed = -220.0
        vessel._flight.horizontal_speed = 40.0
        events = EventLog()
        with Telem(_Session(vessel), events=events) as telem:
            air = telem.read()
            vessel.situation = "splashed"
            vessel._flight.mean_altitude = -2.0
            down = telem.read()
        self.assertEqual(air.landing, "")
        self.assertEqual(down.landing, "catastrophic")
        hits = [e for e in events.events if e.get("event") == "landing"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["landing"], "catastrophic")

    def test_landing_from_hard_splash_fixture(self):
        path = Path(__file__).resolve().parent / "fixtures" / "telem" / "hard-splash.jsonl"
        row = landing_from_jsonl(path)
        self.assertEqual(row["landing"], "catastrophic")
        self.assertGreater(row["impact_ms"], 100.0)
        self.assertEqual(row["sit"], "splashed")
        line = format_landing(row)
        self.assertIn("catastrophic", line)
        self.assertIn("impact=", line)
        self.assertIn("horiz=", line)
        self.assertIn("pitch=", line)
        self.assertNotIn("horiz=?", line)
        self.assertNotIn("pitch=?", line)
        self.assertNotIn(".jsonl", line.split("impact")[0])
        self.assertIsNotNone(row.get("horiz"))
        self.assertIsNotNone(row.get("pitch"))
        block = format_envelope(row)
        self.assertIn("landing: catastrophic", block)
        self.assertIn("eyes:", block)
        self.assertNotIn("kind=state", block)
        self.assertNotIn('"kind": "state"', block)

    def test_read_records_actual_hz(self):
        vessel = _Vessel(alt=40_000.0, sit="flying", speed=200.0)
        clock = {"t": 1000.0}

        def monotonic() -> float:
            return clock["t"]

        with patch("telem.time.monotonic", monotonic):
            with Telem(_Session(vessel)) as telem:
                first = telem.read()
                clock["t"] += 0.2
                cruise = telem.read()
                clock["t"] += 0.05
                near = telem.read()
        self.assertFalse(math.isfinite(first.hz))
        self.assertAlmostEqual(cruise.hz, 5.0)
        self.assertAlmostEqual(near.hz, 20.0)

    def test_readonly_read_does_not_write_jsonl(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        tmp.write_text("", encoding="utf-8")
        _bind_run_jsonl(self, tmp)
        vessel = _Vessel(alt=400.0, sit="flying", speed=200.0)
        session = _Session(vessel)
        session.readonly = True
        with Telem(session, scene="flight") as telem:
            telem.read()
        self.assertEqual(tmp.read_text(encoding="utf-8").strip(), "")
        dest = Path(tempfile.mkdtemp()) / "ship.md"
        import flightlog

        with (
            patch.object(flightlog, "live_records", return_value=True),
            patch.object(flightlog, "SHIP", dest),
        ):
            with Telem(session, scene="flight") as telem:
                telem.read()
        self.assertFalse(dest.is_file())


class TestTapeEyes(unittest.TestCase):
    hops = (
        _tape_log("2026-08-22T23-01-19Z-hop.jsonl"),
        _tape_log("2026-08-22T23-14-23Z-hop.jsonl"),
    )

    def test_hop_envelopes_without_state_rows(self):
        got = []
        for path in self.hops:
            if not path.is_file():
                self.skipTest(f"missing {path}")
            env = envelope(path)
            text = format_envelope(env)
            self.assertNotIn("kind=state", text)
            self.assertGreater(env["samples"], 10)
            self.assertGreater(env["apo_max"], 10_000)
            self.assertAlmostEqual(env["pad"]["heading"], 299, delta=2)
            self.assertIn(env["landing"], {"hard", "catastrophic", "firm", "soft"})
            self.assertLessEqual(len(text), 900)
            self.assertIn("tape:", text)
            self.assertIn("q=", text)
            self.assertIn("ec=", text)
            self.assertIn("events:", text)
            self.assertIn("descent:", text)
            got.append(env)
        self.assertEqual(got[0]["landing"], "catastrophic")
        self.assertGreater(got[0]["impact_ms"], 100)
        self.assertEqual(got[1]["landing"], "hard")
        self.assertGreater(got[1]["impact_ms"], 50)
        self.assertLess(got[1]["impact_ms"], 100)

    def test_windows_are_capped(self):
        path = self.hops[0]
        if not path.is_file():
            self.skipTest(f"missing {path}")
        tape = Tape(path)
        impact = tape.window("impact", max_rows=12)
        self.assertLessEqual(impact["n"], 12)
        self.assertTrue(impact["rows"])
        self.assertNotIn("resources", impact["rows"][0])
        self.assertIn("q", impact["rows"][0])
        self.assertIn("ec", impact["rows"][0])
        pad = tape.window("pad")
        self.assertEqual(pad["n"], 1)
        self.assertEqual(pad["rows"][0]["situation"], "pre_launch")
        apex = tape.window("apex")
        self.assertEqual(apex["n"], 1)
        self.assertGreater(apex["rows"][0]["apo"], 10_000)
        descent = tape.window("descent")
        self.assertGreaterEqual(descent["n"], 1)
        burn = tape.window("burnout")
        self.assertEqual(burn["window"], "burnout")
        air = tape.window("airborne")
        self.assertGreaterEqual(air["n"], 1)
        self.assertEqual(air["rows"][0]["situation"], "flying")
        kinds = tape.events("landing")
        self.assertEqual(len(kinds), 1)
        self.assertEqual(kinds[0]["kind"], "landing")

    def test_thin_tape_surfaces_q_ec_stage(self):
        path = _tape_log("2026-08-22T23-54-24Z-hop.jsonl")
        if not path.is_file():
            self.skipTest(f"missing {path}")
        env = envelope(path)
        text = format_envelope(env)
        self.assertIn("tape:", text)
        self.assertIn("q=", text)
        self.assertNotIn("q=?", text)
        self.assertIn("ec=", text)
        self.assertIn("stage=", text)
        self.assertIn("events: start,end", text)
        air = Tape(path).window("airborne")
        self.assertIn("q", air["rows"][0])
        self.assertGreater(air["rows"][0]["q"], 0)

    def test_wreck_emits_landing_kind(self):
        vessel = _Vessel(alt=74.0, sit="flying", speed=154.0)
        vessel.met = 67.62
        vessel._flight.dynamic_pressure = 0.0
        vessel._flight.vertical_speed = -154.0
        events = EventLog()
        with Telem(_Session(vessel), events=events) as telem:
            first = telem.read()
            second = telem.read()
        self.assertFalse(first.wreck)
        self.assertTrue(second.wreck)
        self.assertTrue(second.landing)
        hits = [e for e in events.events if e.get("event") == "landing"]
        self.assertEqual(len(hits), 1)

    def test_recoverable_edge_emits(self):
        vessel = _Vessel(alt=80.0, sit="landed", speed=0.0)
        vessel.recoverable = False
        events = EventLog()
        with Telem(_Session(vessel), events=events) as telem:
            telem.read()
            vessel.recoverable = True
            snap = telem.read()
        self.assertTrue(snap.recoverable)
        hits = [e for e in events.events if e.get("event") == "recoverable"]
        self.assertEqual(len(hits), 1)
        self.assertTrue(hits[0].get("recoverable"))

    def test_g_force_stream(self):
        vessel = _Vessel(alt=400.0, sit="flying", speed=200.0)
        vessel._flight.g_force = 3.2
        snap = read_snapshot(_Session(vessel))
        self.assertAlmostEqual(snap.g, 3.2)
        self.assertEqual(snap.chute, "none")
        self.assertFalse(snap.sci_run)
        self.assertIsNone(snap.sci_bank)

    def test_sci_bank_from_handoff_event(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "situation": "pre_launch",
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
                "alt": 84.0,
                "apo": 84.0,
                "sci_bank": 1.4718,
            },
            {
                "kind": "state",
                "t": 10.0,
                "situation": "flying",
                "heading": 299.0,
                "horiz": 5.0,
                "pitch": 80.0,
                "alt": 400.0,
                "apo": 12000.0,
                "sci_bank": 1.4718,
            },
            {"kind": "sci_bank", "t": 12.0, "sci": 5.6718, "msg": "sci=5.6718"},
            {"kind": "end", "t": 13.0},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        text = format_envelope(env)
        self.assertAlmostEqual(env["sci_bank"], 5.6718)
        self.assertIn("bank=5.67", text)

    def test_silk_recover_envelope_sit_landed(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
                "alt": 84.0,
                "recoverable": True,
                "chute": "stowed",
            },
            {
                "kind": "state",
                "t": 400.0,
                "met": 380.0,
                "situation": "flying",
                "heading": 299.0,
                "horiz": 0.01,
                "pitch": 90.0,
                "alt": 62.0,
                "v_vert": -5.0,
                "recoverable": False,
                "chute": "deployed",
                "biome": "Forest",
                "wreck": False,
            },
            {
                "kind": "landing",
                "t": 401.0,
                "met": 380.0,
                "landing": "soft",
                "sit": "flying",
                "impact_ms": 5.0,
                "biome": "Forest",
            },
            {"kind": "end", "t": 401.1},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        self.assertEqual(env["sit"], "landed")
        self.assertTrue(env["recoverable"])
        self.assertEqual(env["landing"], "soft")
        self.assertEqual(env["last"]["sit"], "flying")
        self.assertTrue(env["sit_mismatch"])
        self.assertTrue(env["landing_synthesized"])
        text = format_envelope(env)
        self.assertIn("sit=landed", text)
        self.assertIn("rec=yes", text)
        self.assertIn("synth", text)
        self.assertIn("recover=landed", text)

    def test_synthesized_landing_and_sci_idle(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
                "alt": 84.0,
                "q": 0.0,
                "recoverable": True,
                "sci_run": False,
                "sci_rem": 0.0,
                "sci_bank": 2.2905,
            },
            {
                "kind": "state",
                "t": 240.0,
                "met": 482.0,
                "situation": "flying",
                "heading": 297.0,
                "horiz": 87.0,
                "pitch": 65.0,
                "alt": 55125.0,
                "v_vert": -1790.0,
                "q": 937.0,
                "recoverable": False,
                "sci_run": True,
                "sci_rem": 0.0,
                "sci_bank": 2.2905,
            },
            {
                "kind": "state",
                "t": 248.0,
                "met": 525.0,
                "situation": "flying",
                "heading": 298.0,
                "horiz": 98.0,
                "pitch": 65.0,
                "alt": 6054.0,
                "v_vert": -214.0,
                "speed": 235.0,
                "q": 17510.0,
                "recoverable": False,
                "sci_run": True,
                "sci_rem": 0.0,
                "sci_bank": 2.2905,
            },
            {
                "kind": "landing",
                "t": 249.0,
                "met": 525.0,
                "landing": "catastrophic",
                "sit": "flying",
                "impact_ms": 214.0,
                "synthesized": True,
            },
            {"kind": "end", "t": 249.1},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        self.assertEqual(env["last"]["sit"], "flying")
        self.assertGreater(env["last"]["alt"], 5000)
        self.assertGreater(env["last"]["q"], 10_000)
        self.assertFalse(env["last"]["recoverable"])
        self.assertEqual(env["sit"], "flying")
        self.assertFalse(env["sit_mismatch"])
        self.assertTrue(env["landing_synthesized"])
        self.assertFalse(env["sci_paid"])
        self.assertAlmostEqual(env["sci_delta"], 0.0)
        self.assertAlmostEqual(env["sci_rem"], 0.0)
        self.assertTrue(env["thick_air_skip"])
        self.assertGreaterEqual(env["skip_n"], 1)
        skip = env["skips"][0]
        self.assertTrue(skip["thick"])
        self.assertGreater(skip["alt_a"], 18_000)
        self.assertLess(skip["alt_b"], 18_000)
        text = format_envelope(env)
        self.assertIn("synth", text)
        self.assertIn("skip:", text)
        self.assertIn("thick", text)
        self.assertIn("+0", text)
        self.assertIn("sit=flying", text)
        self.assertIn("rec=no", text)
        self.assertIn("landing: catastrophic", format_landing(env))
        self.assertIn("synth", format_landing(env))

    def test_vacuum_coast_4x_is_not_thick_skip(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "alt": 84.0,
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
            },
            {
                "kind": "state",
                "t": 100.0,
                "met": 200.0,
                "situation": "sub_orbital",
                "alt": 210_000.0,
                "q": 0.0,
                "heading": 297.0,
                "horiz": 70.0,
                "pitch": 65.0,
            },
            {
                "kind": "state",
                "t": 108.0,
                "met": 232.0,
                "situation": "sub_orbital",
                "alt": 200_000.0,
                "q": 0.0,
                "heading": 297.0,
                "horiz": 70.0,
                "pitch": 65.0,
            },
            {"kind": "end", "t": 109.0},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        self.assertFalse(env["thick_air_skip"])
        self.assertEqual(env["skip_n"], 0)
        self.assertNotIn("skip:", format_envelope(env))

    def test_window_accepts_comma_names(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 0.0,
                "met": 0.0,
                "situation": "pre_launch",
                "alt": 84.0,
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
            },
            {
                "kind": "state",
                "t": 10.0,
                "met": 10.0,
                "situation": "flying",
                "alt": 400.0,
                "heading": 299.0,
                "horiz": 1.0,
                "pitch": 80.0,
            },
            {"kind": "end", "t": 11.0},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        tape = Tape(tmp)
        pad = tape.window("pad")
        air = tape.window("airborne")
        self.assertEqual(pad["window"], "pad")
        self.assertEqual(air["window"], "airborne")
        buf = StringIO()
        with patch("sys.stdout", buf):
            rc = cmd_telem([str(tmp), "--window", "pad,airborne"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(len(payload["windows"]), 2)
        self.assertEqual(payload["windows"][0]["window"], "pad")
        self.assertEqual(payload["windows"][1]["window"], "airborne")

    def test_0901_tape_eyes_not_last_flight(self):
        path = _tape_log("2026-08-25T09-01-24Z-hop.jsonl")
        if not path.is_file():
            self.skipTest(f"missing {path}")
        env = envelope(path)
        last = env["last"]
        self.assertEqual(last["sit"], "flying")
        self.assertGreater(last["alt"], 5000)
        self.assertGreater(last["q"], 10_000)
        self.assertFalse(last["recoverable"])
        self.assertTrue(env["landing_synthesized"])
        self.assertFalse(env["sci_paid"])
        self.assertAlmostEqual(env["sci_rem"] or 0.0, 0.0)
        self.assertTrue(env["thick_air_skip"])
        text = format_envelope(env)
        self.assertIn("synth", text)
        self.assertIn("skip:", text)
        self.assertIn("thick", text)
        self.assertIn("+0", text)
        self.assertLessEqual(len(text), 1100)

    def test_hz_median_prefers_met(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {"kind": "state", "t": 0.0, "met": 0.0, "situation": "flying", "alt": 100.0},
            {"kind": "state", "t": 10.0, "met": 1.0, "situation": "flying", "alt": 200.0},
            {"kind": "state", "t": 20.0, "met": 2.0, "situation": "flying", "alt": 300.0},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        self.assertAlmostEqual(env["hz_median"], 1.0)

    def test_kind_recover_sit_wins_over_last_snap(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "alt": 84.0,
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
                "recoverable": True,
            },
            {
                "kind": "state",
                "t": 240.0,
                "met": 525.0,
                "situation": "flying",
                "heading": 298.0,
                "horiz": 98.0,
                "pitch": 65.0,
                "alt": 6054.0,
                "v_vert": -214.0,
                "q": 17510.0,
                "recoverable": False,
            },
            {
                "kind": "recover",
                "t": 248.0,
                "met": 540.0,
                "sit": "splashed",
                "situation": "splashed",
                "rec": "yes",
                "recoverable": True,
                "biome": "Water",
            },
            {
                "kind": "landing",
                "t": 249.0,
                "met": 525.0,
                "landing": "catastrophic",
                "sit": "flying",
                "synthesized": True,
            },
            {"kind": "end", "t": 249.1},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        self.assertEqual(env["last"]["sit"], "flying")
        self.assertFalse(env["last"]["recoverable"])
        self.assertEqual(env["sit"], "splashed")
        self.assertTrue(env["recoverable"])
        self.assertTrue(env["sit_mismatch"])
        text = format_envelope(env)
        self.assertIn("recover=splashed", text)
        self.assertIn("rec=no", text)


class _Field:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class _DupGuiModule:
    """kRPC Module.fields / get_field throw on duplicate PAW gui names."""

    name = "ModuleReactionWheel"

    def __init__(self, *, broken=False):
        self.field_list = [_Field("broken", broken)]

    @property
    def fields(self):
        raise ValueError("Key: Reaction Wheels")

    def get_field(self, key):
        raise ValueError("Key: Reaction Wheels")


class TestDescentTape(unittest.TestCase):
    def test_apex_is_peak_alt_not_max_apo(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "alt": 85.0,
                "apo": 85.0,
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
            },
            {
                "kind": "state",
                "t": 40.0,
                "met": 39.6,
                "situation": "flying",
                "alt": 10874.0,
                "apo": 21520.0,
                "v_vert": 453.0,
                "heading": 297.0,
                "horiz": 29.0,
                "pitch": 88.0,
            },
            {
                "kind": "state",
                "t": 100.0,
                "met": 65.6,
                "situation": "flying",
                "alt": 14086.0,
                "apo": 21520.0,
                "v_vert": -36.0,
                "heading": 297.0,
                "horiz": 29.0,
                "pitch": 80.0,
            },
            {
                "kind": "state",
                "t": 211.0,
                "met": 182.6,
                "situation": "flying",
                "alt": 412.0,
                "apo": 829.0,
                "v_vert": -91.0,
                "heading": 260.0,
                "horiz": 10.0,
                "pitch": -3.0,
            },
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        tape = Tape(tmp)
        env = tape.envelope()
        self.assertAlmostEqual(env["alt_max"], 14086.0)
        self.assertAlmostEqual(env["apex"]["alt"], 14086.0)
        self.assertGreaterEqual(env["descent_n"], 2)
        apex = tape.window("apex")
        self.assertAlmostEqual(apex["rows"][0]["alt"], 14086.0)
        descent = tape.window("descent")
        alts = [r["alt"] for r in descent["rows"]]
        self.assertEqual(alts[0], 14086.0)
        self.assertEqual(alts[-1], 412.0)
        impact = tape.window("impact")
        self.assertGreaterEqual(impact["n"], 1)
        text = format_envelope(env)
        self.assertIn("descent:", text)
        self.assertIn("14086", text)
        self.assertIn("412", text)
        self.assertLessEqual(len(text), 900)

    def test_0721_envelope_shows_descent_ladder(self):
        path = _tape_log("2026-08-23T07-21-05Z-hop.jsonl")
        if not path.is_file():
            self.skipTest(f"missing {path}")
        env = envelope(path)
        self.assertGreater(env["alt_max"], 13_000)
        self.assertLess(env["apex"]["alt"], 15_000)
        self.assertGreater(env["apex"]["alt"], 12_000)
        self.assertGreaterEqual(env["descent_n"], 8)
        descent = Tape(path).window("descent")
        alts = [r["alt"] for r in descent["rows"] if r.get("alt") is not None]
        self.assertGreater(alts[0], 10_000)
        self.assertLess(alts[-1], 500)
        text = format_envelope(env)
        self.assertIn("descent:", text)
        self.assertNotIn("kind=state", text)

    def test_0928_envelope_shows_burnout_attitude(self):
        """Apex is peak alt; slew flash is the burn row (Jeb 209/3)."""
        path = _tape_log("2026-08-23T09-28-59Z-hop.jsonl")
        if not path.is_file():
            self.skipTest(f"missing {path}")
        env = envelope(path)
        burn = env.get("burnout") or {}
        self.assertAlmostEqual(burn.get("heading") or 0.0, 209.0, delta=2)
        self.assertAlmostEqual(burn.get("pitch") or 90.0, 3.0, delta=2)
        self.assertGreaterEqual(env.get("burnout_n") or 0, 3)
        text = format_envelope(env)
        self.assertIn("burn:", text)
        self.assertIn("heading=209", text)
        self.assertIn("pitch=3", text)
        self.assertNotIn("kind=state", text)
        self.assertLessEqual(len(text), 900)
        rows = Tape(path).window("burnout")["rows"]
        pitches = [r.get("pitch") for r in rows if r.get("pitch") is not None]
        self.assertTrue(pitches)
        self.assertLess(min(abs(p) for p in pitches), 10.0)

    def test_burnout_picks_min_pitch_not_apex(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "heading": 299.0,
                "pitch": 90.0,
                "horiz": 0.0,
                "alt": 85.0,
                "throttle": 0.0,
                "fuel": 675.0,
            },
            {
                "kind": "state",
                "t": 20.0,
                "met": 1.1,
                "situation": "flying",
                "heading": 299.0,
                "pitch": 90.0,
                "horiz": 0.1,
                "alt": 95.0,
                "throttle": 1.0,
                "fuel": 650.0,
                "v_vert": 22.0,
            },
            {
                "kind": "state",
                "t": 80.0,
                "met": 49.1,
                "situation": "flying",
                "heading": 209.0,
                "pitch": 3.0,
                "horiz": 22.0,
                "alt": 13094.0,
                "throttle": 1.0,
                "fuel": 0.0,
                "v_vert": 10.0,
            },
            {
                "kind": "state",
                "t": 92.0,
                "met": 63.5,
                "situation": "flying",
                "heading": 297.0,
                "pitch": 86.0,
                "horiz": 23.0,
                "alt": 13806.0,
                "throttle": 0.0,
                "fuel": 0.0,
                "v_vert": -23.0,
            },
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        self.assertAlmostEqual(env["apex"]["alt"], 13806.0)
        self.assertAlmostEqual(env["burnout"]["heading"], 209.0)
        self.assertAlmostEqual(env["burnout"]["pitch"], 3.0)
        self.assertIn("burn:", format_envelope(env))

    def test_burnout_skips_cutoff_dump(self):
        """16-47-21Z: cutoff 15/16 is throttle=0; powered hold is 297/65."""
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "heading": 299.0,
                "pitch": 90.0,
                "horiz": 0.0,
                "alt": 85.0,
                "throttle": 0.0,
                "fuel": 1080.0,
            },
            {
                "kind": "state",
                "t": 60.0,
                "met": 24.8,
                "situation": "flying",
                "heading": 297.0,
                "pitch": 65.0,
                "horiz": 97.0,
                "alt": 3955.0,
                "throttle": 1.0,
                "fuel": 657.0,
                "v_vert": 270.0,
            },
            {
                "kind": "state",
                "t": 94.0,
                "met": 58.4,
                "situation": "flying",
                "heading": 297.0,
                "pitch": 65.0,
                "horiz": 282.0,
                "alt": 15624.0,
                "throttle": 1.0,
                "fuel": 83.0,
                "v_vert": 512.0,
            },
            {
                "kind": "state",
                "t": 113.0,
                "met": 74.0,
                "situation": "flying",
                "heading": 15.0,
                "pitch": 16.0,
                "horiz": 167.0,
                "alt": 22538.0,
                "throttle": 0.0,
                "fuel": 0.1,
                "v_vert": 240.0,
            },
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        burn = env.get("burnout") or {}
        self.assertAlmostEqual(burn.get("heading"), 297.0)
        self.assertAlmostEqual(burn.get("pitch"), 65.0)
        self.assertGreater(burn.get("throttle") or 0.0, 0.05)
        burn_line = next(
            line for line in format_envelope(env).splitlines() if line.startswith("burn:")
        )
        self.assertIn("heading=297", burn_line)
        self.assertIn("pitch=65", burn_line)
        self.assertNotIn("heading=15", burn_line)
        rows_w = Tape(tmp).window("burnout")["rows"]
        self.assertTrue(rows_w)
        self.assertTrue(all((r.get("throttle") or 0) > 0.05 for r in rows_w))

    def test_1647_envelope_burn_is_powered_hold(self):
        """Live 16-47-21Z tape: hold 297/65, not cutoff 15/16."""
        path = _tape_log("2026-08-23T16-47-21Z-hop.jsonl")
        if not path.is_file():
            self.skipTest(f"missing {path}")
        env = envelope(path)
        burn = env.get("burnout") or {}
        self.assertAlmostEqual(burn.get("heading") or 0.0, 297.0, delta=3)
        self.assertAlmostEqual(burn.get("pitch") or 0.0, 65.0, delta=3)
        self.assertGreater(burn.get("throttle") or 0.0, 0.05)
        text = format_envelope(env)
        burn_line = next(line for line in text.splitlines() if line.startswith("burn:"))
        self.assertIn("heading=297", burn_line)
        self.assertNotIn("heading=15", burn_line)
        self.assertLessEqual(len(text), 900)
        rows = Tape(path).window("burnout")["rows"]
        self.assertTrue(rows)
        self.assertTrue(all((r.get("throttle") or 0) > 0.05 for r in rows))

    def test_expensive_read_skips_slow_part_walks(self):
        class _Part:
            def __init__(self):
                self.name = "okto"
                self.mod_hits = 0

            @property
            def modules(self):
                self.mod_hits += 1
                return []

        part = _Part()
        vessel = _Vessel(alt=12_000.0, sit="flying", speed=200.0)
        vessel.parts = type("P", (), {"all": [part], "parachutes": [], "root": part})()
        session = _Session(vessel)
        with Telem(session) as telem:
            telem.read()
            hits = part.mod_hits
            self.assertGreater(hits, 0)
            telem._last_read_s = 5.0
            telem._slow_at = time.monotonic() - 10.0
            telem.read()
            self.assertEqual(part.mod_hits, hits)
            # Cheap pulse after an expensive walk must not re-arm (16-47-21Z).
            telem._last_read_s = 0.1
            telem._slow_at = time.monotonic() - 10.0
            telem._slow_cost_s = 5.0
            telem.read()
            self.assertEqual(part.mod_hits, hits)

    def test_fast_path_skips_parts_all(self):
        class _Parts:
            def __init__(self, part):
                self._part = part
                self.hits = 0
                self.parachutes = []
                self.root = part

            @property
            def all(self):
                self.hits += 1
                return [self._part]

        part = type("Part", (), {"name": "okto", "modules": []})()
        parts = _Parts(part)
        vessel = _Vessel(alt=12_000.0, sit="flying", speed=200.0)
        vessel.parts = parts
        with Telem(_Session(vessel)) as telem:
            telem.read()
            n = parts.hits
            self.assertGreater(n, 0)
            telem._last_read_s = 0.1
            telem._slow_at = time.monotonic() - 10.0
            telem._slow_cost_s = 5.0
            telem.read()
            self.assertEqual(parts.hits, n)

    def test_bind_same_vessel_id_keeps_streams(self):
        a = _Vessel(alt=400.0, sit="flying", speed=20.0)
        a.id = "guid-1"
        session = _Session(a)
        with Telem(session) as telem:
            telem.read()
            n = len(session.stream_calls)
            b = _Vessel(alt=500.0, sit="flying", speed=20.0)
            b.id = "guid-1"
            b._flight = a._flight
            b.orbit = a.orbit
            session.active_vessel = b
            telem.read()
            self.assertEqual(len(session.stream_calls), n)


class TestReliabilityFields(unittest.TestCase):
    def test_okto_duplicate_gui_does_not_raise(self):
        wheel = _DupGuiModule()
        part = type("Part", (), {"name": "probeCoreOcto_v2", "modules": [wheel]})()
        vessel = _Vessel(sit="pre_launch")
        vessel.parts = type("P", (), {"all": [part]})()
        self.assertIsNone(reliability_broken(vessel))
        snap = read_snapshot(_Session(vessel))
        self.assertIsNone(snap.broken)

    def test_broken_via_field_list_when_fields_boom(self):
        wheel = _DupGuiModule(broken=True)
        part = type("Part", (), {"name": "probeCoreOcto_v2", "modules": [wheel]})()
        vessel = _Vessel(sit="pre_launch")
        vessel.parts = type("P", (), {"all": [part]})()
        self.assertEqual(
            reliability_broken(vessel),
            "probeCoreOcto_v2:ModuleReactionWheel:broken",
        )

    def test_broken_via_fields_dict(self):
        mod = type(
            "Mod",
            (),
            {"name": "Experiment", "fields": {"broken": True}},
        )()
        part = type("Part", (), {"name": "GooExperiment", "modules": [mod]})()
        vessel = _Vessel(sit="pre_launch")
        vessel.parts = type("P", (), {"all": [part]})()
        self.assertEqual(
            reliability_broken(vessel),
            "GooExperiment:Experiment:broken",
        )


class TestStackShear(unittest.TestCase):
    def test_mass_drop_not_fuel(self):
        prev = {"mass": 1677.0, "fuel": 356.0, "stage": 1, "parts_n": 9}
        cur = {"mass": 270.0, "fuel": 123.0, "stage": 1, "parts_n": 3}
        self.assertTrue(stack_shear(prev, cur))

    def test_staging_is_not_shear(self):
        prev = {"mass": 2825.0, "fuel": 720.0, "stage": 2, "parts_n": 11}
        cur = {"mass": 2489.0, "fuel": 700.0, "stage": 1, "parts_n": 9}
        self.assertFalse(stack_shear(prev, cur))

    def test_burn_is_not_shear(self):
        prev = {"mass": 1804.0, "fuel": 406.0, "stage": 1, "parts_n": 9}
        cur = {"mass": 1283.0, "fuel": 178.0, "stage": 1, "parts_n": 9}
        self.assertFalse(stack_shear(prev, cur))

    def test_parts_drop_is_shear(self):
        prev = {"mass": 1800.0, "fuel": 400.0, "stage": 1, "parts_n": 9}
        cur = {"mass": 1700.0, "fuel": 380.0, "stage": 1, "parts_n": 3}
        self.assertTrue(stack_shear(prev, cur))

    def test_live_read_flags_shear(self):
        vessel = _Vessel(alt=4000.0, sit="flying", speed=200.0, fuel=400.0)
        vessel.mass = 1677.0
        vessel.control.current_stage = 1
        core = type("Part", (), {"name": "probeCoreOcto.v2", "modules": []})()
        tank = type("Part", (), {"name": "proceduralTank", "modules": []})()
        vessel.parts = type("P", (), {"all": [core, tank], "root": core})()
        events = EventLog()
        with Telem(_Session(vessel), events=events) as telem:
            first = telem.read()
            vessel.mass = 270.0
            vessel.parts = type("P", (), {"all": [core], "root": core})()
            second = telem.read()
        self.assertFalse(first.shear)
        self.assertEqual(first.parts_n, 2)
        self.assertTrue(second.shear)
        self.assertIn("shear", second.flags)
        self.assertEqual(second.parts_n, 1)
        self.assertEqual(second.root, "probeCoreOcto.v2")
        self.assertIsNone(second.broken)
        hits = [e for e in events.events if e.get("event") == "shear"]
        self.assertEqual(len(hits), 1)

    def test_envelope_surfaces_shear_on_known_hop(self):
        path = _tape_log("2026-08-23T06-53-50Z-hop.jsonl")
        if not path.is_file():
            self.skipTest(f"missing {path}")
        env = envelope(path)
        text = format_envelope(env)
        self.assertTrue(env["shear"])
        self.assertIn("shear", env["events"])
        self.assertIn("stack:", text)
        self.assertIn("shear=yes", text)
        self.assertIn("mass=", text)
        self.assertIn("broken=none", text)


class TestEngineDead(unittest.TestCase):
    def test_throttle_on_no_plume_fuel_left_is_dead(self):
        cur = {
            "situation": "flying",
            "throttle": 1.0,
            "thrust": 0.0,
            "fuel": 2038.0,
            "parts_n": 30,
        }
        self.assertTrue(engine_dead(cur))
        self.assertIn(
            "engine-dead",
            gates(
                Snapshot(
                    situation="flying",
                    throttle=1.0,
                    thrust=0.0,
                    fuel=2038.0,
                    parts_n=30,
                    engine_dead=True,
                )
            ),
        )

    def test_pad_and_coast_and_empty_are_not_dead(self):
        self.assertFalse(
            engine_dead(
                {
                    "situation": "pre_launch",
                    "throttle": 1.0,
                    "thrust": 0.0,
                    "fuel": 2000.0,
                    "parts_n": 30,
                }
            )
        )
        self.assertFalse(
            engine_dead(
                {
                    "situation": "flying",
                    "throttle": 0.0,
                    "thrust": 0.0,
                    "fuel": 2000.0,
                    "parts_n": 30,
                }
            )
        )
        self.assertFalse(
            engine_dead(
                {
                    "situation": "flying",
                    "throttle": 1.0,
                    "thrust": 0.0,
                    "fuel": 0.0,
                    "parts_n": 30,
                }
            )
        )
        self.assertFalse(
            engine_dead(
                {
                    "situation": "flying",
                    "throttle": 1.0,
                    "thrust": 89000.0,
                    "fuel": 2000.0,
                    "parts_n": 30,
                }
            )
        )

    def test_parts_drop_this_pulse_is_not_dead(self):
        prev = {
            "situation": "flying",
            "throttle": 1.0,
            "thrust": 0.0,
            "fuel": 2038.0,
            "parts_n": 30,
        }
        cur = {
            "situation": "flying",
            "throttle": 1.0,
            "thrust": 0.0,
            "fuel": 2038.0,
            "parts_n": 9,
        }
        self.assertTrue(engine_dead(prev))
        self.assertFalse(engine_dead(cur, prev))

    def test_classify_abort_prefers_dead_over_shear(self):
        states = [
            {
                "kind": "state",
                "situation": "flying",
                "throttle": 1.0,
                "thrust": 0.0,
                "fuel": 2038.0,
                "parts_n": 30,
            },
            {
                "kind": "state",
                "situation": "flying",
                "throttle": 1.0,
                "thrust": 0.0,
                "fuel": 2038.0,
                "parts_n": 9,
                "shear": True,
            },
        ]
        self.assertEqual(classify_abort("shear", states), "engine-dead")
        self.assertEqual(classify_abort("not recoverable", states), "engine-dead")
        self.assertEqual(
            classify_abort("OFFPLAN thrust 0 with fuel left", states),
            "engine-dead",
        )
        self.assertEqual(classify_abort("timeout", states), "timeout")

    def test_classify_abort_keeps_shear_when_still_thrusting(self):
        states = [
            {
                "kind": "state",
                "situation": "flying",
                "throttle": 1.0,
                "thrust": 89000.0,
                "fuel": 400.0,
                "parts_n": 30,
            },
            {
                "kind": "state",
                "situation": "flying",
                "throttle": 1.0,
                "thrust": 80000.0,
                "fuel": 380.0,
                "parts_n": 9,
                "shear": True,
            },
        ]
        self.assertEqual(classify_abort("shear", states), "shear")

    def test_live_read_flags_engine_dead_before_shear(self):
        vessel = _Vessel(alt=900.0, sit="flying", speed=80.0, fuel=2038.0)
        vessel.control.throttle = 1.0
        vessel.thrust = 0.0
        vessel.available_thrust = 0.0
        vessel.mass = 6160.0
        core = type("Part", (), {"name": "probeCoreSphere.v2", "modules": []})()
        tank = type("Part", (), {"name": "proceduralTank", "modules": []})()
        vessel.parts = type("P", (), {"all": [core, tank], "root": core})()
        events = EventLog()
        with Telem(_Session(vessel), events=events) as telem:
            first = telem.read()
            vessel.mass = 400.0
            vessel.parts = type("P", (), {"all": [core], "root": core})()
            second = telem.read()
        self.assertTrue(first.engine_dead)
        self.assertIn("engine-dead", first.flags)
        self.assertEqual(first.parts_n, 2)
        self.assertFalse(first.shear)
        self.assertTrue(second.engine_dead)
        self.assertTrue(second.shear)
        hits = [e for e in events.events if e.get("event") == "engine-dead"]
        self.assertEqual(len(hits), 1)

    def test_160534_tape_names_engine_dead_not_shear(self):
        path = _tape_log("2026-08-26T16-05-34Z-hop.jsonl")
        if not path.is_file():
            self.skipTest(f"missing {path}")
        env = envelope(path)
        text = format_envelope(env)
        self.assertTrue(env["engine_dead"])
        self.assertFalse(env["shear"])
        self.assertIn("engine-dead", env["events"])
        self.assertIn("engine-dead=yes", text)
        self.assertIn("shear=no", text)
        self.assertEqual(classify_abort("shear", path), "engine-dead")
        self.assertEqual(classify_abort("not recoverable", env), "engine-dead")
        tape = Tape(path)
        air = tape.window("airborne")
        thrusts = [r.get("thrust") for r in air["rows"] if "thrust" in r]
        self.assertTrue(thrusts)
        self.assertTrue(any(t == 0 or t == 0.0 for t in thrusts))


class TestWhere(unittest.TestCase):
    def test_downrange_km_cape_north(self):
        from sites import CAPE, downrange_km

        n = downrange_km(CAPE.latitude + 0.01, CAPE.longitude, CAPE.latitude, CAPE.longitude)
        self.assertGreater(n, 1.0)
        self.assertLess(n, 1.3)
        self.assertAlmostEqual(
            downrange_km(CAPE.latitude, CAPE.longitude, CAPE.latitude, CAPE.longitude),
            0.0,
            places=6,
        )

    def test_read_lat_lon_downrange_on_pad(self):
        from sites import CAPE

        vessel = _Vessel(alt=80.0, sit="pre_launch", speed=0.0)
        vessel.biome = "Shores"
        vessel._flight.latitude = CAPE.latitude
        vessel._flight.longitude = CAPE.longitude
        session = _Session(vessel)
        with Telem(session) as telem:
            telem._pad_ll = (CAPE.latitude, CAPE.longitude)
            snap = telem.read()
        self.assertAlmostEqual(snap.lat, CAPE.latitude, places=5)
        self.assertAlmostEqual(snap.lon, CAPE.longitude, places=5)
        self.assertAlmostEqual(snap.downrange, 0.0, places=2)
        self.assertEqual(snap.biome, "Shores")

    def test_envelope_where_line(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "heading": 299.0,
                "pitch": 90.0,
                "horiz": 0.0,
                "alt": 85.0,
                "biome": "Shores",
                "lat": 28.6084,
                "lon": -80.6043,
                "downrange": 0.0,
            },
            {
                "kind": "state",
                "t": 40.0,
                "met": 80.0,
                "situation": "flying",
                "heading": 270.0,
                "pitch": 65.0,
                "horiz": 80.0,
                "alt": 7000.0,
                "apo": 9000.0,
                "biome": "Forest",
                "lat": 28.70,
                "lon": -80.70,
                "downrange": 12.4,
            },
            {
                "kind": "state",
                "t": 90.0,
                "met": 140.0,
                "situation": "landed",
                "heading": 270.0,
                "pitch": 5.0,
                "horiz": 0.0,
                "alt": 12.0,
                "biome": "Forest",
                "lat": 28.71,
                "lon": -80.71,
                "downrange": 13.6,
            },
            {"kind": "landing", "landing": "soft", "sit": "landed", "biome": "Forest"},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        text = format_envelope(env)
        self.assertAlmostEqual(env["lat"], 28.71, places=3)
        self.assertAlmostEqual(env["lon"], -80.71, places=3)
        self.assertAlmostEqual(env["downrange"], 13.6, places=2)
        self.assertEqual(env["biome"], "Forest")
        self.assertIn("Forest", env["biomes"])
        self.assertIn("Shores", env["biomes"])
        self.assertIn("where:", text)
        self.assertIn("lat=28.7100", text)
        self.assertIn("lon=-80.7100", text)
        self.assertIn("down=13.60 km", text)
        self.assertIn("biome=Shores,Forest", text)


class _CommNode:
    def __init__(self, name, home=False):
        self.name = name
        self.is_home = home


class _CommLink:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class _Comms:
    def __init__(self, *, can=True, snr=1.0, home="KSC"):
        self.can_communicate = can
        self.signal_strength = snr
        end = _CommNode(home, True) if home else _CommNode("", False)
        self.control_path = [_CommLink(_CommNode("probe", False), end)]


class TestCommsLink(unittest.TestCase):
    def test_gates_deaf_only_when_link_false(self):
        self.assertIn("deaf", gates(Snapshot(link=False, vessel="probe")))
        self.assertNotIn("deaf", gates(Snapshot(link=None, vessel="probe")))
        self.assertNotIn("deaf", gates(Snapshot(link=True, vessel="probe")))
        line = format_snapshot(Snapshot(vessel="probe", body="Earth", link=False))
        self.assertIn("link=no", line)
        rated = format_snapshot(
            Snapshot(vessel="probe", body="Earth", link=True, rate_bps=64.0)
        )
        self.assertIn("link=yes", rated)
        self.assertIn("rate=64", rated)

    def test_missing_comms_link_none_no_deaf(self):
        vessel = _Vessel(alt=80.0, sit="pre_launch")
        session = _Session(vessel)
        snap = read_snapshot(session)
        self.assertIsNone(snap.link)
        self.assertNotIn("deaf", gates(snap))
        self.assertFalse(math.isfinite(snap.snr))
        self.assertEqual(snap.via, "")
        names = [c[2] for c in session.stream_calls]
        self.assertNotIn("can_communicate", names)

    def test_streams_can_communicate_and_via_home(self):
        vessel = _Vessel(alt=80.0, sit="pre_launch")
        vessel.comms = _Comms(can=True, snr=0.9, home="KSC")
        session = _Session(vessel)
        with Telem(session) as telem:
            snap = telem.read()
        self.assertIs(snap.link, True)
        self.assertAlmostEqual(snap.snr, 0.9)
        self.assertEqual(snap.via, "KSC")
        self.assertNotIn("deaf", snap.flags)
        names = [c[2] for c in session.stream_calls]
        self.assertIn("can_communicate", names)
        self.assertIn("signal_strength", names)
        self.assertEqual(comms_via(vessel), "KSC")

    def test_link_false_flags_deaf(self):
        vessel = _Vessel(
            alt=200_000.0, sit="flying", fuel=10.0, speed=50.0, ec=5, depth=140_000.0
        )
        vessel.orbit.periapsis_altitude = 180_000.0
        vessel.orbit.apoapsis_altitude = 220_000.0
        vessel.comms = _Comms(can=False, snr=0.0, home="")
        snap = read_snapshot(_Session(vessel))
        self.assertIs(snap.link, False)
        self.assertIn("deaf", gates(snap))
        self.assertIn("deaf", snap.flags)
        self.assertIn("link=no", format_snapshot(snap))

    def test_comms_property_throw_fail_open(self):
        class _Boom(_Vessel):
            @property
            def comms(self):
                raise RuntimeError("no comms")

        snap = read_snapshot(_Session(_Boom(alt=80.0, sit="pre_launch")))
        self.assertIsNone(snap.link)
        self.assertNotIn("deaf", gates(snap))

    def test_comms_streams_throw_fail_open(self):
        class _BoomComms:
            @property
            def can_communicate(self):
                raise RuntimeError("boom")

            @property
            def signal_strength(self):
                raise RuntimeError("boom")

            @property
            def control_path(self):
                raise RuntimeError("boom")

        vessel = _Vessel(alt=80.0, sit="pre_launch")
        vessel.comms = _BoomComms()
        snap = read_snapshot(_Session(vessel))
        self.assertIsNone(snap.link)
        self.assertNotIn("deaf", gates(snap))
        self.assertEqual(snap.via, "")

    def test_via_not_on_fast_path(self):
        class _HitComms:
            def __init__(self):
                self.can_communicate = True
                self.signal_strength = 1.0
                self.hits = 0

            @property
            def control_path(self):
                self.hits += 1
                return [_CommLink(_CommNode("probe"), _CommNode("KSC", True))]

        comms = _HitComms()
        vessel = _Vessel(alt=12_000.0, sit="flying", speed=200.0)
        vessel.comms = comms
        with Telem(_Session(vessel)) as telem:
            first = telem.read()
            n = comms.hits
            self.assertGreater(n, 0)
            self.assertEqual(first.via, "KSC")
            telem._last_read_s = 0.1
            telem._slow_at = time.monotonic() - 10.0
            telem._slow_cost_s = 5.0
            second = telem.read()
            self.assertEqual(comms.hits, n)
            self.assertEqual(second.via, "KSC")
            self.assertIs(second.link, True)

    def test_jsonl_includes_link_via(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        tmp.write_text("", encoding="utf-8")
        _bind_run_jsonl(self, tmp)
        vessel = _Vessel(alt=80.0, sit="pre_launch")
        vessel.comms = _Comms(can=True, snr=0.5, home="KSC")
        with Telem(_Session(vessel), scene="flight") as telem:
            telem.read()
        rows = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        states = [row for row in rows if row.get("kind") == "state"]
        self.assertEqual(len(states), 1)
        self.assertTrue(states[0]["link"])
        self.assertEqual(states[0]["via"], "KSC")
        self.assertAlmostEqual(states[0]["snr"], 0.5)

    def test_envelope_link_via_on_where(self):
        tmp = Path(tempfile.mkdtemp()) / "hop.jsonl"
        rows = [
            {
                "kind": "state",
                "t": 1.0,
                "met": 0.0,
                "situation": "pre_launch",
                "heading": 299.0,
                "horiz": 0.0,
                "pitch": 90.0,
                "alt": 84.0,
                "link": True,
                "via": "KSC",
            },
            {
                "kind": "state",
                "t": 10.0,
                "met": 8.0,
                "situation": "flying",
                "heading": 299.0,
                "horiz": 5.0,
                "pitch": 80.0,
                "alt": 400.0,
                "link": False,
                "via": "KSC",
            },
            {"kind": "end", "t": 11.0},
        ]
        tmp.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        env = envelope(tmp)
        text = format_envelope(env)
        self.assertIs(env["link"], False)
        self.assertEqual(env["via"], "KSC")
        self.assertIn("link=no", text)
        self.assertIn("via=KSC", text)
        self.assertIn("where:", text)
