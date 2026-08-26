"""Factory inland hop pulse: light, slew 270, chute, sit-matched science, recover.

Flying card after loft. Pad light is throttle 1 on the engine, then
stage — RF 1-start at engine throttle 0 is spent. kRPC
``control.throttle`` is not the burn. Throttle 0 then 1 is a restart.
hop light is not the burn: ``_pad_hold`` (``hop_factory_pad``) keeps
the start on the pad. After confirmed light, dual-write MainThrottle 1 (UI bar) and
independent setpoint 1 (the flame) until loft/MECO at the lid — not a
pad MECO, not airborne GET throttle 0. Live is independent setpoint /
plume. kRPC Engine.throttle GET is currentThrottle 0 until lit.
Independent still burns when MainThrottle GET is 0 (16-05-34Z MET 9.7
thrust 89 kN). UI GET 0 is a drop, not MECO. Leave MainThrottle 1
after independent off and the UI lies on a dead engine.
Thrust 0 with fuel left and parts intact is OffPlan, not shear.
Uplink abort / MissionAbort ``_cut_pad_engine`` first — abort_pad
cut is MainThrottle only. Independent is enabled once — re-enable
zeros Current Throttle and stage spends the ignition at 0. Dropping
independent after light is a restart with 0 remaining.
FlyingHigh wait is loft to lid alt,
not a dwell at 1 km. Lid hold is independent 1 + SAS vertical until
lid; inland slew after. Splash bind is
not FlyingLow — factory inland still waits the High lid. Airborne
cannot-pay: FlyingLow skip still lofts — High waits the lid, then
Toggle; skip-latch does not drop a bound High card. After lid MECO,
InSpaceLow starts bound cards (LITE/TELEMETRY) — High cannot-pay is
not space-done (16-23-52Z skip-latch, PresMat in space sci +0). After High lid, MECO is MainThrottle 0, setpoint 0, then independent
off. Do not re-enable. Do not hold inland through burnout — that sit
kept throttle 1 at 55 km (17-01-10Z). After that gate, 17-13-14Z still
thrust 1 at 59 km and emptied tanks by MET 153 apo 270 km —
``_hold_lid`` after lid is MECO. Last write after 50 km live is
``_release_pad_throttle`` — ``_hold_or_cut`` hold=1 is not this sit
(20-07-41Z throttle 1 at 63 km fuel 320, apo 281 km). High dwell is
not a burn; plume still up is still the burn. After space dwell, Arm
Nylon on descent so HD comes home — 17-58-57Z chute=stowed at 70 km
vz −1.9 km/s then shear, LITE rem=0 rec=no. Do not loft out of atmo.
Quiet loft honors uplink phys-warp.
Wernher 1× on thick air / high q / silk / burn. FlyingLow skip may still
4×. Then coast, chute, land leftover. Pad boost (fuel, not lofted) does not science or hop-down —
sit=landed at pad alt with fuel is still burning. Parked water/splash
CLIs stay in hop.py. This module must not name those flags. Helpers live
on the hop module so test patches of hop.* still bind.

Orbit stack (``_orbit_stack_sit``: vacuum Terrier on the hang) is not
lid-MECO. SAS on the pad, then AP **while thrusting** — Valiant
``ModuleGimbal`` 5° follows Autopilot; pulse never writes gimbal.
Inland slew after lid MECO has no plume (heading 297 weathercock).
Gravity turn east (heading 90) through first-stage burnout, then
Terrier at apo until Pe ≥ High lid. C-534 Valiant loft is not this.
Forest / Grasslands: same.
"""

from __future__ import annotations

import math
import time
from typing import Callable

import hop as H
from emergencies import Ctx, call
from hop_factory_pad import (
    _apply_pad_throttle,
    _cut_pad_engine,
    _pad_engines,
    _pad_hold,
    _pad_light,
    _pad_plume,
    _pad_thrusting,
    _release_pad_throttle,
)
from phases import OffPlan, check_expect
from physics_warp import (
    airborne_cannot_pay,
    apply_sit_warp,
    chute_arm_sit,
    chute_deploy_sit,
    leftover_call,
    met_elapsed,
    timeout_hit,
)
from screenshot import mission_event
from telem import EventLog, MissionAbort, Telem, gates


def _inland_high_sit(
    tickets: list[object] | None = None,
    *,
    flying_ids: tuple[str, ...] | None = None,
) -> bool:
    """Splash bind is not FlyingLow. Factory inland still waits the High lid.

    Bound FlyingLow flying card is airborne Toggle. Missing flying card
    (splash paying) still lofts High. Unbound leftover High is not the
    latch. Forest / Grasslands: same.
    """
    asked = tickets is not None or flying_ids is not None
    if not asked and H.hop_wants_flying_high():
        return True
    try:
        import sys
        from tickets import list_tickets, science_ids_for

        if not asked and "unittest" in sys.modules:
            return H.hop_wants_flying_high()
        rows = tickets if tickets is not None else list_tickets(open_only=True)
        ids = flying_ids if flying_ids is not None else science_ids_for(
            situation="flying"
        )
    except Exception:
        return H.hop_wants_flying_high()
    if H.bound_card_is_flying_high(list(rows or []), flying_ids=ids or ()) is True:
        return True
    want = {str(e).strip() for e in (ids or ()) if str(e).strip()}
    if not want:
        return True
    for raw in rows or []:
        pl = raw.get("payload") if isinstance(raw, dict) else None
        if not isinstance(pl, dict):
            continue
        eid = str(pl.get("experiment_id") or pl.get("eid") or "").strip()
        sit = str(pl.get("situation") or "").lower().replace(" ", "").replace("_", "")
        if not eid or eid not in want:
            continue
        if "flyinghigh" in sit:
            return True
        if "flying" in sit and "high" not in sit:
            return False
    return True


def _engine_label(engine: object) -> str:
    """kRPC Engine + Part name/title. Cfg is not a part→N table."""
    bits: list[str] = []
    try:
        part = getattr(engine, "part", None)
    except Exception:
        part = None
    for obj in (engine, part):
        if obj is None:
            continue
        for attr in ("name", "title"):
            try:
                raw = getattr(obj, attr, None)
            except Exception:
                continue
            text = str(raw or "").strip().lower()
            if text:
                bits.append(text)
    return " ".join(bits)


def _orbit_stack_sit(vessel: object | None = None) -> bool:
    """Terrier / LV-909 vacuum second stage is the circularize hang.

    C-534 Valiant loft is not this. Pulse never writes gimbal. Forest /
    Grasslands: same.
    """
    if vessel is None:
        return False
    for eng in _pad_engines(vessel):
        label = _engine_label(eng)
        compact = label.replace(" ", "").replace("_", "-")
        if "terrier" in label or "lv-909" in label or "lv909" in compact:
            return True
        if "liquidengine2" in compact:
            return True
    return False


def _orbit_cmd_pitch(
    yawed: bool,
    yaw_n: int,
    flown_pitch: float,
    flown_heading: float,
    met: float,
) -> tuple[float, bool]:
    """Yaw 10° off zenith heading 90, then 25° from up. AP while thrusting."""
    if yawed:
        return H.WATER_PITCH_DEG, True
    captured = (
        math.isfinite(flown_heading)
        and H._heading_err_deg(flown_heading, H.WATER_HEADING_DEG)
        <= H.INLAND_HEADING_CAPTURE_DEG
        and math.isfinite(flown_pitch)
        and float(flown_pitch) <= H.INLAND_YAW_PITCH_DEG + 5.0
    )
    timed_out = math.isfinite(met) and float(met) >= H.INLAND_YAW_MET_S
    unseen = not math.isfinite(flown_heading) and int(yaw_n) >= 2
    if captured or timed_out or unseen:
        return H.WATER_PITCH_DEG, True
    return H.INLAND_YAW_PITCH_DEG, False


def _orbit_peri_ok(snap: object) -> bool:
    """Pe above the High lid is orbit. Apo 268 km with Pe through the planet is not."""
    peri = getattr(snap, "peri", float("nan"))
    try:
        peri_f = float(peri)
    except (TypeError, ValueError):
        peri_f = float("nan")
    return math.isfinite(peri_f) and peri_f >= H.FLYING_HIGH_M


def _orbit_done_sit(snap: object, *, orbit: bool = False) -> bool:
    """Circularized. Recover no. Forest / Grasslands: same."""
    return bool(orbit) and _orbit_peri_ok(snap)


def _circularize_sit(
    snap: object,
    *,
    orbit: bool,
    down: bool,
) -> bool:
    """Apo Terrier until Pe ≥ High lid. Loft Valiant is not this.

    Near apo in space, or already past apo above the lid. Forest /
    Grasslands: same.
    """
    if not orbit or down or _orbit_peri_ok(snap):
        return False
    alt = H._snap_alt(snap)
    apo = getattr(snap, "apo", float("nan"))
    vz = H._snap_v_vert(snap)
    try:
        apo_f = float(apo)
    except (TypeError, ValueError):
        apo_f = float("nan")
    if math.isfinite(alt) and math.isfinite(apo_f) and apo_f > 0.0:
        if alt >= 0.9 * apo_f:
            return True
    if (
        math.isfinite(vz)
        and vz <= 0.0
        and math.isfinite(alt)
        and alt >= H.FLYING_HIGH_M
    ):
        return True
    return False


def _lid_alt_reached(
    snap: object, hop_apo: float, *, flying_high: bool | None = None
) -> bool:
    """FlyingHigh lid is live alt ≥50 km. Predicted apo in thick air is not the lid.

    Gene hop_apo is the cut; Space 140 km is not this sit. 20-07-41Z
    hop_apo=50000 still thrust 1 at 63 km. Forest / Grasslands: same.
    """
    if flying_high is None:
        flying_high = _inland_high_sit()
    if not flying_high:
        return False
    alt = H._snap_alt(snap)
    if not math.isfinite(alt):
        return False
    try:
        lid = float(hop_apo)
    except (TypeError, ValueError):
        lid = float("nan")
    if not math.isfinite(lid) or lid <= 0.0:
        lid = H.FLYING_LOW_M
    else:
        lid = min(lid, H.FLYING_LOW_M)
    return alt >= lid


def _lid_burn_sit(
    snap: object,
    *,
    hop_apo: float,
    flying_high: bool,
    lofted_lid: bool = False,
) -> bool:
    """Leftover LF before lid alt is still the burn sit. Not lofted burnout.

    FlyingHigh wait at ~1 km is not FlyingHigh. Throttle 0 with leftover
    LF is not 4×. Crumbs before lid may coast if q is actually low.
    After lid, leftover LF is not this sit — descent below hop_apo is
    not a 1-start relight. High dwell is not a burn. Forest /
    Grasslands: same.
    """
    if not flying_high or lofted_lid:
        return False
    if _lid_alt_reached(snap, hop_apo, flying_high=flying_high):
        return False
    fuel = H._snap_fuel(snap)
    return math.isfinite(fuel) and fuel > H.WATER_BRAKE_FUEL_MIN


def _keep_start_sit(
    snap: object,
    *,
    lit: bool,
    left_pad: bool,
    down: bool,
    hop_apo: float,
    flying_high: bool,
    lofted_lid: bool = False,
    orbit: bool = False,
) -> bool:
    """After hop light, keep independent setpoint 1 until MECO.

    MainThrottle paints the bar; it is not the RF burn. Airborne GET
    throttle 0 is not MECO — independent still burns. Lid alt, High
    dwell, or crumbs is MECO. After lid, cut independent and
    MainThrottle. Orbit stack is not lid MECO — leftover LF is still
    the first-stage burn. Pad sit after light is still the start.
    Forest / Grasslands: same.
    """
    if not lit or down:
        return False
    if not left_pad:
        return True
    if orbit:
        fuel = H._snap_fuel(snap)
        if not math.isfinite(fuel) or fuel <= H.WATER_BRAKE_FUEL_MIN:
            return False
        reached = lofted_lid or (
            flying_high
            and _lid_alt_reached(snap, hop_apo, flying_high=True)
        )
        if not reached:
            return True
        thrust = getattr(snap, "thrust", float("nan"))
        try:
            thrust_f = float(thrust)
        except (TypeError, ValueError):
            thrust_f = float("nan")
        return math.isfinite(thrust_f) and thrust_f > 0.0
    if flying_high:
        if _high_dwell_sit(reached_lid=lofted_lid, down=down):
            return False
        return _lid_burn_sit(
            snap, hop_apo=hop_apo, flying_high=True, lofted_lid=lofted_lid
        )
    fuel = H._snap_fuel(snap)
    if not math.isfinite(fuel) or fuel <= H.WATER_BRAKE_FUEL_MIN:
        return False
    apo = getattr(snap, "apo", float("nan"))
    try:
        apo_f = float(apo)
    except (TypeError, ValueError):
        apo_f = float("nan")
    if math.isfinite(apo_f) and apo_f >= hop_apo:
        return False
    return True


def _hold_start(
    vessel: object,
    snap: object,
    *,
    keep_start: bool,
    left_pad: bool,
    lit: bool,
    deaf: bool,
) -> bool:
    """Keep independent setpoint 1 until MECO; dual-write the UI bar.

    Airborne GET throttle 0 is not MECO — independent still burns.
    MECO is MainThrottle 0, setpoint 0, then independent off. Leave
    MainThrottle 1 after independent off and the UI lies. Do not
    re-enable. Pad sit still ``_pad_hold``. Forest / Grasslands: same.
    """
    if not left_pad:
        return _pad_hold(vessel, snap, lit=lit, left_pad=False, deaf=deaf)
    if not lit or deaf:
        return False
    if keep_start:
        _apply_pad_throttle(vessel)
        return True
    _release_pad_throttle(vessel)
    return False


def _flameout_sit(
    snap: object,
    vessel: object,
    *,
    keep_start: bool,
    orbit: bool = False,
    lofted_lid: bool = False,
) -> bool:
    """Thrust 0 with fuel left and parts intact is OffPlan, not shear.

    Independent drop is a restart at 0 remaining. Orbit stack after
    lid is first-stage coast — upper fuel is not a Valiant restart.
    Forest / Grasslands: same.
    """
    if not keep_start:
        return False
    if orbit and lofted_lid:
        return False
    fuel = H._snap_fuel(snap)
    if not math.isfinite(fuel) or fuel <= H.WATER_BRAKE_FUEL_MIN:
        return False
    n_parts = H._parts_n(vessel)
    if n_parts is not None and n_parts <= 0:
        return False
    if _pad_thrusting(vessel, snap) or _pad_plume(vessel, snap):
        return False
    return True


def _high_dwell_sit(*, reached_lid: bool, down: bool) -> bool:
    """After FlyingHigh lid, until down. Not a burn.

    17-01-10Z science dwell then hold inland through burnout, throttle 1
    at 55 km. 17-13-14Z that log was gone and tanks still emptied at
    59 km throttle 1. MECO at the lid; inland-burnout is not this.
    Plume still up is still the burn. Do not loft out of atmo.
    Wernher ``want_coast`` already 1× on thick air / high q / silk / burn.
    Quiet loft honors uplink ``phys-warp``. Forest / Grasslands: same.
    """
    return bool(reached_lid) and not down


def _inland_burnout_sit(
    *,
    flying_high: bool,
    reached_lid: bool,
    down: bool,
) -> bool:
    """Slew inland and hold the burn. FlyingHigh after lid is not this.

    17-01-10Z this sit after High Toggle, throttle 1 at 55 km. High
    dwell is MECO, not a second start. Forest / Grasslands: same.
    """
    if down:
        return False
    if flying_high and _high_dwell_sit(reached_lid=reached_lid, down=down):
        return False
    return True


def _leftover_sit(*, down: bool, live_sit: str = "") -> bool:
    """Sit-matched leftover still Toggles when down.

    Airborne cannot-pay is not dwell-done. Forest / Grasslands / Water: same.
    """
    live_l = str(live_sit or "").lower()
    return bool(down or "landed" in live_l or "splash" in live_l)


def _space_low_sit(live_sit: str = "") -> bool:
    """InSpaceLow after lid. Flying at 50 km is not this.

    kRPC sub_orbital / orbiting / escaping. 16-23-52Z High Toggle skip
    never retried in space. Forest / Grasslands: same.
    """
    live = str(live_sit or "").lower().replace(" ", "").replace("_", "")
    if not live or "landed" in live or "splash" in live:
        return False
    if "inspacehigh" in live:
        return False
    return any(
        tok in live
        for tok in ("suborbital", "orbiting", "escaping", "inspacelow", "inspace")
    )


def _space_science_ids() -> tuple[str, ...]:
    """Bound InSpaceLow eids. hop_science_ids situation=flying drops these."""
    try:
        from tickets import science_ids_for

        return science_ids_for(situation="inspacelow")
    except Exception:
        return ()


def _lid_vertical_sit(
    snap: object,
    *,
    hop_apo: float,
    flying_high: bool,
    lofted_lid: bool = False,
) -> bool:
    """FlyingHigh below lid alt stays vertical. Pitch 25 at 1 km is not loft.

    Predicted apo in thick air is not the lid. After lid alt, slew.
    Forest / Grasslands: same.
    """
    if not flying_high or lofted_lid:
        return False
    return not _lid_alt_reached(snap, hop_apo, flying_high=flying_high)


def _hold_lid(
    vessel: object,
    snap: object,
    *,
    hop_apo: float,
    flying_high: bool,
    lofted_lid: bool = False,
    orbit: bool = False,
) -> bool:
    """FlyingHigh below lid: independent 1, SAS vertical. Not inland slew.

    AP engage at zenith has no heading. Inland slew clears SAS and does
    not hold vertical. SAS from light holds the loft until lid alt or
    crumbs. MainThrottle-only is not the RF burn — dual-write with
    independent. After lid, MECO: MainThrottle 0, setpoint 0,
    independent off — leftover LF is the coast. lofted_lid latch is
    not required: live alt ≥50 km is MECO. 17-13-14Z throttle 1 at
    59 km emptied tanks by MET 153. Residual vz is not this sit.
    Orbit stack is not this MECO — AP east while thrusting. Forest /
    Grasslands: same.
    """
    if orbit:
        return False
    if flying_high and (
        lofted_lid or _lid_alt_reached(snap, hop_apo, flying_high=True)
    ):
        _release_pad_throttle(vessel)
        return False
    burn = _lid_burn_sit(
        snap, hop_apo=hop_apo, flying_high=flying_high, lofted_lid=lofted_lid
    )
    vertical = _lid_vertical_sit(
        snap, hop_apo=hop_apo, flying_high=flying_high, lofted_lid=lofted_lid
    )
    if not burn and not vertical:
        return False
    if burn:
        _apply_pad_throttle(vessel)
    if vertical:
        try:
            vessel.control.sas = True
        except Exception:
            pass
    return True


def _space_silk_arm_sit(snap: object) -> bool:
    """After lid, descent Arm. Not thick-air-only.

    17-58-57Z Nylon stowed at 70 km vz −1.9 km/s then shear; LITE rem=0
    rec=no. ``chute_arm_sit`` is ≤18 km — space loft misses that window.
    Climbing after lid is not this. Forest / Grasslands: same.
    """
    if not H._lofted(snap):
        return False
    vz = H._snap_v_vert(snap)
    if math.isfinite(vz):
        return vz < 0.0
    pitch = H._snap_pitch(snap)
    return math.isfinite(pitch) and pitch < 0.0


def _chute_arm_now(
    snap: object,
    *,
    hop_apo: float,
    flying_high: bool,
    crumbs: bool,
    apo_cut: bool,
) -> bool:
    """Arm after lid alt or burnout descent. Climbing wait-burn is not silk.

    FlyingLow is ``chute_arm_sit``. FlyingHigh waits for lid alt or crumbs.
    After lid, descent Arm even above thick air (17-58-57Z). ``chute_arm_sit``
    stays 1× in thick air. Throttle 0 with a full tank is not burnout.
    Forest / Grasslands: same.
    """
    ready = (not flying_high) or crumbs or apo_cut or _lid_alt_reached(
        snap, hop_apo, flying_high=flying_high
    )
    if not ready:
        return False
    if chute_arm_sit(snap):
        return True
    return bool(flying_high) and _space_silk_arm_sit(snap)


def _chute_deploy_now(
    snap: object,
    *,
    hop_apo: float,
    flying_high: bool,
    crumbs: bool,
    apo_cut: bool,
) -> bool:
    """Deploy ≤2 km after lid alt or burnout. FlyingHigh wait-burn is not silk.

    FlyingLow is ``chute_deploy_sit``. ``deploy_chutes`` Arms inside — leftover
    LF before lid is not a canopy. Forest / Grasslands: same.
    """
    if not chute_deploy_sit(snap):
        return False
    if not flying_high:
        return True
    return crumbs or apo_cut or _lid_alt_reached(snap, hop_apo, flying_high=flying_high)


def _offplan_apo_lid(snap: object) -> float:
    """OffPlan apo lid. Gene expect_apo_max raises it; hop_apo is the cut.

    Splash bind is not FlyingLow. Factory inland High uses Space unless
    the plan envelope is higher. FlyingLow stays ≥50 km. Forest /
    Grasslands: same.
    """
    if not _inland_high_sit():
        return H.FLYING_LOW_M
    lid = H.FLYING_HIGH_M
    atm = getattr(snap, "atm_depth", float("nan"))
    try:
        atm_f = float(atm)
    except (TypeError, ValueError):
        atm_f = float("nan")
    if math.isfinite(atm_f) and atm_f > 0.0:
        lid = atm_f
    try:
        from phases import _kv

        raw = _kv().get("expect_apo_max", "")
    except Exception:
        raw = ""
    try:
        plan = float(raw) if str(raw).strip() else float("nan")
    except (TypeError, ValueError):
        plan = float("nan")
    if math.isfinite(plan) and plan > lid:
        return plan
    return lid


def run_factory_vessel(
    session: object,
    vessel: object,
    *,
    events: EventLog | None = None,
    on_log: Callable[[str], None] | None = None,
    science_ids: tuple[str, ...] | None = None,
    abort: Callable[[], bool] | None = None,
    now: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
    timeout: float | None = None,
    pulse: float | None = None,
) -> str:
    """Light, flying card, recover when down or dead-with-HD. Caller Hangars."""
    log_events = events if events is not None else EventLog()
    if science_ids is not None:
        ids = tuple(science_ids)
    else:
        try:
            ids = H.hop_science_ids()
        except MissionAbort:
            ids = ()
    flying_high = _inland_high_sit()
    hop_apo = H.hop_target_apo(space=flying_high)
    ctx = Ctx(session=session, vessel=vessel, events=log_events, science_ids=ids)
    clock = now if now is not None else time.monotonic
    nap = sleep if sleep is not None else time.sleep
    budget = H.DEFAULT_HOP_S if timeout is None else float(timeout)
    t0 = clock()
    lit = False
    did_light = False
    left_pad = False
    started: list[str] = []
    science_attempted = False
    pulses = 0
    said_down = False
    waiting_hd = False
    prev_met: float | None = None
    still_t0: float | None = None
    unpaused = False
    unpause_at: float | None = None
    litho = False
    said_crash = False
    said_pitch = False
    said_hold = False
    said_slew = False
    apo_cut = False
    inland_pitch = H.WATER_PITCH_UP
    inland_yawed = False
    inland_yaw_n = 0
    chute_armed = False
    chute_open = False
    said_deploy = False
    said_coast = [""]
    lofted = False
    met0: float | None = None
    reached_lid = False
    link_was: bool | None = None
    prev_stack_mass = float("nan")
    prev_stack_fuel = float("nan")
    prev_stack_parts: int | None = None
    orbit = _orbit_stack_sit(vessel)
    orbit_staged = False
    said_circ = False
    H._say(f"hop apo={hop_apo:.0f}", on_log)
    if orbit:
        H._say(
            "hop gravity turn east while thrusting, no lid MECO, "
            f"circularize Pe>={H.FLYING_HIGH_M:.0f}",
            on_log,
        )
    elif flying_high:
        H._say(
            f"hop hold vertical until lid {hop_apo:.0f} m, then slew "
            f"inland heading {H.INLAND_HEADING_DEG:g}",
            on_log,
        )
    else:
        H._say(
            f"hop slew yaw {H.INLAND_YAW_FROM_UP:g}° then pitch "
            f"{H.INLAND_PITCH_FROM_UP:g}° inland heading "
            f"{H.INLAND_HEADING_DEG:g} after pad, hold through burnout",
            on_log,
        )

    with Telem(session, events=log_events) as telem:
        while True:
            if abort is not None:
                try:
                    stop = bool(abort())
                except Exception:
                    stop = False
                if stop:
                    _cut_pad_engine(vessel)
                    call("abort_pad", ctx)
                    raise MissionAbort("abort")
            try:
                H._uplink_tick(ctx)
            except MissionAbort:
                _cut_pad_engine(vessel)
                raise
            live = H._active(session, vessel)
            if live is None:
                if left_pad:
                    got = H._finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                raise MissionAbort("no vessel")
            vessel = live
            ctx.vessel = vessel
            snap = telem.read()
            pulses += 1
            orbit = orbit or _orbit_stack_sit(vessel)
            if did_light and met0 is None:
                try:
                    m0 = float(getattr(snap, "met", float("nan")))
                except (TypeError, ValueError):
                    m0 = float("nan")
                if not math.isfinite(m0):
                    vm = H._vessel_met(vessel)
                    m0 = float(vm) if vm is not None else float("nan")
                if math.isfinite(m0):
                    met0 = m0
            deaf = H._zero_stick_if_deaf(vessel, snap)
            H._link_edge(log_events, not deaf, link_was)
            link_was = not deaf
            if not did_light and H.leftover_wreck_before_light(snap, vessel):
                sit = str(getattr(snap, "situation", "") or "") or H._vessel_sit(
                    vessel
                )
                rec = "yes" if H._recoverable(vessel) else "no"
                H._say(
                    f"hop leftover sit={sit} fuel={H._fmt(H._snap_fuel(snap), 1)} "
                    f"recoverable={rec} met={H._fmt(H._vessel_met(vessel), 2)} "
                    "— do not light",
                    on_log,
                )
                if H._recoverable(vessel):
                    got = H._force_recover(vessel, on_log)
                    if got is not None:
                        return got
                if sit in H._LIGHT_SIT:
                    raise MissionAbort("leftover dry — do not light")
                if not said_crash:
                    H._crash_line(vessel, snap, on_log)
                    said_crash = True
                H._leave_crash_ui(
                    session,
                    on_log,
                    total_wreck=H._experiment_count(vessel) == 0,
                )
                raise MissionAbort("not recoverable")
            airborne = H._airborne(snap)
            if airborne:
                if not left_pad:
                    H._say("hop airborne", on_log)
                    log_events.emit("hop", result="airborne")
                    if lofted:
                        mission_event(
                            "airborne",
                            snap,
                            beauty=True,
                            pose="ascent",
                            session=session,
                        )
                left_pad = True
            if H._lofted(snap):
                lofted = True
            if H._reached_high_lid(snap) or _lid_alt_reached(
                snap, hop_apo, flying_high=flying_high
            ):
                reached_lid = True
            down = H._down(snap, flown=left_pad) or litho

            if left_pad and H._vessel_gone(snap, vessel):
                if H._recoverable(vessel):
                    if not said_down:
                        H._say("hop down", on_log)
                        said_down = True
                    got = H._force_recover(vessel, on_log)
                    if got is not None:
                        return got
                if not said_crash:
                    H._crash_line(vessel, snap, on_log)
                    said_crash = True
                H.abort_ksc_leftover(vessel, on_log, why="total wreck")

            if left_pad and not down:
                n_parts = H._parts_n(vessel)
                mass_now = H._snap_mass(snap)
                fuel_now = H._snap_fuel(snap)
                why = H.stack_sheared(
                    prev_stack_mass,
                    mass_now,
                    prev_stack_fuel,
                    fuel_now,
                    prev_stack_parts,
                    n_parts,
                )
                if why:
                    H._say(f"hop shear {why}", on_log)
                    ctx.notes.append("shear")
                    call("hold", ctx)
                    if H._recoverable(vessel):
                        got = H._recover_hd(vessel, on_log)
                        if got is not None:
                            return got
                    call("abort_pad", ctx)
                    raise MissionAbort("shear")
                if math.isfinite(mass_now):
                    prev_stack_mass = mass_now
                if math.isfinite(fuel_now):
                    prev_stack_fuel = fuel_now
                if n_parts is not None:
                    prev_stack_parts = n_parts

            for reason in gates(snap):
                if reason == "empty tanks" or reason.startswith("atmosphere"):
                    continue
                if reason == "shear":
                    continue
                if reason == "ec=0" and H._vessel_gone(snap, vessel):
                    continue
                H._say(f"gate {reason}", on_log)
                if reason == "wreck":
                    down = True
                    continue
                if reason.startswith("reliability"):
                    if down and left_pad:
                        continue
                    call("abort_pad", ctx)
                    raise MissionAbort(reason)
                if reason == "ec=0":
                    has = H._keep_hd(
                        vessel, ids, started, left_pad=left_pad, lit=did_light
                    )
                    if has:
                        if left_pad and H._recoverable(vessel) and not said_down:
                            H._say("hop down", on_log)
                            said_down = True
                        got = H._recover_hd(vessel, on_log)
                        if got is not None:
                            return got
                        if left_pad:
                            if not waiting_hd:
                                H._say("hop ec=0 wait recoverable", on_log)
                                log_events.emit("science_dwell", result="ec")
                            waiting_hd = True
                    elif not left_pad or down:
                        call("abort_pad", ctx)
                        raise MissionAbort(reason)

            arm_now = False
            deploy_now = False
            st_now = str(getattr(snap, "chute", "") or "")
            if st_now in H._CHUTE_OPEN:
                chute_open = True
            if lofted and down:
                apo_cut = True
                _release_pad_throttle(vessel)
            if left_pad and not down:
                if chute_open:
                    apo_cut = True
                if _lid_alt_reached(snap, hop_apo, flying_high=flying_high):
                    apo_cut = True
                if _high_dwell_sit(reached_lid=reached_lid, down=down):
                    apo_cut = True
                fuel_now = H._snap_fuel(snap)
                crumbs = math.isfinite(fuel_now) and fuel_now <= H.WATER_BRAKE_FUEL_MIN
                arm_now = _chute_arm_now(
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    crumbs=crumbs,
                    apo_cut=apo_cut,
                )
                if arm_now:
                    apo_cut = True
                deploy_now = _chute_deploy_now(
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    crumbs=crumbs,
                    apo_cut=apo_cut,
                )
                lid_burn = _lid_burn_sit(
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    lofted_lid=reached_lid,
                )
                if lid_burn and not orbit:
                    apo_cut = False
                elif orbit:
                    apo_cut = False
                elif flying_high and (
                    reached_lid
                    or _lid_alt_reached(
                        snap, hop_apo, flying_high=True
                    )
                ):
                    apo_cut = True
                    _release_pad_throttle(vessel)
                elif apo_cut:
                    _release_pad_throttle(vessel)
                _hold_lid(
                    vessel,
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    lofted_lid=reached_lid,
                    orbit=orbit,
                )
                if orbit and not down and not _orbit_done_sit(
                    snap, orbit=True
                ):
                    alt_now = H._snap_alt(snap)
                    if math.isfinite(alt_now) and alt_now >= H.FLYING_HIGH_M:
                        arm_now = False
                        deploy_now = False

            apo = getattr(snap, "apo", float("nan"))
            try:
                apo_f = float(apo)
            except (TypeError, ValueError):
                apo_f = float("nan")
            lid = _offplan_apo_lid(snap)
            label = "Space" if flying_high else "FlyingLow"
            if (
                left_pad
                and not down
                and not waiting_hd
                and not orbit
                and math.isfinite(apo_f)
                and apo_f > lid
                and not (flying_high and apo_cut)
            ):
                raise OffPlan(f"apo {apo_f:.0f} > {lid:.0f} {label}")
            if left_pad and not down and not waiting_hd:
                check_expect(snap, skip_peri=True, skip_apo=True)

            if not lit:
                if airborne:
                    lit = True
                elif not left_pad and str(snap.situation) in H._LIGHT_SIT:
                    if _pad_light(vessel, on_log, snap, deaf=deaf):
                        lit = True
                        did_light = True
                        log_events.emit("hop", result="light")
                        if lofted:
                            mission_event(
                                "light",
                                snap,
                                beauty=True,
                                pose="pad-plume",
                                session=session,
                            )
            keep_start = _keep_start_sit(
                snap,
                lit=lit,
                left_pad=left_pad,
                down=down,
                hop_apo=hop_apo,
                flying_high=flying_high,
                lofted_lid=reached_lid,
                orbit=orbit,
            )
            if left_pad and not down and _flameout_sit(
                snap,
                vessel,
                keep_start=keep_start,
                orbit=orbit,
                lofted_lid=reached_lid,
            ):
                raise OffPlan("thrust 0 with fuel left")
            _hold_start(
                vessel,
                snap,
                keep_start=keep_start,
                left_pad=left_pad,
                lit=lit,
                deaf=deaf,
            )

            inland_burnout = _inland_burnout_sit(
                flying_high=flying_high,
                reached_lid=reached_lid,
                down=down,
            )
            burning_now = (
                H._burning(vessel, snap, lofted=lofted)
                or _lid_burn_sit(
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    lofted_lid=reached_lid,
                )
                or _pad_plume(vessel, snap)
            )
            if lit and not down and left_pad and not deaf:
                flown_p = H._snap_pitch(snap)
                flown_h = H._snap_heading(snap)
                try:
                    met_slew = float(getattr(snap, "met", float("nan")))
                except (TypeError, ValueError):
                    met_slew = float("nan")
                if orbit:
                    if not inland_yawed:
                        inland_yaw_n += 1
                    inland_pitch, inland_yawed = _orbit_cmd_pitch(
                        inland_yawed,
                        inland_yaw_n,
                        flown_p,
                        flown_h,
                        met_slew,
                    )
                    H._steer_east(
                        vessel,
                        pitch=inland_pitch,
                        flown_pitch=flown_p,
                        flown_heading=flown_h,
                        burning=burning_now,
                    )
                    if not said_slew:
                        H._say(
                            "hop gravity turn east while thrusting "
                            f"heading={H.WATER_HEADING_DEG:g}",
                            on_log,
                        )
                        said_slew = True
                    if inland_yawed and not said_pitch:
                        H._say(
                            f"hop pitch {H.WATER_PITCH_FROM_UP:g}° east "
                            f"heading={H.WATER_HEADING_DEG:g}",
                            on_log,
                        )
                        said_pitch = True
                elif _lid_vertical_sit(
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    lofted_lid=reached_lid,
                ):
                    inland_pitch = H.WATER_PITCH_UP
                    _hold_lid(
                        vessel,
                        snap,
                        hop_apo=hop_apo,
                        flying_high=flying_high,
                        lofted_lid=reached_lid,
                        orbit=orbit,
                    )
                else:
                    if not inland_yawed:
                        inland_yaw_n += 1
                    inland_pitch, inland_yawed = H._inland_cmd_pitch(
                        inland_yawed,
                        inland_yaw_n,
                        flown_p,
                        flown_h,
                        met_slew,
                    )
                    H._steer_inland(
                        vessel,
                        pitch=inland_pitch,
                        flown_pitch=flown_p,
                        flown_heading=flown_h,
                        burning=burning_now if inland_burnout else False,
                    )
                    if not said_slew:
                        H._say(
                            "hop slew yaw inland after pad "
                            f"heading={H.INLAND_HEADING_DEG:g}",
                            on_log,
                        )
                        said_slew = True
                    if inland_yawed and not said_pitch:
                        H._say(
                            f"hop pitch {H.INLAND_PITCH_FROM_UP:g}° inland "
                            f"heading={H.INLAND_HEADING_DEG:g}",
                            on_log,
                        )
                        said_pitch = True
                if inland_burnout and not burning_now and not said_hold:
                    H._say("hop hold inland through burnout", on_log)
                    said_hold = True

            apply_sit_warp(
                session,
                snap,
                left_pad=left_pad,
                down=down,
                burning=burning_now,
                on_log=on_log,
                last=said_coast,
                uplink_rate=H.phys_warp_rate(),
            )

            if left_pad and not down and not chute_open:
                if st_now in H._CHUTE_OPEN:
                    chute_open = True
                else:
                    if not chute_armed and arm_now:
                        st = H.arm_chutes(vessel, on_log)
                        chute_armed = True
                        if st in {"", "none"}:
                            chute_open = True
                        else:
                            H._say(f"hop chute {st}", on_log)
                    if not chute_open and deploy_now:
                        st = H.deploy_chutes(vessel, on_log)
                        if st in H._CHUTE_OPEN:
                            chute_open = True
                        if not said_deploy and st not in {"", "none"}:
                            H._say(f"hop chute {st}", on_log)
                            said_deploy = True
                            mission_event(
                                "chute",
                                snap,
                                beauty=True,
                                pose="chute-silk",
                                session=session,
                            )

            if left_pad and not down and not science_attempted:
                if (not did_light) and H._keep_hd(
                    vessel, ids, started, left_pad=True
                ):
                    science_attempted = True
                    H._say("science keep HD", on_log)
                    log_events.emit("science", result="keep")
                    mission_event(
                        "science",
                        snap,
                        beauty=True,
                        pose="science",
                        session=session,
                    )
                    waiting_hd = True
                elif lofted and (
                    H._snap_alt(snap) >= H.FLYING_LOW_M
                    if flying_high
                    else H._science_ready(snap)
                ):
                    need = H.bound_science_need(
                        live_sit=H._live_sit(vessel, snap),
                        live_biome=H._snap_biome(snap, vessel),
                        alt=H._snap_alt(snap),
                    )
                    started = H._start_paying(vessel, ids, snap, on_log, need)
                    if started:
                        science_attempted = True
                        H._say("science " + ",".join(started), on_log)
                        log_events.emit("science", ids=list(started))
                        mission_event(
                            "science",
                            snap,
                            beauty=True,
                            pose="science",
                            session=session,
                        )
                        H._say("science dwell", on_log)
                        log_events.emit("science_dwell", phase="start")
                    elif ids and not H.card_slots(vessel, ids):
                        science_attempted = True
                        call("abort_pad", ctx)
                        raise MissionAbort(
                            "no science (wanted " + ",".join(ids) + ")"
                        )
                    elif ids:
                        science_attempted = True
                        H._say("science skip (situation cannot pay)", on_log)

            if left_pad and not down:
                _hold_lid(
                    vessel,
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    lofted_lid=reached_lid,
                    orbit=orbit,
                )
                if _circularize_sit(snap, orbit=orbit, down=down):
                    if not orbit_staged:
                        try:
                            vessel.control.activate_next_stage()
                        except Exception:
                            pass
                        orbit_staged = True
                    _apply_pad_throttle(vessel)
                    if not said_circ:
                        H._say("hop circularize Pe", on_log)
                        said_circ = True
                elif _orbit_done_sit(snap, orbit=orbit):
                    _release_pad_throttle(vessel)

            waiting_lid = (
                flying_high
                and did_light
                and not started
                and not science_attempted
                and left_pad
                and not down
            )
            cannot_pay = airborne_cannot_pay(
                lofted=lofted,
                down=down,
                started=started,
                science_attempted=science_attempted,
                waiting_hd=waiting_hd,
            )

            live_now = H._live_sit(vessel, snap)
            live_biome = H._snap_biome(snap, vessel)
            live_l = str(live_now or "").lower()
            wreck_now = bool(getattr(snap, "wreck", False))
            sit_ground = "landed" in live_l or "splash" in live_l
            leftover_now = _leftover_sit(down=down, live_sit=live_now)
            leftover_ids = H.hop_landed_science_ids()
            matching_ids = H.hop_landed_science_ids(
                live_sit=live_now, live_biome=live_biome
            )
            started_ground: list[str] = []
            if (
                left_pad
                and not down
                and lofted
                and reached_lid
                and not waiting_hd
                and _space_low_sit(live_now)
            ):
                space_ids = _space_science_ids()
                need = H.bound_science_need(
                    live_sit=live_now,
                    live_biome=live_biome,
                    alt=H._snap_alt(snap),
                )
                pending = tuple(eid for eid in space_ids if eid not in started)
                more = (
                    H._start_paying(vessel, pending, snap, on_log, need)
                    if pending
                    else []
                )
                if more:
                    started.extend(more)
                    science_attempted = True
                    H._say("science " + ",".join(more), on_log)
                    log_events.emit("science", ids=list(more))
                    mission_event(
                        "science",
                        snap,
                        beauty=True,
                        pose="science",
                        session=session,
                    )
                    H._say("science dwell", on_log)
                    log_events.emit("science_dwell", phase="start")
            if left_pad and leftover_now and not waiting_hd and lofted:
                need = H.bound_science_need(
                    live_sit=live_now,
                    live_biome=live_biome,
                )
                card = tuple(dict.fromkeys((*leftover_ids, *matching_ids)))
                pending = tuple(eid for eid in card if eid not in started)
                more = (
                    H._start_paying(vessel, pending, snap, on_log, need)
                    if pending
                    else []
                )
                if more:
                    started.extend(more)
                    started_ground = more
                    science_attempted = True
                    H._say("science " + ",".join(more), on_log)
                    log_events.emit("science", ids=list(more))
                    mission_event(
                        "science",
                        snap,
                        beauty=True,
                        pose="science",
                        session=session,
                    )
                    H._say("science dwell", on_log)
                    log_events.emit("science_dwell", phase="start")

            if H._abort_high_lid(
                lit=did_light,
                started=started,
                left_pad=left_pad,
                down=down,
                reached_lid=reached_lid,
            ):
                if not H._recoverable(vessel):
                    H._leave_crash_ui(session, on_log, total_wreck=True)
                call("abort_pad", ctx)
                raise MissionAbort("no science (FlyingHigh lid)")

            # Leftover file rem=0 on Toggle is idle, not transmitted.
            # Unpaid leftover that can pay this sit (or any leftover while
            # still flying) blocks recover. SrfLanded does not hold splash.
            unpaid_match = tuple(eid for eid in matching_ids if eid not in started)
            unpaid_any = tuple(eid for eid in leftover_ids if eid not in started)
            wait_leftover = (
                left_pad
                and lofted
                and not wreck_now
                and not waiting_hd
                and (
                    bool(unpaid_match)
                    if sit_ground
                    else bool(unpaid_any)
                )
            )
            hold_card = H._hold_ground_card(vessel, started, ids, snap) or (
                bool(started_ground) and not wreck_now
            )

            pad_boost = H._pad_boosting(
                lit=did_light,
                left_pad=left_pad,
                lofted=lofted,
                down=down,
                burning=burning_now,
            )
            if waiting_lid or hold_card or cannot_pay or wait_leftover:
                pass
            elif pad_boost:
                if not deaf:
                    _apply_pad_throttle(vessel)
            elif left_pad and H._recoverable(vessel) and not _orbit_done_sit(
                snap, orbit=orbit
            ):
                if not said_down:
                    H._say("hop down", on_log)
                    said_down = True
                H._recover_tick(vessel, on_log)
                got = H._recover_hd(vessel, on_log)
                if got is not None:
                    return got
            elif left_pad:
                for other in H._pool(session, vessel):
                    if other is vessel or not H._ours(other):
                        continue
                    hit = H._try_recover(other, on_log)
                    if hit is None:
                        continue
                    H._wait_vessel_gone(session, other, on_log)
                    try:
                        H.go_space_center(session, reload_save=False)
                        H._say("hop dismissed flight results", on_log)
                    except Exception as exc:
                        H.log.warning("hop dismiss flight results: %s", exc)
                    return hit

            met = H._vessel_met(vessel)
            frozen = False
            if cannot_pay:
                still_t0 = None
            elif left_pad and not H._recoverable(vessel):
                still_t0, frozen = H._met_still(met, prev_met, still_t0, clock())
            else:
                still_t0 = None
            sit_now = str(getattr(snap, "situation", "") or "")
            if frozen and sit_now in H._AIR and H._q_zero(snap):
                litho = True
                down = True
            cannot_pay = airborne_cannot_pay(
                lofted=lofted,
                down=down,
                started=started,
                science_attempted=science_attempted,
                waiting_hd=waiting_hd,
            )

            if down and left_pad and not pad_boost:
                if not said_down:
                    H._say("hop down", on_log)
                    said_down = True

            if H._abort_high_lid(
                lit=did_light,
                started=started,
                left_pad=left_pad,
                down=down,
                reached_lid=reached_lid,
            ):
                if not H._recoverable(vessel):
                    H._leave_crash_ui(session, on_log, total_wreck=True)
                call("abort_pad", ctx)
                raise MissionAbort("no science (FlyingHigh lid)")

            pad_boost = H._pad_boosting(
                lit=did_light,
                left_pad=left_pad,
                lofted=lofted,
                down=down,
                burning=burning_now,
            )
            if waiting_lid or hold_card or cannot_pay or wait_leftover:
                pass
            elif pad_boost:
                if not deaf:
                    _apply_pad_throttle(vessel)
            elif left_pad and (down or H._low_flying(snap)) and not _orbit_done_sit(
                snap, orbit=orbit
            ):
                got = H._force_recover(vessel, on_log)
                if got is not None:
                    return got

            if (
                left_pad
                and not down
                and flying_high
                and not orbit
                and (
                    reached_lid
                    or _lid_alt_reached(
                        snap, hop_apo, flying_high=True
                    )
                )
            ):
                _release_pad_throttle(vessel)

            if down and not left_pad:
                _cut_pad_engine(vessel)
                call("abort_pad", ctx)
                raise MissionAbort("wreck")

            if (
                left_pad
                and not said_crash
                and (waiting_hd or down or still_t0 is not None)
                and not H._recoverable(vessel)
            ):
                H._recover_tick(vessel, on_log)

            if frozen:
                sit_v = H._vessel_sit(vessel)
                if H._crash_ui(snap, vessel, frozen=True):
                    if not said_crash:
                        H._crash_line(vessel, snap, on_log)
                        said_crash = True
                    got = H._force_recover(vessel, on_log)
                    if got is not None:
                        return got
                    if not unpaused:
                        H._unpause(session, on_log)
                        unpaused = True
                        unpause_at = clock()
                        still_t0 = None
                        continue
                    if (
                        unpause_at is not None
                        and clock() - unpause_at < H._UNPAUSE_SETTLE_S
                    ):
                        still_t0 = None
                        nap(H._nap_dt(pulse, snap, braking=False))
                        continue
                    H._leave_crash_ui(session, on_log, total_wreck=True)
                    H.abort_ksc_leftover(vessel, on_log, why="total wreck")
                elif sit_v in H._AIR:
                    if not unpaused:
                        H._unpause(session, on_log)
                        unpaused = True
                        unpause_at = clock()
                    still_t0 = None
                elif not unpaused:
                    H._unpause(session, on_log)
                    unpaused = True
                    unpause_at = clock()
                    still_t0 = None
                else:
                    H._say("hop paused wreck", on_log)
                    log_events.emit("hop", result="paused")
                    mission_event("paused", snap)
                    got = H._finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                    raise MissionAbort("not recoverable")
            if met is not None and math.isfinite(met):
                prev_met = met

            try:
                met_now = float(getattr(snap, "met", float("nan")))
            except (TypeError, ValueError):
                met_now = float("nan")
            if not math.isfinite(met_now) and met is not None:
                met_now = met
            elapsed_m = met_elapsed(met_now, met0)
            elapsed_wall = clock() - t0
            timed_out = timeout_hit(
                met=met_now, met0=met0, budget=budget, down=down
            )
            if (
                not timed_out
                and pulses > 1
                and not math.isfinite(elapsed_m)
                and elapsed_wall >= budget
            ):
                timed_out = True
            if timed_out:
                if _orbit_done_sit(snap, orbit=orbit):
                    H._say("hop orbit", on_log)
                    return "orbit"
                if left_pad:
                    got = H._recover_hd(vessel, on_log)
                    if got is not None:
                        return got
                has = H._keep_hd(
                    vessel, ids, started, left_pad=left_pad, lit=did_light
                )
                if has and left_pad and not down:
                    if not waiting_hd:
                        H._say("hop wait recoverable", on_log)
                        waiting_hd = True
                    nap(H._nap_dt(pulse, snap, braking=False))
                    continue
                if down and left_pad:
                    raise MissionAbort("not recoverable")
                shown = elapsed_m if math.isfinite(elapsed_m) else elapsed_wall
                H._say(f"hop timeout {shown:.0f}s", on_log)
                if leftover_call(recoverable=H._recoverable(vessel)) == "recover":
                    got = H._force_recover(vessel, on_log)
                    if got is not None:
                        return got
                if left_pad:
                    H.abort_ksc_leftover(vessel, on_log, why="timeout")
                _cut_pad_engine(vessel)
                raise MissionAbort("timeout")
            nap(H._nap_dt(pulse, snap, braking=False))

    _cut_pad_engine(vessel)
    raise MissionAbort("timeout")
