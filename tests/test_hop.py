"""No-KSP gates for hop: light, flying card, recover when down."""

from __future__ import annotations

import argparse
import json
import math
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from hop import (
    CHUTE_DEPLOY_ALT_M,
    CRAFT,
    HOP_COAST_PHYS_RATE,
    FLYING_HIGH_M,
    FLYING_LOW_M,
    GOO_CRASH_MS,
    HOP_SPLASH_ABORT,
    HOP_TO_WATER_ABORT,
    SPLASH_CRAFT,
    WATER_BRAKE_ALT_MAX_M,
    WATER_BRAKE_FUEL_MIN,
    WATER_BRAKE_GATE_S,
    WATER_BRAKE_HZ,
    WATER_BRAKE_HOVER_THROTTLE,
    WATER_BRAKE_LIGHT_PAD_M,
    WATER_BRAKE_LIGHT_TTI_S,
    WATER_BRAKE_SPEED_M,
    WATER_BRAKE_TTI_S,
    WATER_BRAKE_VZ_CUT,
    _hover_throttle,
    _nap_dt,
    _suicide_need,
    _suicide_throttle,
    WATER_CRAFT,
    WATER_HEADING_DEG,
    WATER_PITCH_DEG,
    WATER_PITCH_FROM_UP,
    WATER_PITCH_SLEW_DPS,
    WATER_PITCH_UP,
    WATER_SLEW_THROTTLE,
    INLAND_HEADING_CAPTURE_DEG,
    INLAND_HEADING_DEG,
    INLAND_PITCH_DEG,
    INLAND_PITCH_FROM_UP,
    INLAND_YAW_FROM_UP,
    INLAND_YAW_MET_S,
    INLAND_YAW_PITCH_DEG,
    SURFACE_NORTH,
    _inland_cmd_pitch,
    _coast_impact_ms,
    _coast_ok,
    _apply_hop_physics,
    _abort_high_lid,
    _burning,
    _command_ok,
    _hold_or_cut,
    _light,
    _link_edge,
    _lofted,
    _pad_boosting,
    _reached_high_lid,
    _steer_east,
    _want_coast_phys,
    _zero_stick_if_deaf,
    _steer_inland,
    inland_direction,
    surface_direction,
    _suicide_gate,
    _suicide_hold,
    _suicide_light,
    _suicide_now,
    _suicide_tti,
    east_direction,
    bound_card_is_flying_high,
    bound_science_need,
    hop_landed_science_ids,
    _live_sit,
    _met_still,
    hop_craft_name,
    hop_craft_path,
    hop_offplan_apo,
    hop_science_alt,
    hop_science_ids,
    _keep_hd,
    _hold_ground_card,
    hop_splash_science,
    hop_target_apo,
    install_and_launch,
    leftover_wreck_before_light,
    leftover_ksc_call,
    abort_ksc_leftover,
    stack_sheared,
    _vessel_gone,
    SHEAR_MASS_FRAC,
    _wait_vessel_gone,
    run_hop,
    run_hop_splash,
    run_hop_to_water,
    run_on_vessel,
    run_phase,
    water_can_steer,
)
from phases import OffPlan, check_expect
from card import HOP_EXPERIMENTS, NO_BOUND_CARD, card_experiment_ids, card_flying_ids
from telem import EventLog, MissionAbort, Telem


def _fast_clock():
    t = [0.0]

    def now():
        return t[0]

    def sleep(dt):
        t[0] += dt if dt else 0.01

    return now, sleep, t


def _isolate_live_tickets(test: unittest.TestCase) -> None:
    """Sequence stubs must not inherit the seated land/splash leftover board."""
    patcher = patch("tickets.list_tickets", return_value=())
    patcher.start()
    test.addCleanup(patcher.stop)


_LAND_AND_SPLASH_THERMO = (
    {
        "id": "T-077",
        "type": "science",
        "payload": {
            "experiment_id": "temperatureScan",
            "situation": "SrfLanded@Forest",
            "biome": "Forest",
            "seq": 0,
        },
    },
    {
        "id": "T-313",
        "type": "science",
        "payload": {
            "experiment_id": "temperatureScan",
            "situation": "SrfSplashed@Forest",
            "biome": "Forest",
            "seq": 1,
        },
    },
)


_LAND_OR_SPLASH = (
    {
        "id": "T-077",
        "type": "science",
        "payload": {
            "experiment_id": "temperatureScan",
            "situation": "SrfLanded@Forest",
            "biome": "Forest",
            "seq": 1,
        },
    },
    {
        "id": "T-287",
        "type": "science",
        "payload": {
            "experiment_id": "kerbalism_TELEMETRY",
            "situation": "SrfLanded@Forest",
            "biome": "Forest",
            "seq": 2,
        },
    },
    {
        "id": "T-288",
        "type": "science",
        "payload": {
            "experiment_id": "kerbalism_TELEMETRY",
            "situation": "SrfSplashed@Forest",
            "biome": "Forest",
            "seq": 3,
        },
    },
)


class _Mod:
    def __init__(self, name, eid, events=None, broken=False):
        self.name = name
        self.fields = {"experiment_id": eid, "broken": broken}
        self.events = list(events or ["Start Experiment"])
        self.triggered: list[str] = []

    def trigger_event(self, name):
        self.triggered.append(name)
        self.fields["status"] = "Running"

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
    def __init__(self):
        self.throttle = 0.0
        self.sas = False
        self.staged = 0

    def activate_next_stage(self):
        self.staged += 1


class _Autopilot:
    """kRPC 0.6: Engaged=True always restarts soft-start; direction is not a hold."""

    def __init__(self):
        self._engaged = False
        self.engage_n = 0
        self.point_n = 0
        self.target_pitch = 0.0
        self.target_heading = 0.0
        self.target_roll = 0.0
        self.target_direction = (0.0, 0.0, 0.0)
        self.up_reference = (1.0, 0.0, 0.0)
        self.reference_frame = None
        self.held = None

    @property
    def engaged(self):
        return self._engaged

    @engaged.setter
    def engaged(self, value):
        if value:
            self.engage_n += 1
            self._engaged = True
        else:
            self._engaged = False

    def engage(self):
        self.engaged = True

    def disengage(self):
        self.engaged = False

    def set_direction_and_up(self, direction, up, roll=0.0):
        self.point_n = getattr(self, "point_n", 0) + 1
        self.target_direction = tuple(float(x) for x in direction)
        self.up_reference = tuple(float(x) for x in up)
        self.target_roll = float(roll)
        self.held = self.target_direction


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


class _Flight:
    def __init__(self, vessel):
        self._vessel = vessel
        self.dynamic_pressure = 0.0
        self.surface_altitude = 80.0

    @property
    def mean_altitude(self):
        return self._vessel._alt

    @property
    def speed(self):
        return self._vessel._speed

    @property
    def vertical_speed(self):
        vz = getattr(self._vessel, "_vz", None)
        if vz is None:
            return float("nan")
        return float(vz)


class _Orbit:
    def __init__(self, apo=80.0, peri=-500_000.0):
        self.body = _Body()
        self.periapsis_altitude = peri
        self.apoapsis_altitude = apo
        self.eccentricity = 0.99
        self.semi_major_axis = 6.4e6
        self.time_to_periapsis = 0.0
        self.time_to_apoapsis = 1.0


class _DeadVessel:
    """kRPC active_vessel proxy whose GUID is already gone."""

    def __init__(self, guid="fbacb1ed-301a-4b89-b2ff-19b3483f6fd8"):
        self._guid = guid

    @property
    def name(self):
        raise ValueError(f"No such vessel {self._guid}")


class _Vessel:
    def __init__(self, modules, *, recoverable=False, sit="pre_launch", ec=10.0):
        self.name = "probe"
        self.situation = sit
        self.recoverable = recoverable
        self.recovered = False
        self.control = _Control()
        self.auto_pilot = _Autopilot()
        self.resources = _Res(ec=ec)
        self.thrust = 0.0
        self.parts = _Parts([_Part("GooExperiment", modules)])
        self.orbit = _Orbit()
        self.surface_reference_frame = "surface"
        self._alt = 80.0
        self._speed = 0.0
        self._vz = None
        self._flight = _Flight(self)

    def flight(self, _rf=None):
        return self._flight

    def recover(self):
        if not self.recoverable:
            raise RuntimeError("not recoverable")
        self.recovered = True


class _Session:
    def __init__(self, vessel):
        self.active_vessel = vessel
        vessels = [vessel] if vessel is not None else []
        self.space_center = type(
            "SC",
            (),
            {
                "rails_warp_factor": 0,
                "physics_warp_factor": 0,
                "vessels": vessels,
            },
        )()
        gs = type(
            "GS",
            (),
            {
                "tracking_station": "tracking_station",
                "space_center": "space_center",
                "flight": "flight",
            },
        )()
        krpc = type("K", (), {"GameScene": gs, "game_scene": "flight"})()
        self.conn = type("C", (), {"krpc": krpc})()

    def add_stream(self, func, obj, name):
        class _S:
            def __call__(self_inner):
                return func(obj, name)

            def remove(self_inner):
                pass

        return _S()


class _Uplink:
    def __init__(self, verb: str):
        self.verb = verb


class TestHopCatalog(unittest.TestCase):
    def test_in_names(self):
        from phases import NAMES

        self.assertIn("hop", NAMES)
        self.assertIn("splash", NAMES)
        self.assertNotIn("hop-to-water", NAMES)
        self.assertNotIn("hop-splash", NAMES)
        self.assertEqual(HOP_EXPERIMENTS, ("kerbalism_TELEMETRY", "temperatureScan"))
        self.assertEqual(CRAFT, "kspstuff-hop-flea-pbc")
        self.assertTrue(hop_craft_path("kspstuff-hop-flea-pbc").is_file())
        self.assertTrue(hop_craft_path("kspstuff-hop-hammer-pbc").is_file())
        from session import SessionError

        with patch(
            "missions.hangar_craft_name",
            return_value="kspstuff-hop-hammer-pbc",
        ):
            self.assertEqual(hop_craft_name(), "kspstuff-hop-hammer-pbc")
        with patch(
            "missions.hangar_craft_name",
            side_effect=SessionError("VAB capable=no — no Hangar (L-039)"),
        ):
            with self.assertRaises(SessionError):
                hop_craft_name()

    def test_source_is_not_a_godfile(self):
        text = Path("hop.py").read_text(encoding="utf-8")
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertNotIn("from watch", text)
        self.assertNotIn("import watch", text)
        self.assertNotIn("from launch", text)
        self.assertNotIn("parts.experiments", text)
        self.assertNotIn("run_ready", text)
        self.assertNotIn("pad_pbc", text)
        self.assertNotIn("parachute", text.lower())
        self.assertIn("run_physics", text)
        self.assertIn("go_space_center", text)
        self.assertIn("from hangar import", text)
        self.assertIn("kspstuff-hop-hammer-pbc", text)
        self.assertIn("uncrewed", blocks.lower())
        self.assertIn("kspstuff-hop-hammer-pbc", blocks)

    def test_apo_clamp(self):
        with patch("hop.hop_wants_flying_high", return_value=False):
            with patch("phases._kv", return_value={"hop_apo": "15000"}):
                self.assertEqual(hop_target_apo(), 15_000.0)
            with patch("phases._kv", return_value={"hop_apo": "18000"}):
                self.assertEqual(hop_target_apo(), 18_000.0)
            with patch("phases._kv", return_value={"hop_apo": "40000"}):
                self.assertEqual(hop_target_apo(), 18_000.0)
            with patch("phases._kv", return_value={"hop_apo": "1000"}):
                self.assertEqual(hop_target_apo(), 8_000.0)
        with patch("hop.hop_wants_flying_high", return_value=False):
            self.assertEqual(hop_science_alt(), 0.0)

    def test_apo_unclamp_flyinghigh(self):
        with patch("hop.hop_wants_flying_high", return_value=True):
            self.assertEqual(hop_offplan_apo(), FLYING_HIGH_M)
            self.assertEqual(hop_science_alt(), FLYING_LOW_M)
            with patch("phases._kv", return_value={"hop_apo": "80000"}):
                self.assertEqual(hop_target_apo(), 80_000.0)
            with patch("phases._kv", return_value={"hop_apo": "40000"}):
                self.assertEqual(hop_target_apo(), 40_000.0)
            with patch("phases._kv", return_value={"hop_apo": "200000"}):
                self.assertEqual(hop_target_apo(), FLYING_HIGH_M)
            with patch("phases._kv", return_value={"hop_apo": "1000"}):
                self.assertEqual(hop_target_apo(), 8_000.0)

    def test_apo_unclamp_hop_splash(self):
        with patch("hop.hop_wants_flying_high", return_value=False):
            with patch(
                "phases._kv",
                return_value={"hop_apo": "80000", "phase": "hop-splash"},
            ):
                self.assertEqual(hop_target_apo(space=True), 80_000.0)
                self.assertEqual(hop_target_apo(), 18_000.0)


class TestHopCoastPhysics(unittest.TestCase):
    def setUp(self):
        from uplink import desk

        self._desk = desk
        self._prev = (desk.hold, desk.skip_warp, desk.phys_warp)
        desk.hold = False
        desk.skip_warp = False
        desk.phys_warp = None

    def tearDown(self):
        desk = self._desk
        desk.hold, desk.skip_warp, desk.phys_warp = self._prev

    def _sc(self, rails=0, phys=0):
        return type(
            "SC",
            (),
            {"rails_warp_factor": rails, "physics_warp_factor": phys},
        )()

    def _sess(self, sc):
        return type("S", (), {"space_center": sc})()

    def _snap(self, **kw):
        return type("Snap", (), kw)()

    def test_factory_rate_is_4x(self):
        self.assertEqual(HOP_COAST_PHYS_RATE, 4)

    def test_want_coast_after_burnout(self):
        snap = self._snap(v_vert=40.0, alt=41_884.0, q=400.0)
        self.assertTrue(
            _want_coast_phys(
                snap,
                left_pad=True,
                down=False,
                chute_open=False,
                burning=False,
            )
        )

    def test_1x_while_burning_chute_down_deploy(self):
        snap = self._snap(v_vert=40.0, alt=41_884.0, q=400.0)
        self.assertFalse(
            _want_coast_phys(
                snap, left_pad=False, down=False, chute_open=False, burning=False
            )
        )
        self.assertFalse(
            _want_coast_phys(
                snap, left_pad=True, down=True, chute_open=False, burning=False
            )
        )
        self.assertTrue(
            _want_coast_phys(
                snap, left_pad=True, down=False, chute_open=True, burning=False
            )
        )
        self.assertFalse(
            _want_coast_phys(
                snap, left_pad=True, down=False, chute_open=False, burning=True
            )
        )
        deploy = self._snap(v_vert=-80.0, alt=1_500.0)
        self.assertFalse(
            _want_coast_phys(
                deploy,
                left_pad=True,
                down=False,
                chute_open=False,
                burning=False,
            )
        )
        silk = self._snap(v_vert=-12.0, alt=800.0, chute="deployed")
        self.assertFalse(
            _want_coast_phys(
                silk,
                left_pad=True,
                down=False,
                chute_open=True,
                burning=False,
            )
        )
        semi = self._snap(v_vert=-20.0, alt=1_200.0, chute="semi_deployed")
        self.assertFalse(
            _want_coast_phys(
                semi,
                left_pad=True,
                down=False,
                chute_open=True,
                burning=False,
            )
        )

    def test_want_coast_not_before_loft(self):
        """18-34-22Z: alt 101 m is pad boost, not coast 3×."""
        pad = self._snap(v_vert=14.0, alt=101.0, fuel=1054.0)
        self.assertFalse(_lofted(pad))
        self.assertFalse(
            _want_coast_phys(
                pad,
                left_pad=True,
                down=False,
                chute_open=False,
                burning=False,
            )
        )
        self.assertTrue(_lofted(self._snap(v_vert=40.0, alt=12_000.0)))

    def test_throttle_zero_on_pad_is_still_burning(self):
        """Throttle 0 with fuel at 101 m is not burnout."""
        vessel = _Vessel([])
        vessel.control.throttle = 0.0
        snap = self._snap(fuel=1054.0, alt=101.0)
        self.assertTrue(_burning(vessel, snap, lofted=False))
        self.assertFalse(_burning(vessel, snap, lofted=True))
        vessel.control.throttle = 1.0
        self.assertTrue(_burning(vessel, snap, lofted=True))
        dry = self._snap(fuel=0.0, alt=101.0)
        self.assertFalse(_burning(vessel, dry, lofted=False))

    def test_abort_high_lid_is_toggle_sit_not_pad_loft(self):
        """1.6 km loft is not a FlyingHigh lid miss."""
        pad = self._snap(situation="flying", alt=1_549.0)
        high = self._snap(situation="flying", alt=50_400.0)
        with patch("hop.hop_wants_flying_high", return_value=True):
            self.assertFalse(_reached_high_lid(pad))
            self.assertTrue(_reached_high_lid(high))
            self.assertFalse(
                _abort_high_lid(
                    lit=True,
                    started=(),
                    left_pad=True,
                    down=True,
                    reached_lid=False,
                )
            )
            self.assertTrue(
                _abort_high_lid(
                    lit=True,
                    started=(),
                    left_pad=True,
                    down=True,
                    reached_lid=True,
                )
            )
            self.assertFalse(
                _abort_high_lid(
                    lit=True,
                    started=("kerbalism_TELEMETRY",),
                    left_pad=True,
                    down=True,
                    reached_lid=True,
                )
            )

    def test_pad_boosting_is_lit_not_lofted(self):
        """Flying pad boost: still burning, not lofted, not landed."""
        self.assertTrue(
            _pad_boosting(
                lit=True,
                left_pad=True,
                lofted=False,
                down=False,
                burning=True,
            )
        )
        self.assertFalse(
            _pad_boosting(
                lit=True,
                left_pad=True,
                lofted=True,
                down=False,
                burning=True,
            )
        )
        self.assertFalse(
            _pad_boosting(
                lit=True,
                left_pad=True,
                lofted=False,
                down=True,
                burning=True,
            )
        )
        self.assertFalse(
            _pad_boosting(
                lit=True,
                left_pad=True,
                lofted=False,
                down=False,
                burning=False,
            )
        )

    def test_factory_coast_sets_4x_rails_0(self):
        sc = self._sc()
        logs: list[str] = []
        last = [""]
        n = _apply_hop_physics(
            self._sess(sc), coast=True, on_log=logs.append, last=last
        )
        self.assertEqual(n, 3)
        self.assertEqual(sc.physics_warp_factor, 3)
        self.assertEqual(sc.rails_warp_factor, 0)
        self.assertEqual(last[0], "4x")
        self.assertTrue(any("hop coast physics 4x rails=0" in x for x in logs))
        n2 = _apply_hop_physics(
            self._sess(sc), coast=True, on_log=logs.append, last=last
        )
        self.assertEqual(n2, 3)
        self.assertEqual(logs.count("hop coast physics 4x rails=0"), 1)

    def test_not_coast_is_1x_silent_at_start(self):
        sc = self._sc(phys=2)
        logs: list[str] = []
        last = [""]
        n = _apply_hop_physics(
            self._sess(sc), coast=False, on_log=logs.append, last=last
        )
        self.assertEqual(n, 0)
        self.assertEqual(sc.physics_warp_factor, 0)
        self.assertEqual(sc.rails_warp_factor, 0)
        self.assertFalse(any("hop physics 1x" in x for x in logs))

    def test_drop_to_1x_logs_once(self):
        sc = self._sc()
        logs: list[str] = []
        last = [""]
        _apply_hop_physics(
            self._sess(sc), coast=True, on_log=logs.append, last=last
        )
        n = _apply_hop_physics(
            self._sess(sc), coast=False, on_log=logs.append, last=last
        )
        self.assertEqual(n, 0)
        self.assertEqual(sc.physics_warp_factor, 0)
        self.assertTrue(any("hop physics 1x" in x for x in logs))

    def test_no_warp_persists_1x(self):
        from uplink import Command, _apply, phys_warp_rate

        _apply(Command(verb="no_warp", arg="", raw="no_warp"))
        self.assertEqual(phys_warp_rate(), 1)
        self.assertEqual(self._desk.phys_warp, 1)
        self.assertTrue(self._desk.skip_warp)
        sc = self._sc(phys=2)
        n = _apply_hop_physics(self._sess(sc), coast=True, last=[""])
        self.assertEqual(n, 0)
        self.assertEqual(sc.physics_warp_factor, 0)

    def test_phys_warp_4_and_warp_2(self):
        from uplink import Command, _apply, phys_warp_rate

        _apply(Command(verb="phys-warp", arg="4", raw="phys-warp 4"))
        self.assertEqual(phys_warp_rate(), 4)
        self.assertFalse(self._desk.skip_warp)
        sc = self._sc()
        n = _apply_hop_physics(self._sess(sc), coast=True, last=[""])
        self.assertEqual(n, 3)
        self.assertEqual(sc.physics_warp_factor, 3)
        self.assertEqual(sc.rails_warp_factor, 0)
        _apply(Command(verb="warp", arg="2", raw="warp 2"))
        self.assertEqual(phys_warp_rate(), 2)
        n = _apply_hop_physics(self._sess(sc), coast=True, last=[""])
        self.assertEqual(n, 1)
        self.assertEqual(sc.physics_warp_factor, 1)

    def test_hold_forces_1x(self):
        from uplink import phys_warp_rate

        self._desk.phys_warp = 4
        self._desk.hold = True
        self.assertEqual(phys_warp_rate(), 1)
        sc = self._sc(phys=3)
        n = _apply_hop_physics(self._sess(sc), coast=True, last=[""])
        self.assertEqual(n, 0)
        self.assertEqual(sc.physics_warp_factor, 0)

    def test_no_warp_callable_latches_desk(self):
        from emergencies import Ctx, no_warp

        sc = self._sc(rails=2, phys=3)
        sess = self._sess(sc)
        no_warp(Ctx(session=sess))
        self.assertEqual(sc.physics_warp_factor, 0)
        self.assertEqual(sc.rails_warp_factor, 0)
        self.assertTrue(self._desk.skip_warp)
        self.assertEqual(self._desk.phys_warp, 1)

    def test_source_never_warpto(self):
        for path in ("hop.py", "hop_factory.py", "physics_warp.py", "pad.py"):
            text = Path(path).read_text(encoding="utf-8")
            self.assertNotIn("WarpTo(", text, path)
            self.assertNotIn("warp_to(", text, path)
        warp = Path("physics_warp.py").read_text(encoding="utf-8")
        self.assertIn("rails_warp_factor = 0", warp)
        self.assertNotIn("rails_warp_factor = 1", warp)
        self.assertIn("_physics_factor", Path("hop.py").read_text(encoding="utf-8"))
        self.assertIn("phys_warp_rate", Path("hop.py").read_text(encoding="utf-8"))
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertIn("phys-warp", blocks)
        self.assertIn("no_warp", blocks)
        self.assertIn("rails 0", blocks)

    def test_factory_pulse_module_is_inland_only(self):
        text = Path("hop_factory.py").read_text(encoding="utf-8")
        self.assertNotIn("wait_water", text)
        self.assertNotIn("wait_splash", text)
        self.assertNotIn("def _loft_after_skip", text)
        self.assertNotIn("def _coast_after_skip", text)
        self.assertIn("apply_sit_warp", text)
        self.assertIn("airborne_cannot_pay", text)
        self.assertIn("chute_arm_sit", text)
        self.assertIn("chute_deploy_sit", text)
        self.assertIn("timeout_hit", text)
        self.assertIn("leftover_call", text)
        self.assertIn("def _chute_arm_now", text)
        self.assertIn("def _chute_deploy_now", text)
        self.assertIn("def _lid_burn_sit", text)
        self.assertIn("def _high_dwell_sit", text)
        self.assertIn("def _lid_vertical_sit", text)
        self.assertIn("def _hold_lid", text)
        self.assertIn("def _offplan_apo_lid", text)
        self.assertIn("def _inland_high_sit", text)
        arm_at = text.find("H.arm_chutes")
        arm_sit_at = text.find("chute_arm_sit(snap)")
        deploy_at = text.find("H.deploy_chutes")
        deploy_sit_at = text.find("chute_deploy_sit(snap)")
        warp_at = text.find("apply_sit_warp(")
        wait_lid_at = text.find("waiting_lid")
        hold_at = text.find("H._hold_or_cut")
        offplan_at = text.find("raise OffPlan")
        self.assertNotEqual(arm_sit_at, -1)
        self.assertNotEqual(deploy_sit_at, -1)
        self.assertNotEqual(warp_at, -1)
        self.assertNotEqual(wait_lid_at, -1)
        self.assertNotEqual(hold_at, -1)
        self.assertNotEqual(offplan_at, -1)
        self.assertGreater(arm_at, arm_sit_at)
        self.assertGreater(deploy_at, deploy_sit_at)
        self.assertGreater(arm_at, warp_at)
        self.assertGreater(wait_lid_at, arm_at)
        self.assertGreater(wait_lid_at, deploy_at)
        warp_chunk = text[warp_at : warp_at + 280]
        self.assertIn("burning=burning_now", warp_chunk)
        self.assertNotIn("_high_dwell_sit", warp_chunk)
        self.assertGreater(wait_lid_at, warp_at)
        self.assertGreater(offplan_at, hold_at)
        self.assertLess(text.count("\n") + 1, 1100)

    def test_run_on_vessel_coasts_3x_then_1x(self):
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        sess = _Session(vessel)
        coast_factors: list[int] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 41_884.0
                vessel._speed = 80.0
                vessel._vz = 40.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 0.0
                vessel.orbit.apoapsis_altitude = 49_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel._flight.dynamic_pressure = 400.0
            elif vessel.situation == "flying":
                coast_factors.append(sess.space_center.physics_warp_factor)
                if t[0] >= 3.0:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=False):
            result = run_on_vessel(
                sess,
                vessel,
                science_ids=("temperatureScan",),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(coast_factors)
        self.assertIn(3, coast_factors)
        self.assertEqual(sess.space_center.rails_warp_factor, 0)
        self.assertEqual(sess.space_center.physics_warp_factor, 0)
        self.assertTrue(any("hop coast physics 4x rails=0" in x for x in logs))
        self.assertNotIn("Deploy chute", chute.triggered)

    def test_uplink_verbs(self):
        from hop import _UPLINK_SKIP
        from uplink import _VERBS

        self.assertIn("phys-warp", _VERBS)
        self.assertIn("warp", _VERBS)
        self.assertIn("no_warp", _VERBS)
        self.assertIn("science", _VERBS)
        self.assertIn("transmit", _VERBS)
        self.assertEqual(_UPLINK_SKIP, frozenset({"stage"}))
        self.assertNotIn("science", _UPLINK_SKIP)
        self.assertNotIn("transmit", _UPLINK_SKIP)


class TestCardIds(unittest.TestCase):
    def test_parse(self):
        text = (
            "- experiment: kerbalism_TELEMETRY\n"
            "  situation: FlyingLow\n"
            "- experiment: temperatureScan\n"
        )
        self.assertEqual(
            card_experiment_ids(text),
            ("kerbalism_TELEMETRY", "temperatureScan"),
        )

    def test_empty_is_empty(self):
        self.assertEqual(card_experiment_ids(""), ())

    def test_flying_skips_splash_goo(self):
        text = (
            "## Flying\n"
            "- experiment: kerbalism_TELEMETRY\n"
            "  situation: FlyingLow\n"
            "- experiment: temperatureScan\n"
            "  situation: FlyingLow\n"
            "## Splash\n"
            "- experiment: mysteryGoo\n"
            "  situation: SrfSplashed\n"
        )
        self.assertEqual(
            card_flying_ids(text),
            ("kerbalism_TELEMETRY", "temperatureScan"),
        )
        self.assertNotIn("mysteryGoo", card_flying_ids(text))

    def test_fixture_card_is_flying_not_splash_goo(self):
        path = Path("tests/fixtures/cards/hop-flying.md")
        with patch("tickets.science_ids_for", return_value=()):
            with patch("tickets.seated_fly_ticket", return_value=None):
                with patch("missions.seated_science_path", return_value=path):
                    ids = hop_science_ids()
        self.assertIn("temperatureScan", ids)
        self.assertNotIn("mysteryGoo", ids)
        self.assertNotIn("geigerCounter", ids)

    def test_empty_card_aborts(self):
        empty = Path("tests/fixtures/cards/empty.md")
        with patch("tickets.science_ids_for", return_value=()):
            with patch("tickets.seated_fly_ticket", return_value=None):
                with patch("missions.seated_science_path", return_value=empty):
                    with self.assertRaises(MissionAbort) as ctx:
                        hop_science_ids()
        self.assertIn(NO_BOUND_CARD, str(ctx.exception))

    def test_fly_science_ids_union_bound(self):
        fly = {"payload": {"science_ids": ["temperatureScan"]}}
        with patch(
            "tickets.science_ids_for",
            return_value=("kerbalism_TELEMETRY", "mysteryGoo"),
        ):
            with patch("tickets.seated_fly_ticket", return_value=fly):
                ids = hop_science_ids()
        self.assertEqual(
            ids,
            ("kerbalism_TELEMETRY", "mysteryGoo", "temperatureScan"),
        )


class TestBoundFlyingCard(unittest.TestCase):
    def test_unbound_leftover_high_is_not_lid(self):
        tickets = [
            {
                "type": "science",
                "id": "T-068",
                "payload": {
                    "experiment_id": "temperatureScan",
                    "situation": "FlyingLow@Forest",
                    "bound": "yes",
                },
            },
            {
                "type": "science",
                "id": "T-069",
                "payload": {
                    "wait_experiment_id": "kerbalism_TELEMETRY",
                    "situation": "FlyingHigh@Forest",
                    "bound": "no",
                },
            },
        ]
        self.assertFalse(
            bound_card_is_flying_high(tickets, flying_ids=("temperatureScan",))
        )

    def test_bound_flyinghigh_is_lid(self):
        tickets = [
            {
                "type": "science",
                "payload": {
                    "experiment_id": "temperatureScan",
                    "situation": "FlyingHigh@Shores",
                },
            }
        ]
        self.assertTrue(
            bound_card_is_flying_high(tickets, flying_ids=("temperatureScan",))
        )

    def test_empty_flying_ids_is_none(self):
        self.assertIsNone(bound_card_is_flying_high([], flying_ids=()))

    def test_inland_high_sit_splash_bind_is_lid(self):
        """flyinghigh-lid: splash bind is not FlyingLow. Factory inland still waits the lid."""
        from hop_factory import _inland_high_sit

        splash = [
            {
                "type": "science",
                "payload": {
                    "experiment_id": "kerbalism_TELEMETRY",
                    "situation": "SrfSplashed@Water",
                },
            },
            {
                "type": "science",
                "payload": {
                    "experiment_id": "temperatureScan",
                    "situation": "SrfSplashed@Water",
                },
            },
        ]
        flying_low = [
            {
                "type": "science",
                "payload": {
                    "experiment_id": "temperatureScan",
                    "situation": "FlyingLow@Forest",
                },
            }
        ]
        leftover_high = [
            {
                "type": "science",
                "payload": {
                    "wait_experiment_id": "kerbalism_TELEMETRY",
                    "situation": "FlyingHigh@Forest",
                },
            }
        ]
        with patch("hop.hop_wants_flying_high", return_value=False):
            self.assertTrue(_inland_high_sit(splash, flying_ids=()))
            self.assertTrue(
                _inland_high_sit(splash, flying_ids=("kerbalism_TELEMETRY",))
            )
            self.assertFalse(
                _inland_high_sit(flying_low, flying_ids=("temperatureScan",))
            )
            self.assertFalse(
                _inland_high_sit(
                    flying_low + leftover_high, flying_ids=("temperatureScan",)
                )
            )
            self.assertTrue(_inland_high_sit(leftover_high, flying_ids=()))
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                self.assertEqual(
                    hop_target_apo(
                        space=_inland_high_sit(splash, flying_ids=())
                    ),
                    50_000.0,
                )
                self.assertEqual(hop_target_apo(), 18_000.0)

    def test_lit_empty_modules_is_not_leftover_hd(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        self.assertFalse(
            _keep_hd(vessel, ("temperatureScan",), [], left_pad=True, lit=True)
        )
        self.assertTrue(
            _keep_hd(vessel, ("temperatureScan",), [], left_pad=True, lit=False)
        )


class TestHopCommandLink(unittest.TestCase):
    """T-326 link-lost: kRPC Control writes without a radio. Fail open."""

    def test_command_ok_link_and_comms(self):
        vessel = _Vessel([])
        deaf = type("S", (), {"link": False})()
        live = type("S", (), {"link": True})()
        missing = type("S", (), {})()
        self.assertFalse(_command_ok(deaf, vessel))
        self.assertTrue(_command_ok(live, vessel))
        self.assertTrue(_command_ok(missing, vessel))
        self.assertTrue(_command_ok(None, vessel))
        self.assertTrue(_command_ok(missing, None))
        vessel.comms = type("C", (), {"can_communicate": False})()
        self.assertFalse(_command_ok(missing, vessel))
        self.assertTrue(_command_ok(live, vessel))
        self.assertFalse(_command_ok(deaf, vessel))
        vessel.comms = type("C", (), {"can_communicate": True})()
        self.assertTrue(_command_ok(missing, vessel))
        vessel.comms = type("C", (), {"can_communicate": None})()
        self.assertTrue(_command_ok(missing, vessel))

        class _Boom:
            @property
            def can_communicate(self):
                raise RuntimeError("hangar")

        vessel.comms = _Boom()
        self.assertTrue(_command_ok(missing, vessel))
        vessel.crew_count = 1
        vessel.comms = type("C", (), {"can_communicate": False})()
        self.assertTrue(_command_ok(deaf, vessel))

    def test_light_aborts_when_deaf_else_stages(self):
        deaf = type("S", (), {"link": False})()
        vessel = _Vessel([])
        vessel.control.sas = True
        vessel.control.throttle = 0.4
        with self.assertRaises(MissionAbort) as ctx:
            _light(vessel, None, deaf)
        self.assertIn("no signal (pad)", str(ctx.exception))
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(vessel.control.throttle, 0.0)
        self.assertFalse(vessel.control.sas)
        live = _Vessel([])
        _light(live, None, type("S", (), {"link": True})())
        self.assertEqual(live.control.staged, 1)
        self.assertEqual(live.control.throttle, 1.0)
        missing = _Vessel([])
        _light(missing, None)
        self.assertEqual(missing.control.staged, 1)
        crewed = _Vessel([])
        crewed.crew_count = 1
        _light(crewed, None, deaf)
        self.assertEqual(crewed.control.staged, 1)

    def test_zero_stick_and_factory_extra_throttle_skip(self):
        vessel = _Vessel([])
        vessel.control.throttle = 1.0
        vessel.control.sas = True
        snap = type("S", (), {"link": False})()
        deaf = _zero_stick_if_deaf(vessel, snap)
        if not deaf:
            vessel.control.throttle = 1.0
        self.assertTrue(deaf)
        self.assertEqual(vessel.control.throttle, 0.0)
        self.assertFalse(vessel.control.sas)
        self.assertEqual(vessel.control.staged, 0)
        live = type("S", (), {"link": True})()
        self.assertFalse(_zero_stick_if_deaf(vessel, live))
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_hold_or_cut_does_not_suicide_when_deaf(self):
        vessel = _Vessel([])
        light = type(
            "S",
            (),
            {
                "link": False,
                "apo": 800.0,
                "fuel": 40.0,
                "alt": 700.0,
                "speed": 220.0,
                "v_vert": -220.0,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            light,
            18_000.0,
            cut=True,
            hold=1.0,
            brake=True,
            braking=True,
        )
        self.assertTrue(cut)
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        live = type(
            "S",
            (),
            {
                "link": True,
                "apo": 800.0,
                "fuel": 40.0,
                "alt": 700.0,
                "speed": 220.0,
                "v_vert": -220.0,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            live,
            18_000.0,
            cut=True,
            hold=1.0,
            brake=True,
            braking=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 1.0)

    def test_suicide_gate_zeros_when_deaf(self):
        vessel = _Vessel([])
        vessel.control.throttle = 0.5
        snap = type(
            "S",
            (),
            {
                "link": False,
                "apo": 800.0,
                "fuel": 40.0,
                "alt": 700.0,
                "speed": 220.0,
                "v_vert": -220.0,
            },
        )()
        now, sleep, _t = _fast_clock()
        self.assertFalse(_suicide_gate(vessel, snap, sleep=sleep, now=now))
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_link_edge_emits_yes_no_only(self):
        ev = EventLog()
        _link_edge(ev, True, None)
        _link_edge(ev, True, True)
        self.assertEqual(ev.events, [])
        _link_edge(ev, False, True)
        self.assertEqual(ev.events[-1]["event"], "link")
        self.assertEqual(ev.events[-1]["link"], 0)
        self.assertEqual(ev.events[-1]["msg"], "link no")
        _link_edge(ev, True, False)
        self.assertEqual(ev.events[-1]["link"], 1)
        self.assertEqual(ev.events[-1]["msg"], "link yes")
        self.assertEqual(len(ev.events), 2)
        _link_edge(None, False, True)

    def test_lid_abort_ignores_deaf(self):
        snap = type("S", (), {"link": False})()
        self.assertFalse(
            _abort_high_lid(
                lit=True,
                started=[],
                left_pad=True,
                down=True,
                reached_lid=False,
            )
        )
        del snap


class TestHopExpect(unittest.TestCase):
    def test_skip_peri(self):
        state = type(
            "S",
            (),
            {"body": "Earth", "peri": -6_000_000.0, "apo": 15_000.0},
        )()
        with patch(
            "phases._kv",
            return_value={
                "expect_body": "Earth",
                "expect_peri_min": "0",
                "expect_apo_max": "20000",
            },
        ):
            check_expect(state, skip_peri=True)
            with self.assertRaises(OffPlan):
                check_expect(state, skip_peri=False)

    def test_apo_still_checked(self):
        state = type(
            "S",
            (),
            {"body": "Earth", "peri": -6_000_000.0, "apo": 40_000.0},
        )()
        with patch(
            "phases._kv",
            return_value={
                "expect_body": "Earth",
                "expect_peri_min": "-500000",
                "expect_apo_max": "18000",
            },
        ):
            with self.assertRaises(OffPlan):
                check_expect(state, skip_peri=True)
            check_expect(state, skip_peri=True, skip_apo=True)


class TestStackShear(unittest.TestCase):
    def test_burnout_mass_drop_is_shear(self):
        """07-06-08Z 1283→270 kg at fuel 0; burn ~2.3 kg/unit does not cover it."""
        why = stack_sheared(1283.6, 270.6, 178.0, 0.0, 9, 9)
        self.assertIsNotNone(why)
        self.assertIn("mass", why)

    def test_boost_fuel_drain_is_not_shear(self):
        self.assertIsNone(stack_sheared(2490.0, 1804.0, 700.6, 406.9, 9, 9))
        self.assertIsNone(stack_sheared(2824.6, 2490.0, 720.0, 700.6, 9, 9))

    def test_parts_drop_is_shear(self):
        why = stack_sheared(270.6, 270.6, 0.0, 0.0, 9, 4)
        self.assertEqual(why, "parts 9->4")

    def test_frac_below_gate(self):
        self.assertGreater(SHEAR_MASS_FRAC, 0.3)
        self.assertIsNone(stack_sheared(1200.0, 1100.0, 100.0, 0.0, 4, 4))

    def test_impact_empty_vessel_is_not_shear(self):
        """07-21-05Z 36 parts through apex; parts 36→0 mass 0 at 412 m."""
        self.assertIsNone(stack_sheared(1601.9, 0.0, 0.0, 0.0, 36, 0))
        self.assertIsNone(stack_sheared(1601.9, 1601.9, 0.0, 0.0, 36, 0))

    def test_vessel_gone_parts_or_mass(self):
        snap = type("S", (), {"mass": 0.0})()
        vessel = _Vessel([], sit="flying")
        vessel.parts.all = []
        self.assertTrue(_vessel_gone(snap, vessel))
        vessel.parts.all = [_Part("probeCoreOcto.v2", [])]
        snap.mass = 0.0
        self.assertTrue(_vessel_gone(snap, vessel))
        snap.mass = 1601.9
        self.assertFalse(_vessel_gone(snap, vessel))


class TestLandOrSplashNeed(unittest.TestCase):
    def test_live_sit_ground_snap_beats_flying_vessel(self):
        """Splash leftover sit-matches when snap is splashed and vessel still flying."""
        vessel = _Vessel([], sit="flying")
        snap = type("S", (), {"situation": "splashed", "biome": "Water"})()
        self.assertEqual(_live_sit(vessel, snap), "splashed")
        land = type("S", (), {"situation": "landed", "biome": "Forest"})()
        self.assertEqual(_live_sit(vessel, land), "landed")
        air = type("S", (), {"situation": "flying", "biome": "Water"})()
        self.assertEqual(_live_sit(vessel, air), "flying")

    def test_live_sit_picks_splash_not_first_seq(self):
        with patch("tickets.list_tickets", return_value=_LAND_OR_SPLASH):
            splash = bound_science_need(live_sit="splashed", live_biome="Forest")
            land = bound_science_need(live_sit="landed", live_biome="Forest")
            flying = bound_science_need(live_sit="flying", live_biome="Forest")
        self.assertEqual(
            splash["kerbalism_TELEMETRY"], ("SrfSplashed@Forest", "Forest")
        )
        self.assertEqual(
            splash["temperatureScan"], ("SrfLanded@Forest", "Forest")
        )
        self.assertEqual(
            land["kerbalism_TELEMETRY"], ("SrfLanded@Forest", "Forest")
        )
        self.assertEqual(
            flying["kerbalism_TELEMETRY"], ("SrfLanded@Forest", "Forest")
        )

    def test_ground_ids_union_land_and_splash(self):
        def fake_ids(*, situation="", craft=""):
            if situation == "landed":
                return ("temperatureScan", "kerbalism_TELEMETRY")
            if situation == "splash":
                return ("kerbalism_TELEMETRY",)
            return ()

        with patch("tickets.science_ids_for", side_effect=fake_ids):
            self.assertEqual(
                hop_landed_science_ids(),
                ("temperatureScan", "kerbalism_TELEMETRY"),
            )

    def test_ground_ids_sit_match_live_landed(self):
        """SrfLanded@Forest leftover is the landed card, not flying or splash-only."""
        with patch("tickets.list_tickets", return_value=_LAND_OR_SPLASH):
            self.assertEqual(
                hop_landed_science_ids(live_sit="landed", live_biome="Forest"),
                ("temperatureScan", "kerbalism_TELEMETRY"),
            )
            self.assertEqual(
                hop_landed_science_ids(live_sit="splashed", live_biome="Forest"),
                ("kerbalism_TELEMETRY",),
            )
            self.assertEqual(
                hop_landed_science_ids(live_sit="flying", live_biome="Forest"),
                (),
            )


class TestHopSequence(unittest.TestCase):
    def setUp(self):
        # Live seated card may be FlyingHigh; sequence stubs fly at 2 km.
        self._fh = patch("hop.hop_wants_flying_high", return_value=False)
        self._fh.start()
        self.addCleanup(self._fh.stop)
        _isolate_live_tickets(self)

    def test_light_science_after_airborne_then_recover(self):
        mod = _Mod("Experiment", "mysteryGoo")
        sits: list[str] = []

        def trigger_event(name):
            sits.append(vessel.situation)
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        mod.trigger_event = trigger_event
        vessel = _Vessel([mod], recoverable=False)
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["flying"])

    def test_factory_pad_light_aborts_when_deaf(self):
        vessel = _Vessel([_Mod("Experiment", "temperatureScan")])
        now, sleep, _t = _fast_clock()

        class _SnapLink:
            def __init__(self, inner):
                self._inner = inner
                self.link = False

            def __getattr__(self, name):
                return getattr(self._inner, name)

        orig = Telem.read

        def wrapped(self):
            return _SnapLink(orig(self))

        with patch.object(Telem, "read", wrapped):
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=sleep,
                    timeout=5.0,
                    pulse=1.0,
                )
        self.assertIn("no signal (pad)", str(ctx.exception))
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_deaf_after_pad_recovers_does_not_abort_lid(self):
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([thermo], recoverable=False)
        now, sleep, t = _fast_clock()
        link = [True]

        class _SnapLink:
            def __init__(self, inner):
                self._inner = inner
                self.link = link[0]

            def __getattr__(self, name):
                return getattr(self._inner, name)

        orig = Telem.read

        def wrapped(self):
            return _SnapLink(orig(self))

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                link[0] = False
            elif vessel.situation == "flying" and thermo.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch.object(Telem, "read", wrapped):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("temperatureScan",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(thermo.triggered, ["Start Experiment"])

    def test_airborne_arms_realchute_without_extra_stage(self):
        """chute-arm-ascent: loft does not Arm. Light is one stage."""
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._vz = 40.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and thermo.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(chute.triggered, [])
        self.assertFalse(any("chute" in x for x in logs))

    def test_descent_deploys_realchute(self):
        """06-53-50Z armed through 206 m / 154 m/s — Deploy on the way down."""
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 1_500.0
                vessel._speed = 120.0
                vessel._vz = -80.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 0.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and "Deploy chute" in chute.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 8.0
                vessel._vz = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertEqual(vessel.control.staged, 1)
        self.assertIn("Arm parachute", chute.triggered)
        self.assertIn("Deploy chute", chute.triggered)
        self.assertNotIn("Cut main chute", chute.triggered)

    def test_apex_does_not_deploy_chute(self):
        """chute-deploy-sit: lofted descent Arms; Deploy still ≤2 km."""
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        apex_triggered: list[list[str]] = []
        arm_alts: list[float] = []
        deploy_alts: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 13_609.0
                vessel._speed = 16.0
                vessel._vz = -5.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 0.0
                vessel.orbit.apoapsis_altitude = 18_463.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                if vessel._alt > CHUTE_DEPLOY_ALT_M:
                    apex_triggered.append(list(chute.triggered))
                if "Arm parachute" in chute.triggered and not arm_alts:
                    arm_alts.append(vessel._alt)
                if "Deploy chute" in chute.triggered:
                    deploy_alts.append(vessel._alt)
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
                elif t[0] >= 5.0:
                    vessel._alt = 1_500.0
                    vessel._speed = 80.0
                    vessel._vz = -80.0
                elif t[0] >= 3.0:
                    vessel._alt = 4_000.0
                    vessel._speed = 80.0
                    vessel._vz = -80.0
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(apex_triggered)
        self.assertTrue(any("Arm parachute" in ev for ev in apex_triggered))
        self.assertTrue(all("Deploy chute" not in ev for ev in apex_triggered))
        self.assertTrue(arm_alts)
        self.assertTrue(all(alt > CHUTE_DEPLOY_ALT_M for alt in arm_alts))
        self.assertIn("Arm parachute", chute.triggered)
        self.assertIn("Deploy chute", chute.triggered)
        self.assertTrue(deploy_alts)
        self.assertTrue(all(alt <= CHUTE_DEPLOY_ALT_M for alt in deploy_alts))
        self.assertTrue(all(alt < 4_000.0 for alt in deploy_alts))

    def test_lofted_descent_arms_at_3km(self):
        """chute-deploy-sit: 11-11-37Z 2.9 km still stowed — Arm on vz<0, not only 2 km."""
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        arm_alts: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_918.0
                vessel._speed = 111.0
                vessel._vz = -80.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 0.0
                vessel._flight.dynamic_pressure = 5_748.0
                vessel.orbit.apoapsis_altitude = 34_222.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and "Arm parachute" in chute.triggered:
                arm_alts.append(vessel._alt)
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 5.0
                vessel._vz = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(arm_alts)
        self.assertTrue(all(alt > CHUTE_DEPLOY_ALT_M for alt in arm_alts))
        self.assertIn("Arm parachute", chute.triggered)
        self.assertNotIn("Deploy chute", chute.triggered)

    def test_waiting_lid_still_arms_chute_on_descent(self):
        """flyinghigh-lid: 13-49-58Z wait FlyingHigh, crumbs+thr 1, Arm on descent."""
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        sess = _Session(vessel)
        arm_alts: list[float] = []
        deploy_alts: list[float] = []
        throttles: list[float] = []
        coast_factors: list[int] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 31_080.0
                vessel._speed = 250.0
                vessel._vz = -81.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 0.292
                vessel._flight.dynamic_pressure = 492.0
                vessel.orbit.apoapsis_altitude = 31_227.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                if "Arm parachute" in chute.triggered and not arm_alts:
                    arm_alts.append(vessel._alt)
                    throttles.append(vessel.control.throttle)
                    coast_factors.append(sess.space_center.physics_warp_factor)
                if "Deploy chute" in chute.triggered:
                    deploy_alts.append(vessel._alt)
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
                elif "Arm parachute" in chute.triggered:
                    vessel._alt = 1_500.0
                    vessel._speed = 80.0
                    vessel._vz = -80.0
                    vessel._flight.dynamic_pressure = 1_200.0
            t[0] += dt if dt else 0.01

        from uplink import desk

        prev = (desk.hold, desk.skip_warp, desk.phys_warp)
        desk.hold = False
        desk.skip_warp = False
        desk.phys_warp = None
        try:
            with patch("hop.hop_wants_flying_high", return_value=True):
                with patch("phases._kv", return_value={"hop_apo": "50000"}):
                    result = run_on_vessel(
                        sess,
                        vessel,
                        science_ids=("kerbalism_TELEMETRY",),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=30.0,
                        pulse=1.0,
                    )
        finally:
            desk.hold, desk.skip_warp, desk.phys_warp = prev
        self.assertEqual(result, "recovered")
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))
        self.assertFalse(any("situation cannot pay" in line for line in logs))
        self.assertEqual(thermo.triggered, [])
        self.assertIn("Arm parachute", chute.triggered)
        self.assertIn("Deploy chute", chute.triggered)
        self.assertTrue(arm_alts)
        self.assertTrue(all(alt > CHUTE_DEPLOY_ALT_M for alt in arm_alts))
        self.assertTrue(deploy_alts)
        self.assertTrue(all(alt <= CHUTE_DEPLOY_ALT_M for alt in deploy_alts))
        self.assertTrue(throttles)
        self.assertTrue(all(thr <= 0.05 for thr in throttles))
        self.assertTrue(coast_factors)
        self.assertTrue(all(f == 0 for f in coast_factors))

    def test_shear_aborts_before_crash_ui(self):
        """07-06-08Z dwelt after 1283→270 until crash UI. Gate is hold+abort."""
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([thermo], recoverable=False)
        vessel.mass = 1283.6
        vessel.resources.fuel = 178.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 13_700.0
                vessel._speed = 300.0
                vessel.orbit.apoapsis_altitude = 20_000.0
            elif vessel.situation == "flying" and vessel.mass > 400.0:
                vessel.mass = 270.6
                vessel.resources.fuel = 0.0
            t[0] += dt if dt else 0.01

        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("temperatureScan",),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertIn("shear", str(ctx.exception).lower())
        self.assertFalse(vessel.recovered)
        self.assertTrue(any("shear" in x for x in logs))

    def test_impact_empty_vessel_does_not_abort_shear(self):
        """07-21-05Z 36 parts through apex; parts 0 mass 0 at 412 m is death."""
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([thermo], recoverable=False)
        vessel.mass = 1601.9
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 10_800.0
                vessel._speed = 80.0
                vessel._vz = 20.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 0.0
                vessel.orbit.apoapsis_altitude = 21_500.0
            elif vessel.situation == "flying" and thermo.triggered and vessel.mass > 1.0:
                vessel.mass = 0.0
                vessel.parts.all = []
                vessel._alt = 412.0
                vessel._speed = 91.0
                vessel._vz = -91.0
            t[0] += dt if dt else 0.01

        with patch("hop.go_space_center") as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertIn("recover-probe --space-center", str(ctx.exception))
        self.assertFalse(any("hop shear" in x for x in logs))
        scene.assert_not_called()
        self.assertLess(t[0], 5.0)

    def test_impact_gone_recoverable_recovers(self):
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([thermo], recoverable=False)
        vessel.mass = 1601.9
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 10_800.0
                vessel._speed = 80.0
                vessel._vz = 20.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 0.0
                vessel.orbit.apoapsis_altitude = 21_500.0
            elif vessel.situation == "flying" and thermo.triggered and vessel.mass > 1.0:
                vessel.mass = 0.0
                vessel.parts.all = []
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel._vz = 0.0
                vessel.situation = "landed"
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertFalse(any("hop shear" in x for x in logs))
        self.assertFalse(any("ksc leftover" in x for x in logs))

    def test_total_wreck_aborts_ksc_leftover_not_recover_spin(self):
        """07-50-48Z: parts 0 mass 0 rec=no — ksc leftover, not recover+ec=0+space_center."""
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([thermo], recoverable=False)
        vessel.name = CRAFT
        vessel.mass = 1601.9
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 8_900.0
                vessel._speed = 80.0
                vessel._vz = 20.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 0.0
                vessel.orbit.apoapsis_altitude = 17_145.0
            elif vessel.situation == "flying" and thermo.triggered and vessel.mass > 1.0:
                vessel.mass = 0.0
                vessel.parts.all = []
                vessel.resources.ec = 0.0
                vessel._alt = 73.0
                vessel._speed = 89.0
                vessel._vz = -89.0
                vessel._flight.dynamic_pressure = 0.0
            t[0] += dt if dt else 0.01

        with patch("hop.go_space_center") as scene:
            with patch("hop.run_physics") as physics:
                with self.assertRaises(MissionAbort) as ctx:
                    run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=("temperatureScan",),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=30.0,
                        pulse=1.0,
                    )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertIn("recover-probe --space-center", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        physics.assert_not_called()
        recover_ticks = [line for line in logs if line.startswith("hop recover sit=")]
        self.assertEqual(recover_ticks, [])
        self.assertFalse(any("gate ec=0" in line for line in logs))
        self.assertNotIn("hop crash ui space_center (total wreck)", logs)
        self.assertLess(t[0], 5.0)

    def test_fresh_hangar_starts_flying_card(self):
        """New Flea that lights: leftover-HD skip must not fire."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        thermo = _Mod("Experiment", "temperatureScan")
        drive = _Mod("HardDrive", "")
        drive.fields = {"Data": "empty"}
        vessel = _Vessel([tel], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel, drive]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and tel.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.bound_science_need", return_value={}):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 1)
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertTrue(any("kerbalism_TELEMETRY" in line for line in logs))
        self.assertFalse(any("keep HD" in line for line in logs))

    def test_does_not_recover_on_pad_without_flight(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=True, sit="pre_launch")
        now, sleep, t = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=sleep,
                timeout=3.0,
                pulse=1.0,
            )
        self.assertIn("timeout", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(mod.triggered, [])

    def test_empty_tanks_are_expected(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=False, sit="flying")
        vessel._alt = 5_000.0
        vessel._speed = 40.0
        vessel.resources.fuel = 0.0
        vessel.orbit.apoapsis_altitude = 14_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertEqual(vessel.control.staged, 0)

    def test_ec_zero_recovers_without_down(self):
        """Airborne EC=0 with HD: recover on first recoverable, even if flying."""
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="flying", ec=0.0)
        vessel._alt = 5_000.0
        vessel._speed = 80.0
        vessel.orbit.apoapsis_altitude = 14_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertEqual(vessel.situation, "flying")

    def test_ec_zero_timeout_waits_then_recovers(self):
        """Do not timeout-dump a dead airborne probe; recover when down."""
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="flying", ec=0.0)
        vessel._alt = 4_000.0
        vessel._speed = 40.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            if t[0] >= 4.0 and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            now=now,
            sleep=nap,
            timeout=2.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertGreaterEqual(t[0], 4.0)

    def test_ec_zero_empty_pad_aborts(self):
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=0.0)
        now, sleep, _t = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                now=now,
                sleep=sleep,
                timeout=5.0,
                pulse=1.0,
            )
        self.assertIn("ec=0", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_ec_zero_down_not_recoverable_aborts(self):
        mod = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([mod], recoverable=False, sit="flying", ec=0.0)
        vessel._alt = 3_000.0
        vessel.orbit.apoapsis_altitude = 10_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = False
            t[0] += dt if dt else 0.01

        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                now=now,
                sleep=nap,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_wreck_waits_recoverable(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], recoverable=False, sit="flying")
        vessel._alt = 8_000.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.situation == "flying" and mod.triggered:
                vessel.situation = "wrecked"
                vessel.recoverable = False
            elif vessel.situation == "wrecked":
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("mysteryGoo",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_apo_overshoot_offplan(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 10_000.0
        vessel.orbit.apoapsis_altitude = 55_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        with patch("hop.hop_wants_flying_high", return_value=False):
            with self.assertRaises(OffPlan) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("mysteryGoo",),
                    now=now,
                    sleep=sleep,
                    timeout=5.0,
                    pulse=1.0,
                )
        self.assertIn("apo", str(ctx.exception))
        self.assertIn("FlyingLow", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_flyinghigh_80km_is_not_offplan(self):
        """Valiant loft 80 km is FlyingHigh, under Space 140 km."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 55_000.0
                vessel.orbit.apoapsis_altitude = 80_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "80000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_flyinghigh_toggle_only_at_50km(self):
        """Bound FlyingHigh: do not Toggle at T+1 FlyingLow (~100 m)."""
        from hop import FLYING_LOW_M

        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()
        alts: list[float] = []
        logs: list[str] = []

        def trigger_event(name):
            alts.append(vessel._alt)
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        mod.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 100.0
                vessel.orbit.apoapsis_altitude = 80_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and vessel._alt < FLYING_LOW_M:
                vessel._alt = 50_400.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "splashed"
                vessel._alt = -0.3
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "80000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertEqual(alts, [50_400.0])
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))
        self.assertGreaterEqual(min(alts), FLYING_LOW_M)

    def test_flyinghigh_low_skip_still_toggles_high_trio(self):
        """science-skip-timeout: FlyingLow cannot-pay does not drop High."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 641
        geiger = _Mod("Experiment", "geigerCounter")
        geiger.fields["remaining"] = 0
        vessel = _Vessel([tel], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere_v2", [tel]),
                _Part("GooExperiment", [goo]),
                _Part("kerbalism-geigercounter", [geiger]),
            ]
        )
        vessel.biome = "Shores"
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        alts: list[float] = []

        def _mark(mod, name):
            alts.append(vessel._alt)
            mod.triggered.append(name)
            mod.fields["status"] = "Running"

        tel.trigger_event = lambda name: _mark(tel, name)
        goo.trigger_event = lambda name: _mark(goo, name)
        geiger.trigger_event = lambda name: _mark(geiger, name)

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel.orbit.apoapsis_altitude = 80_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and vessel._alt < FLYING_LOW_M:
                vessel._alt = 54_477.0
                vessel.situation = "sub_orbital"
            elif vessel.situation == "sub_orbital" and (goo.triggered or geiger.triggered):
                vessel.situation = "splashed"
                vessel._alt = -0.3
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        need = {
            "kerbalism_TELEMETRY": ("FlyingHigh@Forest", "Forest"),
            "mysteryGoo": ("FlyingHigh", "global"),
            "geigerCounter": ("FlyingHigh", ""),
        }
        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("hop.bound_science_need", return_value=need):
                with patch("phases._kv", return_value={"hop_apo": "50000"}):
                    result = run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=(
                            "kerbalism_TELEMETRY",
                            "mysteryGoo",
                            "geigerCounter",
                        ),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=30.0,
                        pulse=1.0,
                    )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(tel.triggered, [])
        self.assertEqual(goo.triggered, ["Start Experiment"])
        self.assertEqual(geiger.triggered, ["Start Experiment"])
        self.assertTrue(alts)
        self.assertTrue(all(alt >= FLYING_LOW_M for alt in alts))
        self.assertFalse(
            any(line == "science skip (situation cannot pay)" for line in logs)
        )

    def test_flyinghigh_never_lid_does_not_toggle_crumbs(self):
        """Down below 50 km: no FlyingLow Toggle, no lid abort, no tank dump."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 1400.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 1_549.0
                vessel.orbit.apoapsis_altitude = 1_611.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("temperatureScan",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, [])
        self.assertEqual(vessel.resources.fuel, 1400.0)
        self.assertLessEqual(vessel.control.throttle, 0.05)

    def test_flyinghigh_short_hop_pays_land_leftover(self):
        """Never 50 km: Forest land leftover still pays. Do not abort the lid."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        vessel.biome = "Forest"
        vessel.resources.fuel = 1400.0
        now, sleep, t = _fast_clock()
        sits: list[str] = []

        def trigger_event(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        thermo.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 1_549.0
                vessel.orbit.apoapsis_altitude = 1_611.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            elif vessel.situation == "landed" and thermo.triggered:
                thermo.fields["remaining"] = 0
                thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("tickets.list_tickets", return_value=_LAND_OR_SPLASH):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("kerbalism_TELEMETRY",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["landed"])
        self.assertEqual(vessel.resources.fuel, 1400.0)
        self.assertLessEqual(vessel.control.throttle, 0.05)

    def test_flyinghigh_lid_aborts_after_toggle_sit(self):
        """Reached 50 km with nothing started, then down: lid abort."""
        mod = _Mod("Experiment", "mysteryGoo")
        mod.fields["remaining"] = 0
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("GooExperiment", [mod])])
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 50_400.0
                vessel.orbit.apoapsis_altitude = 55_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("mysteryGoo",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("FlyingHigh lid", str(ctx.exception))
        self.assertEqual(mod.triggered, [])

    def test_flyinghigh_hop_apo_cut_keeps_apo_in_lid(self):
        """flyinghigh-lid: hop_apo 50 km cuts; apo does not run to Space."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 350.0
        now, sleep, t = _fast_clock()
        apos: list[float] = []
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 30_256.0
                vessel._speed = 565.0
                vessel._vz = 564.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 349.8
                vessel.orbit.apoapsis_altitude = 46_344.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                apos.append(vessel.orbit.apoapsis_altitude)
                if vessel.control.throttle > 0.05:
                    vessel.orbit.apoapsis_altitude += 5_000.0
                    vessel._alt = min(vessel._alt + 2_000.0, 50_400.0)
                    vessel.resources.fuel = max(vessel.resources.fuel - 20.0, 1.0)
                elif mod.triggered:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
                else:
                    vessel._alt = max(vessel._alt, 50_400.0)
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(apos)
        self.assertTrue(any(apo >= 50_000.0 for apo in apos))
        self.assertTrue(all(apo < FLYING_HIGH_M for apo in apos))
        self.assertLessEqual(vessel.control.throttle, 0.05)
        self.assertGreater(vessel.resources.fuel, 1.0)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))

    def test_flyinghigh_space_overshoot_cuts_and_toggles(self):
        """flyinghigh-lid: 15-05-30Z apo 163 km OffPlan before Toggle. Cut hop_apo."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 350.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        throttles: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 62_612.0
                vessel._speed = 1_377.0
                vessel._vz = 1_376.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 350.0
                vessel.orbit.apoapsis_altitude = 163_170.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                throttles.append(vessel.control.throttle)
                if mod.triggered:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(throttles)
        self.assertTrue(all(thr <= 0.05 for thr in throttles))
        self.assertGreater(vessel.resources.fuel, 1.0)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertFalse(any("OFFPLAN" in line or "OffPlan" in line for line in logs))

    def test_offplan_apo_lid_honors_expect_apo_max(self):
        """flyinghigh-lid: plan 400 km is the abort, not Space 140 km."""
        from hop_factory import _offplan_apo_lid

        snap = type("S", (), {"atm_depth": 140_000.0})()
        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"expect_apo_max": "400000"}):
                self.assertEqual(_offplan_apo_lid(snap), 400_000.0)
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                self.assertEqual(_offplan_apo_lid(snap), 140_000.0)
            with patch("phases._kv", return_value={"expect_apo_max": "100000"}):
                self.assertEqual(_offplan_apo_lid(snap), 140_000.0)
        with patch("hop.hop_wants_flying_high", return_value=False):
            with patch("phases._kv", return_value={"expect_apo_max": "18000"}):
                self.assertEqual(_offplan_apo_lid(snap), FLYING_LOW_M)
            with patch("phases._kv", return_value={"expect_apo_max": "400000"}):
                self.assertEqual(_offplan_apo_lid(snap), FLYING_LOW_M)

    def test_flyinghigh_expect_apo_max_is_not_space_offplan(self):
        """flyinghigh-lid: 18-59-08Z apo 163 km < plan 400 km. Not Space OffPlan."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 123.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 41_809.0
                vessel._speed = 1_200.0
                vessel._vz = 1_200.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 123.0
                vessel.orbit.apoapsis_altitude = 163_402.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                if vessel._alt < 50_000.0:
                    vessel._alt = 50_400.0
                elif mod.triggered:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch(
                "phases._kv",
                return_value={"hop_apo": "50000", "expect_apo_max": "400000"},
            ):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertFalse(any("OFFPLAN" in line or "OffPlan" in line for line in logs))

    def test_flyinghigh_over_expect_apo_max_is_offplan(self):
        """flyinghigh-lid: apo above Gene expect_apo_max is still OffPlan."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 41_809.0
        vessel.orbit.apoapsis_altitude = 500_001.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch(
                "phases._kv",
                return_value={"hop_apo": "50000", "expect_apo_max": "400000"},
            ):
                with self.assertRaises(OffPlan) as ctx:
                    run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=("temperatureScan",),
                        now=now,
                        sleep=sleep,
                        timeout=5.0,
                        pulse=1.0,
                    )
        self.assertIn("400000", str(ctx.exception))
        self.assertIn("Space", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_flyinghigh_hop_apo_cuts_on_altitude_not_prediction(self):
        """flyinghigh-lid: 15-24-17Z predicted apo at 2.3 km is not the cut."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 1292.0
        now, sleep, t = _fast_clock()
        throttles_low: list[float] = []
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_279.0
                vessel._speed = 200.0
                vessel._vz = -40.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 1292.0
                vessel._flight.dynamic_pressure = 4_572.0
                vessel.orbit.apoapsis_altitude = 51_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                if vessel._alt < 50_000.0:
                    throttles_low.append(vessel.control.throttle)
                    self.assertGreater(vessel.control.throttle, 0.05)
                    vessel._alt = 50_400.0
                    vessel._vz = 200.0
                    vessel._flight.dynamic_pressure = 400.0
                    vessel.orbit.apoapsis_altitude = 80_000.0
                elif mod.triggered:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(throttles_low)
        self.assertTrue(all(thr > 0.05 for thr in throttles_low))
        self.assertLessEqual(vessel.control.throttle, 0.05)
        self.assertGreater(vessel.resources.fuel, 2.0)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))

    def test_high_dwell_sit_1x_after_lid(self):
        """T-438: High dwell is lid-until-down, not a burn. Quiet loft 4×."""
        from hop_factory import _high_dwell_sit
        from physics_warp import apply_sit_warp, want_coast

        self.assertFalse(_high_dwell_sit(reached_lid=False, down=False))
        self.assertTrue(_high_dwell_sit(reached_lid=True, down=False))
        self.assertFalse(_high_dwell_sit(reached_lid=True, down=True))
        quiet = type(
            "S",
            (),
            {
                "alt": 178_000.0,
                "q": 0.0,
                "v_vert": 941.0,
                "chute": "none",
                "in_atmo": False,
            },
        )()
        self.assertTrue(
            want_coast(quiet, left_pad=True, down=False, burning=False)
        )
        self.assertFalse(
            want_coast(quiet, left_pad=True, down=False, burning=True)
        )
        sc = type(
            "SC", (), {"rails_warp_factor": 0, "physics_warp_factor": 0}
        )()
        krpc = type("K", (), {"paused": False})()
        sess = type(
            "Sess",
            (),
            {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
        )()
        last = [""]
        n = apply_sit_warp(
            sess,
            quiet,
            left_pad=True,
            down=False,
            burning=False,
            last=last,
            uplink_rate=4,
        )
        self.assertEqual(n, 3)
        self.assertEqual(sc.physics_warp_factor, 3)
        self.assertEqual(sc.rails_warp_factor, 0)
        self.assertEqual(last[0], "4x")
        n_burn = apply_sit_warp(
            sess,
            quiet,
            left_pad=True,
            down=False,
            burning=True,
            last=last,
            uplink_rate=4,
        )
        self.assertEqual(n_burn, 0)
        self.assertEqual(sc.physics_warp_factor, 0)

    def test_lid_burn_sit_leftover_before_lid(self):
        """far-shear: leftover LF before lid is still burn. Not 4×."""
        from hop_factory import _lid_burn_sit

        wait = type("S", (), {"alt": 904.0, "fuel": 1413.0})()
        lid = type("S", (), {"alt": 50_400.0, "fuel": 1413.0})()
        crumbs = type("S", (), {"alt": 904.0, "fuel": 1.0})()
        with patch("hop.hop_wants_flying_high", return_value=True):
            self.assertTrue(
                _lid_burn_sit(wait, hop_apo=50_000.0, flying_high=True)
            )
            self.assertFalse(
                _lid_burn_sit(lid, hop_apo=50_000.0, flying_high=True)
            )
            self.assertFalse(
                _lid_burn_sit(crumbs, hop_apo=50_000.0, flying_high=True)
            )
            self.assertFalse(
                _lid_burn_sit(wait, hop_apo=50_000.0, flying_high=False)
            )

    def test_lid_vertical_sit_before_lid(self):
        """flyinghigh-lid: 17-50-46Z pitch 25 at 1 km. Hold vertical until lid alt."""
        from hop_factory import _lid_vertical_sit

        wait = type("S", (), {"alt": 904.0})()
        lid = type("S", (), {"alt": 50_400.0})()
        with patch("hop.hop_wants_flying_high", return_value=True):
            self.assertTrue(
                _lid_vertical_sit(wait, hop_apo=50_000.0, flying_high=True)
            )
            self.assertFalse(
                _lid_vertical_sit(lid, hop_apo=50_000.0, flying_high=True)
            )
            self.assertFalse(
                _lid_vertical_sit(
                    wait, hop_apo=50_000.0, flying_high=True, lofted_lid=True
                )
            )
            self.assertFalse(
                _lid_vertical_sit(wait, hop_apo=50_000.0, flying_high=False)
            )

    def test_splash_bind_holds_vertical_until_lid(self):
        """flyinghigh-lid: splash bind does not drop the lid / pitch 25 from pad."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 1400.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        low_sas: list[bool] = []
        low_thr: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 904.0
                vessel._speed = 80.0
                vessel._vz = 70.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 1400.0
                vessel.orbit.apoapsis_altitude = 782.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and vessel._alt < 50_000.0:
                low_sas.append(vessel.control.sas)
                low_thr.append(vessel.control.throttle)
                self.assertGreater(vessel.control.throttle, 0.05)
                self.assertTrue(vessel.control.sas)
                self.assertFalse(any("pitch 25" in line for line in logs))
                vessel._alt = 50_400.0
                vessel._vz = 200.0
                vessel.orbit.apoapsis_altitude = 80_000.0
            elif vessel.situation == "flying" and vessel._alt >= 50_000.0:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 5.0
                vessel._vz = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=False):
            with patch("hop_factory._inland_high_sit", return_value=True):
                with patch("phases._kv", return_value={"hop_apo": "50000"}):
                    result = run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=("temperatureScan",),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=30.0,
                        pulse=1.0,
                    )
        self.assertEqual(result, "recovered")
        self.assertTrue(low_sas)
        self.assertTrue(all(low_sas))
        self.assertTrue(all(thr > 0.05 for thr in low_thr))
        self.assertTrue(any("hold vertical until lid 50000" in line for line in logs))
        self.assertFalse(any("pitch 25" in line for line in logs))

    def test_hold_lid_throttle_and_sas_before_lid(self):
        """flyinghigh-lid: 18-15-43Z thr 0 at MET 8.6 with leftover LF. Hold 1 + SAS."""
        from hop_factory import _hold_lid

        vessel = _Vessel([])
        vessel.control.throttle = 0.0
        vessel.control.sas = False
        wait = type("S", (), {"alt": 388.7, "fuel": 1430.4, "situation": "flying"})()
        lid = type("S", (), {"alt": 50_400.0, "fuel": 1430.4, "situation": "flying"})()
        with patch("hop.hop_wants_flying_high", return_value=True):
            self.assertTrue(
                _hold_lid(vessel, wait, hop_apo=50_000.0, flying_high=True)
            )
            self.assertEqual(vessel.control.throttle, 1.0)
            self.assertTrue(vessel.control.sas)
            vessel.control.throttle = 0.0
            vessel.control.sas = False
            self.assertFalse(
                _hold_lid(vessel, lid, hop_apo=50_000.0, flying_high=True)
            )
            self.assertEqual(vessel.control.throttle, 0.0)
            self.assertFalse(vessel.control.sas)
            self.assertFalse(
                _hold_lid(vessel, wait, hop_apo=50_000.0, flying_high=False)
            )

    def test_flyinghigh_holds_vertical_until_lid(self):
        """flyinghigh-lid: 17-50-46Z apo 782. Do not pitch 25 while apo is hundreds of m."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 1400.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        low_sas: list[bool] = []
        low_thr: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 904.0
                vessel._speed = 80.0
                vessel._vz = 70.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 1400.0
                vessel.orbit.apoapsis_altitude = 782.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and vessel._alt < 50_000.0:
                low_sas.append(vessel.control.sas)
                low_thr.append(vessel.control.throttle)
                self.assertGreater(vessel.control.throttle, 0.05)
                self.assertTrue(vessel.control.sas)
                self.assertFalse(vessel.auto_pilot.engaged)
                self.assertFalse(any("pitch 25" in line for line in logs))
                vessel._alt = 50_400.0
                vessel._vz = 200.0
                vessel.orbit.apoapsis_altitude = 80_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 5.0
                vessel._vz = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(low_sas)
        self.assertTrue(all(low_sas))
        self.assertTrue(all(thr > 0.05 for thr in low_thr))
        self.assertNotIn(
            inland_direction(INLAND_PITCH_DEG),
            [vessel.auto_pilot.target_direction],
        )
        self.assertTrue(any("hold vertical until lid" in line for line in logs))
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_flyinghigh_wait_is_loft_not_dwell_at_1km(self):
        """flyinghigh-lid: 17-59-29Z wait at light sheared. Loft, do not throttle 0."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 1417.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        low_thr: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 491.6
                vessel._speed = 84.6
                vessel._vz = 84.6
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 1417.0
                vessel._flight.dynamic_pressure = 4_501.8
                vessel.orbit.apoapsis_altitude = 879.8
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and vessel._alt < 50_000.0:
                low_thr.append(vessel.control.throttle)
                self.assertGreater(vessel.control.throttle, 0.05)
                self.assertFalse(any("science wait FlyingHigh" in line for line in logs))
                vessel._alt = 50_400.0
                vessel._vz = 200.0
                vessel._flight.dynamic_pressure = 400.0
                vessel.orbit.apoapsis_altitude = 80_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 5.0
                vessel._vz = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(low_thr)
        self.assertTrue(all(thr > 0.05 for thr in low_thr))
        self.assertGreater(vessel.resources.fuel, 2.0)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))
        self.assertFalse(any("situation cannot pay" in line for line in logs))

    def test_lid_hold_restores_throttle_if_cut_below_lid(self):
        """flyinghigh-lid: 18-15-43Z MET 8.6 thr 0 fuel 1431. Restore hold each pulse."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel.resources.fuel = 1431.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        low_n = [0]
        low_thr: list[float] = []
        low_sas: list[bool] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 421.8
                vessel._speed = 76.6
                vessel._vz = 76.6
                vessel.control.throttle = 1.0
                vessel.control.sas = True
                vessel.resources.fuel = 1431.0
                vessel._flight.dynamic_pressure = 3_700.0
                vessel.orbit.apoapsis_altitude = 738.6
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and vessel._alt < 50_000.0:
                low_thr.append(vessel.control.throttle)
                low_sas.append(vessel.control.sas)
                self.assertGreater(vessel.control.throttle, 0.05)
                self.assertTrue(vessel.control.sas)
                self.assertFalse(vessel.auto_pilot.engaged)
                self.assertFalse(any("pitch 25" in line for line in logs))
                low_n[0] += 1
                if low_n[0] < 5:
                    vessel.control.throttle = 0.0
                    vessel.control.sas = False
                    vessel.resources.fuel = 1430.4
                else:
                    vessel._alt = 50_400.0
                    vessel._vz = 200.0
                    vessel._flight.dynamic_pressure = 400.0
                    vessel.orbit.apoapsis_altitude = 80_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 5.0
                vessel._vz = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertGreaterEqual(low_n[0], 5)
        self.assertTrue(all(thr > 0.05 for thr in low_thr))
        self.assertTrue(all(low_sas))
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_flyinghigh_wait_burn_does_not_arm_below_lid(self):
        """flyinghigh-lid: 15-44-16Z silk at 2 km wait-burn. Arm after lid or burnout."""
        from hop_factory import _chute_arm_now, _chute_deploy_now

        wait = type(
            "S",
            (),
            {"v_vert": -1.276, "alt": 2_348.88, "pitch": 80.414, "chute": "stowed"},
        )()
        climb = type(
            "S",
            (),
            {"v_vert": 148.283, "alt": 1_198.017, "pitch": 89.159, "chute": "stowed"},
        )()
        lid = type(
            "S",
            (),
            {"v_vert": -40.0, "alt": 50_400.0, "pitch": 65.0, "chute": "stowed"},
        )()
        apex = type(
            "S",
            (),
            {"v_vert": -10.278, "alt": 796.895, "pitch": 80.504, "chute": "stowed"},
        )()
        silk = type(
            "S",
            (),
            {"v_vert": -80.0, "alt": 1_500.0, "pitch": -14.0, "chute": "stowed"},
        )()
        kw = dict(hop_apo=50_000.0, crumbs=False, apo_cut=False)
        with patch("hop.hop_wants_flying_high", return_value=True):
            self.assertFalse(
                _chute_arm_now(climb, flying_high=True, **kw)
            )
            self.assertFalse(
                _chute_arm_now(wait, flying_high=True, **kw)
            )
            self.assertTrue(
                _chute_arm_now(
                    wait,
                    hop_apo=50_000.0,
                    flying_high=True,
                    crumbs=True,
                    apo_cut=False,
                )
            )
            self.assertTrue(
                _chute_arm_now(
                    lid,
                    hop_apo=50_000.0,
                    flying_high=True,
                    crumbs=False,
                    apo_cut=True,
                )
            )
            self.assertTrue(
                _chute_arm_now(wait, flying_high=False, **kw)
            )
            self.assertFalse(
                _chute_deploy_now(climb, flying_high=True, **kw)
            )
            self.assertFalse(
                _chute_deploy_now(wait, flying_high=True, **kw)
            )
            self.assertFalse(
                _chute_deploy_now(apex, flying_high=True, **kw)
            )
            self.assertTrue(
                _chute_deploy_now(apex, flying_high=False, **kw)
            )
            self.assertTrue(
                _chute_deploy_now(
                    apex,
                    hop_apo=50_000.0,
                    flying_high=True,
                    crumbs=True,
                    apo_cut=False,
                )
            )
            self.assertTrue(
                _chute_deploy_now(
                    silk,
                    hop_apo=50_000.0,
                    flying_high=True,
                    crumbs=False,
                    apo_cut=True,
                )
            )

        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        vessel.resources.fuel = 1317.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        arm_alts: list[float] = []
        low_throttles: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 1_198.0
                vessel._speed = 148.0
                vessel._vz = 148.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 1317.0
                vessel._flight.dynamic_pressure = 12_513.0
                vessel.orbit.apoapsis_altitude = 2_357.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                if "Arm parachute" in chute.triggered and not arm_alts:
                    arm_alts.append(vessel._alt)
                if vessel._alt < 50_000.0:
                    low_throttles.append(vessel.control.throttle)
                    self.assertGreater(vessel.control.throttle, 0.05)
                    self.assertNotIn("Arm parachute", chute.triggered)
                    if vessel._vz > 0.0:
                        vessel._alt = 2_348.0
                        vessel._vz = -1.3
                        vessel._flight.dynamic_pressure = 3_859.0
                    else:
                        vessel._alt = 50_400.0
                        vessel._vz = -40.0
                        vessel._flight.dynamic_pressure = 400.0
                        vessel.orbit.apoapsis_altitude = 80_000.0
                elif thermo.triggered or "Arm parachute" in chute.triggered:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(low_throttles)
        self.assertTrue(all(thr > 0.05 for thr in low_throttles))
        self.assertIn("Arm parachute", chute.triggered)
        self.assertTrue(arm_alts)
        self.assertTrue(all(alt >= 50_000.0 for alt in arm_alts))
        self.assertFalse(any("science wait FlyingHigh" in line for line in logs))

    def test_flyinghigh_wait_burn_does_not_deploy_below_lid(self):
        """silk-while-burn: FlyingHigh wait at ≤2 km is not Deploy (Arms inside)."""
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        vessel.resources.fuel = 1424.0
        now, sleep, t = _fast_clock()
        pulses = [0]

        def nap(dt):
            pulses[0] += 1
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 796.9
                vessel._speed = 10.0
                vessel._vz = -10.3
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 1424.0
                vessel._flight.dynamic_pressure = 34.0
                vessel.orbit.apoapsis_altitude = 800.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                self.assertNotIn("Arm parachute", chute.triggered)
                self.assertNotIn("Deploy chute", chute.triggered)
                if pulses[0] >= 4:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 5.0
                    vessel._vz = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("phases._kv", return_value={"hop_apo": "50000"}):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertNotIn("Arm parachute", chute.triggered)
        self.assertNotIn("Deploy chute", chute.triggered)

    def test_hammer_18km_overshoot_is_not_offplan(self):
        """SRB cannot hold. 18.8 km is still FlyingLow (< 50 km)."""
        from hop import FLYING_LOW_M

        self.assertGreater(FLYING_LOW_M, 18_858.0)
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 4_800.0
                vessel.orbit.apoapsis_altitude = 18_858.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)

    def test_no_science_aborts(self):
        """Modules present but none start — empty card still aborts."""
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 2_000.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        now, sleep, _t = _fast_clock()
        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                now=now,
                sleep=sleep,
                timeout=5.0,
                pulse=1.0,
            )
        self.assertIn("no science", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(mod.triggered, [])

    def test_unpaid_remaining_skips_then_recovers(self):
        """Sample rem=0 cannot pay — do not Toggle, recover HD."""
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 0
        vessel = _Vessel([goo], recoverable=False)
        vessel.parts = _Parts([_Part("GooExperiment", [goo])])
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.bound_science_need", return_value={}):
            with patch("hop.hop_landed_science_ids", return_value=()):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("mysteryGoo",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(goo.triggered, [])

    def test_srflanded_starts_after_touchdown(self):
        """Bound SrfLanded must not Toggle airborne; start when landed."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 114
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        sits: list[str] = []

        def trigger_event(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        thermo.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            elif vessel.situation == "landed" and thermo.triggered:
                thermo.fields["remaining"] = 0
                thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch(
                "hop.hop_landed_science_ids", return_value=("temperatureScan",)
            ):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["landed"])

    def test_landed_file_rem_zero_holds_until_rem_drops(self):
        """hold-ground-card: leftover 2HOT rem=0 on Toggle is not dwell-done."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        rem_seen: list[float] = []

        def trigger_event(name):
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        thermo.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel._speed = 0.0
                vessel.recoverable = True
            elif vessel.situation == "landed" and thermo.triggered:
                rem_seen.append(float(thermo.fields["remaining"]))
                if thermo.fields["remaining"] == 0:
                    thermo.fields["remaining"] = 83
                elif thermo.fields["remaining"] == 83:
                    thermo.fields["remaining"] = 0
                    thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch(
                "hop.hop_landed_science_ids", return_value=("temperatureScan",)
            ):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertIn(83.0, rem_seen)

    def test_airborne_telemetry_rem_zero_starts_landed_thermo(self):
        """hold-ground-card: airborne TELEMETRY rem=0 does not recover before SrfLanded leftover."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 6
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        vessel = _Vessel([tel], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreOcto.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        sits: list[str] = []
        flying_rec = [False]

        def trigger_tel(name):
            tel.triggered.append(name)
            tel.fields["status"] = "Running"

        def trigger_thermo(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        tel.trigger_event = trigger_tel
        thermo.trigger_event = trigger_thermo

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                if tel.triggered:
                    tel.fields["remaining"] = 0
                    tel.fields["status"] = "Done"
                    vessel.recoverable = True
                    flying_rec[0] = True
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 0.0
            elif vessel.situation == "landed" and thermo.triggered:
                if thermo.fields["remaining"] == 0:
                    thermo.fields["remaining"] = 76
                else:
                    thermo.fields["remaining"] = 0
                    thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch(
                "hop.hop_landed_science_ids", return_value=("temperatureScan",)
            ):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(flying_rec[0])
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["landed"])

    def test_srflanded_ticket_starts_after_airborne_telemetry(self):
        """T-077 SrfLanded@Forest leftover Toggles after TELEMETRY rem=0; T-313 splash does not pin."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 6
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        vessel = _Vessel([tel], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreOcto.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        sits: list[str] = []

        def trigger_tel(name):
            tel.triggered.append(name)
            tel.fields["status"] = "Running"

        def trigger_thermo(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        tel.trigger_event = trigger_tel
        thermo.trigger_event = trigger_thermo

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                if tel.triggered:
                    tel.fields["remaining"] = 0
                    tel.fields["status"] = "Done"
                    vessel.recoverable = True
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 0.0
            elif vessel.situation == "landed" and thermo.triggered:
                if thermo.fields["remaining"] == 0:
                    thermo.fields["remaining"] = 76
                else:
                    thermo.fields["remaining"] = 0
                    thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        with patch("tickets.list_tickets", return_value=_LAND_AND_SPLASH_THERMO):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["landed"])

    def test_hold_ground_card_file_rem_zero_is_done(self):
        """hold-ground-card: TELEMETRY rem=0 transmitted is not a splash dwell."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["status"] = "Running"
        tel.fields["remaining"] = 0
        vessel = _Vessel([tel])
        vessel.parts = _Parts([_Part("probeCoreOcto.v2", [tel])])
        snap = type("S", (), {"situation": "splashed", "wreck": False})()
        ids = ("kerbalism_TELEMETRY",)
        self.assertFalse(_hold_ground_card(vessel, ["kerbalism_TELEMETRY"], ids, snap))
        tel.fields["remaining"] = 6
        self.assertTrue(_hold_ground_card(vessel, ["kerbalism_TELEMETRY"], ids, snap))
        land = type("S", (), {"situation": "landed", "wreck": False})()
        tel.fields["remaining"] = 0
        self.assertFalse(_hold_ground_card(vessel, ["kerbalism_TELEMETRY"], ids, land))

    def test_hold_ground_card_idle_leftover_after_airborne_dwell(self):
        """hold-ground-card: airborne goo rem=0 is not splash leftover done."""
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 0
        goo.fields["status"] = "Done"
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        baro = _Mod("Experiment", "barometerScan")
        baro.fields["remaining"] = 0
        vessel = _Vessel([goo], sit="splashed")
        vessel.parts = _Parts(
            [
                _Part("GooExperiment", [goo]),
                _Part("probeCoreSphere.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
                _Part("sensorBarometer", [baro]),
            ]
        )
        vessel.biome = "Water"
        snap = type("S", (), {"situation": "splashed", "wreck": False, "biome": "Water"})()
        leftover = ("kerbalism_TELEMETRY", "temperatureScan", "barometerScan")
        with patch("hop.hop_landed_science_ids", return_value=leftover):
            self.assertTrue(
                _hold_ground_card(vessel, ["mysteryGoo"], leftover, snap)
            )
        tel.fields["status"] = "Running"
        tel.fields["remaining"] = 6
        with patch("hop.hop_landed_science_ids", return_value=leftover):
            self.assertTrue(
                _hold_ground_card(
                    vessel, ["mysteryGoo", "kerbalism_TELEMETRY"], leftover, snap
                )
            )

    def test_airborne_cannot_pay_dwell_then_splash_leftover(self):
        """hold-ground-card: goo+geiger dwell then Toggle splash leftover."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        baro = _Mod("Experiment", "barometerScan")
        baro.fields["remaining"] = 0
        geiger = _Mod("Experiment", "geigerCounter")
        geiger.fields["remaining"] = 6
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 1.0
        vessel = _Vessel([goo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
                _Part("sensorBarometer", [baro]),
                _Part("kerbalism-geigercounter", [geiger]),
                _Part("GooExperiment", [goo]),
            ]
        )
        vessel.biome = "Shores"
        now, sleep, t = _fast_clock()
        sits: list[str] = []
        logs: list[str] = []

        def bind(mod):
            def trigger_event(name):
                sits.append(vessel.situation)
                mod.triggered.append(name)
                mod.fields["status"] = "Running"

            mod.trigger_event = trigger_event

        for mod in (tel, thermo, baro, geiger, goo):
            bind(mod)
        phase = ["pad"]

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 54_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 80_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.biome = "Shores"
                vessel.resources.fuel = 0.2
                vessel.control.throttle = 0.0
                phase[0] = "coast"
            elif vessel.situation == "flying" and phase[0] == "coast":
                if geiger.triggered:
                    geiger.fields["remaining"] = 0
                    geiger.fields["status"] = "Done"
                if goo.triggered:
                    goo.fields["remaining"] = 0
                    goo.fields["status"] = "Done"
                vessel._alt = 6.0
                vessel.situation = "splashed"
                vessel.biome = "Water"
                vessel._speed = 5.0
                vessel.recoverable = True
                phase[0] = "splash"
            elif vessel.situation == "splashed":
                for mod in (tel, thermo, baro):
                    if mod.triggered:
                        mod.fields["remaining"] = 0
                        mod.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        tickets = (
            {
                "id": "T-028",
                "type": "science",
                "payload": {
                    "experiment_id": "kerbalism_TELEMETRY",
                    "situation": "SrfSplashed@Water",
                    "biome": "Water",
                    "seq": 0,
                },
            },
            {
                "id": "T-422",
                "type": "science",
                "payload": {
                    "experiment_id": "temperatureScan",
                    "situation": "SrfSplashed@Water",
                    "biome": "Water",
                    "seq": 1,
                },
            },
            {
                "id": "T-423",
                "type": "science",
                "payload": {
                    "experiment_id": "barometerScan",
                    "situation": "SrfSplashed@Water",
                    "biome": "Water",
                    "seq": 2,
                },
            },
        )
        with patch("hop.hop_wants_flying_high", return_value=True):
            with patch("hop_factory._inland_high_sit", return_value=True):
                with patch("tickets.list_tickets", return_value=tickets):
                    result = run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=(
                            "barometerScan",
                            "geigerCounter",
                            "mysteryGoo",
                        ),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=30.0,
                        pulse=1.0,
                    )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(geiger.triggered, ["Start Experiment"])
        self.assertEqual(goo.triggered, ["Start Experiment"])
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(baro.triggered, ["Start Experiment"])
        self.assertIn("splashed", sits)
        self.assertTrue(any("cannot pay" in line for line in logs))
        self.assertTrue(
            any("kerbalism_TELEMETRY" in line and "science start" in line for line in logs)
            or tel.triggered
        )

    def test_leftover_sit_down_toggles_unmatched_ids(self):
        """hold-ground-card: leftover still Toggles when down if matching emptied."""
        from hop_factory import _leftover_sit

        self.assertTrue(_leftover_sit(down=True, live_sit="flying"))
        self.assertTrue(_leftover_sit(down=False, live_sit="splashed"))
        self.assertFalse(_leftover_sit(down=False, live_sit="flying"))
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 1.0
        vessel = _Vessel([goo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        vessel.biome = "Shores"
        now, sleep, t = _fast_clock()
        sits: list[str] = []
        logs: list[str] = []

        def bind(mod):
            def trigger_event(name):
                sits.append(vessel.situation)
                mod.triggered.append(name)
                mod.fields["status"] = "Running"

            mod.trigger_event = trigger_event

        bind(tel)
        bind(goo)

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.biome = "Shores"
                vessel.resources.fuel = 0.2
                vessel.control.throttle = 0.0
            elif vessel.situation == "flying" and goo.triggered:
                goo.fields["remaining"] = 0
                goo.fields["status"] = "Done"
                vessel.situation = "splashed"
                vessel.biome = "Water"
                vessel._alt = 6.0
                vessel._speed = 5.0
                vessel.recoverable = True
            elif vessel.situation == "splashed" and tel.triggered:
                tel.fields["remaining"] = 0
                tel.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        def landed_ids(live_sit="", live_biome=""):
            if live_sit or live_biome:
                return ()
            return ("kerbalism_TELEMETRY",)

        need = {
            "kerbalism_TELEMETRY": ("SrfSplashed@Water", "Water"),
            "mysteryGoo": ("", ""),
        }
        with patch("hop.bound_science_need", return_value=need):
            with patch("hop.hop_landed_science_ids", side_effect=landed_ids):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "mysteryGoo"),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(goo.triggered, ["Start Experiment"])
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertIn("splashed", sits)
        self.assertTrue(any("cannot pay" in line for line in logs))

    def test_splash_telemetry_rem_zero_recovers(self):
        """hold-ground-card: splash file rem=0 still running recovers, no uplink abort."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 6
        vessel = _Vessel([tel], recoverable=False)
        vessel.parts = _Parts([_Part("probeCoreOcto.v2", [tel])])
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        sits: list[str] = []

        def trigger_event(name):
            sits.append(vessel.situation)
            tel.triggered.append(name)
            tel.fields["status"] = "Running"

        tel.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "splashed"
                vessel._alt = 0.0
                vessel._speed = 0.0
                vessel.recoverable = True
            elif vessel.situation == "splashed" and tel.triggered:
                tel.fields["remaining"] = 0
            t[0] += dt if dt else 0.01

        need = {"kerbalism_TELEMETRY": ("SrfSplashed@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch(
                "hop.hop_landed_science_ids",
                return_value=("kerbalism_TELEMETRY",),
            ):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("kerbalism_TELEMETRY",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["splashed"])

    def test_srfsplashed_thermo_rem_zero_starts(self):
        """Unstarted 2HOT rem=0 is file duration; splash still Toggles."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 0
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        sits: list[str] = []

        def trigger_event(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        thermo.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "splashed"
                vessel._alt = 0.0
                vessel._speed = 0.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfSplashed@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch(
                "hop.hop_landed_science_ids",
                return_value=("temperatureScan",),
            ):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["splashed"])

    def test_airborne_cannot_pay_skip_once_then_landed(self):
        """science-skip-timeout: airborne skip is not a dwell; SrfLanded after lofted+down."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        sits: list[str] = []
        air_n = [0]

        def trigger_event(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        thermo.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                air_n[0] += 1
                if air_n[0] >= 6:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 0.0
                    vessel.recoverable = True
            elif vessel.situation == "landed" and thermo.triggered:
                thermo.fields["remaining"] = 0
                thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch(
                "hop.hop_landed_science_ids", return_value=("temperatureScan",)
            ):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        skips = [line for line in logs if "situation cannot pay" in line]
        self.assertEqual(skips, ["science skip (situation cannot pay)"])
        self.assertGreaterEqual(air_n[0], 6)
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["landed"])
        self.assertFalse(any("FlyingHigh" in line for line in logs))

    def test_timeout_flying_cannot_pay_is_ksc_leftover(self):
        """science-skip-timeout: flying leftover at budget recovers or ksc leftover."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        vessel = _Vessel([thermo], recoverable=False)
        vessel.name = CRAFT
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 525.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch("hop.hop_landed_science_ids", return_value=("temperatureScan",)):
                with self.assertRaises(MissionAbort) as ctx:
                    run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=("temperatureScan",),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=3.0,
                        pulse=1.0,
                    )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertIn("timeout", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(thermo.triggered, [])
        skips = [line for line in logs if "situation cannot pay" in line]
        self.assertEqual(skips, ["science skip (situation cannot pay)"])
        self.assertTrue(any(line.startswith("hop timeout") for line in logs))

    def test_timeout_flying_recoverable_recovers(self):
        """science-skip-timeout: budget while flying recoverable takes the HD."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts([_Part("sensorThermometer", [thermo])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 525.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying" and t[0] >= 2.5:
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        with patch("hop.bound_science_need", return_value=need):
            with patch("hop.hop_landed_science_ids", return_value=("temperatureScan",)):
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=8.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(thermo.triggered, [])
        skips = [line for line in logs if "situation cannot pay" in line]
        self.assertEqual(skips, ["science skip (situation cannot pay)"])

    def test_airborne_skip_coasts_chutes_then_landed_ids(self):
        """science-skip-timeout: skip is not a 600 s wait; loft, coast, chute, land leftover."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        sits: list[str] = []
        air_n = [0]
        flying_hop_down = [False]
        sess = _Session(vessel)
        sess.space_center.paused = True
        sess.conn.krpc.paused = True
        from uplink import desk

        prev_desk = (desk.hold, desk.skip_warp, desk.phys_warp)
        desk.hold = False
        desk.skip_warp = False
        desk.phys_warp = None

        def trigger_event(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        thermo.trigger_event = trigger_event

        def nap(dt):
            if vessel.situation == "flying" and any(
                line.startswith("hop down") for line in logs
            ):
                flying_hop_down[0] = True
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._vz = 40.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.resources.fuel = 200.0
                vessel.met = 8.0
            elif vessel.situation == "flying":
                air_n[0] += 1
                vessel.met = 8.0 + t[0]
                if air_n[0] == 2:
                    vessel.recoverable = True
                    vessel.resources.fuel = 0.0
                    vessel.control.throttle = 0.0
                    vessel._alt = 41_884.0
                    vessel._vz = 40.0
                    vessel.orbit.apoapsis_altitude = 49_000.0
                    vessel._flight.dynamic_pressure = 400.0
                elif air_n[0] == 4:
                    vessel.recoverable = False
                    vessel.resources.fuel = 0.0
                    vessel.control.throttle = 0.0
                    vessel._alt = 1_500.0
                    vessel._vz = -40.0
                    vessel._speed = 80.0
                elif air_n[0] >= 6:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._vz = 0.0
                    vessel._speed = 5.0
                    vessel.recoverable = True
            elif vessel.situation == "landed" and thermo.triggered:
                thermo.fields["remaining"] = 0
                thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        try:
            with patch("hop.bound_science_need", return_value=need):
                with patch(
                    "hop.hop_landed_science_ids",
                    return_value=("temperatureScan",),
                ):
                    with patch("hop.hop_wants_flying_high", return_value=False):
                        result = run_on_vessel(
                            sess,
                            vessel,
                            science_ids=("temperatureScan",),
                            on_log=logs.append,
                            now=now,
                            sleep=nap,
                            timeout=30.0,
                            pulse=1.0,
                        )
        finally:
            desk.hold, desk.skip_warp, desk.phys_warp = prev_desk

        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        skips = [line for line in logs if "situation cannot pay" in line]
        self.assertEqual(skips, ["science skip (situation cannot pay)"])
        self.assertTrue(any("hop coast physics 4x rails=0" in x for x in logs))
        self.assertIn("Arm parachute", chute.triggered)
        self.assertIn("Deploy chute", chute.triggered)
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["landed"])
        self.assertTrue(any("hop down" in line for line in logs))
        self.assertFalse(flying_hop_down[0])
        self.assertFalse(any(line.startswith("hop timeout") for line in logs))
        self.assertFalse(sess.space_center.paused)
        self.assertFalse(sess.conn.krpc.paused)

    def test_airborne_skip_47km_coasts_then_chute_landed_ids(self):
        """science-skip-timeout: 47 km fuel-0 still coasts 4×, chute ≤2 km, land leftover."""
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        sits: list[str] = []
        air_n = [0]
        flying_hop_down = [False]
        high_warp: list[int] = []
        deploy_alts: list[float] = []
        sess = _Session(vessel)
        sess.space_center.paused = True
        sess.conn.krpc.paused = True
        from uplink import desk

        prev_desk = (desk.hold, desk.skip_warp, desk.phys_warp)
        desk.hold = False
        desk.skip_warp = False
        desk.phys_warp = None

        def trigger_event(name):
            sits.append(vessel.situation)
            thermo.triggered.append(name)
            thermo.fields["status"] = "Running"

        thermo.trigger_event = trigger_event

        def nap(dt):
            if vessel.situation == "flying" and any(
                line.startswith("hop down") for line in logs
            ):
                flying_hop_down[0] = True
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._vz = 40.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.resources.fuel = 200.0
                vessel.met = 8.0
            elif vessel.situation == "flying":
                air_n[0] += 1
                vessel.met = 8.0 + t[0]
                if air_n[0] == 1:
                    vessel.recoverable = False
                    vessel.resources.fuel = 0.0
                    vessel.control.throttle = 0.0
                    vessel._alt = 41_884.0
                    vessel._vz = 368.0
                    vessel._speed = 500.0
                    vessel.orbit.apoapsis_altitude = 49_000.0
                    vessel._flight.dynamic_pressure = 400.0
                elif air_n[0] < 8:
                    high_warp.append(sess.space_center.physics_warp_factor)
                    self.assertFalse(sess.space_center.paused)
                    self.assertFalse(sess.conn.krpc.paused)
                    self.assertNotIn("Deploy chute", chute.triggered)
                    self.assertFalse(flying_hop_down[0])
                    vessel.recoverable = False
                    vessel.resources.fuel = 0.033
                    vessel.control.throttle = 0.0
                    vessel._alt = 41_884.0
                    vessel._vz = 368.0
                    vessel._speed = 500.0
                    vessel.orbit.apoapsis_altitude = 49_000.0
                    vessel._flight.dynamic_pressure = 400.0
                elif air_n[0] < 10:
                    vessel.recoverable = False
                    vessel.resources.fuel = 0.0
                    vessel.control.throttle = 0.0
                    vessel._alt = 1_500.0
                    vessel._vz = -40.0
                    vessel._speed = 80.0
                    vessel.orbit.apoapsis_altitude = 49_000.0
                    vessel._flight.dynamic_pressure = 1_200.0
                    if "Deploy chute" in chute.triggered:
                        deploy_alts.append(vessel._alt)
                else:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._vz = 0.0
                    vessel._speed = 5.0
                    vessel.recoverable = True
                if vessel.situation == "flying":
                    sess.space_center.paused = True
                    sess.conn.krpc.paused = True
            elif vessel.situation == "landed" and thermo.triggered:
                thermo.fields["remaining"] = 0
                thermo.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        need = {"temperatureScan": ("SrfLanded@Forest", "Forest")}
        try:
            with patch("hop.bound_science_need", return_value=need):
                with patch(
                    "hop.hop_landed_science_ids",
                    return_value=("temperatureScan",),
                ):
                    with patch("hop.hop_wants_flying_high", return_value=False):
                        result = run_on_vessel(
                            sess,
                            vessel,
                            science_ids=("temperatureScan",),
                            on_log=logs.append,
                            now=now,
                            sleep=nap,
                            timeout=30.0,
                            pulse=1.0,
                        )
        finally:
            desk.hold, desk.skip_warp, desk.phys_warp = prev_desk

        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        skips = [line for line in logs if "situation cannot pay" in line]
        self.assertEqual(skips, ["science skip (situation cannot pay)"])
        self.assertTrue(any("hop coast physics 4x rails=0" in x for x in logs))
        self.assertTrue(high_warp)
        self.assertTrue(all(w == 3 for w in high_warp))
        self.assertIn("Arm parachute", chute.triggered)
        self.assertIn("Deploy chute", chute.triggered)
        self.assertTrue(deploy_alts)
        self.assertTrue(all(alt <= CHUTE_DEPLOY_ALT_M for alt in deploy_alts))
        self.assertEqual(thermo.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["landed"])
        self.assertTrue(any("hop down" in line for line in logs))
        self.assertFalse(flying_hop_down[0])
        self.assertFalse(any(line.startswith("hop timeout") for line in logs))

    def test_srfsplashed_starts_splash_telem_not_landed_seq(self):
        """18-10-57Z splash leftover T-288, not first-seq SrfLanded T-287."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        vessel = _Vessel([tel], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("probeCoreOcto.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        sits: list[str] = []

        def trigger_event(name):
            sits.append(vessel.situation)
            tel.triggered.append(name)
            tel.fields["status"] = "Running"

        tel.trigger_event = trigger_event

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "splashed"
                vessel._alt = 6.0
                vessel._speed = 5.0
                vessel.recoverable = True
            elif vessel.situation == "splashed" and tel.triggered:
                tel.fields["remaining"] = 0
                tel.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        with patch("tickets.list_tickets", return_value=_LAND_OR_SPLASH):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("temperatureScan", "kerbalism_TELEMETRY"),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["splashed"])
        self.assertEqual(thermo.triggered, [])

    def test_airborne_goo_still_starts_splash_leftover(self):
        """Goo airborne must not skip splash leftover (18-10-57Z / T-307 gate)."""
        goo = _Mod("Experiment", "mysteryGoo")
        goo.fields["remaining"] = 114
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        tel.fields["remaining"] = 0
        thermo = _Mod("Experiment", "temperatureScan")
        thermo.fields["remaining"] = 83
        vessel = _Vessel([goo], recoverable=False)
        vessel.parts = _Parts(
            [
                _Part("GooExperiment", [goo]),
                _Part("probeCoreOcto.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        vessel.biome = "Forest"
        now, sleep, t = _fast_clock()
        sits: list[str] = []

        def trigger_tel(name):
            sits.append(vessel.situation)
            tel.triggered.append(name)
            tel.fields["status"] = "Running"

        tel.trigger_event = trigger_tel

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
            elif vessel.situation == "flying":
                vessel.situation = "splashed"
                vessel._alt = 6.0
                vessel._speed = 5.0
                vessel.recoverable = True
            elif vessel.situation == "splashed":
                if goo.triggered:
                    goo.fields["remaining"] = 0
                    goo.fields["status"] = "Done"
                if tel.triggered:
                    tel.fields["remaining"] = 0
                    tel.fields["status"] = "Done"
            t[0] += dt if dt else 0.01

        with patch("tickets.list_tickets", return_value=_LAND_OR_SPLASH):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=(
                    "temperatureScan",
                    "kerbalism_TELEMETRY",
                    "mysteryGoo",
                ),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(goo.triggered, ["Start Experiment"])
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(sits, ["splashed"])
        self.assertEqual(thermo.triggered, [])

    def test_leftover_no_modules_recovers(self):
        """Dead leftover: Experiment gone. Recover HD. Do not light."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=True)
        vessel._alt = 73.0
        vessel._speed = 10.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
            now=now,
            sleep=sleep,
            timeout=5.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)

    def test_leftover_hd_skips_fresh_start(self):
        """HardDrive already has files — do not Toggle the leftover card."""
        exp = _Mod("Experiment", "kerbalism_TELEMETRY")
        drive = _Mod("HardDrive", "")
        drive.fields = {"Data": "Telemetry Report 0.11 Mb"}
        vessel = _Vessel([exp], sit="flying", ec=0.0, recoverable=True)
        vessel.parts = _Parts(
            [_Part("probeCoreSphere.v2", [exp, drive])]
        )
        vessel._alt = 73.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, _t = _fast_clock()
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
            now=now,
            sleep=sleep,
            timeout=5.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(exp.triggered, [])
        self.assertEqual(vessel.control.staged, 0)

    def test_leftover_no_modules_waits_recoverable(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel._alt = 73.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            if t[0] >= 3.0:
                vessel.recoverable = True

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
            now=now,
            sleep=nap,
            timeout=2.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertGreaterEqual(t[0], 3.0)

    def test_falling_probe_waits_while_met_moves(self):
        """Live fall: MET moving. Do not dismiss Flight Results yet."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 70.0
        vessel._alt = 400.0
        vessel.orbit.apoapsis_altitude = 800.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            vessel.met += dt if dt else 0.01
            vessel._alt = max(80.0, vessel._alt - 40.0)
            if t[0] >= 8.0:
                vessel.recoverable = True

        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=nap,
                timeout=2.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        scene.assert_not_called()
        self.assertGreaterEqual(t[0], 8.0)
        self.assertEqual(vessel.control.staged, 0)

    def test_frozen_wreck_unpause_then_recover(self):
        """Living recover: unpause frozen MET, then recover() — not dismiss."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 65.8
        vessel._alt = 74.0
        vessel._speed = 127.0
        vessel.orbit.apoapsis_altitude = 315.0
        vessel.orbit.periapsis_altitude = -6_362_000.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def unpause(_session):
            vessel.recoverable = True

        with patch("hop.run_physics", side_effect=unpause) as physics:
            with patch("hop.go_space_center") as scene:
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        physics.assert_called()
        scene.assert_not_called()
        self.assertIn("hop unpause", logs)
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertGreaterEqual(t[0], 5.0)

    def test_frozen_wreck_dismiss_without_recover_aborts(self):
        """Catastrophic flying recoverable=no: Space Center, abort, no wait landed."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel._speed = 0.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        now, sleep, t = _fast_clock()
        session = _Session(vessel)

        def dismiss(sess, **_kwargs):
            sess.active_vessel = None

        logs: list[str] = []
        with patch("hop.go_space_center", side_effect=dismiss) as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    session,
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertIn("recover-probe --space-center", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        scene.assert_not_called()
        self.assertIn("hop unpause", logs)
        self.assertTrue(any("hop crash ui sit=flying recoverable=no" in line for line in logs))
        self.assertTrue(
            any("ksc leftover (not space_center)" in line for line in logs)
        )
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertNotIn("hop wait landed recoverable=yes", logs)
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertFalse(any(line.startswith("recovered") for line in logs))
        self.assertLess(t[0], 15.0)

    def test_met_still_is_wall_seconds(self):
        """20 Hz five pulses is 0.25 s — not a crash UI Close."""
        t0, frozen = _met_still(186.48, 186.48, None, 0.0)
        self.assertIsNotNone(t0)
        self.assertFalse(frozen)
        _, frozen = _met_still(186.48, 186.48, t0, 0.25)
        self.assertFalse(frozen)
        _, frozen = _met_still(186.48, 186.48, t0, 5.0)
        self.assertTrue(frozen)

    def test_near_hz_crash_ui_waits_landed(self):
        """23-35-40Z: 20 Hz freeze flying 72.6 m; wait sit=landed (23-14)."""
        mod = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=10.0)
        vessel.name = CRAFT
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            t[0] += dt if dt else 0.01
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 300.0
                vessel._speed = 90.0
                vessel.met = 1.0
                vessel._flight.dynamic_pressure = 100.0
                vessel.orbit.apoapsis_altitude = 20_000.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel.resources.ec = 0.0
                if t[0] < 6.5:
                    vessel._alt = 72.6
                    vessel._speed = 89.0
                    vessel.met = 186.48
                    vessel._flight.dynamic_pressure = 0.0
                else:
                    vessel.situation = "landed"
                    vessel.recoverable = True
                    vessel._alt = 74.0
                    vessel._speed = 0.0
                    vessel._flight.dynamic_pressure = 0.0

        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("temperatureScan",),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=0.05,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        scene.assert_not_called()
        self.assertTrue(any("temperatureScan" in line for line in logs))
        self.assertGreaterEqual(t[0], 6.5)
        self.assertLess(t[0], 20.0)

    def test_lithobrake_q0_flying_is_down_now(self):
        """Lit hop, MET-still + q=0: unpause once; recover if sit=landed."""
        mod = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=9.9)
        vessel.name = CRAFT
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("kerbalism-geigercounter", [mod])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        order: list[str] = []

        def recover():
            order.append("recover")
            if vessel.situation not in ("landed", "splashed") and not vessel.recoverable:
                raise RuntimeError("not recoverable")
            vessel.recovered = True

        vessel.recover = recover

        def nap(dt):
            t[0] += dt if dt else 0.01
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 1_200.0
                vessel.orbit.apoapsis_altitude = 7_500.0
                vessel.orbit.periapsis_altitude = -6_362_000.0
                vessel.met = 10.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel._alt = 75.0
                vessel._speed = 0.0
                vessel._flight.dynamic_pressure = 0.0
                vessel.orbit.apoapsis_altitude = 327.0
                vessel.met = 65.0
                vessel.resources.ec = 9.9

        def unpause(_session):
            vessel.situation = "landed"
            vessel._alt = 78.0
            vessel.recoverable = True

        with patch("hop.run_physics", side_effect=unpause) as physics:
            with patch("hop.go_space_center") as scene:
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        physics.assert_called()
        self.assertIn("recover", order)
        self.assertIn("hop unpause", logs)
        self.assertTrue(any("recovered sit=landed" in line for line in logs))
        self.assertGreaterEqual(t[0], 5.0)
        self.assertLess(t[0], 25.0)
        self.assertEqual(vessel.situation, "landed")

    def test_lithobrake_q0_unpause_recovers_flying(self):
        """Living recover after MET-still q=0: recover() before dismiss."""
        mod = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=9.9)
        vessel.name = CRAFT
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("kerbalism-geigercounter", [mod])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            t[0] += dt if dt else 0.01
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 1_200.0
                vessel.orbit.apoapsis_altitude = 7_500.0
                vessel.orbit.periapsis_altitude = -6_362_000.0
                vessel.met = 10.0
            elif vessel.situation == "flying" and mod.triggered:
                vessel._alt = 75.0
                vessel._speed = 0.0
                vessel._flight.dynamic_pressure = 0.0
                vessel.orbit.apoapsis_altitude = 327.0
                vessel.met = 65.0

        def unpause(_session):
            vessel.recoverable = True

        with patch("hop.run_physics", side_effect=unpause) as physics:
            with patch("hop.go_space_center") as scene:
                result = run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        physics.assert_called()
        scene.assert_not_called()
        self.assertIn("hop unpause", logs)
        self.assertTrue(any("sit=flying recoverable=yes" in line for line in logs))
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertGreaterEqual(t[0], 5.0)
        self.assertLess(t[0], 20.0)

    def test_dismiss_prelaunch_is_not_hop_hd(self):
        """11-09-13Z: do not dismiss flying recoverable=no; pre_launch is not HD."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 65.8
        vessel._alt = 75.0
        vessel._speed = 0.0
        vessel.orbit.apoapsis_altitude = 307.0
        vessel.orbit.periapsis_altitude = -6_362_000.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        session = _Session(vessel)

        def dismiss(*_a, **_k):
            vessel.situation = "pre_launch"
            vessel.recoverable = True

        with patch("hop.go_space_center", side_effect=dismiss) as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    session,
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        self.assertIn("hop crash ui total wreck — ksc leftover (not space_center)", logs)
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertFalse(any(line.startswith("recovered") for line in logs))
        self.assertLess(t[0], 15.0)

    def test_low_flying_recovers_in_flight(self):
        """~199 m flying: recover() while still Flight, before lithobrake."""
        mod = _Mod("Experiment", "geigerCounter")
        vessel = _Vessel([mod], recoverable=False, sit="pre_launch", ec=9.9)
        vessel.name = CRAFT
        vessel.met = 0.0
        vessel.parts = _Parts([_Part("kerbalism-geigercounter", [mod])])
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        order: list[str] = []

        def recover():
            order.append("recover")
            vessel.recovered = True

        vessel.recover = recover

        def nap(dt):
            t[0] += dt if dt else 0.01
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 1_200.0
                vessel.orbit.apoapsis_altitude = 7_500.0
                vessel.orbit.periapsis_altitude = -6_362_000.0
                vessel.met = 10.0
            elif vessel.situation == "flying" and mod.triggered and not vessel.recovered:
                vessel._alt = 199.0
                vessel._speed = 80.0
                vessel._flight.dynamic_pressure = 2_800.0
                vessel.orbit.apoapsis_altitude = 430.0
                vessel.met = 64.0
                vessel.recoverable = True

        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("geigerCounter",),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(mod.triggered, ["Start Experiment"])
        scene.assert_not_called()
        self.assertIn("recover", order)
        self.assertTrue(any("recovered sit=flying" in line for line in logs))
        self.assertNotIn("hop dismissed flight results", logs)
        self.assertLess(t[0], 15.0)

    def test_pad_throttle_zero_does_not_hop_down(self):
        """18-34-22Z: MET 1.8 throttle 0 fuel 1054 alt 101 recovered on the pad."""
        thermo = _Mod("Experiment", "temperatureScan")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([thermo], recoverable=False)
        vessel.resources.fuel = 1054.0
        vessel.parts = _Parts(
            [
                _Part("sensorThermometer", [thermo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        from uplink import desk

        now, sleep, t = _fast_clock()
        logs: list[str] = []
        sess = _Session(vessel)
        pad_phys: list[int] = []
        prev_desk = (desk.hold, desk.skip_warp, desk.phys_warp)
        desk.hold = False
        desk.skip_warp = False
        desk.phys_warp = None

        def nap(dt):
            if vessel._alt <= 250.0 and vessel.situation == "flying":
                pad_phys.append(sess.space_center.physics_warp_factor)
                self.assertFalse(vessel.recovered)
                self.assertNotIn("hop down", logs)
                self.assertNotIn("hop hold inland through burnout", logs)
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 101.0
                vessel._speed = 14.0
                vessel._vz = 14.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 1054.0
                vessel.orbit.apoapsis_altitude = 114.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel._flight.dynamic_pressure = 160.0
                vessel.recoverable = True
                vessel.met = 1.8
            elif vessel.situation == "flying" and t[0] < 2.5:
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 1054.0
                vessel._alt = 101.0
                vessel._vz = 14.0
                vessel._flight.dynamic_pressure = 160.0
                vessel.recoverable = True
                vessel.met = 1.8 + t[0]
            elif vessel.situation == "flying":
                vessel._alt = 41_884.0
                vessel._vz = 40.0
                vessel._speed = 80.0
                vessel.resources.fuel = 0.0
                vessel.control.throttle = 0.0
                vessel.orbit.apoapsis_altitude = 49_000.0
                vessel._flight.dynamic_pressure = 400.0
                vessel.met = 20.0 + t[0]
                vessel.recoverable = False
                if t[0] >= 4.0:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._vz = 0.0
                    vessel._speed = 5.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        try:
            result = run_on_vessel(
                sess,
                vessel,
                science_ids=("temperatureScan",),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        finally:
            desk.hold, desk.skip_warp, desk.phys_warp = prev_desk
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(pad_phys)
        self.assertTrue(all(p == 0 for p in pad_phys))
        self.assertTrue(any("hop coast physics 4x rails=0" in x for x in logs))
        self.assertTrue(any("hop down" in x for x in logs))
        self.assertTrue(any("hop hold inland through burnout" in x for x in logs))

    def test_pad_boost_does_not_dwell_science_or_hop_down(self):
        """Flying 104 m with fuel: 1× boost, no goo, no hop-down. Landed is not boost."""
        goo = _Mod("Experiment", "mysteryGoo")
        chute = _Mod(
            "RealChuteModule",
            "",
            events=["Arm parachute", "Deploy chute", "Cut main chute"],
        )
        vessel = _Vessel([goo], recoverable=False)
        vessel.resources.fuel = 1053.0
        vessel.parts = _Parts(
            [
                _Part("GooExperiment", [goo]),
                _Part("parachuteSingle", [chute]),
            ]
        )
        from uplink import desk

        now, sleep, t = _fast_clock()
        logs: list[str] = []
        sess = _Session(vessel)
        pad_throt: list[float] = []
        prev_desk = (desk.hold, desk.skip_warp, desk.phys_warp)
        desk.hold = False
        desk.skip_warp = False
        desk.phys_warp = None

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 104.0
                vessel._speed = 14.0
                vessel._vz = 14.0
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 1053.0
                vessel.orbit.apoapsis_altitude = 119.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel._flight.dynamic_pressure = 185.0
                vessel.recoverable = False
                vessel.met = 1.88
            elif vessel.situation == "flying" and vessel._alt <= 250.0:
                pad_throt.append(vessel.control.throttle)
                self.assertFalse(vessel.recovered)
                self.assertFalse(goo.triggered)
                self.assertNotIn("hop down", logs)
                self.assertNotIn("science mysteryGoo", logs)
                self.assertNotIn("science dwell", logs)
                vessel.control.throttle = 0.0
                vessel.resources.fuel = 1053.0
                vessel._alt = 104.0
                vessel._vz = -5.0
                vessel._flight.dynamic_pressure = 185.0
                vessel.recoverable = False
                vessel.met = 1.88 + t[0]
                if t[0] >= 1.5:
                    vessel.situation = "flying"
                    vessel._alt = 41_884.0
                    vessel._vz = 40.0
                    vessel._speed = 80.0
                    vessel.resources.fuel = 0.0
                    vessel.control.throttle = 0.0
                    vessel.orbit.apoapsis_altitude = 49_000.0
                    vessel._flight.dynamic_pressure = 400.0
                    vessel.met = 40.0 + t[0]
                    vessel.recoverable = False
            elif vessel.situation == "flying":
                if t[0] >= 4.0:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._vz = 0.0
                    vessel._speed = 5.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        try:
            result = run_on_vessel(
                sess,
                vessel,
                science_ids=("mysteryGoo",),
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        finally:
            desk.hold, desk.skip_warp, desk.phys_warp = prev_desk
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(pad_throt)
        self.assertTrue(any(th > 0.05 for th in pad_throt))
        self.assertTrue(any("hop down" in x for x in logs))
        self.assertTrue(any("hop coast physics 4x rails=0" in x for x in logs))

    def test_frozen_wreck_recovers_hop_debris(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        debris = _Vessel([], sit="landed", ec=0.0, recoverable=True)
        debris.name = CRAFT + " Debris"
        debris.met = 75.56
        session = _Session(vessel)
        session.space_center.vessels = [vessel, debris]
        now, sleep, _t = _fast_clock()
        with patch("hop.go_space_center") as scene:
            result = run_on_vessel(
                session,
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=sleep,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(debris.recovered)
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        scene.assert_called()

    def test_gone_vessel_finishes_hd(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel._alt = 72.0
        vessel.orbit.apoapsis_altitude = 200.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        session = _Session(vessel)
        now, sleep, t = _fast_clock()

        def nap(dt):
            t[0] += dt if dt else 0.01
            session.active_vessel = None

        with patch("hop.go_space_center") as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    session,
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                    now=now,
                    sleep=nap,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("no vessel", str(ctx.exception))
        scene.assert_not_called()
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)

    def test_frozen_wreck_abort_if_dismiss_fails(self):
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.met = 75.56
        vessel._alt = 72.0
        vessel.orbit.apoapsis_altitude = 810.0
        vessel.orbit.periapsis_altitude = -7_000_000.0
        now, sleep, t = _fast_clock()
        with patch("hop.go_space_center", side_effect=RuntimeError("scene")) as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        self.assertEqual(vessel.control.staged, 0)
        self.assertLess(t[0], 15.0)

    def test_crash_ui_frozen_landed_not_recoverable_dismisses(self):
        """13-58-18Z: sit=landed recoverable=no MET frozen — Close, no unpause."""
        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 400.0
        vessel._alt = 2_000.0
        vessel._speed = 80.0
        vessel._flight.dynamic_pressure = 32_700.0
        vessel.orbit.apoapsis_altitude = 90_000.0
        vessel.orbit.periapsis_altitude = -6_361_632.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        landed = [False]

        def nap(dt):
            t[0] += dt if dt else 0.01
            if t[0] >= 2.0 and not landed[0]:
                landed[0] = True
                vessel.situation = "landed"
                vessel._alt = 32.95
                vessel._speed = 0.0
                vessel._flight.dynamic_pressure = 0.0
                vessel.met = 407.46
            elif not landed[0]:
                vessel.met += dt if dt else 0.01

        with patch("hop.go_space_center") as scene:
            with patch("hop.run_physics") as physics:
                with self.assertRaises(MissionAbort) as ctx:
                    run_on_vessel(
                        _Session(vessel),
                        vessel,
                        science_ids=("geigerCounter",),
                        on_log=logs.append,
                        now=now,
                        sleep=nap,
                        timeout=30.0,
                        pulse=1.0,
                    )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        physics.assert_called()
        self.assertTrue(
            any(
                "hop crash ui sit=landed recoverable=no" in line
                and "met=407.46" in line
                and "alt=33.0" in line
                for line in logs
            )
        )
        self.assertIn("hop crash ui total wreck — ksc leftover (not space_center)", logs)
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertIn("hop unpause", logs)
        self.assertNotIn("hop paused wreck", logs)
        self.assertNotIn("hop finish wreck", logs)
        self.assertFalse(any(line.startswith("recovered") for line in logs))
        self.assertLess(t[0], 15.0)
        self.assertGreaterEqual(t[0], 6.0)

    def test_crash_ui_frozen_flying_dismisses_now(self):
        """12-04-13Z: frozen flying q=0 alt~74 is crash UI, not wait landed."""
        vessel = _Vessel([], sit="flying", ec=9.9, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 67.62
        vessel._alt = 74.03
        vessel._speed = 0.0
        vessel._flight.dynamic_pressure = 0.0
        vessel.orbit.apoapsis_altitude = 292.0
        vessel.orbit.periapsis_altitude = -6_362_935.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        with patch("hop.go_space_center") as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("geigerCounter",),
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        scene.assert_not_called()
        self.assertTrue(
            any(
                "hop crash ui sit=flying recoverable=no" in line
                and "met=67.62" in line
                and "alt=74.0" in line
                and "q=0" in line
                for line in logs
            )
        )
        self.assertIn("hop crash ui total wreck — ksc leftover (not space_center)", logs)
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertNotIn("hop wait landed recoverable=yes", logs)
        self.assertLess(t[0], 15.0)
        self.assertGreaterEqual(t[0], 5.0)

    def test_skip_peri_on_ballistic(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 4_000.0
        vessel.orbit.apoapsis_altitude = 14_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch(
            "phases._kv",
            return_value={
                "hop_apo": "15000",
                "expect_body": "Earth",
                "expect_peri_min": "0",
                "expect_apo_max": "20000",
            },
        ):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")

    def test_science_uplink_does_not_toggle_twice(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 3_000.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            if mod.triggered:
                vessel.situation = "landed"
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.take", return_value=_Uplink("science")):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(mod.triggered, ["Start Experiment"])

    def test_transmit_uplink_fires_kerbalism_event_not_toggle(self):
        class _TxMod(_Mod):
            def trigger_event(self, name):
                self.triggered.append(name)
                low = str(name).lower()
                if "start" in low or low == "toggle":
                    self.fields["status"] = "Running"

        mod = _TxMod(
            "Experiment",
            "temperatureScan",
            events=["Start Experiment", "Toggle", "Dump", "Reset", "Transmit"],
        )
        vessel = _Vessel([mod], sit="flying")
        vessel.parts = _Parts([_Part("sensorThermometer", [mod])])
        vessel._alt = 3_000.0
        vessel.orbit.apoapsis_altitude = 12_000.0
        now, sleep, t = _fast_clock()
        cmds = [_Uplink("transmit")]

        def take_once():
            return cmds.pop(0) if cmds else None

        def nap(dt):
            if "Start Experiment" in mod.triggered:
                vessel.situation = "landed"
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("hop.take", side_effect=take_once):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("temperatureScan",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(mod.triggered, ["Transmit", "Start Experiment"])

    def test_cut_throttle_at_hop_apo(self):
        mod = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([mod], sit="flying")
        vessel._alt = 5_000.0
        vessel.orbit.apoapsis_altitude = 16_000.0
        vessel.orbit.periapsis_altitude = -6_000_000.0
        now, sleep, t = _fast_clock()

        def nap(dt):
            self.assertEqual(vessel.control.throttle, 0.0)
            vessel.situation = "landed"
            vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("phases._kv", return_value={"hop_apo": "15000"}):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("mysteryGoo",),
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_no_vessel_hangars(self):
        session = _Session(None)  # type: ignore[arg-type]
        session.active_vessel = None
        with patch("hop.run_hop", return_value="recovered") as hop:
            result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()

    def test_pad_motor_hangars_instead_of_lighting(self):
        vessel = _Vessel([])
        vessel.name = "kspstuff-pad-pbc"
        session = _Session(vessel)
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_pulses_write_state_jsonl(self):
        """Each Telem.read lands alt/apo/peri/sit/MET/EC/fuel on the seated jsonl."""
        import flightlog

        vessel = _Vessel([], sit="flying", ec=0.0, recoverable=False)
        vessel.name = CRAFT
        vessel.met = 7.0
        vessel._alt = 2123.0
        vessel.orbit.apoapsis_altitude = 11562.0
        vessel.orbit.periapsis_altitude = -6_362_500.0
        now, sleep, t = _fast_clock()
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

        def nap(dt):
            t[0] += dt if dt else 0.01
            vessel.met += dt if dt else 0.01
            vessel._alt = max(80.0, vessel._alt - 200.0)
            if t[0] >= 3.0:
                vessel.recoverable = True

        try:
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY", "temperatureScan"),
                now=now,
                sleep=nap,
                timeout=2.0,
                pulse=1.0,
            )
        finally:
            (
                flightlog._path,
                flightlog._t0,
                flightlog._count,
                flightlog._last_write,
                flightlog._last_flags,
            ) = old
        self.assertEqual(result, "recovered")
        rows = [
            json.loads(line)
            for line in tmp.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        states = [row for row in rows if row.get("kind") == "state"]
        self.assertGreaterEqual(len(states), 3)
        first = states[0]
        self.assertEqual(first["situation"], "flying")
        self.assertAlmostEqual(first["alt"], 2123.0)
        self.assertAlmostEqual(first["apo"], 11562.0)
        self.assertAlmostEqual(first["peri"], -6_362_500.0)
        self.assertAlmostEqual(first["met"], 7.0)
        self.assertEqual(first["ec"], 0.0)
        self.assertEqual(first["fuel"], 5.0)
        alts = [row["alt"] for row in states]
        self.assertGreater(max(alts), min(alts))

    def test_already_launched_hop_skips_hangar(self):
        vessel = _Vessel([])
        vessel.name = CRAFT
        session = _Session(vessel)
        with patch("hop.hop_match_name", return_value=CRAFT):
            with patch("hop.run_hop") as hop:
                with patch("hop.run_on_vessel", return_value="recovered") as run:
                    result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        run.assert_called_once()

    def test_spacecenter_leftover_enters_flight_not_hangar(self):
        """KSC overview + leftover Flea: enter Flight. Do not Hangar."""
        vessel = _Vessel([], sit="pre_launch")
        vessel.name = CRAFT
        session = _Session(vessel)
        entered: list[object] = []

        def fake_flight(sess, v=None, **_kwargs):
            entered.append(v or sess.active_vessel)

        with patch("hop.hop_match_name", return_value=CRAFT):
            with patch("hop.game_scene", return_value="space_center"):
                with patch("hop.go_flight", side_effect=fake_flight) as gf:
                    with patch("hop.run_hop") as hop:
                        with patch(
                            "hop.run_on_vessel", return_value="recovered"
                        ) as run:
                            result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        gf.assert_called()
        self.assertIs(entered[0], vessel)
        run.assert_called_once()
        self.assertIs(run.call_args[0][1], vessel)

    def test_tracking_leftover_enters_flight_when_active_none(self):
        leftover = _Vessel([], sit="pre_launch")
        leftover.name = CRAFT
        session = _Session(None)  # type: ignore[arg-type]
        session.active_vessel = None
        session.space_center.vessels = [leftover]
        with patch("hop.hop_match_name", return_value=CRAFT):
            with patch("hop.game_scene", return_value="space_center"):
                with patch("hop.go_flight") as gf:
                    with patch("hop.run_hop") as hop:
                        with patch(
                            "hop.run_on_vessel", return_value="recovered"
                        ) as run:
                            result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        gf.assert_called()
        self.assertIs(gf.call_args[0][1], leftover)
        self.assertIs(run.call_args[0][1], leftover)

    def test_dead_active_guid_scans_pool(self):
        """Dead kRPC GUID is not leftover. Living tracking Flea enters Flight."""
        leftover = _Vessel([], sit="pre_launch")
        leftover.name = CRAFT
        dead = _DeadVessel()
        session = _Session(dead)
        session.space_center.vessels = [dead, leftover]
        with patch("hop.hop_match_name", return_value=CRAFT):
            with patch("hop.game_scene", return_value="space_center"):
                with patch("hop.go_flight") as gf:
                    with patch("hop.run_hop") as hop:
                        with patch(
                            "hop.run_on_vessel", return_value="recovered"
                        ) as run:
                            result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        gf.assert_called()
        self.assertIs(gf.call_args[0][1], leftover)
        self.assertIs(run.call_args[0][1], leftover)

    def test_dead_active_empty_pool_hangars(self):
        """Tracking empty: dead GUID is not leftover. Hangar."""
        dead = _DeadVessel()
        session = _Session(dead)
        session.space_center.vessels = [dead]
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_flying_debris_is_not_leftover(self):
        """Live pool Debris FLYING is not leftover. Hangar (I-017)."""
        ghost = _Vessel([], sit="flying")
        ghost.name = f"{CRAFT} Debris"
        session = _Session(ghost)
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_dead_guid_plus_flying_debris_hangars(self):
        """Ghost FLYING debris in the pool is not leftover. Hangar."""
        dead = _DeadVessel()
        ghost = _Vessel([], sit="flying")
        ghost.name = f"{CRAFT} Debris"
        session = _Session(dead)
        session.space_center.vessels = [dead, ghost]
        with patch("hop.run_hop", return_value="recovered") as hop:
            with patch("hop.run_on_vessel") as run:
                result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_called_once()
        run.assert_not_called()

    def test_unmatched_flea_recovers_without_light(self):
        """PRELAUNCH Flea vs seated Valiant: abort ksc leftover. Do not recover."""
        flea = _Vessel([], sit="pre_launch", recoverable=True)
        flea.name = CRAFT
        session = _Session(flea)
        logs: list[str] = []
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-valiant-pbc"
        ):
            with patch("hop.run_hop", return_value="recovered") as hop:
                with patch("hop.run_on_vessel") as run:
                    with self.assertRaises(MissionAbort) as ctx:
                        run_phase(session, on_log=logs.append)
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertIn("recover-probe --recover", str(ctx.exception))
        self.assertFalse(flea.recovered)
        self.assertEqual(flea.control.staged, 0)
        hop.assert_not_called()
        run.assert_not_called()
        self.assertTrue(any("unmatched" in line for line in logs))
        self.assertTrue(any("ksc leftover" in line or "ksc: leftover" in line for line in logs))

    def test_unmatched_flea_not_recoverable_does_not_hangar(self):
        flea = _Vessel([], sit="pre_launch", recoverable=False)
        flea.name = CRAFT
        session = _Session(flea)
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-valiant-pbc"
        ):
            with patch("hop.run_hop") as hop:
                with patch("hop.run_on_vessel") as run:
                    with self.assertRaises(MissionAbort) as ctx:
                        run_phase(session)
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertIn("recover-probe --space-center", str(ctx.exception))
        self.assertFalse(flea.recovered)
        self.assertEqual(flea.control.staged, 0)
        hop.assert_not_called()
        run.assert_not_called()

    def test_cli_hop_recovers_unmatched_before_hangar(self):
        flea = _Vessel([], sit="pre_launch", recoverable=True)
        flea.name = CRAFT
        session = _Session(flea)
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-valiant-pbc"
        ):
            with patch("hop.hop_science_ids", return_value=("temperatureScan",)):
                with patch("hop.install_and_launch") as hangar:
                    with patch("hop.wait_vessel_ready", return_value="ready"):
                        with patch(
                            "hop.run_on_vessel", return_value="recovered"
                        ) as run:
                            with self.assertRaises(MissionAbort) as ctx:
                                run_hop(session)
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertFalse(flea.recovered)
        self.assertEqual(flea.control.staged, 0)
        hangar.assert_not_called()
        run.assert_not_called()

    def test_hop_name_with_geiger_pbc_is_leftover_not_pad(self):
        """Substring geiger-pbc is not the pad motor (I-013)."""
        vessel = _Vessel([])
        vessel.name = "kspstuff-hop-flea-geiger-pbc"
        session = _Session(vessel)
        with patch(
            "hop.hop_match_name", return_value="kspstuff-hop-flea-geiger-pbc"
        ):
            with patch("hop.run_hop") as hop:
                with patch("hop.run_on_vessel", return_value="recovered") as run:
                    result = run_phase(session)
        self.assertEqual(result, "recovered")
        hop.assert_not_called()
        run.assert_called_once()


class TestPhaseHopUncrewed(unittest.TestCase):
    def test_cmd_phase_skips_seat(self):
        from main import cmd_phase

        session = _Session(_Vessel([], recoverable=True))
        args = argparse.Namespace(name="hop", timeout=0.0)
        with patch("missions.assert_seated") as seated:
            with patch("hop.run_phase", return_value="recovered"):
                code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 0)

    def test_cmd_hop_skips_seat(self):
        from main import cmd_hop

        session = _Session(_Vessel([], recoverable=True))
        args = argparse.Namespace(timeout=0.0)
        with patch("missions.assert_seated") as seated:
            with patch("hop.run_hop", return_value="recovered"):
                code = cmd_hop(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 0)


class _FakeHangar:
    def __init__(self, root: Path):
        self.root = root
        self.calls: list[dict] = []

    def ships(self, facility: str = "VAB") -> Path:
        path = self.root / facility
        path.mkdir(parents=True, exist_ok=True)
        return path

    def launch(self, session, name, *, recover=True, uncrewed=False, **_kwargs):
        self.calls.append(
            {"name": name, "uncrewed": uncrewed, "recover": recover}
        )
        session.active_vessel = _Vessel([], sit="pre_launch")
        session.active_vessel.name = name


class TestInstallSigned(unittest.TestCase):
    def test_copies_named_file(self):
        from hangar import install_signed

        src = hop_craft_path("kspstuff-hop-hammer-pbc")
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            install_signed(
                session,
                "kspstuff-hop-hammer-pbc",
                hangar=fake,
                src=src,
            )
            dest = fake.ships("VAB") / "kspstuff-hop-hammer-pbc.craft"
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.read_bytes(), src.read_bytes())


class TestHopHangar(unittest.TestCase):
    def test_copies_hammer_not_flea_or_pad(self):
        src = hop_craft_path("kspstuff-hop-hammer-pbc").read_bytes()
        self.assertIn(b"solidBooster", src)
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            with patch("hop.discover_hangar", return_value=fake):
                with patch("hop.hop_craft_name", return_value="kspstuff-hop-hammer-pbc"):
                    install_and_launch(session)
            dest = fake.ships("VAB") / "kspstuff-hop-hammer-pbc.craft"
            self.assertTrue(dest.is_file())
            self.assertEqual(dest.read_bytes(), src)
            text = dest.read_text(encoding="utf-8")
            self.assertNotIn("kspstuff-pad-pbc", text)
            self.assertNotIn("kspstuff-hop-flea-pbc", text)
            self.assertNotIn("kerbalism-geigercounter", text)
            self.assertEqual(fake.calls[0]["name"], "kspstuff-hop-hammer-pbc")
            self.assertTrue(fake.calls[0]["uncrewed"])
            self.assertEqual(session.active_vessel.name, "kspstuff-hop-hammer-pbc")

    def test_refuses_pad_and_geiger_names(self):
        session = _Session(None)  # type: ignore[arg-type]
        for bad in ("kspstuff-pad-pbc", "kspstuff-geiger-pbc"):
            with patch("hop.hop_craft_name", return_value=bad):
                with self.assertRaises(MissionAbort) as ctx:
                    install_and_launch(session)
            self.assertIn("refused", str(ctx.exception))
            self.assertIn(bad, str(ctx.exception))

    def test_allows_hop_name_containing_geiger_pbc(self):
        """Refuse exact pad/geiger names, not substring geiger-pbc (I-013)."""
        session = _Session(None)  # type: ignore[arg-type]
        session.active_vessel = None
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            with patch(
                "hop.hop_craft_name", return_value="kspstuff-hop-flea-geiger-pbc"
            ):
                with patch("hop.discover_hangar", return_value=fake):
                    with patch("hangar.install_signed", return_value="ok") as inst:
                        install_and_launch(session)
        inst.assert_called_once()
        self.assertEqual(inst.call_args.args[1], "kspstuff-hop-flea-geiger-pbc")

    def test_missing_ksp_aborts(self):
        session = _Session(None)  # type: ignore[arg-type]
        with patch("hop.hop_craft_name", return_value="kspstuff-hop-hammer-pbc"):
            with patch("hop.discover_hangar", return_value=None):
                with self.assertRaises(MissionAbort) as ctx:
                    install_and_launch(session)
        self.assertIn("KSP", str(ctx.exception))

    def test_run_hop_hangars_then_lights(self):
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            with patch("hop.discover_hangar", return_value=fake):
                with patch("hop.hop_craft_name", return_value="kspstuff-hop-hammer-pbc"):
                    with patch("hop.hop_science_ids", return_value=("temperatureScan",)):
                        with patch("hop.time.sleep"):
                            with patch("hop.run_on_vessel", return_value="recovered") as run:
                                result = run_hop(session)
            self.assertEqual(result, "recovered")
            self.assertEqual(fake.calls[0]["name"], "kspstuff-hop-hammer-pbc")
            self.assertTrue(fake.calls[0]["uncrewed"])
            run.assert_called_once()
            self.assertIs(run.call_args[0][1], session.active_vessel)


class _Scene:
    def __init__(self, name):
        self.name = name


class _Krpc:
    def __init__(self, scene="space_center"):
        self._scene = _Scene(scene)
        self.GameScene = type(
            "GS",
            (),
            {
                "space_center": _Scene("space_center"),
                "flight": _Scene("flight"),
            },
        )()

    @property
    def game_scene(self):
        return self._scene

    @game_scene.setter
    def game_scene(self, val):
        self._scene = val if hasattr(val, "name") else _Scene(str(val))


class _StuckKrpc(_Krpc):
    @property
    def game_scene(self):
        return self._scene

    @game_scene.setter
    def game_scene(self, val):
        return


class _FlightSession:
    def __init__(self, vessel, scene="space_center", stuck=False):
        self.active_vessel = vessel
        krpc = _StuckKrpc(scene) if stuck else _Krpc(scene)
        sc = type("SC", (), {"active_vessel": vessel})()
        self.space_center = sc
        self.conn = type("C", (), {"krpc": krpc, "space_center": sc})()
        self.switch_settle_s = 0.0

    def require_connected(self):
        return None

    def switch_to(self, vessel, settle=None):
        self.active_vessel = vessel
        if not isinstance(self.conn.krpc, _StuckKrpc):
            self.conn.krpc.game_scene = self.conn.krpc.GameScene.flight


class TestGoFlight(unittest.TestCase):
    def test_enters_flight_from_space_center(self):
        from hangar import go_flight

        vessel = _Vessel([])
        vessel.name = CRAFT
        session = _FlightSession(vessel, scene="space_center")
        with patch("hangar.time.sleep"):
            go_flight(session, vessel, timeout=2.0)
        self.assertEqual(session.conn.krpc.game_scene.name, "flight")

    def test_already_flight_is_noop(self):
        from hangar import go_flight

        vessel = _Vessel([])
        session = _FlightSession(vessel, scene="flight")
        with patch("hangar.time.sleep") as nap:
            go_flight(session, vessel)
        nap.assert_not_called()

    def test_timeout_if_scene_stuck(self):
        from hangar import go_flight
        from session import SessionError

        vessel = _Vessel([])
        vessel.name = CRAFT
        session = _FlightSession(vessel, scene="space_center", stuck=True)
        with patch("hangar.time.sleep"):
            with patch("hangar.time.monotonic", side_effect=[0.0, 1.0, 1.0]):
                with self.assertRaises(SessionError) as ctx:
                    go_flight(session, vessel, timeout=0.01)
        self.assertIn("flight", str(ctx.exception))
        self.assertIn(CRAFT, str(ctx.exception))


class TestLoadSave(unittest.TestCase):
    def test_load_persistent_not_quicksave(self):
        from hangar import load_save
        from session import SessionError

        sc = type("SC", (), {})()
        sc.load = lambda name: setattr(sc, "loaded", name)
        session = type("S", (), {"space_center": sc})()
        self.assertEqual(load_save(session, "rd-engineering101"), "load rd-engineering101")
        self.assertEqual(sc.loaded, "rd-engineering101")
        with self.assertRaises(SessionError):
            load_save(session, "quicksave")
        with self.assertRaises(SessionError):
            load_save(session, "persistent")


class TestWaitVesselReady(unittest.TestCase):
    def test_ready_when_parts_and_flight(self):
        from hangar import wait_vessel_ready

        vessel = _Vessel([])
        session = _FlightSession(vessel, scene="flight")
        with patch("hangar.time.sleep") as nap:
            msg = wait_vessel_ready(session, vessel, timeout=1.0)
        nap.assert_not_called()
        self.assertIn("hangar ready", msg)
        self.assertIn("parts=", msg)

    def test_timeout_if_parts_empty(self):
        from hangar import wait_vessel_ready
        from session import SessionError

        vessel = _Vessel([])
        vessel.parts = _Parts([])
        session = _FlightSession(vessel, scene="flight")
        with patch("hangar.time.sleep"):
            with patch("hangar.time.monotonic", side_effect=[0.0, 0.2, 2.0]):
                with self.assertRaises(SessionError) as ctx:
                    wait_vessel_ready(session, vessel, timeout=1.0)
        self.assertIn("vessel ready", str(ctx.exception))


class TestHopInland(unittest.TestCase):
    """08-29-36Z: vertical hop heading 299 horiz 0 stayed Shores."""

    def setUp(self):
        self._fh = patch("hop.hop_wants_flying_high", return_value=False)
        self._fh.start()
        self.addCleanup(self._fh.stop)
        _isolate_live_tickets(self)

    def test_inland_constants(self):
        self.assertEqual(INLAND_HEADING_DEG, 270.0)
        self.assertEqual(INLAND_PITCH_FROM_UP, 25.0)
        self.assertEqual(INLAND_PITCH_DEG, 65.0)
        self.assertEqual(INLAND_YAW_FROM_UP, 10.0)
        self.assertEqual(INLAND_YAW_PITCH_DEG, 80.0)
        self.assertEqual(INLAND_HEADING_CAPTURE_DEG, 20.0)
        self.assertEqual(INLAND_YAW_MET_S, 6.0)
        self.assertEqual(CHUTE_DEPLOY_ALT_M, 2_000.0)
        self.assertNotEqual(INLAND_HEADING_DEG, WATER_HEADING_DEG)
        self.assertGreater(INLAND_YAW_PITCH_DEG, INLAND_PITCH_DEG)

    def test_inland_direction_is_up_then_west(self):
        up = inland_direction(WATER_PITCH_UP)
        self.assertAlmostEqual(up[0], 1.0, places=6)
        self.assertAlmostEqual(up[1], 0.0, places=6)
        self.assertAlmostEqual(up[2], 0.0, places=6)
        west = inland_direction(0.0)
        self.assertAlmostEqual(west[0], 0.0, places=6)
        self.assertAlmostEqual(west[1], 0.0, places=6)
        self.assertAlmostEqual(west[2], -1.0, places=6)
        d = inland_direction(INLAND_PITCH_DEG)
        self.assertLess(d[2], 0.0)
        self.assertAlmostEqual(d[1], 0.0, places=6)
        n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
        self.assertAlmostEqual(n, 1.0, places=6)
        self.assertEqual(
            inland_direction(INLAND_PITCH_DEG),
            surface_direction(INLAND_PITCH_DEG, INLAND_HEADING_DEG),
        )

    def test_steer_inland_does_not_command_roll_zero(self):
        vessel = _Vessel([])
        _steer_inland(vessel, pitch=WATER_PITCH_UP)
        # 09-16-24Z: Eulers logged 270, flew pad 297. Direction is not the hold.
        # 09-44-59Z: engage at zenith yawed 340 at burnout — hold 65 first.
        self.assertNotEqual(vessel.auto_pilot.target_heading, INLAND_HEADING_DEG)
        self.assertEqual(vessel.auto_pilot.up_reference, SURFACE_NORTH)
        self.assertEqual(vessel.auto_pilot.target_roll, 0.0)
        self.assertEqual(
            vessel.auto_pilot.held, inland_direction(WATER_PITCH_UP)
        )
        self.assertFalse(vessel.auto_pilot.engaged)
        self.assertEqual(vessel.auto_pilot.engage_n, 0)
        _steer_inland(vessel, pitch=INLAND_YAW_PITCH_DEG)
        self.assertTrue(vessel.auto_pilot.engaged)
        self.assertEqual(vessel.auto_pilot.engage_n, 1)
        self.assertEqual(
            vessel.auto_pilot.held, inland_direction(INLAND_YAW_PITCH_DEG)
        )
        _steer_inland(vessel, pitch=INLAND_PITCH_DEG)
        self.assertTrue(vessel.auto_pilot.engaged)
        self.assertEqual(vessel.auto_pilot.engage_n, 1)
        self.assertEqual(vessel.auto_pilot.up_reference, SURFACE_NORTH)
        self.assertEqual(
            vessel.auto_pilot.held,
            inland_direction(INLAND_PITCH_DEG),
        )
        self.assertNotEqual(vessel.auto_pilot.target_heading, INLAND_HEADING_DEG)
        _steer_inland(vessel, pitch=INLAND_PITCH_DEG)
        self.assertEqual(vessel.auto_pilot.engage_n, 1)

    def test_steer_inland_repaint_if_flipped_east(self):
        """10-17-18Z: engaged latch skipped rewrite; burnout 38/−10."""
        vessel = _Vessel([])
        _steer_inland(vessel, pitch=INLAND_PITCH_DEG)
        n = vessel.auto_pilot.point_n
        want = inland_direction(INLAND_PITCH_DEG)
        _steer_inland(vessel, pitch=INLAND_PITCH_DEG)
        self.assertEqual(vessel.auto_pilot.point_n, n)
        _steer_inland(
            vessel,
            pitch=INLAND_PITCH_DEG,
            flown_pitch=66.0,
            flown_heading=297.0,
        )
        self.assertEqual(vessel.auto_pilot.point_n, n)
        _steer_inland(
            vessel,
            pitch=INLAND_PITCH_DEG,
            flown_pitch=26.0,
            flown_heading=353.0,
        )
        self.assertGreater(vessel.auto_pilot.point_n, n)
        self.assertEqual(vessel.auto_pilot.target_direction, want)
        n2 = vessel.auto_pilot.point_n
        _steer_inland(
            vessel,
            pitch=INLAND_PITCH_DEG,
            flown_pitch=-10.0,
            flown_heading=38.0,
        )
        self.assertGreater(vessel.auto_pilot.point_n, n2)
        self.assertEqual(vessel.auto_pilot.engage_n, 1)
        self.assertEqual(vessel.auto_pilot.held, want)
        self.assertEqual(vessel.auto_pilot.target_direction, want)
        self.assertLess(vessel.auto_pilot.held[2], 0.0)

    def test_steer_inland_repaint_writes_target_direction(self):
        """10-33-44Z: set_direction_and_up while engaged did not stick."""
        vessel = _Vessel([])
        ap = vessel.auto_pilot

        def silent_point(direction, up, roll=0.0):
            ap.point_n += 1
            ap.up_reference = tuple(float(x) for x in up)
            ap.target_roll = float(roll)

        ap.set_direction_and_up = silent_point
        want = inland_direction(INLAND_PITCH_DEG)
        _steer_inland(vessel, pitch=INLAND_PITCH_DEG)
        self.assertEqual(ap.target_direction, want)
        ap.target_direction = (1.0, 0.0, 0.0)
        _steer_inland(
            vessel,
            pitch=INLAND_PITCH_DEG,
            flown_pitch=26.0,
            flown_heading=353.0,
        )
        self.assertEqual(ap.target_direction, want)
        self.assertEqual(ap.engage_n, 1)

    def test_inland_cmd_pitch_yaw_then_65(self):
        """16-47-21Z: slam 65 flew pad 297; yaw 80/270 first."""
        pitch, yawed = _inland_cmd_pitch(False, 1, 90.0, 299.0, 1.8)
        self.assertEqual(pitch, INLAND_YAW_PITCH_DEG)
        self.assertFalse(yawed)
        pitch, yawed = _inland_cmd_pitch(False, 3, 80.0, 275.0, 3.0)
        self.assertEqual(pitch, INLAND_PITCH_DEG)
        self.assertTrue(yawed)
        pitch, yawed = _inland_cmd_pitch(False, 4, 89.0, 297.0, 6.0)
        self.assertEqual(pitch, INLAND_PITCH_DEG)
        self.assertTrue(yawed)
        pitch, yawed = _inland_cmd_pitch(False, 1, float("nan"), float("nan"), float("nan"))
        self.assertEqual(pitch, INLAND_YAW_PITCH_DEG)
        self.assertFalse(yawed)
        pitch, yawed = _inland_cmd_pitch(False, 2, float("nan"), float("nan"), float("nan"))
        self.assertEqual(pitch, INLAND_PITCH_DEG)
        self.assertTrue(yawed)
        pitch, yawed = _inland_cmd_pitch(True, 1, 90.0, 299.0, 1.8)
        self.assertEqual(pitch, INLAND_PITCH_DEG)
        self.assertTrue(yawed)

    def test_steer_inland_no_repaint_after_cutoff_pitch_dump(self):
        """16-47-21Z envelope 15/16 is fuel=0 — do not rewrite."""
        vessel = _Vessel([])
        _steer_inland(vessel, pitch=INLAND_PITCH_DEG)
        n = vessel.auto_pilot.point_n
        _steer_inland(
            vessel,
            pitch=INLAND_PITCH_DEG,
            flown_pitch=16.0,
            flown_heading=15.0,
            burning=False,
        )
        self.assertEqual(vessel.auto_pilot.point_n, n)
        _steer_inland(
            vessel,
            pitch=INLAND_PITCH_DEG,
            flown_pitch=-10.0,
            flown_heading=38.0,
            burning=False,
        )
        self.assertGreater(vessel.auto_pilot.point_n, n)
        n2 = vessel.auto_pilot.point_n
        _steer_inland(
            vessel,
            pitch=INLAND_PITCH_DEG,
            flown_pitch=16.0,
            flown_heading=15.0,
            burning=True,
        )
        self.assertGreater(vessel.auto_pilot.point_n, n2)

    def test_slew_inland_after_pad(self):
        """Do not slam 65 at light; 090 is Water."""
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([thermo], recoverable=False)
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        pad_dir: list[tuple[float, float, float]] = []
        air_dir: list[tuple[float, float, float]] = []
        air_throt: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                pad_dir.append(vessel.auto_pilot.target_direction)
                vessel.situation = "landed"
                vessel._alt = 40.0
                vessel._speed = 20.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "landed":
                pad_dir.append(vessel.auto_pilot.target_direction)
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
            elif vessel.situation == "flying":
                air_dir.append(vessel.auto_pilot.target_direction)
                air_throt.append(vessel.control.throttle)
                if thermo.triggered and t[0] >= 6.0:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(pad_dir)
        self.assertTrue(all(d != inland_direction(INLAND_PITCH_DEG) for d in pad_dir))
        self.assertTrue(air_dir)
        self.assertEqual(air_dir[0], inland_direction(INLAND_YAW_PITCH_DEG))
        self.assertLess(air_dir[0][2], 0.0)
        self.assertIn(inland_direction(INLAND_PITCH_DEG), air_dir)
        self.assertEqual(
            vessel.auto_pilot.held, inland_direction(INLAND_PITCH_DEG)
        )
        self.assertNotEqual(
            vessel.auto_pilot.held, east_direction(INLAND_PITCH_DEG)
        )
        self.assertEqual(vessel.auto_pilot.up_reference, SURFACE_NORTH)
        self.assertEqual(vessel.auto_pilot.engage_n, 1)
        self.assertNotEqual(vessel.auto_pilot.target_heading, INLAND_HEADING_DEG)
        self.assertFalse(
            any(abs(th - WATER_SLEW_THROTTLE) < 1e-6 for th in air_throt)
        )
        self.assertTrue(any("inland" in line and "slew" in line for line in logs))
        self.assertFalse(any("east" in line and "slew" in line for line in logs))

    def test_holds_ap_inland_through_burnout(self):
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([thermo], recoverable=False)
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        dry_engaged: list[bool] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 14_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "flying":
                if vessel.resources.fuel <= 0:
                    dry_engaged.append(vessel.auto_pilot.engaged)
                if vessel.resources.fuel > 0 and t[0] >= 2.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                elif vessel.resources.fuel <= 0 and thermo.triggered and t[0] >= 4.0:
                    vessel.situation = "landed"
                    vessel._alt = 80.0
                    vessel._speed = 0.0
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan",),
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(dry_engaged)
        self.assertTrue(all(dry_engaged))
        self.assertEqual(vessel.auto_pilot.engage_n, 1)
        self.assertEqual(vessel.auto_pilot.point_n, 4)
        self.assertEqual(
            vessel.auto_pilot.held, inland_direction(INLAND_PITCH_DEG)
        )
        self.assertEqual(vessel.auto_pilot.up_reference, SURFACE_NORTH)
        self.assertNotEqual(vessel.auto_pilot.target_heading, INLAND_HEADING_DEG)
        self.assertGreater(len(dry_engaged), 1)
        self.assertTrue(any("hold inland through burnout" in line for line in logs))

    def test_blocks_inland(self):
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertIn("heading **270**", blocks)
        self.assertIn("08-29-36Z", blocks)
        self.assertIn("7.5° stayed Shores", blocks)
        self.assertIn("set_direction_and_up", blocks)
        self.assertIn("09-28-59Z", blocks)
        self.assertIn("09-44-59Z", blocks)
        self.assertIn("09-59-28Z", blocks)
        self.assertIn("10-17-18Z", blocks)
        self.assertIn("10-33-44Z", blocks)
        self.assertIn("16-47-21Z", blocks)


class TestHopToWater(unittest.TestCase):
    def setUp(self):
        _isolate_live_tickets(self)
        fh = patch("hop.hop_wants_flying_high", return_value=False)
        fh.start()
        self.addCleanup(fh.stop)

    def test_flea_refuses_without_hangar(self):
        session = _Session(None)  # type: ignore[arg-type]
        with patch("hop.hop_craft_name", return_value=CRAFT):
            with patch("hop.install_and_launch") as hangar:
                with self.assertRaises(MissionAbort) as ctx:
                    run_hop_to_water(session)
        hangar.assert_not_called()
        self.assertEqual(str(ctx.exception), HOP_TO_WATER_ABORT)
        self.assertIn("no torque", str(ctx.exception))
        self.assertIn("Shores", str(ctx.exception))

    def test_steer_gate(self):
        self.assertFalse(water_can_steer(CRAFT))
        self.assertFalse(water_can_steer("kspstuff-hop-hammer-pbc"))
        self.assertTrue(water_can_steer(WATER_CRAFT))
        self.assertTrue(water_can_steer("kspstuff-hop-valiant-t7-pbc"))
        self.assertEqual(WATER_PITCH_FROM_UP, 25.0)
        self.assertEqual(WATER_PITCH_UP, 90.0)
        self.assertEqual(WATER_PITCH_DEG, 65.0)
        self.assertEqual(WATER_PITCH_SLEW_DPS, 10.0)
        self.assertEqual(WATER_SLEW_THROTTLE, 0.4)
        self.assertEqual(WATER_HEADING_DEG, 90.0)
        self.assertTrue(hop_craft_path(WATER_CRAFT).is_file())

    def test_valiant_hangars(self):
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            with patch("hop.discover_hangar", return_value=fake):
                with patch("hop.hop_craft_name", return_value=WATER_CRAFT):
                    with patch(
                        "hop.hop_to_water_science",
                        return_value=(("temperatureScan",), ("mysteryGoo",)),
                    ):
                        with patch("hop.time.sleep"):
                            with patch(
                                "hop.run_on_vessel", return_value="recovered"
                            ) as run:
                                result = run_hop_to_water(session)
            self.assertEqual(result, "recovered")
            self.assertEqual(fake.calls[0]["name"], WATER_CRAFT)
            run.assert_called_once()
            kwargs = run.call_args.kwargs
            self.assertTrue(kwargs.get("wait_water"))
            self.assertEqual(kwargs.get("splash_ids"), ("mysteryGoo",))
            self.assertEqual(kwargs.get("science_ids"), ("temperatureScan",))

    def test_cmd_phase_skips_seat_and_aborts_flea(self):
        from main import cmd_phase
        from telem import MissionAbort

        session = _Session(_Vessel([]))
        args = argparse.Namespace(name="hop", timeout=0.0)
        with patch("hop.run_hop", side_effect=MissionAbort("flea refused")):
            with patch("missions.assert_seated") as seated:
                code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 2)

    def test_blocks_name(self):
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertIn("hop-to-water", blocks)
        self.assertIn("25", blocks)
        self.assertIn("valiant-east-pbc", blocks)
        self.assertIn("Flea still", blocks)
        self.assertIn("do not light", blocks)
        self.assertIn("PRELAUNCH is a lie", blocks)
        self.assertIn("through burnout", blocks)
        self.assertIn("after left_pad", blocks)
        self.assertIn("0.4", blocks)
        self.assertIn("16-11-58Z", blocks)
        self.assertIn("16-57-24Z", blocks)
        self.assertIn("set_direction_and_up", blocks)
        self.assertIn("22-03-59Z", blocks)
        self.assertIn("22-45-26Z", blocks)
        self.assertIn("10-11-27Z", blocks)
        self.assertIn("suicide", blocks.lower())
        self.assertIn("Retired campaign notes", blocks)

    def test_pitch_east_waits_splash(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        flying_recovered: list[bool] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "flying":
                flying_recovered.append(vessel.recovered)
                if tel.triggered:
                    vessel.recoverable = True
                if t[0] >= 5.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(flying_recovered)
        self.assertFalse(any(flying_recovered))
        self.assertEqual(
            vessel.auto_pilot.held, east_direction(WATER_PITCH_DEG)
        )
        self.assertNotEqual(vessel.auto_pilot.target_heading, WATER_HEADING_DEG)
        self.assertEqual(vessel.auto_pilot.up_reference, SURFACE_NORTH)
        self.assertFalse(vessel.auto_pilot.engaged)
        self.assertEqual(tel.triggered, ["Start Experiment"])
        self.assertEqual(goo.triggered, ["Start Experiment"])
        self.assertTrue(
            any(
                f"{WATER_PITCH_FROM_UP:g}" in line and "east" in line
                for line in logs
            )
        )

    def test_holds_ap_east_through_burnout(self):
        """15-26-18Z: do not disengage AP at fuel=0 while still flying."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        dry_engaged: list[bool] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "flying":
                if vessel.resources.fuel <= 0:
                    dry_engaged.append(vessel.auto_pilot.engaged)
                if vessel.resources.fuel > 0 and t[0] >= 2.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                elif vessel.resources.fuel <= 0 and t[0] >= 4.0:
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(dry_engaged)
        self.assertTrue(all(dry_engaged))
        self.assertFalse(vessel.auto_pilot.engaged)
        self.assertTrue(
            any("hold east through burnout" in line for line in logs)
        )

    def test_slew_east_after_pad_low_throttle(self):
        """16-11-58Z: do not slam AP 65 at light TWR 5 (bare stack shears)."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        pad_dir: list[tuple[float, float, float]] = []
        pad_engaged: list[bool] = []
        air_dir: list[tuple[float, float, float]] = []
        air_throt: list[float] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                pad_dir.append(vessel.auto_pilot.target_direction)
                pad_engaged.append(vessel.auto_pilot.engaged)
                vessel.situation = "landed"
                vessel._alt = 40.0
                vessel._speed = 20.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "landed":
                pad_dir.append(vessel.auto_pilot.target_direction)
                pad_engaged.append(vessel.auto_pilot.engaged)
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
            elif vessel.situation == "flying":
                air_dir.append(vessel.auto_pilot.target_direction)
                air_throt.append(vessel.control.throttle)
                if tel.triggered:
                    vessel.recoverable = True
                if t[0] >= 6.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(pad_dir)
        self.assertTrue(all(d != east_direction(WATER_PITCH_DEG) for d in pad_dir))
        self.assertTrue(all(not e for e in pad_engaged))
        self.assertTrue(air_dir)
        self.assertNotEqual(air_dir[0], east_direction(WATER_PITCH_UP))
        self.assertNotEqual(air_dir[0], east_direction(WATER_PITCH_DEG))
        self.assertGreater(air_dir[0][2], 0.0)
        self.assertTrue(any(abs(th - WATER_SLEW_THROTTLE) < 1e-6 for th in air_throt))
        self.assertEqual(
            vessel.auto_pilot.held, east_direction(WATER_PITCH_DEG)
        )
        self.assertEqual(vessel.auto_pilot.engage_n, 1)
        self.assertEqual(vessel.auto_pilot.up_reference, SURFACE_NORTH)
        self.assertTrue(any("slew" in line and "after pad" in line for line in logs))

    def test_east_direction_is_up_then_east(self):
        up = east_direction(WATER_PITCH_UP)
        self.assertAlmostEqual(up[0], 1.0, places=6)
        self.assertAlmostEqual(up[1], 0.0, places=6)
        self.assertAlmostEqual(up[2], 0.0, places=6)
        east = east_direction(0.0)
        self.assertAlmostEqual(east[0], 0.0, places=6)
        self.assertAlmostEqual(east[1], 0.0, places=6)
        self.assertAlmostEqual(east[2], 1.0, places=6)
        d = east_direction(WATER_PITCH_DEG)
        self.assertAlmostEqual(d[1], 0.0, places=6)
        self.assertGreater(d[2], 0.0)
        n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
        self.assertAlmostEqual(n, 1.0, places=6)

    def test_steer_east_does_not_command_roll_zero(self):
        """16-57-24Z: target_roll=0 vs zenith tumbled heading off 090."""
        vessel = _Vessel([])
        _steer_east(vessel, pitch=WATER_PITCH_UP)
        self.assertNotEqual(vessel.auto_pilot.target_heading, WATER_HEADING_DEG)
        self.assertEqual(vessel.auto_pilot.up_reference, SURFACE_NORTH)
        self.assertEqual(
            vessel.auto_pilot.held, east_direction(WATER_PITCH_UP)
        )
        self.assertFalse(vessel.auto_pilot.engaged)
        self.assertEqual(vessel.auto_pilot.engage_n, 0)
        _steer_east(vessel, pitch=WATER_PITCH_DEG)
        self.assertTrue(vessel.auto_pilot.engaged)
        self.assertEqual(vessel.auto_pilot.engage_n, 1)
        self.assertEqual(
            vessel.auto_pilot.held, east_direction(WATER_PITCH_DEG)
        )
        self.assertNotEqual(vessel.auto_pilot.target_heading, WATER_HEADING_DEG)

    def test_suicide_now_is_low_and_fast_not_apo_fall(self):
        high = type(
            "S",
            (),
            {"fuel": 40.0, "alt": 15_000.0, "speed": 215.0},
        )()
        self.assertFalse(_suicide_now(high))
        early = type(
            "S",
            (),
            {"fuel": 200.0, "alt": 37_000.0, "speed": 846.0},
        )()
        self.assertFalse(_suicide_now(early))
        self.assertGreater(37_000.0, WATER_BRAKE_ALT_MAX_M)
        low = type(
            "S",
            (),
            {"fuel": 40.0, "alt": 2_000.0, "speed": 220.0},
        )()
        self.assertTrue(_suicide_now(low))
        slow = type(
            "S",
            (),
            {"fuel": 40.0, "alt": 2_000.0, "speed": WATER_BRAKE_SPEED_M},
        )()
        self.assertFalse(_suicide_now(slow))
        lofting = type(
            "S",
            (),
            {
                "fuel": 46.0,
                "alt": 1_640.0,
                "speed": 43.3,
                "v_vert": 19.0,
            },
        )()
        self.assertFalse(_suicide_now(lofting))
        dry = type("S", (), {"fuel": 0.0, "alt": 2_000.0, "speed": 220.0})()
        self.assertFalse(_suicide_now(dry))
        early_23 = type(
            "S",
            (),
            {
                "fuel": 106.0,
                "alt": 3_750.0,
                "speed": 204.0,
                "v_vert": -194.0,
            },
        )()
        self.assertGreater(3_750.0 / 194.0, WATER_BRAKE_TTI_S)
        self.assertFalse(_suicide_now(early_23))
        crumbs = type(
            "S",
            (),
            {
                "fuel": 0.61,
                "alt": 1_050.0,
                "speed": 183.0,
                "v_vert": -183.0,
            },
        )()
        self.assertLessEqual(0.61, WATER_BRAKE_FUEL_MIN)
        self.assertFalse(_suicide_now(crumbs))
        late = type(
            "S",
            (),
            {
                "fuel": 16.6,
                "alt": 1_050.0,
                "speed": 183.0,
                "v_vert": -183.0,
            },
        )()
        self.assertTrue(_suicide_now(late))

    def test_suicide_hold_ignores_tti_until_vz_cut(self):
        """22-57-36Z: MET 181 tti 19 vz −72 must stay on; vz +19 cuts."""
        mid = type(
            "S",
            (),
            {
                "fuel": 72.6,
                "alt": 3_000.0,
                "speed": 88.0,
                "v_vert": -72.3,
            },
        )()
        self.assertGreater(3_000.0 / 88.0, WATER_BRAKE_TTI_S)
        self.assertTrue(_suicide_hold(mid))
        self.assertFalse(_suicide_now(mid))
        up = type(
            "S",
            (),
            {
                "fuel": 46.4,
                "alt": 1_642.0,
                "speed": 43.3,
                "v_vert": 19.5,
            },
        )()
        self.assertFalse(_suicide_hold(up))
        self.assertGreater(WATER_BRAKE_VZ_CUT, -72.3)

    def test_suicide_hold_does_not_predict_cut_at_minus_30(self):
        """08-44-32Z: MET 178 vz −29.9 leftover 60 stays on; +24 is a cut."""
        mid = type(
            "S",
            (),
            {
                "fuel": 60.6,
                "alt": 1_682.0,
                "speed": 31.8,
                "v_vert": -29.88,
            },
        )()
        self.assertTrue(_suicide_hold(mid))
        self.assertTrue(_suicide_hold(mid, prev_vz=-113.06, dt=1.56))
        from_23 = type(
            "S",
            (),
            {
                "fuel": 70.2,
                "alt": 3_456.0,
                "speed": 75.7,
                "v_vert": -65.16,
            },
        )()
        self.assertTrue(_suicide_hold(from_23, prev_vz=-194.4, dt=2.1))
        seen = type(
            "S",
            (),
            {
                "fuel": 47.3,
                "alt": 3_414.0,
                "speed": 38.3,
                "v_vert": 24.47,
            },
        )()
        self.assertFalse(_suicide_hold(seen))
        self.assertFalse(_suicide_now(seen))

    def test_hold_or_cut_latches_and_suicides(self):
        """22-03-59Z / T-011: do not recut 0.4 when apo falls; leftover LF later."""
        vessel = _Vessel([])
        loft = type(
            "S",
            (),
            {"apo": 19_000.0, "fuel": 100.0, "alt": 15_000.0, "speed": 200.0},
        )()
        cut, braking = _hold_or_cut(
            vessel, loft, 18_000.0, cut=False, hold=WATER_SLEW_THROTTLE, brake=True
        )
        self.assertTrue(cut)
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        fall = type(
            "S",
            (),
            {"apo": 17_000.0, "fuel": 100.0, "alt": 15_000.0, "speed": 215.0},
        )()
        cut, braking = _hold_or_cut(
            vessel, fall, 18_000.0, cut=cut, hold=WATER_SLEW_THROTTLE, brake=True
        )
        self.assertTrue(cut)
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        near = type(
            "S",
            (),
            {"apo": 2_500.0, "fuel": 40.0, "alt": 2_000.0, "speed": 220.0},
        )()
        cut, braking = _hold_or_cut(
            vessel, near, 18_000.0, cut=cut, hold=WATER_SLEW_THROTTLE, brake=True
        )
        self.assertTrue(cut)
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        self.assertGreater(_suicide_tti(near), WATER_BRAKE_LIGHT_TTI_S)
        light = type(
            "S",
            (),
            {
                "apo": 800.0,
                "fuel": 40.0,
                "alt": 700.0,
                "speed": 220.0,
                "v_vert": -220.0,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            light,
            18_000.0,
            cut=cut,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 1.0)
        hop, hop_brake = _hold_or_cut(
            vessel, near, 18_000.0, cut=True, hold=1.0, brake=False
        )
        self.assertTrue(hop)
        self.assertFalse(hop_brake)
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_hold_or_cut_suicide_holds_when_tti_rises(self):
        """22-57-36Z: do not cut leftover LF because TTI rose after the first pulse."""
        vessel = _Vessel([])
        start = type(
            "S",
            (),
            {
                "apo": 3_828.0,
                "fuel": 104.7,
                "alt": 1_954.0,
                "speed": 200.8,
                "v_vert": -184.3,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            start,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        self.assertGreater(_suicide_tti(start), WATER_BRAKE_LIGHT_TTI_S)
        risen = type(
            "S",
            (),
            {
                "apo": 2_024.0,
                "fuel": 72.6,
                "alt": 3_000.0,
                "speed": 88.0,
                "v_vert": -72.3,
            },
        )()
        self.assertGreater(3_000.0 / 88.0, WATER_BRAKE_TTI_S)
        cut, braking = _hold_or_cut(
            vessel,
            risen,
            18_000.0,
            cut=cut,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=braking,
        )
        self.assertTrue(cut)
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        lofted = type(
            "S",
            (),
            {
                "apo": 1_665.0,
                "fuel": 46.4,
                "alt": 1_642.0,
                "speed": 43.3,
                "v_vert": 19.5,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            lofted,
            18_000.0,
            cut=cut,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=braking,
        )
        self.assertTrue(cut)
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_hold_or_cut_suicide_holds_at_minus_30_then_skips_high_relight(self):
        """08-44-32Z: vz −29.9 leftover 60 stays on; tti 19 leftover is not a slam."""
        vessel = _Vessel([])
        first = type(
            "S",
            (),
            {
                "apo": 2_000.0,
                "fuel": 60.6,
                "alt": 1_682.0,
                "speed": 31.8,
                "v_vert": -29.88,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            first,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
            prev_vz=-113.06,
            dt=1.56,
        )
        self.assertTrue(cut)
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        high = type(
            "S",
            (),
            {
                "apo": 3_444.0,
                "fuel": 16.6,
                "alt": 2_526.0,
                "speed": 129.0,
                "v_vert": -125.8,
            },
        )()
        self.assertGreater(2_526.0 / 125.8, WATER_BRAKE_TTI_S)
        self.assertFalse(_suicide_now(high))
        cut, braking = _hold_or_cut(
            vessel,
            high,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=False,
        )
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        cut, braking = _hold_or_cut(
            vessel,
            high,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=False,
            hover=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 1.0)
        slam = type(
            "S",
            (),
            {
                "apo": 2_700.0,
                "fuel": 16.6,
                "alt": 1_050.0,
                "speed": 183.0,
                "v_vert": -183.0,
            },
        )()
        self.assertTrue(_suicide_now(slam))
        cut, braking = _hold_or_cut(
            vessel,
            slam,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=False,
            spent=True,
        )
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_nap_dt_bursts_while_braking(self):
        snap = type(
            "S",
            (),
            {"situation": "flying", "alt": 3_456.0, "v_vert": -65.16},
        )()
        self.assertEqual(_nap_dt(1.0, snap, braking=True), 1.0)
        self.assertAlmostEqual(
            _nap_dt(None, snap, braking=True), 1.0 / WATER_BRAKE_HZ
        )
        self.assertGreater(_nap_dt(None, snap, braking=False), 0.15)
        self.assertGreater(WATER_BRAKE_GATE_S, 1.0)

    def test_suicide_gate_cuts_at_vz_not_minus_30(self):
        """08-44-32Z leftover 60: 20 Hz gate holds through −30 and cuts at −10."""
        vessel = _Vessel([])
        vessel.resources.fuel = 60.6
        vessel._alt = 1_682.0
        vessel._speed = 31.8
        vessel._vz = -29.88
        snap = type(
            "S",
            (),
            {
                "fuel": 60.6,
                "alt": 1_682.0,
                "speed": 31.8,
                "v_vert": -29.88,
            },
        )()
        now, sleep, t = _fast_clock()

        def nap(dt):
            step = dt if dt else 1.0 / WATER_BRAKE_HZ
            thr = vessel.control.throttle
            if thr >= 1.0:
                vessel._vz += 55.0 * step
            elif thr > 0.0:
                vessel._vz = min(-8.0, vessel._vz + 8.0 * step)
            t[0] += step
            if t[0] > 0.8:
                t[0] = WATER_BRAKE_GATE_S + 1.0

        still = _suicide_gate(vessel, snap, sleep=nap, now=now, hover=True)
        self.assertTrue(still)
        self.assertGreater(vessel.control.throttle, 0.0)
        self.assertLess(vessel.control.throttle, 1.0)
        self.assertGreaterEqual(vessel._vz, WATER_BRAKE_VZ_CUT)
        self.assertLess(vessel._vz, 20.0)
        self.assertFalse(_coast_ok(snap))

    def test_suicide_light_is_tti_3_5_not_watch_12(self):
        """09-48 MET 175 alt 2378 vz −223 is watch; light at TTI ≤ 3.5."""
        watch = type(
            "S",
            (),
            {
                "fuel": 110.1,
                "alt": 2_377.7,
                "speed": 223.8,
                "v_vert": -223.0,
            },
        )()
        light = type(
            "S",
            (),
            {
                "fuel": 110.1,
                "alt": 700.0,
                "speed": 223.8,
                "v_vert": -223.0,
            },
        )()
        recut = type(
            "S",
            (),
            {
                "fuel": 50.41,
                "alt": 1_674.9,
                "speed": 11.6,
                "v_vert": -7.7,
            },
        )()
        self.assertEqual(WATER_BRAKE_LIGHT_TTI_S, 3.5)
        self.assertLessEqual(_suicide_tti(watch), WATER_BRAKE_TTI_S)
        self.assertTrue(_suicide_now(watch))
        self.assertFalse(_suicide_light(watch))
        self.assertTrue(_suicide_light(light))
        self.assertGreater(_suicide_tti(recut), WATER_BRAKE_TTI_S)
        self.assertFalse(_suicide_now(recut))
        self.assertTrue(_suicide_need(recut))
        self.assertTrue(_suicide_now(recut, hover=True))
        rebuild = type(
            "S",
            (),
            {
                "fuel": 50.41,
                "alt": 1_659.2,
                "speed": 21.5,
                "v_vert": -20.1,
            },
        )()
        self.assertTrue(_suicide_now(rebuild, hover=True))
        self.assertFalse(_suicide_light(rebuild))

    def test_hold_or_cut_09_48_watch_not_thr1_until_light_or_hover(self):
        """09-48: TTI 11 dump is watch; leftover 50 at vz −20 hovers without TTI≤12."""
        vessel = _Vessel([])
        watch = type(
            "S",
            (),
            {
                "apo": 4_911.0,
                "fuel": 110.1,
                "alt": 2_377.7,
                "speed": 223.8,
                "v_vert": -223.0,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            watch,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        recut = type(
            "S",
            (),
            {
                "apo": 1_676.8,
                "fuel": 50.41,
                "alt": 1_674.9,
                "speed": 11.6,
                "v_vert": -7.7,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            recut,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
            hover=True,
        )
        self.assertTrue(braking)
        self.assertAlmostEqual(
            vessel.control.throttle, WATER_BRAKE_HOVER_THROTTLE
        )
        self.assertFalse(_coast_ok(recut))
        rebuild = type(
            "S",
            (),
            {
                "apo": 1_676.7,
                "fuel": 50.41,
                "alt": 1_659.2,
                "speed": 21.5,
                "v_vert": -20.1,
            },
        )()
        self.assertGreater(_suicide_tti(rebuild), WATER_BRAKE_TTI_S)
        cut, braking = _hold_or_cut(
            vessel,
            rebuild,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=False,
            hover=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 1.0)

    def test_suicide_gate_waits_light_tti_then_holds_through_minus_30(self):
        """09-48: do not throttle 1 at TTI 11; 08-44: once lit, hold through −30."""
        vessel = _Vessel([])
        vessel.resources.fuel = 110.1
        vessel._alt = 2_377.7
        vessel._speed = 223.8
        vessel._vz = -223.0
        watch = type(
            "S",
            (),
            {
                "fuel": 110.1,
                "alt": 2_377.7,
                "speed": 223.8,
                "v_vert": -223.0,
            },
        )()
        now, sleep, t = _fast_clock()
        seen = []

        def wait_nap(dt):
            step = dt if dt else 1.0 / WATER_BRAKE_HZ
            seen.append(vessel.control.throttle)
            vessel._alt = max(1.0, vessel._alt + vessel._vz * step)
            t[0] += step
            if t[0] > 0.2:
                t[0] = WATER_BRAKE_GATE_S + 1.0

        still = _suicide_gate(vessel, watch, sleep=wait_nap, now=now)
        self.assertTrue(still)
        self.assertTrue(seen)
        self.assertTrue(all(thr == 0.0 for thr in seen))
        self.assertEqual(vessel.control.throttle, 0.0)

        vessel.resources.fuel = 110.1
        vessel._alt = 700.0
        vessel._speed = 223.8
        vessel._vz = -223.0
        light = type(
            "S",
            (),
            {
                "fuel": 110.1,
                "alt": 700.0,
                "speed": 223.8,
                "v_vert": -223.0,
            },
        )()
        self.assertTrue(_suicide_light(light))
        now, sleep, t = _fast_clock()
        lit = []

        def burn_nap(dt):
            step = dt if dt else 1.0 / WATER_BRAKE_HZ
            lit.append(vessel.control.throttle)
            if vessel.control.throttle >= 1.0:
                vessel._vz += 55.0 * step
            t[0] += step

        still = _suicide_gate(vessel, light, sleep=burn_nap, now=now)
        self.assertIn(1.0, lit)
        self.assertGreaterEqual(vessel._vz, WATER_BRAKE_VZ_CUT)
        self.assertLess(vessel._vz, 20.0)
        self.assertFalse(_coast_ok(light))
        self.assertTrue(still or vessel.control.throttle == 0.0)

    def test_suicide_gate_09_48_hover_relights_without_tti12(self):
        """09-48 leftover 50 at vz −20 must throttle 1 even when TTI is 83 s."""
        vessel = _Vessel([])
        vessel.resources.fuel = 50.41
        vessel._alt = 1_659.2
        vessel._speed = 21.5
        vessel._vz = -20.1
        rebuild = type(
            "S",
            (),
            {
                "fuel": 50.41,
                "alt": 1_659.2,
                "speed": 21.5,
                "v_vert": -20.1,
            },
        )()
        self.assertGreater(_suicide_tti(rebuild), WATER_BRAKE_TTI_S)
        now, sleep, t = _fast_clock()
        lit = []

        def burn_nap(dt):
            step = dt if dt else 1.0 / WATER_BRAKE_HZ
            lit.append(vessel.control.throttle)
            if vessel.control.throttle >= 1.0:
                vessel._vz += 55.0 * step
            t[0] += step

        still = _suicide_gate(
            vessel, rebuild, sleep=burn_nap, now=now, hover=True
        )
        self.assertIn(1.0, lit)
        self.assertGreaterEqual(vessel._vz, WATER_BRAKE_VZ_CUT)
        self.assertFalse(_coast_ok(rebuild))
        self.assertTrue(still or vessel.control.throttle == 0.0)

    def test_suicide_10_11_crumbs_at_195_do_not_rebuild(self):
        """10-11-27Z: MET 208.9 crumbs 1.98 vz −9.4 alt 195 is not a hover."""
        crumbs = type(
            "S",
            (),
            {
                "fuel": 1.98,
                "alt": 195.3,
                "speed": 9.2,
                "v_vert": -9.4,
            },
        )()
        leftover = type(
            "S",
            (),
            {
                "fuel": 40.0,
                "alt": 195.3,
                "speed": 9.2,
                "v_vert": -9.4,
            },
        )()
        self.assertGreater(_coast_impact_ms(crumbs), GOO_CRASH_MS)
        self.assertFalse(_coast_ok(crumbs))
        self.assertFalse(_suicide_need(crumbs))
        self.assertFalse(_suicide_now(crumbs, hover=True))
        self.assertTrue(_suicide_need(leftover))
        self.assertTrue(_suicide_now(leftover, hover=True))
        self.assertFalse(_suicide_hold(leftover))
        vessel = _Vessel([])
        cut, braking = _hold_or_cut(
            vessel,
            leftover,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
            hover=True,
        )
        self.assertTrue(braking)
        self.assertAlmostEqual(
            vessel.control.throttle, WATER_BRAKE_HOVER_THROTTLE
        )
        self.assertGreater(_hover_throttle(vessel), 0.0)
        self.assertLess(_hover_throttle(vessel), 1.0)
        vessel.resources.fuel = 40.0
        vessel._alt = 195.3
        vessel._speed = 9.2
        vessel._vz = -9.4
        now, sleep, t = _fast_clock()
        seen = []

        def nap(dt):
            step = dt if dt else 1.0 / WATER_BRAKE_HZ
            seen.append(vessel.control.throttle)
            thr = vessel.control.throttle
            if thr >= 1.0:
                vessel._vz += 55.0 * step
            elif thr > 0.0:
                vessel._vz = min(-8.0, vessel._vz + 4.0 * step)
                vessel._alt = max(2.0, vessel._alt + vessel._vz * step)
            t[0] += step
            if t[0] > 0.4:
                t[0] = WATER_BRAKE_GATE_S + 1.0

        still = _suicide_gate(
            vessel, leftover, sleep=nap, now=now, hover=True
        )
        self.assertTrue(still)
        self.assertTrue(seen)
        self.assertNotIn(1.0, seen)
        self.assertGreater(max(seen), 0.0)
        self.assertLess(vessel._vz, 0.0)
        crumbs_cut, crumbs_brake = _hold_or_cut(
            vessel,
            crumbs,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
            hover=True,
        )
        self.assertFalse(crumbs_brake)
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_suicide_throttle_kill_then_hover(self):
        """Kill is throttle 1; vz-cut with leftover is TWR≈1, not slam 1."""
        vessel = _Vessel([])
        kill = type(
            "S",
            (),
            {
                "fuel": 108.7,
                "alt": 2_415.1,
                "speed": 223.6,
                "v_vert": -222.5,
            },
        )()
        band = type(
            "S",
            (),
            {
                "fuel": 40.0,
                "alt": 195.3,
                "speed": 9.2,
                "v_vert": -9.4,
            },
        )()
        self.assertEqual(_suicide_throttle(vessel, kill, lit=False), 0.0)
        self.assertEqual(_suicide_throttle(vessel, kill, lit=True), 1.0)
        self.assertAlmostEqual(
            _suicide_throttle(vessel, band, lit=True),
            WATER_BRAKE_HOVER_THROTTLE,
        )
        self.assertGreater(WATER_BRAKE_LIGHT_PAD_M, 0.0)
        self.assertLess(WATER_BRAKE_LIGHT_PAD_M, 195.0)

    def test_coast_ok_is_goo_crash_not_vz_cut(self):
        """09-11 recut 1766/−19 and 08-44 1682/−30 coast well above Goo 12."""
        recut_09 = type(
            "S",
            (),
            {
                "fuel": 57.1,
                "alt": 1_766.0,
                "speed": 20.1,
                "v_vert": -19.31,
            },
        )()
        recut_08 = type(
            "S",
            (),
            {
                "fuel": 60.6,
                "alt": 1_682.0,
                "speed": 31.8,
                "v_vert": -29.88,
            },
        )()
        near = type(
            "S",
            (),
            {
                "fuel": 40.0,
                "alt": 2.0,
                "speed": 8.2,
                "v_vert": -8.0,
            },
        )()
        loft = type(
            "S",
            (),
            {
                "fuel": 30.3,
                "alt": 910.0,
                "speed": 7.4,
                "v_vert": 2.71,
            },
        )()
        self.assertEqual(GOO_CRASH_MS, 12.0)
        self.assertGreater(WATER_BRAKE_VZ_CUT, -GOO_CRASH_MS)
        self.assertGreater(_coast_impact_ms(recut_09), 80.0)
        self.assertFalse(_coast_ok(recut_09))
        self.assertGreater(_coast_impact_ms(recut_08), 80.0)
        self.assertFalse(_coast_ok(recut_08))
        self.assertLessEqual(_coast_impact_ms(near), GOO_CRASH_MS)
        self.assertTrue(_coast_ok(near))
        self.assertFalse(_coast_ok(loft))

    def test_hold_or_cut_hover_slam_leftover_57_until_coast_ok(self):
        """09-11 leftover 57 at vz −19 is hover-slam, not TTI pulse or spent-cut."""
        vessel = _Vessel([])
        arm = type(
            "S",
            (),
            {
                "apo": 4_982.0,
                "fuel": 114.1,
                "alt": 2_462.0,
                "speed": 223.5,
                "v_vert": -222.5,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            arm,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        recut = type(
            "S",
            (),
            {
                "apo": 1_782.0,
                "fuel": 57.1,
                "alt": 1_766.0,
                "speed": 20.1,
                "v_vert": -19.31,
            },
        )()
        self.assertLess(recut.v_vert, WATER_BRAKE_VZ_CUT)
        self.assertFalse(_coast_ok(recut))
        cut, braking = _hold_or_cut(
            vessel,
            recut,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        at_cut = type(
            "S",
            (),
            {
                "apo": 1_760.0,
                "fuel": 50.0,
                "alt": 1_750.0,
                "speed": 9.5,
                "v_vert": -9.5,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            at_cut,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
            hover=True,
        )
        self.assertTrue(braking)
        self.assertAlmostEqual(
            vessel.control.throttle, WATER_BRAKE_HOVER_THROTTLE
        )
        self.assertFalse(_coast_ok(at_cut))
        rebuild = type(
            "S",
            (),
            {
                "apo": 1_763.0,
                "fuel": 57.1,
                "alt": 1_158.0,
                "speed": 110.1,
                "v_vert": -110.3,
            },
        )()
        self.assertLessEqual(1_158.0 / 110.3, WATER_BRAKE_TTI_S)
        self.assertTrue(_suicide_now(rebuild))
        self.assertTrue(_suicide_now(rebuild, hover=True))
        self.assertFalse(_suicide_now(rebuild, spent=True))
        cut, braking = _hold_or_cut(
            vessel,
            rebuild,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=False,
            hover=True,
        )
        self.assertTrue(braking)
        self.assertEqual(vessel.control.throttle, 1.0)
        near = type(
            "S",
            (),
            {
                "apo": 8.0,
                "fuel": 40.0,
                "alt": 2.0,
                "speed": 8.2,
                "v_vert": -8.0,
            },
        )()
        self.assertTrue(_coast_ok(near))
        self.assertFalse(_suicide_now(near, hover=True))
        cut, braking = _hold_or_cut(
            vessel,
            near,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=True,
        )
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        pulse = type(
            "S",
            (),
            {
                "apo": 593.0,
                "fuel": 13.8,
                "alt": 443.0,
                "speed": 55.2,
                "v_vert": -55.5,
            },
        )()
        cut, braking = _hold_or_cut(
            vessel,
            pulse,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=False,
            spent=True,
        )
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)
        crumbs = type(
            "S",
            (),
            {
                "apo": 345.0,
                "fuel": 1.16,
                "alt": 333.0,
                "speed": 16.5,
                "v_vert": -16.8,
            },
        )()
        self.assertFalse(_suicide_now(crumbs))
        self.assertFalse(_suicide_now(crumbs, hover=True))
        cut, braking = _hold_or_cut(
            vessel,
            crumbs,
            18_000.0,
            cut=True,
            hold=WATER_SLEW_THROTTLE,
            brake=True,
            braking=False,
            hover=True,
        )
        self.assertFalse(braking)
        self.assertEqual(vessel.control.throttle, 0.0)

    def test_suicide_hold_cuts_seen_plus_vz(self):
        """08-44-32Z MET 188.9 vz +2.7 is a cut, not a leftover loft."""
        up = type(
            "S",
            (),
            {
                "fuel": 30.3,
                "alt": 910.0,
                "speed": 7.4,
                "v_vert": 2.71,
            },
        )()
        self.assertFalse(_suicide_hold(up))
        self.assertFalse(_suicide_now(up))
        loft = type(
            "S",
            (),
            {
                "fuel": 8.46,
                "alt": 967.0,
                "speed": 85.9,
                "v_vert": 85.18,
            },
        )()
        self.assertFalse(_suicide_hold(loft))
        self.assertFalse(_suicide_now(loft))

    def test_wait_water_does_not_recut_then_suicides(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        coast_throt: list[float] = []
        seen_brake = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 15_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 19_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = WATER_SLEW_THROTTLE
                vessel.resources.fuel = 50.0
            elif vessel.situation == "flying":
                if vessel.orbit.apoapsis_altitude >= 18_000.0:
                    self.assertEqual(vessel.control.throttle, 0.0)
                    vessel.orbit.apoapsis_altitude = 12_000.0
                    vessel._alt = 12_000.0
                    vessel._speed = 80.0
                elif vessel._alt > 3_000.0:
                    coast_throt.append(vessel.control.throttle)
                    vessel._alt = 2_000.0
                    vessel._speed = 220.0
                    vessel.resources.fuel = 40.0
                    vessel.orbit.apoapsis_altitude = 2_500.0
                elif vessel.control.throttle >= 0.99:
                    seen_brake.append(True)
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch("phases._kv", return_value={"hop_apo": "18000"}):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                splash_ids=("mysteryGoo",),
                wait_water=True,
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(coast_throt)
        self.assertTrue(all(th == 0.0 for th in coast_throt))
        self.assertTrue(seen_brake)
        self.assertTrue(any("suicide leftover LF" in line for line in logs))
        self.assertEqual(vessel.auto_pilot.target_pitch, WATER_PITCH_UP)

    def test_landed_aborts_not_splashed(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([tel], recoverable=True, sit="pre_launch")
        vessel.name = WATER_CRAFT
        now, sleep, t = _fast_clock()

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
            elif vessel.situation == "flying" and tel.triggered:
                vessel.situation = "landed"
                vessel._alt = 80.0
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with self.assertRaises(MissionAbort) as ctx:
            run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("kerbalism_TELEMETRY",),
                splash_ids=("mysteryGoo",),
                wait_water=True,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertIn("not splashed", str(ctx.exception))
        self.assertFalse(vessel.recovered)

    def test_pad_landed_after_light_is_not_shores(self):
        """14-45-33Z: KSP sit=landed on pad hop-off is not a Shores miss."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "landed"
                vessel._alt = 97.0
                vessel._speed = 49.2
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
                vessel.thrust = 89_000.0
            elif vessel.situation == "landed":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 12_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
            elif vessel.situation == "flying":
                if tel.triggered:
                    vessel.recoverable = True
                if t[0] >= 3.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed" and goo.triggered:
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
                vessel.recoverable = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertGreaterEqual(vessel.control.staged, 1)
        self.assertTrue(any("pitch" in line and "east" in line for line in logs))
        self.assertFalse(any("not splashed" in line for line in logs))

    def test_leftover_wreck_fuel0_does_not_light_or_science(self):
        """14-52-25Z: leftover flying MET 13.8 fuel=0 is crash UI, not a pad."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([tel, thermo], sit="flying", ec=9.3, recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.met = 13.8
        vessel._alt = 83.2
        vessel._speed = 0.0
        vessel.thrust = 0.0
        vessel.resources.fuel = 0.0
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel]),
                _Part("sensorThermometer", [thermo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        with patch("hop.go_space_center") as scene:
            with self.assertRaises(MissionAbort) as ctx:
                run_on_vessel(
                    _Session(vessel),
                    vessel,
                    science_ids=("temperatureScan", "kerbalism_TELEMETRY"),
                    splash_ids=("mysteryGoo",),
                    wait_water=True,
                    on_log=logs.append,
                    now=now,
                    sleep=sleep,
                    timeout=30.0,
                    pulse=1.0,
                )
        self.assertIn("not recoverable", str(ctx.exception))
        self.assertFalse(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(tel.triggered, [])
        self.assertEqual(thermo.triggered, [])
        scene.assert_not_called()
        self.assertTrue(any("do not light" in line for line in logs))
        self.assertTrue(
            any("sit=flying" in line and "fuel=0.0" in line for line in logs)
        )
        self.assertNotIn("hop airborne", logs)
        self.assertFalse(any(line.startswith("science ") for line in logs))
        self.assertIn("hop crash ui tracking (not pad reload)", logs)
        self.assertNotIn("hop dismissed crash ui", logs)
        self.assertLess(t[0], 5.0)

    def test_leftover_wreck_recoverable_recovers_without_science(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([tel], sit="flying", ec=9.3, recoverable=True)
        vessel.name = WATER_CRAFT
        vessel.met = 13.8
        vessel._alt = 83.2
        vessel._speed = 0.0
        vessel.resources.fuel = 0.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("kerbalism_TELEMETRY",),
            splash_ids=("mysteryGoo",),
            wait_water=True,
            on_log=logs.append,
            now=now,
            sleep=sleep,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(tel.triggered, [])
        self.assertTrue(any("do not light" in line for line in logs))
        self.assertLess(t[0], 2.0)

    def test_leftover_splashed_starts_card_before_recover(self):
        """18-03-12Z: leftover sit=splashed EC=0 recoverable — start splash, not dark recover."""
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        vessel = _Vessel([tel, goo], sit="splashed", ec=0.0, recoverable=True)
        vessel.name = SPLASH_CRAFT
        vessel.met = 532.18
        vessel._alt = 0.6
        vessel._speed = 0.0
        vessel.resources.fuel = 0.0
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        order: list[str] = []

        def nap(dt):
            if tel.triggered and "tel" not in order:
                order.append("tel")
                tel.fields["status"] = "Done"
                tel.fields["Has Data"] = True
            elif goo.triggered:
                if "goo" not in order:
                    order.append("goo")
                goo.fields["status"] = "Done"
                goo.fields["Has Data"] = True
            t[0] += dt if dt else 0.01

        result = run_on_vessel(
            _Session(vessel),
            vessel,
            science_ids=("temperatureScan", "kerbalism_TELEMETRY"),
            splash_ids=("kerbalism_TELEMETRY", "mysteryGoo"),
            wait_splash=True,
            on_log=logs.append,
            now=now,
            sleep=nap,
            timeout=30.0,
            pulse=1.0,
        )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(order, ["tel", "goo"])
        self.assertFalse(any("do not light" in line for line in logs))
        self.assertTrue(any(line.startswith("science ") for line in logs))

    def test_hop_to_water_splashed_leftover_recovers_then_hangars(self):
        """22-45-26Z: matching sit=splashed fuel=0 recoverable — abort ksc leftover."""
        leftover = _Vessel([], sit="splashed", ec=0.0, recoverable=True)
        leftover.name = WATER_CRAFT
        leftover.met = 212.2
        leftover.resources.fuel = 0.0
        leftover.parts = _Parts([])
        fresh = _Vessel([], sit="pre_launch", recoverable=False)
        fresh.name = WATER_CRAFT
        fresh.resources.fuel = 5.0
        session = _Session(leftover)
        logs: list[str] = []

        def hangar_launch(sess, **_kw):
            sess.active_vessel = fresh
            sess.space_center.vessels = [fresh]

        with patch("hop.hop_craft_name", return_value=WATER_CRAFT):
            with patch("hop.hop_match_name", return_value=WATER_CRAFT):
                with patch(
                    "hop.hop_to_water_science",
                    return_value=(("kerbalism_TELEMETRY",), ("mysteryGoo",)),
                ):
                    with patch(
                        "hop.install_and_launch", side_effect=hangar_launch
                    ) as hangar:
                        with patch(
                            "hop.wait_vessel_ready", return_value="hangar ready"
                        ):
                            with patch("hop.go_space_center") as scene:
                                with patch("hop._wait_vessel_gone"):
                                    with patch(
                                        "hop.run_on_vessel",
                                        return_value="recovered",
                                    ) as run:
                                        with self.assertRaises(MissionAbort) as ctx:
                                            run_hop_to_water(
                                                session, on_log=logs.append
                                            )
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertIn("recover-probe --recover", str(ctx.exception))
        self.assertFalse(leftover.recovered)
        self.assertEqual(leftover.control.staged, 0)
        hangar.assert_not_called()
        run.assert_not_called()
        scene.assert_not_called()
        self.assertTrue(any("ksc leftover" in line or "ksc: leftover" in line for line in logs))
        self.assertTrue(any("sit=splashed" in line for line in logs))

    def test_hop_to_water_leftover_wreck_does_not_hangar(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        vessel = _Vessel([tel], sit="flying", ec=9.3, recoverable=False)
        vessel.name = WATER_CRAFT
        vessel.met = 13.8
        vessel._alt = 83.2
        vessel._speed = 0.0
        vessel.resources.fuel = 0.0
        session = _Session(vessel)
        with patch("hop.hop_craft_name", return_value=WATER_CRAFT):
            with patch("hop.hop_match_name", return_value=WATER_CRAFT):
                with patch(
                    "hop.hop_to_water_science",
                    return_value=(("kerbalism_TELEMETRY",), ("mysteryGoo",)),
                ):
                    with patch("hop.install_and_launch") as hangar:
                        with patch("hop.go_space_center"):
                            with patch("hop.time.sleep"):
                                with self.assertRaises(MissionAbort) as ctx:
                                    run_hop_to_water(session)
        self.assertIn("not recoverable", str(ctx.exception))
        hangar.assert_not_called()
        self.assertEqual(vessel.control.staged, 0)
        self.assertEqual(tel.triggered, [])

    def test_leftover_wreck_predicate_dry_flying(self):
        snap = type(
            "S",
            (),
            {
                "situation": "flying",
                "fuel": 0.0,
                "q": 0.0,
                "speed": 0.0,
            },
        )()
        vessel = _Vessel([], sit="flying", recoverable=False)
        self.assertTrue(leftover_wreck_before_light(snap, vessel))
        snap.fuel = 5.0
        self.assertFalse(leftover_wreck_before_light(snap, vessel))
        snap.fuel = 0.0
        snap.speed = 80.0
        snap.q = 1200.0
        self.assertFalse(leftover_wreck_before_light(snap, vessel))
        pad = type("S", (), {"situation": "pre_launch", "fuel": 0.0, "q": 0.0, "speed": 0.0})()
        self.assertTrue(leftover_wreck_before_light(pad, vessel))
        pad.fuel = 5.0
        self.assertFalse(leftover_wreck_before_light(pad, vessel))


class TestKscLeftoverAbort(unittest.TestCase):
    def test_recoverable_calls_recover_probe(self):
        self.assertEqual(
            leftover_ksc_call(True),
            "python main.py recover-probe --recover",
        )
        self.assertEqual(
            leftover_ksc_call(False),
            "python main.py recover-probe --space-center",
        )

    def test_abort_prints_kv_and_does_not_recover(self):
        vessel = _Vessel([], sit="splashed", recoverable=True)
        logs: list[str] = []
        with self.assertRaises(MissionAbort) as ctx:
            abort_ksc_leftover(vessel, logs.append)
        self.assertFalse(vessel.recovered)
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertEqual(logs[0], "ksc: leftover")
        self.assertEqual(logs[1], "sit: splashed")
        self.assertEqual(logs[2], "recoverable: yes")
        self.assertEqual(logs[3], "call: python main.py recover-probe --recover")


class TestWaitVesselGone(unittest.TestCase):
    def test_returns_when_pool_empty(self):
        session = type(
            "S", (), {"space_center": type("C", (), {"vessels": []})()}
        )()
        vessel = _Vessel([], sit="pre_launch", recoverable=True)
        logs: list[str] = []
        with patch("hop._vessel_live", return_value=False):
            with patch("hop._pool", return_value=[]):
                _wait_vessel_gone(session, vessel, logs.append, timeout=1.0)
        self.assertTrue(any("gone" in line for line in logs))


class TestHopSplash(unittest.TestCase):
    def setUp(self):
        _isolate_live_tickets(self)

    def test_flea_refuses_without_hangar(self):
        session = _Session(None)  # type: ignore[arg-type]
        with patch("hop.hop_craft_name", return_value=CRAFT):
            with patch("hop.install_and_launch") as hangar:
                with self.assertRaises(MissionAbort) as ctx:
                    run_hop_splash(session)
        hangar.assert_not_called()
        self.assertEqual(str(ctx.exception), HOP_SPLASH_ABORT)

    def test_valiant_hangars_vertical(self):
        with tempfile.TemporaryDirectory() as raw:
            fake = _FakeHangar(Path(raw))
            session = _Session(None)  # type: ignore[arg-type]
            session.active_vessel = None
            with patch("hop.discover_hangar", return_value=fake):
                with patch("hop.hop_craft_name", return_value=SPLASH_CRAFT):
                    with patch(
                        "hop.hop_splash_science",
                        return_value=("kerbalism_TELEMETRY", "mysteryGoo"),
                    ):
                        with patch("hop.time.sleep"):
                            with patch(
                                "hop.run_on_vessel", return_value="recovered"
                            ) as run:
                                result = run_hop_splash(session)
        self.assertEqual(result, "recovered")
        self.assertEqual(fake.calls[0]["name"], SPLASH_CRAFT)
        kwargs = run.call_args.kwargs
        self.assertTrue(kwargs.get("wait_splash"))
        self.assertFalse(kwargs.get("wait_water"))
        self.assertEqual(kwargs.get("science_ids"), ())
        self.assertEqual(
            kwargs.get("splash_ids"),
            ("kerbalism_TELEMETRY", "mysteryGoo"),
        )

    def test_cmd_phase_skips_seat_and_aborts_flea(self):
        from main import cmd_phase
        from telem import MissionAbort

        session = _Session(_Vessel([]))
        args = argparse.Namespace(name="hop", timeout=0.0)
        with patch("hop.run_hop", side_effect=MissionAbort("flea refused")):
            with patch("missions.assert_seated") as seated:
                code = cmd_phase(session, args)
        seated.assert_not_called()
        self.assertEqual(code, 2)

    def test_leftover_wreck_aborts_ksc_leftover(self):
        leftover = _Vessel([], sit="pre_launch", recoverable=True)
        leftover.name = SPLASH_CRAFT
        leftover.parts = _Parts([])
        session = _Session(leftover)
        logs: list[str] = []
        with patch("hop.hop_craft_name", return_value=SPLASH_CRAFT):
            with patch("hop.hop_match_name", return_value=SPLASH_CRAFT):
                with patch(
                    "hop.hop_splash_science",
                    return_value=("kerbalism_TELEMETRY", "mysteryGoo"),
                ):
                    with patch("hop.install_and_launch") as hangar:
                        with patch("hop.go_space_center") as scene:
                            with self.assertRaises(MissionAbort) as ctx:
                                run_hop_splash(session, on_log=logs.append)
        self.assertIn("ksc leftover", str(ctx.exception))
        self.assertFalse(leftover.recovered)
        hangar.assert_not_called()
        scene.assert_not_called()
        self.assertTrue(any("ksc: leftover" in line for line in logs))

    def test_blocks_name(self):
        blocks = Path("docs/program/blocks.md").read_text(encoding="utf-8")
        self.assertIn("hop-splash", blocks)
        self.assertIn("t7-splash", blocks)
        self.assertIn("east slew", blocks)
        self.assertIn("80 km", blocks)
        self.assertIn("east-fin PRELAUNCH", blocks)
        self.assertIn("stay cut", blocks)
        self.assertIn("suicide", blocks.lower())
        self.assertIn("Retired campaign notes", blocks)

    def test_vertical_no_east_no_flying_toggle(self):
        tel = _Mod("Experiment", "kerbalism_TELEMETRY")
        goo = _Mod("Experiment", "mysteryGoo")
        thermo = _Mod("Experiment", "temperatureScan")
        vessel = _Vessel([tel, goo, thermo], recoverable=False)
        vessel.name = SPLASH_CRAFT
        vessel.parts = _Parts(
            [
                _Part("probeCoreSphere.v2", [tel, thermo]),
                _Part("GooExperiment", [goo]),
            ]
        )
        now, sleep, t = _fast_clock()
        logs: list[str] = []
        flying_recovered: list[bool] = []
        air_heading: list[float] = []
        order: list[str] = []

        def nap(dt):
            if vessel.control.staged and vessel.situation == "pre_launch":
                vessel.situation = "flying"
                vessel._alt = 2_000.0
                vessel._speed = 80.0
                vessel.orbit.apoapsis_altitude = 40_000.0
                vessel.orbit.periapsis_altitude = -6_000_000.0
                vessel.control.throttle = 1.0
                vessel.resources.fuel = 5.0
            elif vessel.situation == "flying":
                flying_recovered.append(vessel.recovered)
                air_heading.append(vessel.auto_pilot.target_heading)
                if tel.triggered and "tel" not in order:
                    order.append("tel-air")
                if t[0] >= 5.0:
                    vessel.control.throttle = 0.0
                    vessel.resources.fuel = 0.0
                    vessel.situation = "splashed"
                    vessel._alt = 0.0
                    vessel._speed = 0.0
            elif vessel.situation == "splashed":
                if tel.triggered and "tel" not in order:
                    order.append("tel")
                    tel.fields["status"] = "Done"
                    tel.fields["Has Data"] = True
                elif goo.triggered:
                    if "goo" not in order:
                        order.append("goo")
                    goo.fields["status"] = "Done"
                    goo.fields["Has Data"] = True
                    vessel.recoverable = True
            t[0] += dt if dt else 0.01

        with patch(
            "phases._kv",
            return_value={"hop_apo": "80000", "phase": "hop-splash"},
        ):
            result = run_on_vessel(
                _Session(vessel),
                vessel,
                science_ids=("temperatureScan", "kerbalism_TELEMETRY"),
                splash_ids=("kerbalism_TELEMETRY", "mysteryGoo"),
                wait_splash=True,
                on_log=logs.append,
                now=now,
                sleep=nap,
                timeout=30.0,
                pulse=1.0,
            )
        self.assertEqual(result, "recovered")
        self.assertTrue(vessel.recovered)
        self.assertTrue(flying_recovered)
        self.assertFalse(any(flying_recovered))
        self.assertFalse(thermo.triggered)
        self.assertNotIn("tel-air", order)
        self.assertEqual(order, ["tel", "goo"])
        self.assertFalse(any(h == WATER_HEADING_DEG for h in air_heading))
        self.assertNotEqual(vessel.auto_pilot.target_heading, WATER_HEADING_DEG)
        self.assertTrue(any("no flying Toggle" in line for line in logs))
        self.assertFalse(any("east" in line and "slew" in line for line in logs))

    def test_splash_card_empty_flying(self):
        text = (
            "## Splash\n"
            "- experiment: kerbalism_TELEMETRY\n"
            "  situation: SrfSplashed\n"
            "- experiment: mysteryGoo\n"
            "  situation: SrfSplashed\n"
        )
        from card import card_flying_ids, card_splash_ids

        self.assertEqual(card_flying_ids(text), ())
        self.assertEqual(
            card_splash_ids(text),
            ("kerbalism_TELEMETRY", "mysteryGoo"),
        )
        path = Path(tempfile.mkdtemp()) / "science.md"
        path.write_text(text, encoding="utf-8")
        with patch("tickets.science_ids_for", return_value=()):
            with patch("missions.seated_science_path", return_value=path):
                self.assertEqual(
                    hop_splash_science(),
                    ("kerbalism_TELEMETRY", "mysteryGoo"),
                )
        self.assertTrue(hop_craft_path(SPLASH_CRAFT).is_file())
        self.assertTrue(water_can_steer(SPLASH_CRAFT))
