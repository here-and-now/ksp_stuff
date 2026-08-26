"""RF live throttle is independent, not UI MainThrottle.

kRPC ``control.throttle`` moves the MainThrottle bar. RealFuels burns
on ``independentThrottlePercentage`` / PAW Current Throttle. Enable
independent once — re-enable zeros the setpoint and a 1-start stage
fires at 0. ``Engine.throttle`` GET is ``currentThrottle`` (0 until
lit) — not the command. UI echo is optional radio; it is not the
burn. Throttle 0 then 1 is a restart. Forest / Grasslands: same.

Lars pad-RF stays ``hop_factory_pad``. This catalog is the sit
ascent / hop_factory may call. Tests lock these blocks.
"""

from __future__ import annotations

import math

LIVE_MIN = 0.05
_SETPOINT_KEYS = ("independentThrottlePercentage", "Current Throttle")
_IGNITION_KEYS = ("ignitions", "ignitionsRemaining", "Ignitions Remaining")


def engines(vessel: object) -> list[object]:
    """Live engines on this hang. kRPC ``parts.engines``."""
    try:
        return list(getattr(getattr(vessel, "parts", None), "engines", None) or [])
    except Exception:
        return []


def parse_throttle(raw: object) -> float:
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


def module_field(module: object, *keys: str) -> object | None:
    """One PAW / KSPField value. Never ``Module.fields`` (duplicate gui)."""
    if not keys:
        return None
    want = {str(k).lower() for k in keys}
    getter_id = getattr(module, "get_field_by_id", None)
    if callable(getter_id):
        for key in keys:
            try:
                val = getter_id(key)
            except Exception:
                continue
            if val is None or val == "":
                continue
            return val
    try:
        flist = list(getattr(module, "field_list", None) or [])
    except Exception:
        flist = []
    for field in flist:
        try:
            fname = str(getattr(field, "name", "") or "")
        except Exception:
            continue
        if fname.lower() not in want:
            continue
        try:
            val = getattr(field, "value", None)
        except Exception:
            continue
        if val is None or val == "":
            continue
        return val
    try:
        by_id = getattr(module, "fields_by_id", None)
    except Exception:
        by_id = None
    if isinstance(by_id, dict):
        for key in keys:
            if key in by_id and by_id[key] not in (None, ""):
                return by_id[key]
    return None


def _parse_count(raw: object) -> float:
    """Ignitions remaining. 0 is spent. Unlimited is not a number."""
    if isinstance(raw, bool) or raw is None:
        return float("nan")
    text = str(raw).strip().replace("%", "")
    if not text:
        return float("nan")
    head = text.split()[0]
    if head.lower() in {"unlimited", "n/a", "none", "?"}:
        return float("nan")
    try:
        value = float(head)
    except (TypeError, ValueError):
        return float("nan")
    if not math.isfinite(value):
        return float("nan")
    return value


def to_percent(value: float) -> float:
    """PAW independentThrottlePercentage is 0–100."""
    frac = parse_throttle(value)
    if not math.isfinite(frac):
        return float("nan")
    return frac * 100.0


def write_setpoint(engine: object, value: float = 1.0) -> None:
    """Write independentThrottlePercentage. 1.0 is the ignition meet."""
    percent = to_percent(value)
    if not math.isfinite(percent):
        return
    for mod in _engine_modules(engine):
        setter_id = getattr(mod, "set_field_float_by_id", None)
        if callable(setter_id):
            for key in _SETPOINT_KEYS:
                try:
                    setter_id(key, percent)
                except Exception:
                    pass
        setter = getattr(mod, "set_field_float", None)
        if callable(setter):
            for key in _SETPOINT_KEYS:
                try:
                    setter(key, percent)
                except Exception:
                    pass


def setpoint(engine: object) -> float:
    """Independent command 0–1. Not kRPC Engine.throttle GET."""
    for mod in _engine_modules(engine):
        value = parse_throttle(module_field(mod, *_SETPOINT_KEYS))
        if math.isfinite(value):
            return value
    independent = False
    try:
        independent = bool(getattr(engine, "independent_throttle", False))
    except Exception:
        independent = False
    if independent:
        try:
            raw = getattr(engine, "throttle", None)
        except Exception:
            raw = None
        value = parse_throttle(raw)
        if math.isfinite(value):
            return value
    return float("nan")


def actual(engine: object) -> float:
    """kRPC Engine.throttle GET / currentThrottle. 0 until lit."""
    found = float("nan")
    try:
        raw = getattr(engine, "throttle", None)
    except Exception:
        raw = None
    value = parse_throttle(raw)
    if math.isfinite(value):
        found = value
    for mod in _engine_modules(engine):
        value = parse_throttle(module_field(mod, "currentThrottle"))
        if math.isfinite(value) and (not math.isfinite(found) or value > found):
            found = value
    return found


def ignitions(engine: object) -> float:
    """RF ignitions remaining. Cfg is not live remaining."""
    for mod in _engine_modules(engine):
        value = _parse_count(module_field(mod, *_IGNITION_KEYS))
        if math.isfinite(value):
            return value
    return float("nan")


def enable_once(engine: object) -> None:
    """Independent on once. Re-enable zeros Current Throttle."""
    already = False
    try:
        already = bool(getattr(engine, "independent_throttle", False))
    except Exception:
        already = False
    if already:
        return
    try:
        engine.independent_throttle = True
    except Exception:
        pass


def live(vessel: object) -> float:
    """Commanded independent 0–1. UI MainThrottle GET is not this."""
    found = float("nan")
    for eng in engines(vessel):
        value = setpoint(eng)
        if math.isfinite(value) and (not math.isfinite(found) or value > found):
            found = value
    return found


def rf_sit(vessel: object) -> bool:
    """This hang is RF: ModuleEnginesRF or finite ignitions remaining."""
    for eng in engines(vessel):
        ign = ignitions(eng)
        if math.isfinite(ign):
            return True
        for mod in _engine_modules(eng):
            try:
                name = str(getattr(mod, "name", "") or "")
            except Exception:
                name = ""
            if "moduleenginesrf" in name.lower():
                return True
    return False


def apply(vessel: object, value: float = 1.0) -> None:
    """Write live RF throttle. Independent setpoint, not UI MainThrottle.

    Enable independent once. UI MainThrottle may echo for radio; a
    no-op bar still lights when the setpoint is 1. Forest /
    Grasslands: same.
    """
    frac = parse_throttle(value)
    if not math.isfinite(frac):
        frac = 1.0
    frac = min(max(frac, 0.0), 1.0)
    try:
        control = getattr(vessel, "control", None)
        if control is not None:
            try:
                control.sas = True
            except Exception:
                pass
            try:
                control.throttle = frac
            except Exception:
                pass
    except Exception:
        pass
    for eng in engines(vessel):
        enable_once(eng)
        try:
            eng.throttle = frac
        except Exception:
            pass
        write_setpoint(eng, frac)
        try:
            eng.active = True
        except Exception:
            pass


def cut(vessel: object, *, abort: bool = False) -> None:
    """MECO: setpoint 0, then independent off. UI 0 is not enough.

    Independent still burns when MainThrottle GET is 0. Dropping
    independent then re-enabling is a restart. ``abort`` also sets
    engine active False. Do not raise ignitions. Forest /
    Grasslands: same.
    """
    try:
        control = getattr(vessel, "control", None)
        if control is not None:
            control.throttle = 0.0
    except Exception:
        pass
    for eng in engines(vessel):
        try:
            eng.throttle = 0.0
        except Exception:
            pass
        write_setpoint(eng, 0.0)
        try:
            eng.independent_throttle = False
        except Exception:
            pass
        if abort:
            try:
                eng.active = False
            except Exception:
                pass


def thrusting(vessel: object, snap: object | None = None) -> bool:
    """Engine is producing thrust. Independent command is not this."""
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
    for eng in engines(vessel):
        try:
            value = float(getattr(eng, "thrust", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value) and value > 1.0:
            return True
        got = actual(eng)
        if math.isfinite(got) and got > LIVE_MIN:
            return True
    return False


def burning(vessel: object, snap: object | None = None, *, lofted: bool = False) -> bool:
    """Live setpoint or thrust with fuel. UI MainThrottle GET is not cutoff.

    A 0-tick on the bar after light is not MECO — independent still
    burns. Real burnout is fuel gone, or live 0 after a real loft.
    """
    fuel = float("nan")
    if snap is not None:
        try:
            fuel = float(getattr(snap, "fuel", float("nan")))
        except (TypeError, ValueError):
            fuel = float("nan")
    if math.isfinite(fuel) and fuel <= 0.0:
        return False
    commanded = live(vessel)
    if math.isfinite(commanded) and commanded > LIVE_MIN:
        return True
    if thrusting(vessel, snap):
        return True
    return not lofted
