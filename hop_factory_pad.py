"""RF pad sit: throttle 1 on the engine, then stage, keep that start.

Pad 1 g still lights. Independent throttle is the ignition meet —
enable once. Re-enabling zeros the setpoint; stage then spends the
only ignition at 0. Live is the independent setpoint (PAW Current
Throttle / independentThrottlePercentage), not kRPC Engine.throttle
GET (currentThrottle is 0 until lit — wait-for-GET never stages)
and not independent True with setpoint 0. After thrusting,
MainThrottle 1 is the burn. Commanded throttle 0 after loft is MECO.
Throttle 0 then 1 is a restart. Forest / Grasslands: same.
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


def _parse_throttle(raw: object) -> float:
    """0–1 throttle from a float, percent string, or 0–100 field."""
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


def _engine_modules(engine: object) -> list[object]:
    """Part modules on this engine. Never ``Module.fields`` (duplicate PAW)."""
    try:
        part = getattr(engine, "part", None)
    except Exception:
        part = None
    if part is None:
        return []
    try:
        return list(getattr(part, "modules", None) or [])
    except Exception:
        return []


def _engine_setpoint(engine: object) -> float:
    """Independent command. Not kRPC Engine.throttle GET (currentThrottle).

    kRPC 0.6 GET is actual output: 0 until the engine is lit. The meet
    is independentThrottlePercentage / PAW Current Throttle. Forest /
    Grasslands: same.
    """
    for mod in _engine_modules(engine):
        getter_id = getattr(mod, "get_field_by_id", None)
        if callable(getter_id):
            try:
                value = _parse_throttle(getter_id("independentThrottlePercentage"))
            except Exception:
                value = float("nan")
            if math.isfinite(value):
                return value
        try:
            flist = list(getattr(mod, "field_list", None) or [])
        except Exception:
            flist = []
        for field in flist:
            try:
                fname = str(getattr(field, "name", "") or "")
            except Exception:
                continue
            if fname not in (
                "independentThrottlePercentage",
                "Current Throttle",
            ):
                continue
            try:
                value = _parse_throttle(getattr(field, "value", None))
            except Exception:
                value = float("nan")
            if math.isfinite(value):
                return value
    return float("nan")


def _write_engine_setpoint(engine: object) -> None:
    """Write independentThrottlePercentage 100 after enable. Not a re-enable."""
    for mod in _engine_modules(engine):
        setter = getattr(mod, "set_field_float_by_id", None)
        if callable(setter):
            try:
                setter("independentThrottlePercentage", 100.0)
            except Exception:
                pass


def _engine_throttle(engine: object) -> float:
    """Ignition command on this engine. kRPC control.throttle is not this.

    Independent on: PAW Current Throttle / independentThrottlePercentage.
    kRPC Engine.throttle GET is currentThrottle — 0 until lit. Forest /
    Grasslands: same.
    """
    independent = False
    try:
        independent = bool(getattr(engine, "independent_throttle", False))
    except Exception:
        independent = False
    if independent:
        commanded = _engine_setpoint(engine)
        if math.isfinite(commanded):
            return commanded
    try:
        raw = getattr(engine, "throttle", None)
    except Exception:
        raw = None
    return _parse_throttle(raw)


def _pad_engine_live(vessel: object) -> bool | None:
    """Ignition command already on a live engine. None if no engine.

    kRPC control.throttle is not the burn. Independent True with
    setpoint 0 is not live — re-enable zeros the meet. kRPC
    Engine.throttle GET is not live either: currentThrottle stays 0
    until the engine is lit. Forest / Grasslands: same.
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
        _write_engine_setpoint(eng)


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

    RF spends the only ignition when stage fires. Live is the
    independent setpoint, not independent True, not kRPC throttle,
    and not Engine.throttle GET (currentThrottle is 0 until lit).
    Re-apply on the stage pulse zeros the setpoint this tick.
    Throttle 0 then 1 is a restart. Pad 1 g still lights when the
    command is 1 at ignition. hop light is not the burn. Forest /
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

    hop light is not the burn. Re-enabling independent zeros the
    setpoint — wait-for-GET then never stages. Pad sit throttle 0
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
