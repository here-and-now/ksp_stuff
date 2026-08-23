"""Factory inland hop pulse: light, slew 270, chute, sit-matched science, recover.

Parked water/splash CLIs stay in hop.py. This module must not name those
flags. Helpers live on the hop module so test patches of hop.* still bind.
"""

from __future__ import annotations

import math
import time
from typing import Callable

import hop as H
from emergencies import Ctx, call
from phases import OffPlan, check_expect
from screenshot import mission_event
from telem import EventLog, MissionAbort, Telem, gates


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
    prev_stack_mass = float("nan")
    prev_stack_fuel = float("nan")
    prev_stack_parts: int | None = None
    H._say(f"hop apo={hop_apo:.0f}", on_log)
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

            apo = getattr(snap, "apo", float("nan"))
            try:
                apo_f = float(apo)
            except (TypeError, ValueError):
                apo_f = float("nan")
            lid = H.hop_offplan_apo()
            label = "Space" if H.hop_wants_flying_high() else "FlyingLow"
            if H.hop_wants_flying_high():
                atm = getattr(snap, "atm_depth", float("nan"))
                try:
                    atm_f = float(atm)
                except (TypeError, ValueError):
                    atm_f = float("nan")
                if math.isfinite(atm_f) and atm_f > 0.0:
                    lid = atm_f
            if (
                left_pad
                and not down
                and not waiting_hd
                and math.isfinite(apo_f)
                and apo_f > lid
            ):
                raise OffPlan(f"apo {apo_f:.0f} > {lid:.0f} {label}")
            if left_pad and not down and not waiting_hd:
                check_expect(snap, skip_peri=True, skip_apo=True)

            if not lit:
                if airborne:
                    lit = True
                elif not left_pad and str(snap.situation) in H._LIGHT_SIT:
                    H._light(vessel, on_log)
                    lit = True
                    did_light = True
                    log_events.emit("hop", result="light")
                    mission_event(
                        "light",
                        snap,
                        beauty=True,
                        pose="pad-plume",
                        session=session,
                    )

            if left_pad and not down:
                apo_cut, _braking = H._hold_or_cut(
                    vessel,
                    snap,
                    hop_apo,
                    cut=apo_cut,
                    hold=1.0,
                    brake=False,
                    braking=False,
                )
                del _braking

            burning_now = H._burning(vessel, snap, lofted=lofted)
            if lit and not down and left_pad:
                flown_p = H._snap_pitch(snap)
                flown_h = H._snap_heading(snap)
                try:
                    met_slew = float(getattr(snap, "met", float("nan")))
                except (TypeError, ValueError):
                    met_slew = float("nan")
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

            if left_pad and not down and not chute_open:
                st_now = str(getattr(snap, "chute", "") or "")
                if st_now in H._CHUTE_OPEN:
                    chute_open = True
                else:
                    if not chute_armed:
                        st = H.arm_chutes(vessel, on_log)
                        chute_armed = True
                        if st in {"", "none"}:
                            chute_open = True
                        else:
                            H._say(f"hop chute {st}", on_log)
                    if not chute_open and not burning_now:
                        vz_ch = H._snap_v_vert(snap)
                        try:
                            alt_ch = float(getattr(snap, "alt", float("nan")))
                        except (TypeError, ValueError):
                            alt_ch = float("nan")
                        descending = math.isfinite(vz_ch) and vz_ch < 0.0
                        if (
                            descending
                            and math.isfinite(alt_ch)
                            and 0.0 < alt_ch <= H.CHUTE_DEPLOY_ALT_M
                        ):
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

            H._apply_hop_physics(
                session,
                coast=H._want_coast_phys(
                    snap,
                    left_pad=left_pad,
                    down=down,
                    chute_open=chute_open,
                    burning=burning_now,
                ),
                on_log=on_log,
                last=said_coast,
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
                elif H._science_ready(snap):
                    need = H.bound_science_need(
                        live_sit=H._live_sit(vessel, snap),
                        live_biome=H._snap_biome(snap, vessel),
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
                        H._say("science skip (situation cannot pay)", on_log)
                elif H.hop_wants_flying_high() and not said_lid:
                    H._say("science wait FlyingHigh", on_log)
                    said_lid = True

            missed_lid = (
                H.hop_wants_flying_high()
                and did_light
                and not started
                and left_pad
                and down
            )
            if missed_lid:
                if not H._recoverable(vessel):
                    H._leave_crash_ui(session, on_log, total_wreck=True)
                call("abort_pad", ctx)
                raise MissionAbort("no science (FlyingHigh lid)")

            waiting_lid = (
                H.hop_wants_flying_high()
                and did_light
                and not started
                and left_pad
                and not down
            )

            if left_pad and down and not waiting_hd:
                need = H.bound_science_need(
                    live_sit=H._live_sit(vessel, snap),
                    live_biome=H._snap_biome(snap, vessel),
                )
                landed_ids = H.hop_landed_science_ids()
                pending = tuple(eid for eid in landed_ids if eid not in started)
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

            hold_card = H._hold_ground_card(vessel, started, ids, snap)

            pad_boost = H._pad_boosting(
                lit=did_light,
                left_pad=left_pad,
                lofted=lofted,
                down=down,
                burning=burning_now,
            )
            if waiting_lid or hold_card:
                pass
            elif pad_boost:
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
            if left_pad and not H._recoverable(vessel):
                still_t0, frozen = H._met_still(met, prev_met, still_t0, clock())
            else:
                still_t0 = None
            sit_now = str(getattr(snap, "situation", "") or "")
            if frozen and sit_now in H._AIR and H._q_zero(snap):
                litho = True
                down = True

            if down and left_pad:
                if not said_down:
                    H._say("hop down", on_log)
                    said_down = True

            if (
                H.hop_wants_flying_high()
                and did_light
                and not started
                and left_pad
                and down
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
            if waiting_lid or hold_card:
                pass
            elif pad_boost:
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

            elapsed = clock() - t0
            if pulses > 1 and elapsed >= budget:
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
                H._say(f"hop timeout {elapsed:.0f}s", on_log)
                raise MissionAbort("timeout")
            nap(H._nap_dt(pulse, snap, braking=False))

    raise MissionAbort("timeout")
