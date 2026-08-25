"""RF pad sit: throttle 1 on the engine, then stage, keep that start.

Pad 1 g still lights. kRPC ``control.throttle`` is not the burn.
Independent throttle is the ignition meet. Airborne is still this start
— dropping independent throttle is a restart. Release only at MECO
(commanded throttle 0 after loft) or down. Forest / Grasslands: same.
"""

from __future__ import annotations

import math
from typing import Callable

import hop as H
from telem import MissionAbort


def _pad_engines(vessel: object) -> list[object]:
    """Live engines on this hang. kRPC ``parts.engines``."""
    try:
        return list(getattr(getattr(vessel, "parts", None), "engines", None) or [])
    except Exception:
        return []


def _engine_throttle(engine: object) -> float:
    """Current Throttle on this engine. kRPC control.throttle is not this."""
    try:
        raw = getattr(engine, "throttle", None)
    except Exception:
        raw = None
    if isinstance(raw, bool) or raw is None:
        return float("nan")
    try:
        value = float(str(raw).strip().replace("%", ""))
    except (TypeError, ValueError):
        return float("nan")
    if not math.isfinite(value):
        return float("nan")
    if value > 1.5:
        value = value / 100.0
    return value


def _pad_engine_live(vessel: object) -> bool | None:
    """Throttle already on a live engine. None if this hang has no engine.

    kRPC control.throttle is not the burn. RF Current Throttle /
    independent throttle is. Forest / Grasslands: same.
    """
    engines = _pad_engines(vessel)
    if not engines:
        return None
    for eng in engines:
        thr = _engine_throttle(eng)
        if math.isfinite(thr) and thr > 0.05:
            return True
        try:
            if bool(getattr(eng, "independent_throttle", False)):
                return True
        except Exception:
            pass
    return False


def _apply_pad_throttle(vessel: object) -> None:
    """Throttle 1 on control and on the engines. Pad 1 g still lights."""
    try:
        control = vessel.control
        control.sas = True
        control.throttle = 1.0
    except Exception:
        pass
    for eng in _pad_engines(vessel):
        try:
            eng.independent_throttle = True
        except Exception:
            pass
        try:
            eng.throttle = 1.0
        except Exception:
            pass


def _release_pad_throttle(vessel: object) -> None:
    """MECO hands the engine to MainThrottle 0. Not an airborne handoff."""
    for eng in _pad_engines(vessel):
        try:
            eng.independent_throttle = False
        except Exception:
            pass


def _pad_light(
    vessel: object,
    on_log: Callable[[str], None] | None,
    snap: object | None,
    *,
    deaf: bool,
) -> bool:
    """Pad light: throttle 1 on the engine, then stage. One start.

    RF spends the only ignition when stage fires. kRPC control.throttle
    is not the burn — ignition meets throttle on the engine. Throttle 0
    then 1 is a restart. Pad 1 g still lights when the engine throttle
    is 1 at ignition. ``_light`` writes throttle then stages in one call
    — too late for the game tick. hop light is not the burn —
    ``_pad_hold`` keeps throttle 1 on the engine until MECO. Forest /
    Grasslands: same.
    """
    if deaf:
        H._light(vessel, on_log, snap)
        return True
    try:
        control = vessel.control
    except Exception as exc:
        raise MissionAbort(f"light failed: {exc}") from exc
    live = _pad_engine_live(vessel)
    if live is None:
        try:
            throttle = float(getattr(control, "throttle", 0.0) or 0.0)
        except (TypeError, ValueError):
            throttle = 0.0
        live = bool(math.isfinite(throttle) and throttle > 0.05)
    _apply_pad_throttle(vessel)
    if not live:
        return False
    try:
        control.sas = True
    except Exception:
        pass
    try:
        control.activate_next_stage()
    except Exception as exc:
        raise MissionAbort(f"light failed: {exc}") from exc
    H._say("hop light", on_log)
    return True


def _pad_hold(
    vessel: object,
    snap: object,
    *,
    lit: bool,
    left_pad: bool,
    deaf: bool,
) -> bool:
    """After pad light, keep throttle 1 on the engine until MECO.

    hop light is not the burn. kRPC control.throttle is not the burn.
    Independent throttle is the start. Airborne is still that start —
    dropping independent throttle is a restart with 0 remaining.
    Commanded throttle 0 after loft is MECO, not a restoke. Pad sit
    throttle 0 is a drop: write 1. Pad 1 g still lights. Forest /
    Grasslands: same.
    """
    if not lit or deaf:
        return False
    left = left_pad or H._airborne(snap) or H._down(snap, flown=left_pad)
    if left:
        try:
            throttle = float(getattr(vessel.control, "throttle", 0.0) or 0.0)
        except Exception:
            throttle = 0.0
        if H._down(snap, flown=left_pad) or throttle <= 0.05:
            _release_pad_throttle(vessel)
            return False
    _apply_pad_throttle(vessel)
    return True
