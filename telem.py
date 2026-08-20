"""Structured flight telemetry. Not FlightWatch.

Streams use kRPC 0.6 ``add_stream(getattr, obj, name)``. Gates use the
live body's ``atmosphere_depth``. Each :meth:`Telem.read` writes a
``kind=state`` row to the seated run jsonl (alt, apo, peri, situation,
MET, EC, fuel). :class:`EventLog` stays in-memory unless given a path.
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

log = logging.getLogger("kspstuff")

_STREAM_PROPS: tuple[tuple[str, str], ...] = (
    ("flight", "mean_altitude"),
    ("flight", "dynamic_pressure"),
    ("flight", "surface_altitude"),
    ("orbit", "apoapsis_altitude"),
    ("orbit", "periapsis_altitude"),
    ("orbit", "eccentricity"),
    ("orbit", "semi_major_axis"),
    ("orbit", "time_to_periapsis"),
    ("orbit", "time_to_apoapsis"),
)

_PAD = frozenset({"pre_launch", "prelaunch", "landed", "splashed"})
_FUELS = (
    "ElectricCharge",
    "SolidFuel",
    "LiquidFuel",
    "Oxidizer",
    "Kerosene",
    "LqdOxygen",
    "LqdHydrogen",
    "MonoPropellant",
    "Hydrazine",
    "Food",
    "Oxygen",
    "Water",
)


class MissionAbort(RuntimeError):
    """Gate, wreck, empty tanks with leftover speed, or honest pad abort."""


def _enum_name(value: Any, default: str = "?") -> str:
    if value is None:
        return default
    name = getattr(value, "name", None)
    if isinstance(name, str):
        return name.lower().replace("-", "_")
    text = str(value)
    return text.rsplit(".", 1)[-1].lower().replace("-", "_") if text else default


def _finite(value: Any, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


@dataclass(slots=True)
class Snapshot:
    scene: str = "?"
    vessel: str | None = None
    body: str = "?"
    situation: str = "?"
    alt: float = float("nan")
    peri: float = float("nan")
    apo: float = float("nan")
    ecc: float = float("nan")
    q: float = float("nan")
    atm_depth: float = float("nan")
    in_atmo: bool = False
    wreck: bool = False
    throttle: float = float("nan")
    thrust: float = float("nan")
    speed: float = float("nan")
    met: float = float("nan")
    ec: float | None = None
    fuel: float | None = None
    lf: float | None = None
    broken: str | None = None
    resources: dict[str, float] = field(default_factory=dict)
    flags: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["in_atmo"] = int(self.in_atmo)
        data["wreck"] = int(self.wreck)
        data["flags"] = list(self.flags)
        return data


def format_snapshot(snap: Snapshot) -> str:
    if snap.vessel is None:
        return f"status vessel=none scene={snap.scene}"
    ec = "?" if snap.ec is None else f"{snap.ec:g}"
    fuel = "?" if snap.fuel is None else f"{snap.fuel:g}"
    return (
        f"status body={snap.body} sit={snap.situation} "
        f"alt={snap.alt:.1f} peri={snap.peri:.1f} apo={snap.apo:.1f} "
        f"atm={snap.atm_depth:.1f} in_atmo={int(snap.in_atmo)} "
        f"ec={ec} fuel={fuel} wreck={int(snap.wreck)} "
        f"vessel={snap.vessel}"
    )


def in_atmosphere(alt: float, body: Any) -> bool:
    """True when altitude is below this body's atmosphere_depth."""
    try:
        if not bool(getattr(body, "has_atmosphere", False)):
            return False
        depth = float(body.atmosphere_depth)
    except (TypeError, ValueError, AttributeError):
        return False
    if not math.isfinite(alt) or not math.isfinite(depth):
        return False
    return alt < depth


def resource_amount(vessel: Any, name: str) -> float | None:
    try:
        resources = vessel.resources
    except Exception:
        return None
    try:
        return float(resources.amount(name))
    except Exception:
        pass
    try:
        item = resources.named(name)
        return float(item.amount)
    except Exception:
        return None


def _module_flag(module: Any, *keys: str) -> str | None:
    fields = getattr(module, "fields", None)
    for key in keys:
        val = None
        if isinstance(fields, dict) and key in fields:
            val = fields[key]
        else:
            getter = getattr(module, "get_field", None)
            if callable(getter):
                try:
                    val = getter(key)
                except Exception:
                    val = None
            if val is None:
                val = getattr(module, key, None)
        if val in (True, 1, "1", "True", "true", "yes"):
            return key
    return None


def reliability_broken(vessel: Any) -> str | None:
    try:
        parts = list(vessel.parts.all)
    except Exception:
        return None
    for part in parts:
        try:
            modules = list(part.modules)
        except Exception:
            continue
        pname = getattr(part, "name", "?")
        for module in modules:
            hit = _module_flag(
                module, "broken", "isBroken", "malfunction", "failed"
            )
            if hit:
                mname = getattr(module, "name", "?")
                return f"{pname}:{mname}:{hit}"
    return None


def gates(snap: Snapshot) -> list[str]:
    """Body-relative gates. No Kerbin DIP/ESC strings."""
    out: list[str] = []
    if snap.wreck:
        out.append("wreck")
    if snap.broken:
        out.append(f"reliability {snap.broken}")
    sit = snap.situation
    if snap.vessel is not None and snap.ec is not None and snap.ec <= 0:
        out.append("ec=0")
    if (
        snap.fuel is not None
        and snap.fuel <= 0
        and math.isfinite(snap.speed)
        and snap.speed > 5.0
        and sit not in _PAD
    ):
        out.append("empty tanks")
    if (
        snap.in_atmo
        and sit not in _PAD
        and math.isfinite(snap.peri)
        and math.isfinite(snap.atm_depth)
        and snap.peri < snap.atm_depth
        and math.isfinite(snap.apo)
        and snap.apo > snap.atm_depth
    ):
        out.append(
            f"atmosphere alt={snap.alt:.0f} peri={snap.peri:.0f} "
            f"atm={snap.atm_depth:.0f}"
        )
    return out


class EventLog:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.events: list[dict[str, Any]] = []

    def emit(self, kind: str, **fields: Any) -> dict[str, Any]:
        rec: dict[str, Any] = {"event": kind, **fields}
        self.events.append(rec)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, default=str) + "\n")
        return rec


class Telem:
    """Subscribe once; :meth:`read` each loop. No 1 Hz prose controller."""

    def __init__(
        self,
        session: Any,
        *,
        events: EventLog | None = None,
        scene: str = "?",
    ) -> None:
        self.session = session
        self.events = events if events is not None else EventLog()
        self.scene = scene
        self._flight: Any = None
        self._orbit: Any = None
        self._body: Any = None
        self._streams: dict[str, Any] = {}
        self._vessel: Any = None

    def close(self) -> None:
        for stream in self._streams.values():
            try:
                stream.remove()
            except Exception:
                pass
        self._streams.clear()
        self._flight = None
        self._orbit = None
        self._body = None
        self._vessel = None

    def __enter__(self) -> Telem:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _bind(self, vessel: Any) -> None:
        if vessel is self._vessel and self._streams:
            return
        self.close()
        self._vessel = vessel
        if vessel is None:
            return
        self._flight = vessel.flight()
        self._orbit = vessel.orbit
        self._body = self._orbit.body
        add_stream: Callable[..., Any] = self.session.add_stream
        for group, prop in _STREAM_PROPS:
            obj = self._flight if group == "flight" else self._orbit
            self._streams[f"{group}.{prop}"] = add_stream(getattr, obj, prop)

    def _stream(self, key: str, fallback: Any = float("nan")) -> float:
        stream = self._streams.get(key)
        if stream is None:
            return _finite(fallback)
        try:
            return _finite(stream())
        except Exception:
            return _finite(fallback)

    def read(self) -> Snapshot:
        try:
            vessel = self.session.active_vessel
        except Exception:
            vessel = None
        if vessel is None:
            snap = Snapshot(scene=self.scene, vessel=None)
            self.events.emit("snapshot", **snap.as_dict())
            _record_run(self.session, snap)
            return snap
        self._bind(vessel)
        body = self._body
        alt = self._stream("flight.mean_altitude")
        peri = self._stream("orbit.periapsis_altitude")
        apo = self._stream("orbit.apoapsis_altitude")
        ecc = self._stream("orbit.eccentricity")
        q = self._stream("flight.dynamic_pressure")
        atm = _finite(getattr(body, "atmosphere_depth", float("nan")))
        sit = _enum_name(getattr(vessel, "situation", None))
        wreck = sit in {"wrecked", "wreck"} or (
            math.isfinite(alt) and alt < -10.0
        )
        resources: dict[str, float] = {}
        for name in _FUELS:
            amount = resource_amount(vessel, name)
            if amount is not None:
                resources[name] = amount
        ec = resources.get("ElectricCharge")
        fuel = None
        for key in (
            "SolidFuel",
            "Kerosene",
            "LiquidFuel",
            "LqdHydrogen",
            "Hydrazine",
        ):
            if key in resources:
                fuel = (fuel or 0.0) + resources[key]
        throttle = _finite(getattr(getattr(vessel, "control", None), "throttle", float("nan")))
        thrust = float("nan")
        try:
            thrust = float(vessel.thrust)
        except Exception:
            pass
        speed = float("nan")
        try:
            speed = float(vessel.flight().speed)
        except Exception:
            pass
        met = _finite(getattr(vessel, "met", float("nan")))
        broken = reliability_broken(vessel)
        snap = Snapshot(
            scene=self.scene,
            vessel=str(getattr(vessel, "name", "vessel")),
            body=str(getattr(body, "name", "?")),
            situation=sit,
            alt=alt,
            peri=peri,
            apo=apo,
            ecc=ecc,
            q=q,
            atm_depth=atm,
            in_atmo=in_atmosphere(alt, body),
            wreck=wreck,
            throttle=throttle,
            thrust=thrust,
            speed=speed,
            met=met,
            ec=ec,
            fuel=fuel,
            lf=fuel,
            broken=broken,
            resources=resources,
        )
        reasons = gates(snap)
        snap.flags = tuple(reasons)
        self.events.emit("snapshot", **snap.as_dict())
        for reason in reasons:
            self.events.emit("gate", reason=reason)
        if snap.ec is not None and snap.ec <= 0:
            self.events.emit("resource_low", resource="ElectricCharge", amount=snap.ec)
        _record_run(self.session, snap)
        return snap


def _record_run(session: Any, snap: Snapshot) -> None:
    """Write this pulse to the seated jsonl. No-op if helm has not started."""
    try:
        from flightlog import record
    except Exception:
        return
    ut = None
    try:
        ut = float(getattr(getattr(session, "space_center", None), "ut"))
    except (TypeError, ValueError, AttributeError):
        ut = None
    tag = snap.scene if snap.scene and snap.scene != "?" else ""
    try:
        record(snap, tag=tag, ut=ut, force=True)
    except Exception:
        log.debug("flightlog record failed", exc_info=True)


def read_snapshot(session: Any, *, scene: str = "?", events: EventLog | None = None) -> Snapshot:
    with Telem(session, events=events, scene=scene) as telem:
        return telem.read()
