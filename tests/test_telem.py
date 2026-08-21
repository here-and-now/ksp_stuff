"""Telemetry snapshots, body-relative gates, emergency table identity."""

from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from emergencies import CALLABLES, Ctx, abort_pad, call, cut, hold
from telem import EventLog, Telem, format_snapshot, gates, in_atmosphere, read_snapshot
import uplink


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


class _Flight:
    def __init__(self, alt=100.0, q=0.0, surf=80.0, speed=0.0):
        self.mean_altitude = alt
        self.dynamic_pressure = q
        self.surface_altitude = surf
        self.speed = speed
        self.vertical_speed = 0.0


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
        self.met = 0.0
        self._flight = _Flight(alt=alt, speed=speed)
        self.orbit = _Orbit(_Body(depth=depth), peri=-500_000.0, apo=alt)
        self.parts = type("P", (), {"all": []})()

    def flight(self):
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
        self.assertIn("ec=0", row.get("flags") or [])
        self.assertEqual(row["ut"], 62610.0)

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
            "abort_pad",
        ):
            self.assertIn(name, CALLABLES)
            self.assertIs(uplink.CALLABLES[name], CALLABLES[name])
        self.assertIs(uplink.CALLABLES["abort_pad"], abort_pad)

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
