"""Factory inland hop pulse: light, slew 270, chute, sit-matched science, recover.

Flying card after loft. FlyingHigh wait is loft to lid alt, not a dwell
at 1 km. Lid hold is throttle 1 + SAS vertical until lid; inland slew
after. Airborne cannot-pay: FlyingLow skip still lofts — High waits the
lid, then Toggle; skip-latch does not drop a bound High card. After
High lid, 1× (dwell / reentry). FlyingLow skip may still 4×. Then
coast, chute, land leftover. Pad boost (fuel, not lofted) does not science or hop-down —
sit=landed at pad alt with fuel is still burning. Parked water/splash
CLIs stay in hop.py. This module must not name those flags. Helpers live
on the hop module so test patches of hop.* still bind.
"""

from __future__ import annotations

import math
import time
from typing import Callable

import hop as H
from emergencies import Ctx, call
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


def _lid_alt_reached(snap: object, hop_apo: float) -> bool:
    """FlyingHigh hop_apo is live altitude. Predicted apo in thick air is not the lid."""
    if not H.hop_wants_flying_high():
        return False
    alt = H._snap_alt(snap)
    return math.isfinite(alt) and alt >= hop_apo


def _lid_burn_sit(
    snap: object, *, hop_apo: float, flying_high: bool
) -> bool:
    """Leftover LF before lid alt is still the burn sit. Not lofted burnout.

    FlyingHigh wait at ~1 km is not FlyingHigh. Throttle 0 with leftover
    LF is not 4×. Crumbs before lid may coast if q is actually low.
    After lid, ``_high_dwell_sit`` is 1×.
    """
    if not flying_high:
        return False
    if _lid_alt_reached(snap, hop_apo):
        return False
    fuel = H._snap_fuel(snap)
    return math.isfinite(fuel) and fuel > H.WATER_BRAKE_FUEL_MIN


def _high_dwell_sit(*, reached_lid: bool, down: bool) -> bool:
    """After FlyingHigh lid, 1×. Skip FlyingLow may still 4×.

    Paying High dwell and High descent are not lofted burnout.
    Forest / Grasslands: same.
    """
    return bool(reached_lid) and not down


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
    return not _lid_alt_reached(snap, hop_apo)


def _hold_lid(
    vessel: object,
    snap: object,
    *,
    hop_apo: float,
    flying_high: bool,
    lofted_lid: bool = False,
) -> bool:
    """FlyingHigh below lid: throttle 1, SAS vertical. Not inland slew.

    AP engage at zenith has no heading. Inland slew clears SAS and does
    not hold vertical. SAS from light holds the loft until lid alt or
    crumbs. Forest / Grasslands: same.
    """
    burn = _lid_burn_sit(snap, hop_apo=hop_apo, flying_high=flying_high)
    vertical = _lid_vertical_sit(
        snap, hop_apo=hop_apo, flying_high=flying_high, lofted_lid=lofted_lid
    )
    if not burn and not vertical:
        return False
    try:
        control = vessel.control
    except Exception:
        return True
    if burn:
        try:
            control.throttle = 1.0
        except Exception:
            pass
    if vertical:
        try:
            control.sas = True
        except Exception:
            pass
    return True


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
    Throttle 0 with a full tank is not burnout. Forest / Grasslands: same.
    """
    if not chute_arm_sit(snap):
        return False
    if not flying_high:
        return True
    return crumbs or apo_cut or _lid_alt_reached(snap, hop_apo)


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
    return crumbs or apo_cut or _lid_alt_reached(snap, hop_apo)


def _offplan_apo_lid(snap: object) -> float:
    """OffPlan apo lid. Gene expect_apo_max raises it; hop_apo is the cut.

    FlyingLow stays ≥50 km so an SRB overshoot is not OffPlan. FlyingHigh
    sit is Space unless the plan envelope is higher. A paying FlyingHigh
    loft under that envelope is not Space OffPlan. Forest / Grasslands: same.
    """
    lid = H.hop_offplan_apo()
    if not H.hop_wants_flying_high():
        return lid
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
    ids = science_ids if science_ids is not None else H.hop_science_ids()
    hop_apo = H.hop_target_apo()
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
    said_lid = False
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
    H._say(f"hop apo={hop_apo:.0f}", on_log)
    if H.hop_wants_flying_high():
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
                    call("abort_pad", ctx)
                    raise MissionAbort("abort")
            H._uplink_tick(ctx)
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
            if H._reached_high_lid(snap):
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
                try:
                    vessel.control.throttle = 0.0
                except Exception:
                    pass
            if left_pad and not down:
                if chute_open:
                    apo_cut = True
                flying_high = H.hop_wants_flying_high()
                if _lid_alt_reached(snap, hop_apo):
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
                    snap, hop_apo=hop_apo, flying_high=flying_high
                )
                if lid_burn:
                    apo_cut = False
                else:
                    apo_cut, _braking = H._hold_or_cut(
                        vessel,
                        snap,
                        math.inf if flying_high else hop_apo,
                        cut=apo_cut,
                        hold=1.0,
                        brake=False,
                        braking=False,
                    )
                    del _braking
                _hold_lid(
                    vessel,
                    snap,
                    hop_apo=hop_apo,
                    flying_high=flying_high,
                    lofted_lid=reached_lid,
                )

            apo = getattr(snap, "apo", float("nan"))
            try:
                apo_f = float(apo)
            except (TypeError, ValueError):
                apo_f = float("nan")
            lid = _offplan_apo_lid(snap)
            label = "Space" if H.hop_wants_flying_high() else "FlyingLow"
            if (
                left_pad
                and not down
                and not waiting_hd
                and math.isfinite(apo_f)
                and apo_f > lid
                and not (H.hop_wants_flying_high() and apo_cut)
            ):
                raise OffPlan(f"apo {apo_f:.0f} > {lid:.0f} {label}")
            if left_pad and not down and not waiting_hd:
                check_expect(snap, skip_peri=True, skip_apo=True)

            if not lit:
                if airborne:
                    lit = True
                elif not left_pad and str(snap.situation) in H._LIGHT_SIT:
                    H._light(vessel, on_log, snap)
                    if not deaf:
                        try:
                            vessel.control.throttle = 1.0
                        except Exception:
                            pass
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

            burning_now = H._burning(vessel, snap, lofted=lofted) or _lid_burn_sit(
                snap,
                hop_apo=hop_apo,
                flying_high=H.hop_wants_flying_high(),
            )
            if lit and not down and left_pad and not deaf:
                flown_p = H._snap_pitch(snap)
                flown_h = H._snap_heading(snap)
                try:
                    met_slew = float(getattr(snap, "met", float("nan")))
                except (TypeError, ValueError):
                    met_slew = float("nan")
                flying_high = H.hop_wants_flying_high()
                if _lid_vertical_sit(
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
                        burning=burning_now,
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
                if not burning_now and not said_hold:
                    H._say("hop hold inland through burnout", on_log)
                    said_hold = True

            apply_sit_warp(
                session,
                snap,
                left_pad=left_pad,
                down=down,
                burning=burning_now
                or _high_dwell_sit(reached_lid=reached_lid, down=down),
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
                elif lofted and H._science_ready(snap):
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
                    elif ids and not H.hop_wants_flying_high():
                        science_attempted = True
                        H._say("science skip (situation cannot pay)", on_log)
                    elif H.hop_wants_flying_high() and not said_lid:
                        H._say("science wait FlyingHigh", on_log)
                        said_lid = True
                elif (
                    H.hop_wants_flying_high()
                    and not said_lid
                    and _lid_alt_reached(snap, hop_apo)
                ):
                    H._say("science wait FlyingHigh", on_log)
                    said_lid = True

            if left_pad and not down:
                _hold_lid(
                    vessel,
                    snap,
                    hop_apo=hop_apo,
                    flying_high=H.hop_wants_flying_high(),
                    lofted_lid=reached_lid,
                )

            waiting_lid = (
                H.hop_wants_flying_high()
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
            ground_now = down or "landed" in live_l or "splash" in live_l
            leftover_ids = H.hop_landed_science_ids()
            matching_ids = H.hop_landed_science_ids(
                live_sit=live_now, live_biome=live_biome
            )
            started_ground: list[str] = []
            if left_pad and ground_now and not waiting_hd and lofted:
                need = H.bound_science_need(
                    live_sit=live_now,
                    live_biome=live_biome,
                )
                pending = tuple(eid for eid in matching_ids if eid not in started)
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
                    if ground_now
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
                    try:
                        vessel.control.throttle = 1.0
                    except Exception:
                        pass
            elif left_pad and H._recoverable(vessel):
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
                    try:
                        vessel.control.throttle = 1.0
                    except Exception:
                        pass
            elif left_pad and (down or H._low_flying(snap)):
                got = H._force_recover(vessel, on_log)
                if got is not None:
                    return got

            if down and not left_pad:
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
                raise MissionAbort("timeout")
            nap(H._nap_dt(pulse, snap, braking=False))

    raise MissionAbort("timeout")
