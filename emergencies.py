"""Named emergency callables. Helm and Gene uplink use this table.

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
    "abort_pad": "abort_pad",
    "abort": "abort_pad",
}


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
    sc = getattr(session, "space_center", None)
    if sc is None:
        return
    try:
        sc.rails_warp_factor = 0
    except Exception:
        pass
    try:
        sc.physics_warp_factor = 0
    except Exception:
        pass


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
