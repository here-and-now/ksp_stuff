"""Kerbalism science via part.modules; recover vs honest abort."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from catalog import Catalog, ExperimentCfg, merge_experiment_cfg
from pad import (
    TEMPLATE,
    arm_chutes,
    deploy_chutes,
    install_and_launch,
    pad_craft_path,
    pad_science_ids,
    recover_or_abort,
    run_on_vessel,
)
from card import NO_BOUND_CARD, card_pad_ids
from science import (
    PAD_EC_MARGIN,
    card_complete,
    card_has_data,
    card_wait_line,
    experiment_can_pay,
    experiment_done,
    ground_card_done,
    hd_has_data,
    pad_dwell_s,
    pad_ec_rate,
    paying_eids,
    sit_matches,
    start_experiments,
    stop_experiments,
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
    current_stage = 0

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


class _Krpc:
    def __init__(self):
        self.paused = True
        self.GameScene = type("GS", (), {"flight": "flight"})()
        self.game_scene = type("S", (), {"name": "flight"})()


class _Session:
    def __init__(self, vessel):
        self.active_vessel = vessel
        self.space_center = type(
            "SC",
            (),
            {
                "rails_warp_factor": 0,
                "physics_warp_factor": 0,
                "paused": True,
                "ut": 0.0,
            },
        )()
        krpc = _Krpc()
        self.conn = type("C", (), {"krpc": krpc, "space_center": self.space_center})()

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

    def test_splash_paw_without_experiment_module(self):
        """18-15-08Z: Kerbalism Experiment gone; Stayputnik TELEMETRY + goo PAW."""
        tel = _Mod("ModuleCommand", "", events=["Toggle"])
        tel.fields = {"status": "Ready"}
        goo = _Mod("ModuleScienceExperiment", "", events=["Start Experiment"])
        goo.fields = {"status": "Ready"}
        ant = _Mod("ModuleDeployableAntenna", "", events=["Toggle"])
        ant.fields = {}
        stay = _Part("probeCoreSphere_v2", [tel])
        goo_p = _Part("GooExperiment", [goo])
        ant_p = _Part("SurfAntenna", [ant])
        vessel = _Vessel([tel, goo, ant])
        vessel.parts = _Parts([stay, goo_p, ant_p])
        ran = start_experiments(
            vessel, names=("kerbalism_TELEMETRY", "mysteryGoo")
        )
        self.assertEqual(ran, ["kerbalism_TELEMETRY", "mysteryGoo"])
        self.assertEqual(tel.triggered, ["Toggle"])
        self.assertEqual(goo.triggered, ["Start Experiment"])
        self.assertEqual(ant.triggered, [])

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

    def test_same_eid_prefers_native_part(self):
        """Stayputnik thermo is a duplicate of 2HOT. One Toggle."""
        stay = _Mod("Experiment", "temperatureScan")
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([stay])
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [stay]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        lines: list[str] = []
        ran = start_experiments(
            vessel, names=("temperatureScan",), on_log=lines.append
        )
        self.assertEqual(ran, ["temperatureScan"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(stay.triggered, [])
        self.assertTrue(any("already" in x or "prefer" in x for x in lines))

    def test_geiger_prefers_counter_part_not_stayputnik_paw(self):
        """F-013: kerbalism-geigercounter ranks 0. Idle PAW rem=0 is not a file."""
        from science import _slot_rank, card_run_rem, card_wait_line

        stay = _Mod("Experiment", "geigerCounter")
        stay.fields["remaining"] = 0
        stay.fields["status"] = "waiting"
        inst = _Mod("Experiment", "geigerCounter")
        inst.fields["remaining"] = 497
        inst.fields["status"] = "Ready"
        paw = _Part("probeCoreSphere.v2", [stay])
        native = _Part("kerbalism-geigercounter_1183042711", [inst])
        self.assertEqual(_slot_rank(native, "geigerCounter"), 0)
        self.assertGreater(_slot_rank(paw, "geigerCounter"), 0)
        vessel = _Vessel([stay])
        vessel.parts = _Parts([paw, native])
        lines: list[str] = []
        ran = start_experiments(
            vessel, names=("geigerCounter",), on_log=lines.append
        )
        self.assertEqual(ran, ["geigerCounter"])
        self.assertEqual(inst.triggered, ["Start Experiment"])
        self.assertEqual(stay.triggered, [])
        self.assertTrue(any("kerbalism-geigercounter" in x or "prefer" in x or "already" in x for x in lines))
        wait = card_wait_line(vessel, ("geigerCounter",))
        self.assertIn("geigerCounter", wait)
        self.assertNotIn("geigerCounter run=1 rem=0", wait)
        self.assertNotIn(",", wait)
        running, rem = card_run_rem(vessel, ("geigerCounter",))
        self.assertFalse(running)
        self.assertEqual(rem, 497)

    def test_geiger_paw_only_still_starts(self):
        stay = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([stay])
        vessel.parts = _Parts([_Part("probeCoreSphere.v2", [stay])])
        ran = start_experiments(vessel, names=("geigerCounter",))
        self.assertEqual(ran, ["geigerCounter"])
        self.assertEqual(stay.triggered, ["Start Experiment"])

    def test_flying_card_order_one_each(self):
        stay_thermo = _Mod("Experiment", "temperatureScan")
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        hot = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([stay_thermo])
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [stay_thermo, tel]),
                _Part("sensorThermometer", [hot]),
            ]
        )
        ran = start_experiments(
            vessel, names=("kerbalism_TELEMETRY", "temperatureScan")
        )
        self.assertEqual(ran, ["kerbalism_TELEMETRY", "temperatureScan"])
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(hot.triggered, ["Start Experiment"])
        self.assertEqual(stay_thermo.triggered, [])

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

    def test_stops_running_before_recover(self):
        """17-23-34Z rem that Kerbalism ran must flush before recover()."""
        mod = _Mod(
            "Experiment",
            "temperatureScan",
            events=["Start Experiment", "Stop"],
            running=True,
        )
        vessel = _Vessel([mod], recoverable=True)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        self.assertEqual(recover_or_abort(vessel), "recovered")
        self.assertIn("Stop", mod.triggered)
        self.assertTrue(vessel.recovered)


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

    def test_card_has_data_idle_telemetry_remaining(self):
        """Duration TELEMETRY remaining=0 is pad-data, not leftover HD."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        vessel = _Vessel([tel])
        self.assertTrue(card_has_data(vessel, ("kerbalism_TELEMETRY",)))
        self.assertFalse(
            card_has_data(vessel, ("kerbalism_TELEMETRY",), remaining=False)
        )

    def test_hd_has_data_without_experiment(self):
        drive = _Mod("HardDrive", "")
        drive.fields = {"Data": "Telemetry Report 0.11 Mb"}
        empty = _Mod("HardDrive", "")
        empty.fields = {"Data": "empty"}
        none = _Mod("HardDrive", "")
        none.fields = {"Data": "no files"}
        vessel = _Vessel([])
        vessel.parts = _Parts([_Part("probeCoreSphere.v2", [drive])])
        self.assertTrue(hd_has_data(vessel))
        blank = _Vessel([])
        blank.parts = _Parts([_Part("probeCoreSphere.v2", [empty])])
        self.assertFalse(hd_has_data(blank))
        quiet = _Vessel([])
        quiet.parts = _Parts([_Part("probeCoreSphere.v2", [none])])
        self.assertFalse(hd_has_data(quiet))
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


class TestPadCardIds(unittest.TestCase):
    def test_pad_section_skips_flying_and_splash(self):
        text = (
            "## Flying\n"
            "- experiment: kerbalism_TELEMETRY\n"
            "  situation: FlyingLow\n"
            "## Pad\n"
            "- experiment: geigerCounter\n"
            "  situation: SrfLanded\n"
            "## Splash\n"
            "- experiment: mysteryGoo\n"
            "  situation: SrfSplashed\n"
        )
        self.assertEqual(card_pad_ids(text), ("geigerCounter",))
        self.assertNotIn("mysteryGoo", card_pad_ids(text))
        self.assertNotIn("kerbalism_TELEMETRY", card_pad_ids(text))

    def test_empty_card_aborts(self):
        self.assertEqual(card_pad_ids(""), ())
        with patch("tickets.science_ids_for", return_value=()):
            with patch("missions.seated_science_path") as path:
                path.return_value = Path("/no/such/science.md")
                with self.assertRaises(MissionAbort) as ctx:
                    pad_science_ids()
                self.assertIn(NO_BOUND_CARD, str(ctx.exception))
            empty = Path("tests/fixtures/cards/empty.md")
            with patch("missions.seated_science_path", return_value=empty):
                with self.assertRaises(MissionAbort) as ctx:
                    pad_science_ids()
                self.assertIn(NO_BOUND_CARD, str(ctx.exception))

    def test_fixture_card_is_geiger_not_f005(self):
        path = Path("tests/fixtures/cards/pad-geiger.md")
        with patch("tickets.science_ids_for", return_value=()):
            with patch("missions.seated_science_path", return_value=path):
                ids = pad_science_ids()
        self.assertEqual(ids, ("geigerCounter",))
        self.assertNotIn("mysteryGoo", ids)
        self.assertNotIn("temperatureScan", ids)

    def test_science_tickets_skip_markdown(self):
        path = Path("tests/fixtures/cards/pad-geiger.md")
        with patch("tickets.science_ids_for", return_value=("temperatureScan",)):
            with patch("missions.seated_science_path", return_value=path):
                ids = pad_science_ids()
        self.assertEqual(ids, ("temperatureScan",))

    def test_run_on_vessel_reads_seated_card(self):
        """Default science_ids is the seated pad card, not PAD_EXPERIMENTS."""
        mod = _Mod("Experiment", "geigerCounter", done=True)
        vessel = _Vessel([mod], recoverable=True)
        vessel.parts = _Parts([_Part("probeCoreSphere.v2", [mod])])
        now, sleep = _fast_clock()
        with patch("pad.pad_science_ids", return_value=("geigerCounter",)):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                now=now,
                sleep=sleep,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])


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

    def test_timeout_empty_hd_aborts(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=True)
        now, sleep = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertIn("empty HD", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_timeout_with_data_recovers(self):
        mod = _Mod("Experiment", "mysteryGoo", done=True)
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

    def test_timeout_empty_hd_aborts_without_met_clock(self):
        mod = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([mod], recoverable=True)
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("probeCoreSphere.v2", [mod])])
        now, sleep = _fast_clock()
        logs: list[str] = []
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("geigerCounter",),
                on_log=logs.append,
                now=now,
                sleep=sleep,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertIn("dwell timeout empty HD", str(ctx.exception))
        self.assertNotIn("MET frozen", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertFalse(any("MET frozen" in x for x in logs))
        self.assertTrue(any("pad unpause" in x for x in logs))
        self.assertTrue(any("pad launch clock" in x for x in logs))
        self.assertEqual(vessel.control.staged, 1)

    def test_recording_met_zero_does_not_abort(self):
        mod = _Mod("Experiment", "geigerCounter", running=True)
        mod.fields["remaining"] = 3.0
        vessel = _Vessel([mod], recoverable=True)
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("probeCoreSphere.v2", [mod])])
        now, sleep0 = _fast_clock()
        sess = _Session(vessel)
        sess.space_center.ut = 100.0

        def sleep(dt):
            sleep0(dt)
            rem = float(mod.fields.get("remaining", 0)) - dt
            mod.fields["remaining"] = max(0.0, rem)
            sess.space_center.ut += dt
            if rem <= 0:
                mod.fields["status"] = "Done"
                mod.fields["Has Data"] = True

        logs: list[str] = []
        result = run_on_vessel(
            sess,
            vessel,
            science_ids=("geigerCounter",),
            on_log=logs.append,
            now=now,
            sleep=sleep,
            timeout=2.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertFalse(any("MET frozen" in x for x in logs))
        self.assertTrue(any("pad physics 3x rails=0" in x for x in logs))
        self.assertTrue(any("pad physics 1x" in x for x in logs))
        self.assertEqual(sess.space_center.rails_warp_factor, 0)
        self.assertEqual(sess.space_center.physics_warp_factor, 0)

    def test_pad_source_never_rails_or_warpto(self):
        pad = Path("pad.py").read_text(encoding="utf-8")
        warp = Path("physics_warp.py").read_text(encoding="utf-8")
        for text in (pad, warp):
            self.assertNotIn("WarpTo(", text)
            self.assertNotIn("warp_to(", text)
        self.assertIn("rails_warp_factor = 0", warp)
        self.assertNotIn("rails_warp_factor = 1", warp)
        self.assertIn("from physics_warp import", pad)

    def test_landed_does_not_stage(self):
        mod = _Mod("Experiment", "mysteryGoo", done=True)
        vessel = _Vessel([mod], recoverable=True, sit="landed")
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
        self.assertEqual(vessel.control.staged, 0)

    def test_dwell_unpauses_before_loop(self):
        """Hangar leave-paused: always set paused=False, do not wait for the flag."""
        from hangar import run_physics

        sc = type("SC", (), {"rails_warp_factor": 2, "physics_warp_factor": 3, "paused": True})()
        krpc = _Krpc()
        session = type("S", (), {"conn": type("C", (), {"krpc": krpc})(), "space_center": sc})()
        run_physics(session)
        self.assertFalse(krpc.paused)
        self.assertFalse(sc.paused)
        self.assertEqual(sc.rails_warp_factor, 0)
        self.assertEqual(sc.physics_warp_factor, 0)

        mod = _Mod("Experiment", "mysteryGoo", done=True)
        vessel = _Vessel([mod], recoverable=True)
        now, sleep = _fast_clock()
        logs: list[str] = []
        sess = _Session(vessel)
        sess.conn.krpc.paused = True
        result = run_on_vessel(
            sess,
            vessel,
            science_ids=("mysteryGoo",),
            on_log=logs.append,
            now=now,
            sleep=sleep,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertFalse(sess.conn.krpc.paused)
        self.assertTrue(any("pad unpause" in x for x in logs))

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


class TestCardWaitLine(unittest.TestCase):
    def test_names_remaining_and_clock(self):
        mod = _Mod("Experiment", "geigerCounter", running=True)
        mod.fields["remaining"] = 0.4
        vessel = _Vessel([mod])
        vessel.parts = _Parts([_Part("probeCoreSphere.v2", [mod])])
        line = card_wait_line(
            vessel, ("geigerCounter",), met=12.3, sit="landed", ec=280.0
        )
        self.assertTrue(line.startswith("wait science"))
        self.assertIn("geigerCounter", line)
        self.assertIn("part=", line)
        self.assertIn("file=open", line)
        self.assertIn("rem=0.4", line)
        self.assertIn("met=12.3", line)
        self.assertIn("sit=landed", line)

    def test_rem_zero_running_is_recording(self):
        mod = _Mod("Experiment", "geigerCounter", running=True)
        mod.fields["remaining"] = 0
        vessel = _Vessel([mod])
        vessel.parts = _Parts([_Part("kerbalism-geigercounter", [mod])])
        line = card_wait_line(vessel, ("geigerCounter",))
        self.assertIn("file=recording", line)
        self.assertIn("run=1", line)


class TestSituationCanPay(unittest.TestCase):
    def test_sample_remaining_zero_skips(self):
        mod = _Mod("Experiment", "mysteryGoo")
        mod.fields["remaining"] = 0
        vessel = _Vessel([mod])
        vessel.parts = _Parts([_Part("GooExperiment", [mod])])
        lines: list[str] = []
        ran = start_experiments(
            vessel, names=("mysteryGoo",), on_log=lines.append
        )
        self.assertEqual(ran, [])
        self.assertEqual(mod.triggered, [])
        self.assertTrue(any("cannot pay" in x for x in lines))
        self.assertEqual(
            paying_eids(vessel, ("mysteryGoo",), sit="splashed", biome="Forest"),
            [],
        )

    def test_duration_remaining_zero_still_starts(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        vessel = _Vessel([tel])
        vessel.parts = _Parts([_Part("probeCoreOcto.v2", [tel])])
        ran = start_experiments(vessel, names=("kerbalism_TELEMETRY",))
        self.assertEqual(ran, ["kerbalism_TELEMETRY"])
        self.assertEqual(tel.triggered, ["Start Experiment"])

        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        tv = _Vessel([thermo], sit="splashed")
        tv.parts = _Parts([_Part("sensorThermometer", [thermo])])
        need = {"temperatureScan": ("SrfSplashed@Forest", "Forest")}
        self.assertEqual(
            paying_eids(
                tv,
                ("temperatureScan",),
                sit="splashed",
                biome="Forest",
                need=need,
            ),
            ["temperatureScan"],
        )
        ran = start_experiments(
            tv,
            names=("temperatureScan",),
            sit="splashed",
            biome="Forest",
            need=need,
        )
        self.assertEqual(ran, ["temperatureScan"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])

        geiger = _Mod("Experiment", "geigerCounter")
        geiger.fields["remaining"] = 0
        gv = _Vessel([geiger], sit="flying")
        gv.parts = _Parts([_Part("kerbalism-geigercounter", [geiger])])
        need_g = {"geigerCounter": ("FlyingHigh", "")}
        self.assertEqual(
            paying_eids(
                gv,
                ("geigerCounter",),
                sit="flying",
                biome="Shores",
                need=need_g,
                alt=54_477.0,
            ),
            ["geigerCounter"],
        )
        ran = start_experiments(
            gv,
            names=("geigerCounter",),
            sit="flying",
            biome="Shores",
            need=need_g,
            alt=54_477.0,
        )
        self.assertEqual(ran, ["geigerCounter"])
        self.assertEqual(geiger.triggered, ["Start Experiment"])

        baro = _Mod("Experiment", "barometerScan")
        baro.fields["remaining"] = 0
        bv = _Vessel([baro], sit="splashed")
        bv.parts = _Parts([_Part("sensorBarometer", [baro])])
        need_b = {"barometerScan": ("SrfSplashed@Water", "Water")}
        self.assertEqual(
            paying_eids(
                bv,
                ("barometerScan",),
                sit="splashed",
                biome="Water",
                need=need_b,
            ),
            ["barometerScan"],
        )
        ran = start_experiments(
            bv,
            names=("barometerScan",),
            sit="splashed",
            biome="Water",
            need=need_b,
        )
        self.assertEqual(ran, ["barometerScan"])
        self.assertEqual(baro.triggered, ["Start Experiment"])

    def test_bound_need_stays_in_card(self):
        """Splash leftover stays in-card. Flying skip is cannot-pay, not not-in-card."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        baro = _Mod("Experiment", "barometerScan")
        baro.fields["remaining"] = 0
        geiger = _Mod("Experiment", "geigerCounter")
        geiger.fields["remaining"] = 0
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 1.0
        vessel = _Vessel([goo], sit="flying")
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
                _Part("sensorBarometer", [baro]),
                _Part("kerbalism-geigercounter", [geiger]),
                _Part("GooExperiment", [goo]),
            ]
        )
        need = {
            "kerbalism_TELEMETRY": ("SrfSplashed@Water", "Water"),
            "temperatureScan": ("SrfSplashed@Water", "Water"),
            "barometerScan": ("SrfSplashed@Water", "Water"),
        }
        names = ("barometerScan", "geigerCounter", "mysteryGoo")
        lines: list[str] = []
        ran = start_experiments(
            vessel,
            names=names,
            on_log=lines.append,
            sit="flying",
            biome="Shores",
            need=need,
            alt=54_000.0,
        )
        self.assertEqual(ran, ["geigerCounter", "mysteryGoo"])
        self.assertFalse(any("not in card" in x for x in lines if "TELEMETRY" in x))
        self.assertFalse(
            any("not in card" in x for x in lines if "temperatureScan" in x)
        )
        self.assertFalse(
            any("not in card" in x for x in lines if "barometerScan" in x)
        )
        self.assertTrue(any("cannot pay" in x and "kerbalism_TELEMETRY" in x for x in lines))
        self.assertTrue(any("cannot pay" in x and "temperatureScan" in x for x in lines))
        self.assertTrue(any("cannot pay" in x and "barometerScan" in x for x in lines))
        self.assertEqual(tel.triggered, [])
        self.assertEqual(thermo.triggered, [])
        self.assertEqual(baro.triggered, [])

        tel.triggered.clear()
        thermo.triggered.clear()
        baro.triggered.clear()
        geiger.triggered.clear()
        goo.triggered.clear()
        lines.clear()
        ran = start_experiments(
            vessel,
            names=names,
            on_log=lines.append,
            sit="splashed",
            biome="Water",
            need=need,
        )
        self.assertIn("kerbalism_TELEMETRY", ran)
        self.assertIn("temperatureScan", ran)
        self.assertIn("barometerScan", ran)
        self.assertFalse(any("not in card" in x for x in lines))
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(baro.triggered, ["Start Experiment"])
        paid = paying_eids(
            vessel, names, sit="splashed", biome="Water", need=need
        )
        self.assertIn("barometerScan", paid)
        self.assertNotIn("kerbalism_TELEMETRY", paid)
        self.assertNotIn("temperatureScan", paid)
        paid_bound = paying_eids(
            vessel,
            ("kerbalism_TELEMETRY", "temperatureScan", "barometerScan"),
            sit="splashed",
            biome="Water",
            need=need,
        )
        self.assertEqual(
            paid_bound,
            ["kerbalism_TELEMETRY", "temperatureScan", "barometerScan"],
        )

    def test_srflanded_skips_while_flying(self):
        mod = _Mod("Experiment", "temperatureScan")
        mod.fields["remaining"] = 114
        vessel = _Vessel([mod], sit="flying")
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        ran = start_experiments(
            vessel,
            names=("temperatureScan",),
            sit="flying",
            biome="Forest",
            need=need,
        )
        self.assertEqual(ran, [])
        self.assertEqual(mod.triggered, [])

    def test_wrong_biome_skips(self):
        mod = _Mod("Experiment", "temperatureScan")
        mod.fields["remaining"] = 138
        vessel = _Vessel([mod], sit="flying")
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        need = {"temperatureScan": ("FlyingLow@Grasslands", "Grasslands")}
        ran = start_experiments(
            vessel,
            names=("temperatureScan",),
            sit="flying",
            biome="Forest",
            need=need,
        )
        self.assertEqual(ran, [])
        self.assertEqual(
            paying_eids(
                vessel,
                ("temperatureScan",),
                sit="flying",
                biome="Forest",
                need=need,
            ),
            [],
        )

    def test_matching_flyinglow_starts(self):
        mod = _Mod("Experiment", "temperatureScan")
        mod.fields["remaining"] = 138
        vessel = _Vessel([mod], sit="flying")
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        need = {"temperatureScan": ("FlyingLow@Grasslands", "Grasslands")}
        ran = start_experiments(
            vessel,
            names=("temperatureScan",),
            sit="flying",
            biome="Grasslands",
            need=need,
        )
        self.assertEqual(ran, ["temperatureScan"])

    def test_sit_matches_helpers(self):
        self.assertTrue(sit_matches("flying", "Forest", "FlyingLow@Forest", "Forest"))
        self.assertFalse(sit_matches("flying", "Forest", "SrfLanded@Forest", "Forest"))
        self.assertFalse(
            sit_matches("flying", "Forest", "FlyingLow@Grasslands", "Grasslands")
        )
        self.assertTrue(sit_matches("landed", "Forest", "SrfLanded@Forest", "Forest"))
        self.assertTrue(sit_matches("splashed", "Forest", "SrfSplashed@Forest", "Forest"))
        self.assertFalse(
            sit_matches("splashed", "Forest", "SrfLanded@Forest", "Forest")
        )
        self.assertFalse(
            sit_matches("landed", "Forest", "SrfSplashed@Forest", "Forest")
        )
        self.assertTrue(sit_matches("flying", "", "FlyingLow@Grasslands", "Grasslands"))
        self.assertFalse(
            sit_matches("flying", "Forest", "FlyingHigh@Forest", "Forest")
        )
        self.assertFalse(
            sit_matches(
                "flying", "Forest", "FlyingHigh@Forest", "Forest", alt=880.0
            )
        )
        self.assertTrue(
            sit_matches(
                "flying",
                "Forest",
                "FlyingHigh@Forest",
                "Forest",
                alt=50_400.0,
            )
        )
        self.assertTrue(
            sit_matches(
                "flying",
                "Shores",
                "FlyingHigh",
                "global",
                alt=50_400.0,
            )
        )
        self.assertTrue(
            sit_matches(
                "sub_orbital",
                "Shores",
                "FlyingHigh",
                "",
                alt=54_477.0,
            )
        )
        self.assertFalse(
            sit_matches(
                "flying",
                "Shores",
                "FlyingHigh",
                "global",
                alt=880.0,
            )
        )
        self.assertFalse(
            sit_matches(
                "landed",
                "Forest",
                "FlyingHigh@Forest",
                "Forest",
                alt=50_400.0,
            )
        )
        self.assertFalse(
            sit_matches(
                "flying",
                "Shores",
                "InSpaceLow",
                "global",
                alt=50_400.0,
            )
        )
        self.assertTrue(
            sit_matches(
                "sub_orbital",
                "Shores",
                "InSpaceLow",
                "",
                alt=187_000.0,
            )
        )
        self.assertTrue(
            sit_matches("orbiting", "", "InSpaceLow", "global")
        )
        self.assertFalse(
            sit_matches("flying", "Shores", "InSpaceLow", "", alt=98_000.0)
        )

    def test_stop_does_not_toggle(self):
        mod = _Mod(
            "Experiment",
            "temperatureScan",
            events=["Toggle", "Stop"],
            running=True,
        )
        vessel = _Vessel([mod])
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        self.assertEqual(stop_experiments(vessel), ["temperatureScan"])
        self.assertEqual(mod.triggered, ["Stop"])

    def test_ground_card_done_sample_spent(self):
        mod = _Mod("Experiment", "temperatureScan", running=True)
        mod.fields["remaining"] = 0
        vessel = _Vessel([mod])
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        self.assertTrue(ground_card_done(vessel, ("temperatureScan",)))
        tel = _Mod("Experiment", "kerbalism_TELEMETRY", running=True)
        tel.fields["remaining"] = 0
        tv = _Vessel([tel])
        tv.parts = _Parts([_Part("probeCoreOcto.v2", [tel])])
        self.assertTrue(ground_card_done(tv, ("kerbalism_TELEMETRY",)))
        tel.fields["remaining"] = 6
        self.assertFalse(ground_card_done(tv, ("kerbalism_TELEMETRY",)))
        tel.fields["remaining"] = 0
        self.assertTrue(experiment_can_pay(tel, "kerbalism_TELEMETRY"))
        del tel.fields["remaining"]
        self.assertFalse(ground_card_done(tv, ("kerbalism_TELEMETRY",)))
        idle = _Mod("Experiment", "temperatureScan", running=True)
        iv = _Vessel([idle])
        iv.parts = _Parts([_Part("sensorThermometer", [idle])])
        self.assertTrue(ground_card_done(iv, ("temperatureScan",)))
        self.assertTrue(experiment_can_pay(idle, "temperatureScan"))

    def test_ground_card_idle_file_rem_zero_not_done(self):
        """hold-ground-card: unstarted file rem=0 is not splash leftover done."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        vessel = _Vessel([thermo])
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        self.assertFalse(ground_card_done(vessel, ("temperatureScan",)))
        self.assertFalse(experiment_done(thermo, eid="temperatureScan"))
        self.assertTrue(experiment_can_pay(thermo, "temperatureScan"))
        baro = _Mod("Experiment", "barometerScan")
        baro.fields["remaining"] = 0
        bv = _Vessel([baro])
        bv.parts = _Parts([_Part("sensorBarometer", [baro])])
        self.assertFalse(ground_card_done(bv, ("barometerScan",)))
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 0
        gv = _Vessel([goo])
        gv.parts = _Parts([_Part("GooExperiment", [goo])])
        self.assertTrue(ground_card_done(gv, ("mysteryGoo",)))
        self.assertTrue(experiment_done(goo, eid="mysteryGoo"))


class _Uplink:
    def __init__(self, verb: str):
        self.verb = verb


class _FakeHangar:
    def __init__(self, root: Path):
        self.root = root
        self.calls: list[dict] = []
        self.installed: list[str] = []

    def ships(self, facility: str = "VAB") -> Path:
        path = self.root / facility
        path.mkdir(parents=True, exist_ok=True)
        return path

    def install(self, craft, *, overwrite=True, **_kwargs):
        self.installed.append(craft.name)
        dest = self.ships("VAB") / f"{craft.name}.craft"
        dest.write_text(f"ship = {craft.name}\n", encoding="utf-8")
        return dest

    def launch(self, session, name, *, recover=True, uncrewed=False, **_kwargs):
        self.calls.append(
            {"name": name, "uncrewed": uncrewed, "recover": recover}
        )
        session.active_vessel = _Vessel([], sit="pre_launch")
        session.active_vessel.name = name


class TestPadHangar(unittest.TestCase):
    def test_copies_geiger_file_not_pad_pbc_template(self):
        src = pad_craft_path("kspstuff-geiger-pbc")
        self.assertTrue(src.is_file())
        raw_src = src.read_bytes()
        self.assertIn(b"kerbalism-geigercounter", raw_src)
        with tempfile.TemporaryDirectory() as tmp:
            fake = _FakeHangar(Path(tmp))
            session = _Session(_Vessel([]))
            session.active_vessel = None
            with patch("pad.discover_hangar", return_value=fake):
                with patch("missions.pad_craft_name", return_value="kspstuff-geiger-pbc"):
                    with patch("craft.pad_pbc") as gen:
                        install_and_launch(session)
            dest = fake.ships("VAB") / "kspstuff-geiger-pbc.craft"
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.read_bytes(), raw_src)
            self.assertNotIn("kspstuff-pad-pbc", dest.read_text(encoding="utf-8"))
            gen.assert_not_called()
            self.assertEqual(fake.installed, [])
            self.assertEqual(fake.calls[0]["name"], "kspstuff-geiger-pbc")
            self.assertTrue(fake.calls[0]["uncrewed"])
            self.assertEqual(session.active_vessel.name, "kspstuff-geiger-pbc")

    def test_missing_named_craft_does_not_generate_template(self):
        session = _Session(_Vessel([]))
        with patch("pad.discover_hangar") as hangar:
            hangar.return_value.ksp_root = Path("/tmp")
            hangar.return_value.ships.return_value = Path("/tmp")
            with patch("missions.pad_craft_name", return_value="kspstuff-no-such"):
                with patch("pad.pad_craft_path", return_value=Path("/no/such.craft")):
                    with patch("craft.pad_pbc") as gen:
                        with self.assertRaises(MissionAbort) as ctx:
                            install_and_launch(session)
        gen.assert_not_called()
        self.assertIn("F-013", str(ctx.exception))
        self.assertIn("kspstuff-no-such", str(ctx.exception))

    def test_template_name_still_pad_pbc(self):
        self.assertEqual(TEMPLATE, "kspstuff-pad-pbc")


class TestPadLaunchClock(unittest.TestCase):
    def test_flea_stage_does_not_light(self):
        from pad import _launch_clock

        vessel = _Vessel([], sit="pre_launch")
        vessel.control.current_stage = 1
        logs: list[str] = []
        _launch_clock(vessel, logs.append)
        self.assertEqual(vessel.control.staged, 0)
        self.assertTrue(any("skip stage=1" in x for x in logs))


class TestPadUplink(unittest.TestCase):
    def test_science_before_start_does_not_toggle_twice(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=True)
        now, sleep = _fast_clock()
        with patch("pad.take", return_value=_Uplink("science")):
            with self.assertRaises(MissionAbort):
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("mysteryGoo",),
                    now=now,
                    sleep=sleep,
                    timeout=2.0,
                    pulse=1.0,
                )
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
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(mod.triggered, ["Start Experiment"])


class _KrpcChute:
    def __init__(self):
        self.armed = False
        self.deployed = False
        self.state = "stowed"

    def deploy(self):
        self.deployed = True
        self.state = "deployed"


class TestArmChutes(unittest.TestCase):
    def test_none_without_chute(self):
        vessel = _Vessel([])
        self.assertEqual(arm_chutes(vessel), "none")
        self.assertEqual(vessel.control.staged, 0)

    def test_realchute_arm_not_stage(self):
        mod = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([mod])
        vessel.parts = _Parts([_Part("parachuteSingle", [mod])])
        logs: list[str] = []
        st = arm_chutes(vessel, logs.append)
        self.assertEqual(st, "armed")
        self.assertEqual(mod.triggered, ["Arm parachute"])
        self.assertEqual(vessel.control.staged, 0)
        self.assertTrue(any("chute" in x for x in logs))

    def test_krpc_parachute_sets_armed(self):
        ch = _KrpcChute()
        vessel = _Vessel([])
        vessel.parts.parachutes = [ch]
        st = arm_chutes(vessel)
        self.assertTrue(ch.armed)
        self.assertEqual(st, "armed")
        self.assertEqual(vessel.control.staged, 0)

    def test_ignores_experiment_modules(self):
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod])
        self.assertEqual(arm_chutes(vessel), "none")
        self.assertEqual(mod.triggered, [])

    def test_deploy_realchute_not_cut(self):
        """06-53-50Z kRPC armed never Deploy; 154 m/s packed."""
        mod = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([mod])
        vessel.parts = _Parts([_Part("parachuteSingle", [mod])])
        st = deploy_chutes(vessel)
        self.assertEqual(st, "deployed")
        self.assertEqual(mod.triggered, ["Arm parachute", "Deploy chute"])
        self.assertEqual(vessel.control.staged, 0)

    def test_skips_procedural_chute_module(self):
        proc = _Mod(
            "ProceduralChute",
            "",
            events=["Arm parachute", "Deploy chute"],
        )
        vessel = _Vessel([proc])
        vessel.parts = _Parts([_Part("parachuteSingle", [proc])])
        st = arm_chutes(vessel)
        self.assertEqual(proc.triggered, [])
        self.assertNotEqual(st, "armed")
        self.assertEqual(vessel.control.staged, 0)


class TestPadModule(unittest.TestCase):
    def test_no_flightwatch_import(self):
        text = Path("pad.py").read_text(encoding="utf-8")
        self.assertNotIn("from watch", text)
        self.assertNotIn("import watch", text)
        self.assertNotIn("from watch import", text)
        self.assertIn("uncrewed=True", text)
