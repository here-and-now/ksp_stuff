"""Orbit-stack ascent compose from control blocks.

Live RF throttle is ``rf_throttle`` (independent, not UI MainThrottle).
Warp clock is ``physics_warp``. Hangar / leftover / recover helpers
live on parked ``hop.py``. ``python main.py hop`` still dispatches
inland to hop_factory. ``python main.py ascent`` is this file.

Valiant loft now: apply live 1 until High lid MECO, then coast.
Heading while live is Autopilot east (SAS off, engage once, surface
frame) — SAS Stability is not a heading. ``RF.apply`` paints SAS on;
hold_live clears it once left_pad. Do not wait Terrier. Keyboard
pitch/yaw on SAS is not this. After lid MECO independent is off: no
plume, no moment. Last write after lid is ``RF.cut``. Plume still up
is still the burn — warp follows ``RF.burning``, not the keep flag
(06-52-19Z / 22-11-37Z UI throttle 0 thrust 100 kN past 50 km then
4× emptied tanks apo 257–323 km). Terrier two-stage later: keep live
through first-stage burnout (same east turn — no lid MECO), stage,
vacuum apply live near apo until Pe ≥ space. Timeout leftover from
High is silk/coast until down+recoverable — not ``ksc leftover``
while lofted rec=no (06-52-19Z MET 604 alt 135 km chute stowed;
22-11-37Z chute armed still flying). Pad never-loft leftover stays
leftover. Circularized recover no. Do not freeze Flea / Hammer /
4t / splash-090. Forest / Grasslands: same function. Tests lock
these sits, not a dead hang.
"""

from __future__ import annotations

import math
import time
from typing import Callable

import hop as H
import rf_throttle as RF
from emergencies import Ctx, call
from physics_warp import (
    apply_sit_warp,
    chute_arm_sit,
    chute_deploy_sit,
    leftover_call,
    space_low_sit as space_low_block,
    timeout_hit,
    unpause_clock,
)
from telem import EventLog, MissionAbort, Telem

LID_M = H.FLYING_LOW_M
SPACE_PE_M = H.FLYING_HIGH_M
FUEL_MIN = H.WATER_BRAKE_FUEL_MIN


def vacuum_stage_sit(vessel: object | None = None) -> bool:
    """Vacuum second stage on the hang (Terrier / LV-909). Valiant loft is not this."""
    if vessel is None:
        return False
    for eng in RF.engines(vessel):
        bits: list[str] = []
        for obj in (eng, getattr(eng, "part", None)):
            if obj is None:
                continue
            for attr in ("name", "title", "tag"):
                try:
                    raw = getattr(obj, attr, None)
                except Exception:
                    continue
                text = str(raw or "").strip().lower()
                if text:
                    bits.append(text)
        label = " ".join(bits)
        compact = label.replace(" ", "").replace("_", "-")
        if "terrier" in label or "lv-909" in label or "lv909" in compact:
            return True
        if "liquidengine2" in compact:
            return True
    return False


def loft_lid_sit(snap: object, hop_apo: float) -> bool:
    """Live alt ≥ High lid (50 km). Predicted apo in thick air is not the lid."""
    alt = H._snap_alt(snap)
    if not math.isfinite(alt):
        return False
    try:
        lid = float(hop_apo)
    except (TypeError, ValueError):
        lid = float("nan")
    if not math.isfinite(lid) or lid <= 0.0:
        lid = LID_M
    else:
        lid = min(lid, LID_M)
    return alt >= lid


def keep_live_sit(
    snap: object,
    *,
    lit: bool,
    left_pad: bool,
    down: bool,
    hop_apo: float,
    two_stage: bool = False,
    lofted_lid: bool = False,
) -> bool:
    """After light, keep independent live until MECO.

    Airborne UI MainThrottle GET 0 is not MECO. Loft: lid alt or
    crumbs — 06-52-19Z 59 km still thrusting is this sit, not keep.
    Two-stage: leftover LF is still the first-stage burn — no lid
    MECO. Pad sit after light is still the start.
    """
    if not lit or down:
        return False
    if not left_pad:
        return True
    fuel = H._snap_fuel(snap)
    if math.isfinite(fuel) and fuel <= FUEL_MIN:
        return False
    if two_stage:
        thrust = getattr(snap, "thrust", float("nan"))
        try:
            thrust_f = float(thrust)
        except (TypeError, ValueError):
            thrust_f = float("nan")
        if lofted_lid and math.isfinite(thrust_f) and thrust_f <= 1.0:
            return False
        return True
    if lofted_lid or loft_lid_sit(snap, hop_apo):
        return False
    return math.isfinite(fuel) and fuel > FUEL_MIN


def loft_meco_sit(
    snap: object,
    *,
    hop_apo: float,
    two_stage: bool = False,
    lofted_lid: bool = False,
) -> bool:
    """Single-stage loft MECO at High lid. Two-stage is not this."""
    if two_stage:
        return False
    return lofted_lid or loft_lid_sit(snap, hop_apo)


def turn_live_sit(
    *,
    lit: bool,
    left_pad: bool,
    down: bool,
    keep_live: bool,
    deaf: bool = False,
) -> bool:
    """AP heading while independent still 1. SAS hold is not this.

    Pad sit is still the start. After lid MECO independent is off —
    no plume, no moment. Do not wait Terrier. Forest / Grasslands: same.
    """
    return bool(lit and left_pad and keep_live and not down and not deaf)


def turn_cmd_pitch(
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


def space_low_sit(
    live_sit: str = "",
    *,
    lofted_lid: bool = False,
    down: bool = False,
) -> bool:
    """InSpaceLow after lid. Flying at 50 km is not this.

    Compose gate is lofted_lid / down. Live sit is physics_warp.
    Forest / Grasslands: same.
    """
    if not lofted_lid or down:
        return False
    return space_low_block(live_sit)


def circularize_sit(
    snap: object,
    *,
    two_stage: bool,
    down: bool,
    staged: bool = False,
) -> bool:
    """Apo vacuum burn until Pe ≥ space. Loft Valiant is not this."""
    if not two_stage or not staged or down:
        return False
    peri = getattr(snap, "peri", float("nan"))
    try:
        peri_f = float(peri)
    except (TypeError, ValueError):
        peri_f = float("nan")
    if math.isfinite(peri_f) and peri_f >= SPACE_PE_M:
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
    return (
        math.isfinite(vz)
        and vz <= 0.0
        and math.isfinite(alt)
        and alt >= LID_M
    )


def orbit_done_sit(snap: object, *, two_stage: bool = False) -> bool:
    """Circularized. Recover no."""
    if not two_stage:
        return False
    peri = getattr(snap, "peri", float("nan"))
    try:
        peri_f = float(peri)
    except (TypeError, ValueError):
        peri_f = float("nan")
    return math.isfinite(peri_f) and peri_f >= SPACE_PE_M


def lofted_wait_sit(
    *,
    lofted: bool,
    down: bool,
    recoverable: bool,
    two_stage: bool = False,
) -> bool:
    """Timeout clock is not leftover from High.

    Silk/coast until down and recoverable. Pad never-loft leftover
    stays leftover. Circularize / orbit rec=no is honest.
    Forest / Grasslands: same.
    """
    if two_stage or down or recoverable or not lofted:
        return False
    return True


def stage_sit(
    snap: object,
    *,
    two_stage: bool,
    staged: bool,
    keep_live: bool,
    down: bool,
) -> bool:
    """First-stage burnout, vacuum engine waiting. Not loft MECO."""
    if not two_stage or staged or down or keep_live:
        return False
    fuel = H._snap_fuel(snap)
    if math.isfinite(fuel) and fuel > FUEL_MIN:
        thrust = getattr(snap, "thrust", float("nan"))
        try:
            thrust_f = float(thrust)
        except (TypeError, ValueError):
            thrust_f = float("nan")
        if math.isfinite(thrust_f) and thrust_f > 1.0:
            return False
    return True


def light(
    vessel: object,
    on_log: Callable[[str], None] | None,
    snap: object | None,
    *,
    deaf: bool,
) -> bool:
    """Apply live 1, then stage. Independent is the meet, not the bar.

    Do not gate stage on UI MainThrottle or Engine.throttle GET.
    Confirmed light is plume / currentThrottle rising after the
    engine fires. Forest / Grasslands: same.
    """
    if deaf:
        H._light(vessel, on_log, snap)
        return True
    commanded = RF.live(vessel)
    if not (math.isfinite(commanded) and commanded > RF.LIVE_MIN):
        RF.apply(vessel, 1.0)
        return False
    try:
        control = vessel.control
    except Exception as exc:
        raise MissionAbort(f"light failed: {exc}") from exc
    try:
        control.sas = True
    except Exception:
        pass
    RF.apply(vessel, 1.0)
    if RF.rf_sit(vessel) and RF.thrusting(vessel, snap):
        H._say("ascent light", on_log)
        return True
    try:
        control.activate_next_stage()
    except Exception as exc:
        raise MissionAbort(f"light failed: {exc}") from exc
    H._say("ascent light", on_log)
    return True


def hold_live(vessel: object, *, sas: bool = False) -> None:
    """Restoke independent 1 without re-enable.

    ``RF.apply`` paints SAS on. SAS Stability is not a heading — pad
    sit may keep it; the east turn clears it. Forest / Grasslands: same.
    """
    RF.apply(vessel, 1.0)
    if sas:
        return
    try:
        control = getattr(vessel, "control", None)
        if control is not None:
            control.sas = False
    except Exception:
        pass


def run_ascent_vessel(
    session: object,
    vessel: object,
    *,
    events: EventLog | None = None,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    now: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
    timeout: float | None = None,
    pulse: float | None = None,
) -> str:
    """Light, keep live, lid MECO or two-stage circularize, recover.

    Caller Hangars. Parked water/splash stay in hop.py.
    Timeout leftover uses leftover_call (recover vs ksc leftover), not
    emergencies.call — ``ksc leftover`` is not an emergency verb.
    Lofted rec=no keeps silk/coast until down+recoverable.
    """
    log_events = events if events is not None else EventLog()
    hop_apo = H.hop_target_apo(space=True)
    ctx = Ctx(session=session, vessel=vessel, events=log_events, science_ids=())
    clock = now if now is not None else time.monotonic
    nap = sleep if sleep is not None else time.sleep
    budget = H.DEFAULT_HOP_S if timeout is None else float(timeout)
    t0 = clock()
    lit = False
    left_pad = False
    lofted = False
    lofted_lid = False
    staged = False
    said_down = False
    said_meco = False
    said_coast = [""]
    started: list[str] = []
    chute_armed = False
    said_wait = False
    met0: float | None = None
    turn_yawed = False
    turn_yaw_n = 0
    said_turn = False
    two_stage = vacuum_stage_sit(vessel)
    H._say(f"ascent apo={hop_apo:.0f}", on_log)
    H._say(
        "ascent gravity turn east while thrusting "
        f"heading={H.WATER_HEADING_DEG:g}",
        on_log,
    )
    if two_stage:
        H._say(
            "ascent no lid MECO, "
            f"circularize Pe>={SPACE_PE_M:.0f}",
            on_log,
        )
    else:
        H._say(
            f"ascent hold live until lid {min(hop_apo, LID_M):.0f} m, then MECO",
            on_log,
        )

    unpause_clock(session)
    with Telem(session, events=log_events) as telem:
        while True:
            if abort is not None:
                try:
                    stop = bool(abort())
                except Exception:
                    stop = False
                if stop:
                    RF.cut(vessel, abort=True)
                    call("abort_pad", ctx)
                    raise MissionAbort("abort")
            try:
                H._uplink_tick(ctx)
            except MissionAbort:
                RF.cut(vessel, abort=True)
                raise
            live = H._active(session, vessel)
            if live is None:
                raise MissionAbort("no vessel")
            vessel = live
            ctx.vessel = vessel
            snap = telem.read()
            deaf = H._zero_stick_if_deaf(vessel, snap)
            if deaf:
                RF.cut(vessel, abort=True)
            two_stage = two_stage or vacuum_stage_sit(vessel)
            down = H._down(snap, flown=left_pad)
            if H._airborne(snap) or down:
                left_pad = True
            lofted = lofted or H._lofted(snap)
            if loft_lid_sit(snap, hop_apo):
                lofted_lid = True
            if lit and met0 is None:
                met0 = H._vessel_met(vessel)
            if not lit:
                if light(vessel, on_log, snap, deaf=deaf):
                    lit = True
                    met0 = H._vessel_met(vessel)
                nap(H._nap_dt(pulse, snap))
                continue
            keep = keep_live_sit(
                snap,
                lit=lit,
                left_pad=left_pad,
                down=down,
                hop_apo=hop_apo,
                two_stage=two_stage,
                lofted_lid=lofted_lid,
            )
            if keep and not deaf:
                hold_live(vessel, sas=not left_pad)
            elif lit and not deaf:
                if loft_meco_sit(
                    snap,
                    hop_apo=hop_apo,
                    two_stage=two_stage,
                    lofted_lid=lofted_lid,
                ):
                    RF.cut(vessel)
                    if not said_meco:
                        H._say("ascent MECO", on_log)
                        said_meco = True
                if stage_sit(
                    snap,
                    two_stage=two_stage,
                    staged=staged,
                    keep_live=keep,
                    down=down,
                ):
                    try:
                        vessel.control.activate_next_stage()
                    except Exception as exc:
                        raise MissionAbort(f"stage failed: {exc}") from exc
                    RF.apply(vessel, 1.0)
                    staged = True
                    H._say("ascent stage", on_log)
                if circularize_sit(
                    snap, two_stage=two_stage, down=down, staged=staged
                ):
                    hold_live(vessel)
                elif orbit_done_sit(snap, two_stage=two_stage):
                    RF.cut(vessel)
                    H._say("ascent circularized", on_log)
                    return "ascent orbit"
            if turn_live_sit(
                lit=lit,
                left_pad=left_pad,
                down=down,
                keep_live=keep,
                deaf=deaf,
            ):
                flown_p = H._snap_pitch(snap)
                flown_h = H._snap_heading(snap)
                try:
                    met_slew = float(getattr(snap, "met", float("nan")))
                except (TypeError, ValueError):
                    met_slew = float("nan")
                if not turn_yawed:
                    turn_yaw_n += 1
                cmd_pitch, turn_yawed = turn_cmd_pitch(
                    turn_yawed,
                    turn_yaw_n,
                    flown_p,
                    flown_h,
                    met_slew,
                )
                H._steer_east(
                    vessel,
                    pitch=cmd_pitch,
                    flown_pitch=flown_p,
                    flown_heading=flown_h,
                    burning=True,
                )
                if not said_turn:
                    H._say(
                        "ascent turn east while live "
                        f"heading={H.WATER_HEADING_DEG:g}",
                        on_log,
                    )
                    said_turn = True
            live_now = H._live_sit(vessel, snap)
            live_biome = H._snap_biome(snap, vessel)
            if space_low_sit(live_now, lofted_lid=lofted_lid, down=down):
                try:
                    from tickets import science_ids_for

                    space_ids = science_ids_for(situation="inspacelow")
                except Exception:
                    space_ids = ()
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
                    H._say("ascent science " + ",".join(more), on_log)
            if (
                lofted_lid
                and not down
                and not chute_armed
                and chute_arm_sit(snap)
            ):
                H.arm_chutes(vessel, on_log)
                chute_armed = True
            if lofted_lid and not down and chute_deploy_sit(snap):
                H.deploy_chutes(vessel, on_log)
            burning_now = RF.burning(vessel, snap, lofted=lofted)
            apply_sit_warp(
                session,
                snap,
                left_pad=left_pad,
                down=down,
                burning=burning_now,
                on_log=on_log,
                last=said_coast,
            )
            met = H._vessel_met(vessel)
            if timeout_hit(met=met, met0=met0, budget=budget, down=down):
                rec = H._recoverable(vessel)
                why = leftover_call(recoverable=rec)
                if why == "recover":
                    RF.cut(vessel, abort=True)
                    got = H._force_recover(vessel, on_log)
                    if got is not None:
                        return got
                if lofted_wait_sit(
                    lofted=lofted,
                    down=down,
                    recoverable=rec,
                    two_stage=two_stage,
                ):
                    if not said_wait:
                        H._say("ascent wait recoverable", on_log)
                        said_wait = True
                else:
                    RF.cut(vessel, abort=True)
                    H.abort_ksc_leftover(vessel, on_log, why="timeout")
            if left_pad and down and H._recoverable(vessel):
                if not said_down:
                    H._say("ascent down", on_log)
                    said_down = True
                H._recover_tick(vessel, on_log)
                got = H._force_recover(vessel, on_log)
                if got is not None:
                    return got
            if clock() - t0 > budget * 4 and down:
                raise MissionAbort("timeout")
            nap(H._nap_dt(pulse, snap))
    raise MissionAbort("timeout")


def run_ascent(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """``python main.py ascent``: Hangar seated craft when pad empty, then loft.

    Unmatched leftover aborts ``ksc leftover``. Do not recover-then-Hangar.
    """
    leftover = H._find_unmatched_leftover(session)
    if leftover is not None:
        H._recover_unmatched_leftover(session, leftover, on_log)
    H.install_and_launch(session)
    try:
        msg = H.wait_vessel_ready(session)
    except Exception as exc:
        raise MissionAbort(f"no vessel after launch: {exc}") from exc
    H._say(msg, on_log)
    vessel = H._active_vessel(session)
    if vessel is None:
        raise MissionAbort("no vessel after launch")
    if H._is_pad_motor(vessel):
        raise MissionAbort("Hangar put kspstuff-pad-pbc — refused")
    return run_ascent_vessel(session, vessel, on_log=on_log, abort=abort)
