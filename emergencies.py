"""Named emergency callables. Commander and Gene uplink use this table.

New names require a library change, not a heredoc in a phase.
``loop.md`` is not the stick.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

log = logging.getLogger("kspstuff")

NAMES: tuple[str, ...] = (
    "hold",
    "cut",
    "no_warp",
    "stage",
    "recover",
    "science",
    "transmit",
    "abort_pad",
)

# Uplink verbs that map onto NAMES.
ALIASES: dict[str, str] = {
    "hold": "hold",
    "freeze": "hold",
    "cut": "cut",
    "no_warp": "no_warp",
    "no-warp": "no_warp",
    "stage": "stage",
    "recover": "recover",
    "science": "science",
    "transmit": "transmit",
    "abort_pad": "abort_pad",
    "abort": "abort_pad",
}

# Kerbalism TX is an Experiment event. Never Toggle (start/stop) or stock dump.
_TX_NEVER = ("toggle", "dump", "reset")


@dataclass
class Ctx:
    session: Any
    vessel: Any = None
    events: Any = None
    science_ids: tuple[str, ...] | None = None
    notes: list[str] = field(default_factory=list)


def _vessel(ctx: Ctx) -> Any:
    if ctx.vessel is not None:
        return ctx.vessel
    try:
        return ctx.session.active_vessel
    except Exception:
        return None


def _emit(ctx: Ctx, kind: str, **fields: Any) -> None:
    events = ctx.events
    if events is None:
        return
    emit = getattr(events, "emit", None)
    if callable(emit):
        emit(kind, **fields)


def _lithobrake(vessel: Any) -> bool:
    if vessel is None:
        return False
    try:
        orbit = vessel.orbit
        peri = float(orbit.periapsis_altitude)
        alt = float(vessel.flight().mean_altitude)
        body = orbit.body
        in_atmo = bool(getattr(body, "has_atmosphere", False)) and alt < float(
            body.atmosphere_depth
        )
        return peri < 0.0 and not in_atmo and alt < 30_000.0
    except Exception:
        return False


def _drop_warp(session: Any) -> None:
    from physics_warp import set_factor

    set_factor(session, 0)


def hold(ctx: Ctx) -> str:
    """Cut throttle and warp. Lithobrake (airless, peri < 0, alt < 30 km) keeps throttle 1."""
    vessel = _vessel(ctx)
    _drop_warp(ctx.session)
    if vessel is None:
        _emit(ctx, "call", name="hold")
        return "hold"
    try:
        control = vessel.control
        if _lithobrake(vessel):
            control.throttle = 1.0
            ctx.notes.append("lithobrake")
        else:
            control.throttle = 0.0
        try:
            ap = vessel.auto_pilot
            ap.disengage()
        except Exception:
            try:
                vessel.auto_pilot.engaged = False
            except Exception:
                pass
    except Exception:
        log.debug("hold control failed", exc_info=True)
    _emit(ctx, "call", name="hold")
    return "hold"


def cut(ctx: Ctx) -> str:
    vessel = _vessel(ctx)
    if vessel is not None:
        try:
            vessel.control.throttle = 0.0
        except Exception:
            pass
    _emit(ctx, "call", name="cut")
    return "cut"


def no_warp(ctx: Ctx) -> str:
    _drop_warp(ctx.session)
    try:
        from uplink import desk

        desk.skip_warp = True
        desk.phys_warp = 1
    except Exception:
        pass
    _emit(ctx, "call", name="no_warp")
    return "no_warp"


def stage(ctx: Ctx) -> str:
    vessel = _vessel(ctx)
    if vessel is not None:
        try:
            vessel.control.activate_next_stage()
        except Exception:
            pass
    _emit(ctx, "call", name="stage")
    return "stage"


def recover(ctx: Ctx) -> str:
    vessel = _vessel(ctx)
    if vessel is None:
        _emit(ctx, "call", name="recover", ok=0)
        return "recover"
    try:
        if bool(getattr(vessel, "recoverable", False)):
            try:
                from science import stop_experiments

                stop_experiments(vessel)
            except Exception:
                log.debug("science stop before recover failed", exc_info=True)
            try:
                from flightlog import record_recover_vessel

                record_recover_vessel(vessel)
            except Exception:
                log.debug("kind=recover tape failed", exc_info=True)
            vessel.recover()
            _emit(ctx, "call", name="recover", ok=1)
            return "recovered"
    except Exception:
        log.debug("recover failed", exc_info=True)
    _emit(ctx, "call", name="recover", ok=0)
    return "recover"


def science(ctx: Ctx) -> str:
    from science import start_experiments

    vessel = _vessel(ctx)
    if vessel is None:
        _emit(ctx, "call", name="science", ids=[])
        return "science"
    ids = start_experiments(vessel, names=ctx.science_ids)
    _emit(ctx, "science", ids=list(ids))
    _emit(ctx, "call", name="science")
    return "science:" + ",".join(ids) if ids else "science"


def _is_tx_event(text: str) -> bool:
    low = (text or "").strip().lower()
    if not low or any(w in low for w in _TX_NEVER):
        return False
    return "transmit" in low


def _fire_tx_event(module: Any) -> bool:
    """Kerbalism Experiment Transmit event. Not stock Experiment.transmit()."""
    try:
        event_list = list(getattr(module, "event_list", None) or [])
    except Exception:
        event_list = []
    for ev in event_list:
        gui = str(getattr(ev, "gui_name", "") or "")
        ident = str(getattr(ev, "name", "") or "")
        if not (_is_tx_event(gui) or _is_tx_event(ident)):
            continue
        if getattr(ev, "active", True) is False:
            continue
        trig = getattr(ev, "trigger", None)
        if callable(trig):
            try:
                trig()
                return True
            except Exception:
                continue
    try:
        names = list(getattr(module, "events", None) or [])
    except Exception:
        names = []
    for ev_name in names:
        if not _is_tx_event(str(ev_name)):
            continue
        trigger = getattr(module, "trigger_event", None)
        if callable(trigger):
            try:
                trigger(ev_name)
                return True
            except Exception:
                pass
        by_id = getattr(module, "trigger_event_by_id", None)
        if callable(by_id):
            try:
                by_id(ev_name)
                return True
            except Exception:
                continue
    return False


def transmit(ctx: Ctx) -> str:
    """Flag Kerbalism files via Experiment TX events. Never stock dump/reset."""
    from science import iter_science_modules

    vessel = _vessel(ctx)
    if vessel is None:
        _emit(ctx, "call", name="transmit", ids=[])
        return "transmit"
    want = None
    if ctx.science_ids is not None:
        want = {str(n).strip() for n in ctx.science_ids if str(n).strip()}
    done: list[str] = []
    for _part, module, eid in iter_science_modules(vessel):
        label = str(eid or "").strip() or str(getattr(module, "name", "") or "Experiment")
        if want is not None and label not in want:
            continue
        if _fire_tx_event(module):
            done.append(label)
    _emit(ctx, "transmit", ids=list(done))
    _emit(ctx, "call", name="transmit")
    return "transmit:" + ",".join(done) if done else "transmit"


def abort_pad(ctx: Ctx) -> str:
    cut(ctx)
    result = recover(ctx)
    _emit(ctx, "call", name="abort_pad")
    return "abort_pad" if result != "recovered" else "abort_pad:recovered"


CALLABLES: dict[str, Callable[[Ctx], str]] = {
    "hold": hold,
    "cut": cut,
    "no_warp": no_warp,
    "stage": stage,
    "recover": recover,
    "science": science,
    "transmit": transmit,
    "abort_pad": abort_pad,
}


def resolve(verb: str) -> str | None:
    key = verb.lower().strip().replace("-", "_")
    if key in CALLABLES:
        return key
    mapped = ALIASES.get(verb.lower().strip())
    if mapped in CALLABLES:
        return mapped
    return None


def call(verb: str, ctx: Ctx) -> str:
    name = resolve(verb)
    if name is None:
        raise KeyError(f"unknown emergency {verb}")
    return CALLABLES[name](ctx)
