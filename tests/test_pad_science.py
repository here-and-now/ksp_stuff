"""Kerbalism science via part.modules; recover vs honest abort."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from catalog import Catalog, ExperimentCfg, merge_experiment_cfg
from pad import recover_or_abort, run_on_vessel
from science import (
    PAD_EC_MARGIN,
    card_complete,
    card_has_data,
    experiment_done,
    hd_has_data,
    pad_dwell_s,
    pad_ec_rate,
    start_experiments,
)
from telem import EventLog, MissionAbort


def _fast_clock():
    t = [0.0]

    def now():
        return t[0]

    def sleep(dt):
        t[0] += dt if dt else 0.01

    return now, sleep


class _Mod:
    def __init__(self, name, eid, events=None, broken=False, done=False, running=False):
        self.name = name
        self.fields = {"experiment_id": eid, "broken": broken}
        if running:
            self.fields["status"] = "Running"
        if done:
            self.fields["Has Data"] = True
            self.fields["status"] = "Done"
        self.events = list(events or ["Start Experiment"])
        self.triggered: list[str] = []

    def trigger_event(self, name):
        self.triggered.append(name)

    def get_field(self, key):
        return self.fields[key]


class _Part:
    def __init__(self, name, modules):
        self.name = name
        self.modules = modules


class _Parts:
    def __init__(self, parts):
        self.all = parts

    @property
    def experiments(self):
        raise AssertionError("must not use vessel.parts.experiments")


class _Control:
    throttle = 0.0
    staged = 0

    def activate_next_stage(self):
        self.staged += 1


class _Body:
    name = "Earth"
    has_atmosphere = True
    atmosphere_depth = 140_000.0


class _Res:
    def __init__(self, ec=10.0, fuel=5.0):
        self.ec = float(ec)
        self.fuel = float(fuel)

    def amount(self, n):
        return {"ElectricCharge": self.ec, "SolidFuel": self.fuel}.get(n, 0.0)


class _Vessel:
    def __init__(self, modules, *, recoverable=True, sit="pre_launch", ec=10.0):
        self.name = "probe"
        self.situation = sit
        self.recoverable = recoverable
        self.recovered = False
        self.control = _Control()
        self.resources = _Res(ec=ec)
        self.thrust = 0.0
        self.parts = _Parts([_Part("GooExperiment", modules)])
        self.orbit = type(
            "O",
            (),
            {
                "body": _Body(),
                "periapsis_altitude": -500_000.0,
                "apoapsis_altitude": 80.0,
                "eccentricity": 0.99,
                "semi_major_axis": 6.4e6,
                "time_to_periapsis": 0.0,
                "time_to_apoapsis": 1.0,
            },
        )()
        self._alt = 80.0

    def flight(self):
        return type(
            "F",
            (),
            {
                "mean_altitude": self._alt,
                "dynamic_pressure": 0.0,
                "surface_altitude": 80.0,
                "speed": 0.0,
            },
        )()

    def recover(self):
        if not self.recoverable:
            raise RuntimeError("not recoverable")
        self.recovered = True


class _Session:
    def __init__(self, vessel):
        self.active_vessel = vessel
        self.space_center = type("SC", (), {"rails_warp_factor": 0, "physics_warp_factor": 0})()

    def add_stream(self, func, obj, name):
        class _S:
            def __call__(self_inner):
                return func(obj, name)

            def remove(self_inner):
                pass

        return _S()


class _Field:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.gui_name = name


class _BoomFields:
    def __init__(self, name, eid, events=None, broken=False):
        self.name = name
        self.events = list(events or ["Start Experiment"])
        self.triggered: list[str] = []
        self._eid = eid
        self._broken = broken

    @property
    def fields(self):
        raise RuntimeError("duplicate field names")

    def trigger_event(self, name):
        self.triggered.append(name)

    def get_field(self, key):
        raise RuntimeError("no gui field")


class TestKerbalismStart(unittest.TestCase):
    def test_starts_without_stock_run(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("mysteryGoo",))
        self.assertEqual(ran, ["mysteryGoo"])
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_skips_broken(self):
        mod = _Mod("Experiment", "mysteryGoo", broken=True)
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("mysteryGoo",))
        self.assertEqual(ran, [])
        self.assertEqual(mod.triggered, [])

    def test_leftover_stock_module(self):
        mod = _Mod("ModuleScienceExperiment", "temperatureScan")
        mod.fields = {"experimentID": "temperatureScan", "broken": False}
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("temperatureScan",))
        self.assertEqual(ran, ["temperatureScan"])
        self.assertTrue(mod.triggered)

    def test_infers_eid_from_part_when_fields_are_paw(self):
        mod = _Mod("Experiment", "")
        mod.fields = {"status": "Ready", "broken": False}
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("mysteryGoo",))
        self.assertEqual(ran, ["mysteryGoo"])
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_field_list_id_not_gui_name(self):
        mod = _Mod("Experiment", "")
        mod.fields = {"status": "Ready"}
        mod.field_list = [_Field("experiment_id", "temperatureScan")]
        vessel = _Vessel([mod])
        vessel.parts.all[0].name = "sensorThermometer"
        ran = start_experiments(vessel, names=("temperatureScan",))
        self.assertEqual(ran, ["temperatureScan"])

    def test_config_values_eid(self):
        mod = _Mod("Experiment", "")
        mod.fields = {}
        mod.config = type("C", (), {"values": {"experiment_id": "mysteryGoo"}})()
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("mysteryGoo",))
        self.assertEqual(ran, ["mysteryGoo"])

    def test_fields_throw_still_infers_part(self):
        mod = _BoomFields("Experiment", "")
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("mysteryGoo",))
        self.assertEqual(ran, ["mysteryGoo"])

    def test_toggle_event_id(self):
        mod = _Mod("Experiment", "mysteryGoo", events=["ToggleEvent"])
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("mysteryGoo",))
        self.assertEqual(ran, ["mysteryGoo"])
        self.assertEqual(mod.triggered, ["ToggleEvent"])

    def test_modules_with_name_proxy_starts_once(self):
        inner = _Mod("Experiment", "mysteryGoo")
        part = _Part("GooExperiment", [inner])

        class _DupParts(_Parts):
            def modules_with_name(self, name):
                if name != "Experiment":
                    return []
                clone = _Mod("Experiment", "mysteryGoo")
                clone.triggered = inner.triggered
                clone.events = inner.events
                clone.fields = inner.fields
                clone.part = part
                return [clone]

        vessel = _Vessel([inner])
        vessel.parts = _DupParts([part])
        lines: list[str] = []
        ran = start_experiments(vessel, names=("mysteryGoo",), on_log=lines.append)
        self.assertEqual(ran, ["mysteryGoo"])
        self.assertEqual(inner.triggered, ["Start Experiment"])
        self.assertEqual([x for x in lines if x.startswith("science start")], ["science start mysteryGoo"])

    def test_same_eid_two_parts_both_start(self):
        stay = _Mod("Experiment", "temperatureScan")
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([stay])
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [stay]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        ran = start_experiments(vessel, names=("temperatureScan",))
        self.assertEqual(ran, ["temperatureScan", "temperatureScan"])
        self.assertEqual(stay.triggered, ["Start Experiment"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])

    def test_stock_leftover_same_part_once(self):
        ksm = _Mod("Experiment", "temperatureScan")
        stock = _Mod("ModuleScienceExperiment", "temperatureScan")
        stock.fields = {"experimentID": "temperatureScan", "broken": False}
        part = _Part("sensorThermometer", [stock, ksm])
        vessel = _Vessel([stock, ksm])
        vessel.parts = _Parts([part])
        ran = start_experiments(vessel, names=("temperatureScan",))
        self.assertEqual(ran, ["temperatureScan"])
        self.assertEqual(ksm.triggered, ["Start Experiment"])
        self.assertEqual(stock.triggered, [])

    def test_keep_already_running(self):
        class _Stop:
            name = "StopExperiment"
            gui_name = "Stop Experiment"
            active = True

            def trigger(self):
                raise AssertionError("must not stop a running experiment")

        mod = _Mod("Experiment", "mysteryGoo", events=["ToggleEvent"])
        mod.event_list = [_Stop()]
        vessel = _Vessel([mod])
        ran = start_experiments(vessel, names=("mysteryGoo",))
        self.assertEqual(ran, ["mysteryGoo"])
        self.assertEqual(mod.triggered, [])

    def test_card_skip_logged_once(self):
        inner = _Mod("Experiment", "seismicScan")
        part = _Part("probeCoreSphere.v2", [inner])

        class _DupParts(_Parts):
            def modules_with_name(self, name):
                if name != "Experiment":
                    return []
                clone = _Mod("Experiment", "seismicScan")
                clone.part = part
                return [clone]

        vessel = _Vessel([inner])
        vessel.parts = _DupParts([part])
        lines: list[str] = []
        ran = start_experiments(vessel, names=("mysteryGoo",), on_log=lines.append)
        self.assertEqual(ran, [])
        skips = [x for x in lines if "not in card" in x]
        self.assertEqual(len(skips), 1)


class TestRecoverAbort(unittest.TestCase):
    def test_recover(self):
        v = _Vessel([], recoverable=True)
        self.assertEqual(recover_or_abort(v), "recovered")
        self.assertTrue(v.recovered)

    def test_honest_abort(self):
        v = _Vessel([], recoverable=False)
        with self.assertRaises(MissionAbort) as ctx:
            recover_or_abort(v)
        self.assertIn("not recoverable", str(ctx.exception))


class TestExperimentDone(unittest.TestCase):
    def test_has_data_not_running(self):
        mod = _Mod("Experiment", "mysteryGoo", done=True)
        self.assertTrue(experiment_done(mod))

    def test_running_is_not_done(self):
        mod = _Mod("Experiment", "mysteryGoo", running=True)
        self.assertFalse(experiment_done(mod, saw_running=True))

    def test_stopped_after_running(self):
        mod = _Mod("Experiment", "mysteryGoo")
        mod.fields["status"] = "stopped"
        self.assertTrue(experiment_done(mod, saw_running=True))
        self.assertFalse(experiment_done(mod, saw_running=False))

    def test_card_complete_needs_all_slots(self):
        goo = _Mod("Experiment", "mysteryGoo", done=True)
        thermo = _Mod("Experiment", "temperatureScan", running=True)
        vessel = _Vessel([goo])
        vessel.parts = _Parts(
            [
                _Part("GooExperiment", [goo]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        self.assertFalse(card_complete(vessel, ("mysteryGoo", "temperatureScan")))
        thermo.fields["status"] = "Done"
        thermo.fields["Has Data"] = True
        self.assertTrue(card_complete(vessel, ("mysteryGoo", "temperatureScan")))

    def test_card_has_data_any_slot(self):
        goo = _Mod("Experiment", "mysteryGoo", done=True)
        thermo = _Mod("Experiment", "temperatureScan", running=True)
        vessel = _Vessel([goo])
        vessel.parts = _Parts(
            [
                _Part("GooExperiment", [goo]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        self.assertTrue(card_has_data(vessel, ("mysteryGoo", "temperatureScan")))
        empty = _Mod("Experiment", "mysteryGoo")
        self.assertFalse(card_has_data(_Vessel([empty]), ("mysteryGoo",)))

    def test_hd_has_data_without_experiment(self):
        drive = _Mod("HardDrive", "")
        drive.fields = {"Data": "Telemetry Report 0.11 Mb"}
        empty = _Mod("HardDrive", "")
        empty.fields = {"Data": "empty"}
        vessel = _Vessel([])
        vessel.parts = _Parts([_Part("probeCoreSphere.v2", [drive])])
        self.assertTrue(hd_has_data(vessel))
        blank = _Vessel([])
        blank.parts = _Parts([_Part("probeCoreSphere.v2", [empty])])
        self.assertFalse(hd_has_data(blank))
        self.assertFalse(hd_has_data(_Vessel([])))

    def test_dwell_budget_uses_size_over_sample_count(self):
        cat = Catalog()
        cat.experiments["mysteryGoo"] = ExperimentCfg(
            id="mysteryGoo",
            data_rate=0.669266770670827,
            sample_amount=1,
            size_mb=429.0,
        )
        budget = pad_dwell_s(("mysteryGoo",), catalog=cat)
        self.assertGreater(budget, 600.0)
        self.assertLess(budget, 800.0)
        self.assertNotAlmostEqual(budget, 1.0 / 0.669266770670827, places=1)

    def test_dwell_budget_fallback(self):
        self.assertEqual(pad_dwell_s(("mysteryGoo",)), 900.0)
        self.assertEqual(pad_dwell_s(()), 0.0)

    def test_dwell_caps_to_remaining_ec(self):
        cat = Catalog()
        cat.experiments["mysteryGoo"] = ExperimentCfg(
            id="mysteryGoo",
            data_rate=0.669266770670827,
            sample_amount=1,
            size_mb=429.0,
            ec_rate=0.18,
        )
        wall = pad_dwell_s(("mysteryGoo",), catalog=cat)
        self.assertGreater(wall, 600.0)
        budget = pad_dwell_s(("mysteryGoo",), catalog=cat, ec=10.0)
        expect = (10.0 / 0.18) * PAD_EC_MARGIN
        self.assertAlmostEqual(budget, expect, places=5)
        self.assertLess(budget, wall)
        self.assertAlmostEqual(pad_ec_rate(("mysteryGoo",), catalog=cat), 0.18)

    def test_merge_keeps_slowest_rate(self):
        store: dict = {}
        merge_experiment_cfg(store, "mysteryGoo", data_rate=1.34, size_mb=100)
        merge_experiment_cfg(store, "mysteryGoo", data_rate=0.669, size_mb=429)
        merge_experiment_cfg(store, "mysteryGoo", ec_rate=0.9)
        merge_experiment_cfg(store, "mysteryGoo", ec_rate=0.18)
        spec = store["mysteryGoo"]
        self.assertEqual(spec.data_rate, 0.669)
        self.assertEqual(spec.size_mb, 429)
        self.assertEqual(spec.ec_rate, 0.18)


class TestPadOnVessel(unittest.TestCase):
    def test_science_then_recover(self):
        mod = _Mod("Experiment", "mysteryGoo", done=True)
        vessel = _Vessel([mod], recoverable=True)
        events = EventLog()
        now, sleep = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            events=events,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=sleep,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(any(e["event"] == "science" for e in events.events))
        self.assertTrue(any(e.get("result") == "done" for e in events.events))

    def test_not_yet_done_does_not_recover(self):
        mod = _Mod("Experiment", "mysteryGoo")

        def trigger_event(name):
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        mod.trigger_event = trigger_event
        vessel = _Vessel([mod], recoverable=True)
        ticks: list[bool] = []
        t = [0.0]

        def now():
            return t[0]

        def sleep(dt):
            ticks.append(vessel.recovered)
            self.assertFalse(vessel.recovered)
            mod.fields["status"] = "Done"
            mod.fields["Has Data"] = True
            t[0] += dt

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=sleep,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(ticks, [False])
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_timeout_recovers_without_done_flag(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=True)
        now, sleep = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=sleep,
            timeout=2.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertGreaterEqual(now(), 2.0)

    def test_empty_science_aborts(self):
        vessel = _Vessel([], recoverable=True)
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel), vessel, science_ids=("mysteryGoo", "temperatureScan")
            )
        self.assertIn("no science", str(ctx.exception))
        self.assertTrue(vessel.recovered)

    def test_briefed_none_recovers(self):
        vessel = _Vessel([], recoverable=True)
        result = run_on_vessel(_Session(vessel), vessel, science_ids=())
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_reliability_gate(self):
        mod = _Mod("Experiment", "mysteryGoo")
        broken = _Mod("Reliability", "", events=[])
        broken.fields["malfunction"] = True
        vessel = _Vessel([mod, broken], recoverable=False, sit="flying")
        vessel._alt = 50_000.0
        with self.assertRaises(MissionAbort):
            run_on_vessel(_Session(vessel), vessel, science_ids=("mysteryGoo",))

    def test_ec_zero_is_gate(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=0.0)
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(_Session(vessel), vessel, science_ids=("mysteryGoo",))
        self.assertIn("ec=0", str(ctx.exception))

    def test_ec_zero_with_data_recovers(self):
        mod = _Mod("Experiment", "mysteryGoo", done=True)
        vessel = _Vessel([mod], recoverable=True, sit="pre_launch", ec=0.0)
        now, sleep = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=sleep,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_ec_zero_after_running_recovers(self):
        mod = _Mod("Experiment", "mysteryGoo")

        def trigger_event(name):
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        mod.trigger_event = trigger_event
        vessel = _Vessel([mod], recoverable=True, sit="pre_launch", ec=5.0)
        t = [0.0]

        def now():
            return t[0]

        def sleep(dt):
            vessel.resources.ec = 0.0
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=sleep,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_ec_budget_recovers_before_catalog_wall(self):
        mod = _Mod("Experiment", "mysteryGoo")
        mod.fields["ec_rate"] = 0.18
        mod.fields["status"] = "Running"
        vessel = _Vessel([mod], recoverable=True, ec=1.0)
        now, sleep = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=sleep,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertLess(now(), 20.0)
        self.assertGreaterEqual(now(), (1.0 / 0.18) * PAD_EC_MARGIN)


class _Uplink:
    def __init__(self, verb: str):
        self.verb = verb


class TestPadUplink(unittest.TestCase):
    def test_science_before_start_does_not_toggle_twice(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=True)
        now, sleep = _fast_clock()
        with patch("pad.take", return_value=_Uplink("science")):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_science_during_dwell_does_not_toggle_again(self):
        mod = _Mod("Experiment", "mysteryGoo")

        def trigger_event(name):
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        mod.trigger_event = trigger_event
        vessel = _Vessel([mod], recoverable=True)
        n = [0]

        def fake_take():
            n[0] += 1
            return _Uplink("science") if n[0] >= 2 else None

        t = [0.0]

        def now():
            return t[0]

        def sleep(dt):
            mod.fields["status"] = "Done"
            mod.fields["Has Data"] = True
            t[0] += dt if dt else 0.01

        with patch("pad.take", fake_take):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_abort_before_start_does_not_continue(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=True)
        with patch("pad.take", return_value=_Uplink("abort_pad")):
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel), vessel, science_ids=("mysteryGoo",)
                )
        self.assertIn("abort", str(ctx.exception).lower())
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, [])

    def test_stage_does_not_light_srb(self):
        mod = _Mod("Experiment", "mysteryGoo", done=True)
        vessel = _Vessel([mod], recoverable=True)
        now, sleep = _fast_clock()
        with patch("pad.take", return_value=_Uplink("stage")):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(mod.triggered, ["Start Experiment"])


class TestPadModule(unittest.TestCase):
    def test_no_flightwatch_import(self):
        text = Path("pad.py").read_text(encoding="utf-8")
        self.assertNotIn("from watch", text)
        self.assertNotIn("import watch", text)
        self.assertNotIn("from watch import", text)
        self.assertIn("uncrewed=True", text)
