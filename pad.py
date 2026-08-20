"""Pad science compose. Not hop.py.

Hangar a PBC Start probe, start Kerbalism Experiment modules, dwell
until the HD has the card (or remaining EC is gone), recover or abort
honestly. Pad EC=0 with data recovers; empty HD aborts.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from emergencies import Ctx, call
from hangar import discover_hangar
from science import (
    PAD_EXPERIMENTS,
    card_complete,
    card_has_data,
    pad_dwell_s,
    start_experiments,
)
from telem import EventLog, MissionAbort, Telem, gates
from uplink import take

log = logging.getLogger("kspstuff")

CRAFT = "kspstuff-pad-pbc"
_PULSE_S = 1.0
_DWELL_ABORT = frozenset({"abort_pad", "abort", "hold", "freeze", "recover"})


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def _ec_has_science(
    vessel: object,
    science_ids: tuple[str, ...] | list[str],
    saw_running: dict[tuple, bool],
    pulses: int,
) -> bool:
    """Pad EC=0 is not a wreck if the HD already has data, or we already ran."""
    if card_has_data(vessel, science_ids):
        return True
    if pulses <= 1:
        return False
    return any(saw_running.values())


def _load_catalog() -> object | None:
    try:
        from catalog import load_catalog

        hangar = discover_hangar()
        if hangar is None:
            return None
        return load_catalog(hangar.ksp_root)
    except Exception:
        return None


def dwell_for_card(
    session: object,
    vessel: object,
    *,
    science_ids: tuple[str, ...] | list[str],
    events: EventLog,
    on_log: Callable[[str], None] | None = None,
    ctx: Ctx,
    now: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
    timeout: float | None = None,
    abort: Callable[[], bool] | None = None,
    pulse: float = _PULSE_S,
) -> str:
    """Telem pulse until card HD is done, catalog duration, or honest abort.

    Does not Toggle. Does not recover on the first pulse.
    """
    clock = now if now is not None else time.monotonic
    nap = sleep if sleep is not None else time.sleep
    budget = timeout
    t0 = clock()
    saw_running: dict[tuple, bool] = {}
    pulses = 0
    _say("science dwell", on_log)
    events.emit("science_dwell", phase="start")
    with Telem(session, events=events) as telem:
        while True:
            if abort is not None:
                try:
                    stop = bool(abort())
                except Exception:
                    stop = False
                if stop:
                    call("abort_pad", ctx)
                    raise MissionAbort("abort")
            cmd = take()
            if cmd is not None:
                verb = str(getattr(cmd, "verb", "") or "").lower().replace("-", "_")
                try:
                    call(cmd.verb, ctx)
                except KeyError:
                    pass
                if verb in _DWELL_ABORT:
                    raise MissionAbort(verb)
            snap = telem.read()
            pulses += 1
            for reason in gates(snap):
                _say(f"gate {reason}", on_log)
                if reason == "wreck" or reason.startswith("reliability"):
                    call("abort_pad", ctx)
                    raise MissionAbort(reason)
                if reason == "ec=0":
                    card_complete(vessel, science_ids, saw_running)
                    if _ec_has_science(vessel, science_ids, saw_running, pulses):
                        _say("science dwell ec=0 with data", on_log)
                        events.emit("science_dwell", result="ec")
                        return "ec"
                    call("abort_pad", ctx)
                    raise MissionAbort(reason)
            if pulses > 1 and card_complete(vessel, science_ids, saw_running):
                _say("science dwell done", on_log)
                events.emit("science_dwell", result="done")
                return "done"
            if pulses == 1:
                card_complete(vessel, science_ids, saw_running)
            elapsed = clock() - t0
            if budget is None:
                budget = pad_dwell_s(
                    science_ids,
                    vessel=vessel,
                    catalog=_load_catalog(),
                    ec=snap.ec,
                )
            if pulses > 1 and elapsed >= budget:
                _say(f"science dwell timeout {elapsed:.0f}s", on_log)
                events.emit("science_dwell", result="timeout", s=elapsed)
                return "timeout"
            nap(pulse)


def recover_or_abort(vessel: object) -> str:
    """Recover the HD if KSP will allow it; otherwise honest abort."""
    try:
        ok = bool(getattr(vessel, "recoverable", False))
    except Exception:
        ok = False
    if ok:
        getattr(vessel, "recover")()
        return "recovered"
    raise MissionAbort("not recoverable")


def run_on_vessel(
    session: object,
    vessel: object,
    *,
    events: EventLog | None = None,
    on_log: Callable[[str], None] | None = None,
    science_ids: tuple[str, ...] = PAD_EXPERIMENTS,
    abort: Callable[[], bool] | None = None,
    now: Callable[[], float] | None = None,
    sleep: Callable[[float], None] | None = None,
    timeout: float | None = None,
    pulse: float = _PULSE_S,
) -> str:
    """Science, dwell until HD has the card, recover/abort."""
    log_events = events if events is not None else EventLog()
    ctx = Ctx(
        session=session,
        vessel=vessel,
        events=log_events,
        science_ids=science_ids,
    )
    cmd = take()
    if cmd is not None:
        try:
            call(cmd.verb, ctx)
        except KeyError:
            pass
    started = start_experiments(vessel, names=science_ids, on_log=on_log)
    if started:
        _say("science " + ",".join(started), on_log)
        log_events.emit("science", ids=list(started))
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
        _say("science (none)", on_log)
        if science_ids:
            wanted = ",".join(science_ids)
            call("abort_pad", ctx)
            raise MissionAbort(f"no science (wanted {wanted})")
        with Telem(session, events=log_events) as telem:
            snap = telem.read()
        for reason in gates(snap):
            _say(f"gate {reason}", on_log)
            if reason == "wreck" or reason.startswith("reliability") or reason == "ec=0":
                call("abort_pad", ctx)
                raise MissionAbort(reason)
    result = recover_or_abort(vessel)
    _say(result, on_log)
    return result


def install_and_launch(session: object, *, recover: bool = True) -> None:
    from craft import pad_pbc
    from catalog import load_catalog
    from missions import pad_craft_name

    wanted = pad_craft_name()
    hangar = discover_hangar()
    if hangar is None:
        raise MissionAbort("KSP install not found (KSPSTUFF_KSP or ~/Games/KSP-rss)")
    catalog = load_catalog(hangar.ksp_root)
    craft = pad_pbc(wanted, catalog=catalog)
    hangar.install(craft, overwrite=True)
    hangar.launch(session, craft.name, recover=recover, uncrewed=True)


def run_pad(
    session: object,
    *,
    recover: bool = True,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    events: EventLog | None = None,
) -> str:
    """Hangar + Kerbalism pad science. Probes are uncrewed."""
    log_events = events if events is not None else EventLog()
    install_and_launch(session, recover=recover)
    time.sleep(1.0)
    try:
        vessel = session.active_vessel  # type: ignore[attr-defined]
    except Exception as exc:
        raise MissionAbort(f"no vessel after launch: {exc}") from exc
    if vessel is None:
        raise MissionAbort("no vessel after launch")
    return run_on_vessel(
        session, vessel, events=log_events, on_log=on_log, abort=abort
    )


def run_phase(
    session: object,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
) -> str:
    """``phase pad``: already launched. No Hangar."""
    try:
        vessel = session.active_vessel  # type: ignore[attr-defined]
    except Exception:
        vessel = None
    if vessel is None:
        raise MissionAbort("no active vessel — python main.py pad to Hangar")
    return run_on_vessel(session, vessel, on_log=on_log, abort=abort)
