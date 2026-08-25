"""Splash-goo block.

After hop: leftover Flea only. Do not Hangar. Do not light. Do not start
mysteryGoo airborne. Wait until splashed, one Toggle on GooExperiment,
dwell the splash card, recover HD when splashed/recoverable. Landed is
not Water. Hop leftover at SpaceCenter enters Flight. Frozen Flight
Results recovers debris then leaves the scene. Splash goo is not a hop
start — hop recovers on first recoverable and would kill this dwell.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Callable


from emergencies import Ctx, call
from hop import (
    _STILL_MET,
    _STILL_N,
    _active,
    _ensure_flight,
    _find_hop_vessel,
    _finish_hd,
    _hd_ready,
    _is_pad_motor,
    _recover_hd,
    _vessel_met,
)
from pad import dwell_for_card
from card import NO_BOUND_CARD, card_splash_ids
from science import (
    hd_has_data,
    start_experiments,
)
from screenshot import mission_event
from telem import EventLog, MissionAbort, Telem, gates
from uplink import take

log = logging.getLogger("kspstuff")

_PULSE_S = 1.0
_ABORT_UPLINK = frozenset({"abort_pad", "abort", "hold", "freeze", "recover"})
# Extra-stage is splash's. Science/transmit are Gene radio (Kerbalism events).
_UPLINK_SKIP = frozenset({"stage"})
_SPLASHED = frozenset({"splashed"})
_LANDED = frozenset({"landed"})
_PAD_SIT = frozenset({"pre_launch", "prelaunch"})


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def splash_science_ids() -> tuple[str, ...]:
    """Splash experiments. Science tickets first; science.md is fallback."""
    from tickets import science_ids_for

    ids = science_ids_for(situation="splash")
    if ids:
        return ids
    from missions import seated_science_path

    path = seated_science_path()
    if not path.is_file():
        raise MissionAbort(NO_BOUND_CARD)
    ids = card_splash_ids(path.read_text(encoding="utf-8"))
    if not ids:
        raise MissionAbort(NO_BOUND_CARD)
    return ids


def _sit(snap: object) -> str:
    return str(getattr(snap, "situation", "") or "")


def _uplink_tick(ctx: Ctx) -> None:
    cmd = take()
    if cmd is None:
        return
    verb = str(getattr(cmd, "verb", "") or "").lower().replace("-", "_")
    if verb in _UPLINK_SKIP:
        return
    try:
        call(cmd.verb, ctx)
    except KeyError:
        pass
    if verb in _ABORT_UPLINK:
        raise MissionAbort(verb)


def run_on_vessel(
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
    pulse: float = _PULSE_S,
) -> str:
    """Wait for Water, start splash goo, dwell, recover. Caller does not Hangar."""
    log_events = events if events is not None else EventLog()
    ids = science_ids if science_ids is not None else splash_science_ids()
    ctx = Ctx(session=session, vessel=vessel, events=log_events, science_ids=ids)
    clock = now if now is not None else time.monotonic
    nap = sleep if sleep is not None else time.sleep
    prev_met: float | None = None
    still = 0
    _say("splash wait water", on_log)

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
            _uplink_tick(ctx)
            live = _active(session, vessel)
            if live is None:
                got = _finish_hd(session, vessel, on_log)
                if got is not None:
                    return got
                raise MissionAbort("no vessel")
            vessel = live
            ctx.vessel = vessel
            snap = telem.read()
            sit = _sit(snap)
            splashed = sit in _SPLASHED
            landed = sit in _LANDED

            for reason in gates(snap):
                if reason == "empty tanks" or reason.startswith("atmosphere"):
                    continue
                _say(f"gate {reason}", on_log)
                if reason == "wreck":
                    if splashed:
                        continue
                    got = _finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                    raise MissionAbort("wreck")
                if reason.startswith("reliability"):
                    call("abort_pad", ctx)
                    raise MissionAbort(reason)
                if reason == "ec=0":
                    if _hd_ready(vessel, ids, []) or hd_has_data(vessel):
                        got = _recover_hd(vessel, on_log)
                        if got is not None:
                            return got
                        got = _finish_hd(session, vessel, on_log)
                        if got is not None:
                            return got
                    # Card not started (17-46-04Z hop-splash): do not kill
                    # splash wait on EC=0. Start TELEMETRY/goo after Water.
                    continue

            if sit in _PAD_SIT:
                raise MissionAbort("not splashed (still on pad)")
            if landed and not splashed:
                raise MissionAbort("not splashed")
            if splashed:
                _say("splash down", on_log)
                log_events.emit("splash", result="down")
                mission_event(
                    "splash",
                    snap,
                    beauty=True,
                    pose="splash",
                    session=session,
                )
                break

            met = _vessel_met(vessel)
            if met is not None and not math.isfinite(met):
                got = _finish_hd(session, vessel, on_log)
                if got is not None:
                    return got
                raise MissionAbort("not recoverable")
            if (
                met is not None
                and prev_met is not None
                and abs(met - prev_met) < _STILL_MET
            ):
                still += 1
                if still >= _STILL_N:
                    _say("splash paused wreck", on_log)
                    got = _finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                    raise MissionAbort("not recoverable")
            else:
                still = 0
            if met is not None and math.isfinite(met):
                prev_met = met
            nap(pulse)

    # Card order: TELEMETRY 30 s then goo 641 s (tape 1.0 — not both at once).
    for eid in ids:
        started = start_experiments(vessel, names=(eid,), on_log=on_log)
        if started:
            _say("science " + ",".join(started), on_log)
            log_events.emit("science", ids=list(started))
            mission_event(
                "science",
                beauty=True,
                pose="science",
                session=session,
            )
            dwell_for_card(
                session,
                vessel,
                science_ids=tuple(started),
                events=log_events,
                on_log=on_log,
                ctx=ctx,
                now=now,
                sleep=sleep,
                timeout=timeout,
                abort=abort,
                pulse=pulse,
            )
        else:
            if hd_has_data(vessel) or eid == "kerbalism_TELEMETRY":
                _say(
                    f"science keep {eid} (already started or HD)",
                    on_log,
                )
                dwell_for_card(
                    session,
                    vessel,
                    science_ids=(eid,),
                    events=log_events,
                    on_log=on_log,
                    ctx=ctx,
                    now=now,
                    sleep=sleep,
                    timeout=timeout,
                    abort=abort,
                    pulse=pulse,
                )
            else:
                call("abort_pad", ctx)
                raise MissionAbort("no science (wanted " + eid + ")")

    got = _recover_hd(vessel, on_log)
    if got is not None:
        return got
    _say("splash wait recoverable", on_log)
    still = 0
    prev_met = None
    t1 = clock()
    with Telem(session, events=log_events) as telem:
        while True:
            if abort is not None:
                try:
                    stop = bool(abort())
                except Exception:
                    stop = False
                if stop:
                    raise MissionAbort("abort")
            live = _active(session, vessel)
            if live is None:
                got = _finish_hd(session, vessel, on_log)
                if got is not None:
                    return got
                raise MissionAbort("no vessel")
            vessel = live
            snap = telem.read()
            got = _recover_hd(vessel, on_log)
            if got is not None:
                return got
            met = _vessel_met(vessel)
            if met is not None and not math.isfinite(met):
                got = _finish_hd(session, vessel, on_log)
                if got is not None:
                    return got
                raise MissionAbort("not recoverable")
            if (
                met is not None
                and prev_met is not None
                and abs(met - prev_met) < _STILL_MET
            ):
                still += 1
                if still >= _STILL_N:
                    got = _finish_hd(session, vessel, on_log)
                    if got is not None:
                        return got
                    raise MissionAbort("not recoverable")
            else:
                still = 0
            if met is not None and math.isfinite(met):
                prev_met = met
            if timeout is not None and clock() - t1 >= float(timeout):
                raise MissionAbort("not recoverable")
            nap(pulse)


def run_phase(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """``python main.py splash`` / ``phase splash``: leftover hop Flea. No Hangar."""
    vessel = _find_hop_vessel(session)
    if vessel is None:
        raise MissionAbort(
            "no hop leftover — hop first (not Hangar pad; not a second Flea)"
        )
    if _is_pad_motor(vessel):
        raise MissionAbort("splash refused kspstuff-pad-pbc — need hop Flea")
    splash_science_ids()
    _ensure_flight(session, vessel, on_log)
    live = session.active_vessel if hasattr(session, "active_vessel") else vessel
    try:
        if live is not None:
            vessel = live
    except Exception:
        pass
    return run_on_vessel(session, vessel, on_log=on_log, abort=abort)


def run_splash(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """Same as ``phase splash``. Never Hangars."""
    return run_phase(session, on_log=on_log, abort=abort)
