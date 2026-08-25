"""RF pad sit: throttle 1 on the engine, then stage, keep that start.

Pad 1 g still lights. Independent throttle is the ignition meet —
enable once. Re-enabling zeros Current Throttle; stage then spends
the only ignition at 0. Live is engine Current Throttle, not
independent True. After thrusting, MainThrottle 1 is the burn.
Commanded throttle 0 after loft is MECO. Throttle 0 then 1 is a
restart. Forest / Grasslands: same.
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
    """Current Throttle already on a live engine. None if no engine.

    kRPC control.throttle is not the burn. Independent True with
    Current Throttle 0 is not live — re-enable zeros the meet.
    Forest / Grasslands: same.
    """
    engines = _pad_engines(vessel)
    if not engines:
        return None
    for eng in engines:
        thr = _engine_throttle(eng)
        if math.isfinite(thr) and thr > 0.05:
            return True
    return False


def _apply_pad_throttle(vessel: object) -> None:
    """Throttle 1 on control and on the engines. Enable independent once."""
    try:
        control = vessel.control
        control.sas = True
        control.throttle = 1.0
    except Exception:
        pass
    for eng in _pad_engines(vessel):
        already = False
        try:
            already = bool(getattr(eng, "independent_throttle", False))
        except Exception:
            already = False
        if not already:
            try:
                eng.independent_throttle = True
            except Exception:
                pass
        try:
            eng.throttle = 1.0
        except Exception:
            pass


def _release_pad_throttle(vessel: object) -> None:
    """MainThrottle drives stack feed. Independent was the ignition meet."""
    for eng in _pad_engines(vessel):
        try:
            eng.independent_throttle = False
        except Exception:
            pass


def _pad_thrusting(vessel: object, snap: object) -> bool:
    """Engine is producing thrust. Independent is not this."""
    for obj in (vessel, snap):
        if obj is None:
            continue
        for key in ("thrust", "available_thrust"):
            try:
                value = float(getattr(obj, key, 0.0) or 0.0)
            except (TypeError, ValueError):
                continue
            if math.isfinite(value) and value > 1.0:
                return True
    for eng in _pad_engines(vessel):
        try:
            value = float(getattr(eng, "thrust", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value) and value > 1.0:
            return True
    return False


def _pad_light(
    vessel: object,
    on_log: Callable[[str], None] | None,
    snap: object | None,
    *,
    deaf: bool,
) -> bool:
    """Pad light: throttle 1 on the engine, then stage. One start.

    RF spends the only ignition when stage fires. Live is engine
    Current Throttle, not independent True and not kRPC throttle.
    Re-apply on the stage pulse zeros Current Throttle this tick.
    Throttle 0 then 1 is a restart. Pad 1 g still lights when the
    engine throttle is 1 at ignition. hop light is not the burn.
    Forest / Grasslands: same.
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
    if not live:
        _apply_pad_throttle(vessel)
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
    """After pad light, keep the start. Independent is enabled once.

    hop light is not the burn. Re-enabling independent zeros Current
    Throttle — wait-for-thrust then never thrusts. Pad sit throttle 0
    is a drop: write 1 without toggling independent. Once thrusting,
    MainThrottle 1 is the burn. Commanded throttle 0 after loft is
    MECO. Pad 1 g still lights. Forest / Grasslands: same.
    """
    if not lit or deaf:
        return False
    down = H._down(snap, flown=left_pad)
    left = left_pad or H._airborne(snap) or down
    try:
        throttle = float(getattr(vessel.control, "throttle", 0.0) or 0.0)
    except Exception:
        throttle = 0.0
    if down or (left and throttle <= 0.05):
        _release_pad_throttle(vessel)
        return False
    if left or _pad_thrusting(vessel, snap):
        _release_pad_throttle(vessel)
        try:
            control = vessel.control
            control.sas = True
            control.throttle = 1.0
        except Exception:
            pass
        return True
    _apply_pad_throttle(vessel)
    return True
