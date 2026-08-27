"""Orbit ascent compose + RF live throttle blocks. Not hop.py envelopes."""

from __future__ import annotations

from pathlib import Path

import rf_throttle as RF
from hop import WATER_HEADING_DEG, WATER_PITCH_DEG, WATER_PITCH_UP
from ascent import (
    circularize_sit,
    hold_live,
    keep_live_sit,
    light,
    loft_lid_sit,
    loft_meco_sit,
    lofted_wait_sit,
    orbit_done_sit,
    space_low_sit,
    stage_sit,
    turn_cmd_pitch,
    turn_live_sit,
    vacuum_stage_sit,
)


class _NoopControl:
    """UI MainThrottle writes do nothing. RF live must still move."""

    def __init__(self):
        object.__setattr__(self, "throttle", 0.0)
        object.__setattr__(self, "sas", False)
        object.__setattr__(self, "staged", 0)

    def activate_next_stage(self):
        self.staged += 1

    def __setattr__(self, name, value):
        if name == "throttle":
            return
        object.__setattr__(self, name, value)


class _Control:
    def __init__(self):
        self.throttle = 0.0
        self.sas = False
        self.staged = 0

    def activate_next_stage(self):
        self.staged += 1


class _Mod:
    def __init__(self, engine: "_RfEngine"):
        self.name = "ModuleEnginesRF"
        self._engine = engine

    def get_field_by_id(self, key: str):
        if key == "independentThrottlePercentage":
            return self._engine.pct
        if key == "ignitions":
            return self._engine.ignitions
        if key == "currentThrottle":
            return self._engine.actual
        raise ValueError(key)

    def set_field_float_by_id(self, key: str, value: float):
        if key != "independentThrottlePercentage":
            raise ValueError(key)
        self._engine.pct = float(value)


class _Part:
    def __init__(self, engine: "_RfEngine", *, name: str = "restock-engine-125-valiant"):
        self.modules = [_Mod(engine)]
        self.name = name


class _RfEngine:
    def __init__(self, *, name: str = "restock-engine-125-valiant"):
        self._independent = False
        self.pct = 0.0
        self.actual = 0.0
        self.ignitions = 1
        self.active = False
        self.independent_sets = 0
        self.thrust = 0.0
        self.name = name
        self.part = _Part(self, name=name)

    @property
    def independent_throttle(self):
        return self._independent

    @independent_throttle.setter
    def independent_throttle(self, value):
        self.independent_sets += 1
        value = bool(value)
        if value:
            self.pct = 0.0
        self._independent = value

    @property
    def throttle(self):
        return self.actual

    @throttle.setter
    def throttle(self, value):
        if self._independent:
            self.pct = float(value) * 100.0


class _Parts:
    def __init__(self, engines: list):
        self.engines = engines


class _Vessel:
    def __init__(self, engine: _RfEngine, *, noop_ui: bool = False):
        self.control = _NoopControl() if noop_ui else _Control()
        self.parts = _Parts([engine])


def _snap(**kv):
    return type("S", (), kv)()


def test_apply_writes_independent_when_ui_bar_is_noop():
    engine = _RfEngine()
    vessel = _Vessel(engine, noop_ui=True)
    RF.apply(vessel, 1.0)
    assert engine.independent_throttle is True
    assert engine.pct == 100.0
    assert vessel.control.throttle == 0.0
    assert engine.independent_sets == 1


def test_apply_does_not_reenable_independent():
    engine = _RfEngine()
    vessel = _Vessel(engine)
    RF.apply(vessel, 1.0)
    RF.apply(vessel, 1.0)
    assert engine.independent_sets == 1
    assert engine.pct == 100.0


def test_live_is_independent_not_mainthrottle_get():
    engine = _RfEngine()
    vessel = _Vessel(engine)
    RF.apply(vessel, 1.0)
    vessel.control.throttle = 0.0
    engine.actual = 0.0
    assert RF.live(vessel) > 0.05
    assert RF.burning(vessel, _snap(fuel=2000.0, thrust=89_000.0), lofted=True)


def test_cut_zeros_independent_when_ui_bar_is_noop():
    engine = _RfEngine()
    vessel = _Vessel(engine, noop_ui=True)
    RF.apply(vessel, 1.0)
    object.__setattr__(vessel.control, "throttle", 1.0)
    RF.cut(vessel)
    assert engine.independent_throttle is False
    assert engine.pct <= 5.0
    assert vessel.control.throttle == 1.0


def test_burning_ignores_ui_mainthrottle_get():
    engine = _RfEngine()
    vessel = _Vessel(engine)
    RF.apply(vessel, 1.0)
    vessel.control.throttle = 0.0
    snap = _snap(fuel=2038.0, thrust=89_273.0)
    assert RF.burning(vessel, snap, lofted=True)
    RF.cut(vessel)
    snap0 = _snap(fuel=227.0, thrust=0.0)
    assert not RF.burning(vessel, snap0, lofted=True)


def test_light_stages_after_independent_live_not_ui_bar():
    engine = _RfEngine()
    vessel = _Vessel(engine, noop_ui=True)
    snap = _snap(situation="pre_launch", thrust=0.0, fuel=2238.0, link=True)
    assert light(vessel, None, snap, deaf=False) is False
    assert vessel.control.staged == 0
    assert engine.pct == 100.0
    assert light(vessel, None, snap, deaf=False) is True
    assert vessel.control.staged == 1


def test_loft_meco_sit_is_high_lid_not_two_stage():
    lid = _snap(alt=50_400.0, fuel=227.0, situation="flying")
    assert loft_lid_sit(lid, 50_000.0)
    assert loft_meco_sit(lid, hop_apo=50_000.0, two_stage=False)
    assert not loft_meco_sit(lid, hop_apo=50_000.0, two_stage=True)
    below = _snap(alt=12_000.0, fuel=2000.0, situation="flying")
    assert not loft_meco_sit(below, hop_apo=50_000.0)


def test_turn_live_sit_is_plume_not_pad_or_meco():
    assert turn_live_sit(
        lit=True, left_pad=True, down=False, keep_live=True, deaf=False
    )
    assert not turn_live_sit(
        lit=True, left_pad=False, down=False, keep_live=True, deaf=False
    )
    assert not turn_live_sit(
        lit=True, left_pad=True, down=False, keep_live=False, deaf=False
    )
    assert not turn_live_sit(
        lit=True, left_pad=True, down=True, keep_live=True, deaf=False
    )
    assert not turn_live_sit(
        lit=True, left_pad=True, down=False, keep_live=True, deaf=True
    )


def test_turn_cmd_pitch_is_east_not_sas_zenith():
    pitch, yawed = turn_cmd_pitch(False, 0, 90.0, float("nan"), 0.0)
    assert pitch == WATER_PITCH_UP - 10.0
    assert not yawed
    pitch, yawed = turn_cmd_pitch(False, 3, 80.0, WATER_HEADING_DEG, 8.0)
    assert pitch == WATER_PITCH_DEG
    assert yawed
    assert WATER_HEADING_DEG == 90.0
    assert WATER_HEADING_DEG != 270.0


def test_keep_live_sit_loft_until_lid():
    fly = _snap(alt=12_000.0, fuel=2000.0, thrust=90_000.0, situation="flying")
    assert keep_live_sit(
        fly, lit=True, left_pad=True, down=False, hop_apo=50_000.0, two_stage=False
    )
    lid = _snap(alt=50_400.0, fuel=227.0, thrust=90_000.0, situation="flying")
    assert not keep_live_sit(
        lid, lit=True, left_pad=True, down=False, hop_apo=50_000.0, two_stage=False
    )
    assert keep_live_sit(
        lid, lit=True, left_pad=True, down=False, hop_apo=50_000.0, two_stage=True
    )


def test_keep_live_false_at_lid_while_plume_up():
    """06-52-19Z / 22-11-37Z: 52 km still thrusting is MECO, not keep."""
    lid = _snap(
        alt=52_698.0, fuel=326.0, thrust=99_993.0, situation="flying"
    )
    assert loft_lid_sit(lid, 50_000.0)
    assert loft_meco_sit(lid, hop_apo=50_000.0, two_stage=False)
    assert not keep_live_sit(
        lid, lit=True, left_pad=True, down=False, hop_apo=50_000.0, two_stage=False
    )
    engine = _RfEngine()
    vessel = _Vessel(engine)
    RF.apply(vessel, 1.0)
    engine.thrust = 99_993.0
    assert RF.burning(vessel, lid, lofted=True)


def test_hold_live_clears_sas_once_left_pad():
    engine = _RfEngine()
    vessel = _Vessel(engine)
    vessel.control.sas = True
    hold_live(vessel, sas=True)
    assert vessel.control.sas is True
    assert RF.live(vessel) > 0.05
    hold_live(vessel, sas=False)
    assert vessel.control.sas is False
    assert RF.live(vessel) > 0.05
    assert engine.independent_sets == 1


def test_vacuum_stage_sit_is_terrier_not_valiant():
    valiant = _Vessel(_RfEngine())
    assert not vacuum_stage_sit(valiant)
    terrier = _Vessel(_RfEngine(name="liquidEngine2"))
    terrier.parts.engines[0].part.name = "liquidEngine2"
    terrier.parts.engines[0].name = "liquidEngine2"
    assert vacuum_stage_sit(terrier)


def test_circularize_and_stage_sits():
    apo = _snap(
        alt=140_000.0,
        apo=145_000.0,
        peri=-200_000.0,
        v_vert=-10.0,
        fuel=80.0,
        thrust=0.0,
        situation="sub_orbital",
    )
    assert circularize_sit(apo, two_stage=True, down=False, staged=True)
    assert not circularize_sit(apo, two_stage=False, down=False, staged=True)
    assert not orbit_done_sit(apo, two_stage=True)
    done = _snap(peri=150_000.0, apo=160_000.0, alt=155_000.0)
    assert orbit_done_sit(done, two_stage=True)
    burnout = _snap(fuel=1.0, thrust=0.0, alt=60_000.0)
    assert stage_sit(
        burnout, two_stage=True, staged=False, keep_live=False, down=False
    )
    assert not stage_sit(
        burnout, two_stage=False, staged=False, keep_live=False, down=False
    )


def test_space_low_sit_after_lid_not_flying():
    assert space_low_sit("sub_orbital", lofted_lid=True, down=False)
    assert space_low_sit("InSpaceLow", lofted_lid=True, down=False)
    assert not space_low_sit("flying", lofted_lid=True, down=False)
    assert not space_low_sit("sub_orbital", lofted_lid=False, down=False)
    assert not space_low_sit("sub_orbital", lofted_lid=True, down=True)


def test_source_hop_parked_orbit_is_ascent():
    hop = Path("hop.py").read_text(encoding="utf-8")
    ascent = Path("ascent.py").read_text(encoding="utf-8")
    factory = Path("hop_factory.py").read_text(encoding="utf-8")
    assert "python main.py ascent" in hop
    assert "parked for those rockets" in hop
    assert "from hop_factory import run_factory_vessel" in hop
    assert "from ascent import" not in hop
    assert "import rf_throttle" in ascent
    assert "from physics_warp import" in ascent
    assert "space_low_sit as space_low_block" in ascent
    assert "from hop_factory import" not in ascent
    assert "independentThrottlePercentage" in Path("rf_throttle.py").read_text(
        encoding="utf-8"
    )
    assert "def turn_live_sit" in ascent
    assert "H._steer_east" in ascent
    assert "vacuum_stage_sit" not in Path("ascent.py").read_text(
        encoding="utf-8"
    ).split("def turn_live_sit")[1].split("def turn_cmd_pitch")[0]
    keep_at = ascent.find("if keep and not deaf:")
    turn_at = ascent.find("H._steer_east")
    two_stage_say = ascent.find("ascent gravity turn east while thrusting")
    assert keep_at != -1 and turn_at != -1
    assert turn_at > keep_at
    assert two_stage_say != -1
    assert "if two_stage:" not in ascent[two_stage_say - 40 : two_stage_say]
    assert "hold_live(vessel, sas=not left_pad)" in ascent
    assert "burning_now = RF.burning(vessel, snap, lofted=lofted)" in ascent
    assert "if keep else False" not in ascent
    cut_at = ascent.find("RF.cut(vessel)")
    warp_at = ascent.find("apply_sit_warp(")
    assert cut_at != -1 and warp_at != -1
    assert cut_at < warp_at
    assert "not UI MainThrottle" in Path("rf_throttle.py").read_text(encoding="utf-8")
    assert "def run_factory_vessel" in factory
    main = Path("main.py").read_text(encoding="utf-8")
    assert 'add_parser(\n        "ascent"' in main or '"ascent"' in main
    assert "cmd_ascent" in main


def test_lofted_wait_sit_not_leftover_from_high():
    """Timeout leftover from High is silk/coast until down+recoverable."""
    assert lofted_wait_sit(lofted=True, down=False, recoverable=False)
    assert not lofted_wait_sit(lofted=True, down=True, recoverable=False)
    assert not lofted_wait_sit(lofted=True, down=False, recoverable=True)
    assert not lofted_wait_sit(lofted=False, down=False, recoverable=False)
    assert not lofted_wait_sit(
        lofted=True, down=False, recoverable=False, two_stage=True
    )


def test_timeout_leftover_uses_leftover_call_not_emergency_verb():
    """T-555: leftover_call names recover vs ksc leftover, not emergencies.call."""
    from physics_warp import leftover_call

    assert leftover_call(recoverable=True) == "recover"
    assert leftover_call(recoverable=False) == "ksc leftover"
    ascent = Path("ascent.py").read_text(encoding="utf-8")
    assert "leftover_call" in ascent
    assert "abort_ksc_leftover" in ascent
    assert "lofted_wait_sit" in ascent
    assert "ascent wait recoverable" in ascent
    assert "call(why," not in ascent
    assert 'call("ksc leftover"' not in ascent
    timeout_at = ascent.find("timeout_hit(")
    leftover_at = ascent.find("leftover_call(")
    recover_at = ascent.find('== "recover"')
    wait_at = ascent.find("lofted_wait_sit(", leftover_at)
    abort_at = ascent.find("abort_ksc_leftover")
    assert timeout_at != -1 and leftover_at != -1
    assert leftover_at > timeout_at
    assert recover_at > leftover_at
    assert wait_at > leftover_at
    assert abort_at > wait_at
