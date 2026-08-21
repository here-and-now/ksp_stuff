"""Structured flight telemetry. Not FlightWatch.

Streams use kRPC 0.6 ``add_stream(getattr, obj, name)``. Gates use the
live body's ``atmosphere_depth``. Each :meth:`Telem.read` writes a
``kind=state`` row to the seated run jsonl (alt, apo, peri, situation,
MET, EC, fuel, surface horiz, heading, pitch, AoA, biome, v_vert).
:class:`EventLog` stays in-memory unless given a path.
``vessel.flight()`` with no frame is the vessel origin — ``speed`` is
always ~0. Surface kinematics use the body's ``reference_frame``.

Cadence is adaptive: cruise ~5 Hz, ~20 Hz near the surface so a hard
splash is a tape, not three rows 2 s apart. Landing class is derived
from the flying→splashed/landed transition and linked onto the fly
ticket (skim: one line; jsonl stays ``--deep``).
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
_DOWN = frozenset({"landed", "splashed"})
_AIR = frozenset({"flying", "sub_orbital", "suborbital", "escaping", "orbiting"})
CRUISE_HZ = 5.0
NEAR_HZ = 20.0
NEAR_ALT_M = 2000.0
TTI_BURST_S = 8.0
IMPACT_SOFT_MS = 15.0
IMPACT_FIRM_MS = 50.0
IMPACT_HARD_MS = 100.0
G0 = 9.80665
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
    horiz: float = float("nan")
    v_vert: float = float("nan")
    g: float = float("nan")
    landing: str = ""
    heading: float = float("nan")
    pitch: float = float("nan")
    aoa: float = float("nan")
    biome: str = ""
    met: float = float("nan")
    ec: float | None = None
    fuel: float | None = None
    lf: float | None = None
    broken: str | None = None
    stage: int | None = None
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
        f"horiz={snap.horiz:.0f} vz={snap.v_vert:.0f} "
        f"hdg={snap.heading:.0f} "
        f"pitch={snap.pitch:.0f} aoa={snap.aoa:.0f} biome={snap.biome or '?'} "
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
            pname = str(getattr(part, "name", "?") or "?")
        except Exception:
            continue
        try:
            modules = list(part.modules)
        except Exception:
            continue
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


def impact_speed(
    *,
    v_vert: float = float("nan"),
    speed: float = float("nan"),
    horiz: float = float("nan"),
) -> float:
    """Signed-down speed at contact. Prefer |v_vert|, else speed, else horiz."""
    if math.isfinite(v_vert):
        return abs(float(v_vert))
    if math.isfinite(speed) and speed > 0.05:
        if math.isfinite(horiz) and abs(horiz) + 0.05 < speed:
            down = speed * speed - horiz * horiz
            if down > 0:
                return math.sqrt(down)
        return abs(float(speed))
    if math.isfinite(horiz):
        return abs(float(horiz))
    return float("nan")


def classify_impact(speed_ms: float) -> str:
    """soft <15, firm <50, hard <100, catastrophic ≥100 m/s. Empty if unknown."""
    if not math.isfinite(speed_ms) or speed_ms < 0:
        return ""
    if speed_ms >= IMPACT_HARD_MS:
        return "catastrophic"
    if speed_ms >= IMPACT_FIRM_MS:
        return "hard"
    if speed_ms >= IMPACT_SOFT_MS:
        return "firm"
    return "soft"


def pulse_s(snap: Snapshot) -> float:
    """Hop loop nap. Cruise 5 Hz; 20 Hz below 2 km or time-to-impact < 8 s."""
    sit = (snap.situation or "").lower()
    if sit in _PAD and sit not in {"splashed", "landed"}:
        return 1.0 / CRUISE_HZ
    alt = snap.alt
    vz = snap.v_vert
    if sit in _DOWN:
        return 1.0 / CRUISE_HZ
    if math.isfinite(alt) and alt < NEAR_ALT_M:
        return 1.0 / NEAR_HZ
    if math.isfinite(vz) and vz < 0 and math.isfinite(alt) and alt > 0:
        tti = alt / max(0.1, -vz)
        if tti < TTI_BURST_S:
            return 1.0 / NEAR_HZ
    return 1.0 / CRUISE_HZ


def format_landing(row: dict[str, Any]) -> str:
    landing = row.get("landing") or "unknown"
    impact = row.get("impact_ms")
    try:
        imp = f"{float(impact):.0f}"
    except (TypeError, ValueError):
        imp = "?"
    hdg = row.get("heading")
    try:
        hdg_s = f"{float(hdg):.0f}"
    except (TypeError, ValueError):
        hdg_s = "?"
    sit = row.get("sit") or row.get("situation") or "?"
    return f"landing: {landing} impact={imp} m/s heading={hdg_s} sit={sit}"


def landing_from_jsonl(path: str | Path) -> dict[str, Any]:
    """Disk, no kRPC. First flying→splashed/landed transition on a run tape."""
    src = Path(path)
    rows: list[dict[str, Any]] = []
    if src.is_file():
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    states = [r for r in rows if r.get("kind") == "state"]
    dts = []
    prev_t = None
    for r in states:
        t = r.get("t")
        try:
            tf = float(t)
        except (TypeError, ValueError):
            continue
        if prev_t is not None and tf > prev_t:
            dts.append(tf - prev_t)
        prev_t = tf
    dts.sort()
    hz_median = None
    if dts:
        med = dts[len(dts) // 2]
        hz_median = round(1.0 / med, 2) if med > 0 else None
    last_air: dict[str, Any] | None = None
    landing_row: dict[str, Any] | None = None
    for r in rows:
        if r.get("kind") == "landing":
            landing_row = r
            break
    down: dict[str, Any] | None = None
    for r in states:
        sit = str(r.get("situation") or "").lower()
        if sit in _AIR:
            last_air = r
        elif sit in _DOWN and down is None:
            down = r
            break
    air = last_air or {}
    hit = down or {}
    v_vert = _finite(air.get("v_vert"), float("nan"))
    speed = _finite(air.get("speed"), float("nan"))
    horiz = _finite(air.get("horiz"), float("nan"))
    impact = impact_speed(v_vert=v_vert, speed=speed, horiz=horiz)
    landing = ""
    if landing_row and landing_row.get("landing"):
        landing = str(landing_row.get("landing") or "")
        impact = _finite(landing_row.get("impact_ms"), impact)
    if not landing:
        landing = classify_impact(impact) or "unknown"
    met_air = _finite(air.get("met"), float("nan"))
    met_down = _finite(hit.get("met"), float("nan"))
    dt_s = None
    if math.isfinite(met_air) and math.isfinite(met_down):
        dt_s = round(met_down - met_air, 3)
    out: dict[str, Any] = {
        "run": src.name,
        "path": str(src),
        "landing": landing,
        "impact_ms": None if not math.isfinite(impact) else round(float(impact), 3),
        "v_vert": None if not math.isfinite(v_vert) else round(float(v_vert), 3),
        "speed": None if not math.isfinite(speed) else round(float(speed), 3),
        "horiz": None if not math.isfinite(horiz) else round(float(air.get("horiz") or horiz), 3),
        "heading": None
        if not math.isfinite(_finite(air.get("heading")))
        else round(float(air.get("heading")), 3),
        "alt_before": None
        if not math.isfinite(_finite(air.get("alt")))
        else round(float(air.get("alt")), 3),
        "sit": hit.get("situation") or (landing_row or {}).get("sit") or "",
        "biome": hit.get("biome") or air.get("biome") or "",
        "met": None if not math.isfinite(met_down) else round(float(met_down), 3),
        "dt_s": dt_s,
        "samples": len(states),
        "hz_median": hz_median,
    }
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
    """Subscribe once; :meth:`read` each loop. Cadence is :func:`pulse_s`."""

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
        self._kin: Any = None
        self._orbit: Any = None
        self._body: Any = None
        self._streams: dict[str, Any] = {}
        self._vessel: Any = None
        self._met_was: float | None = None
        self._prev_v_vert: float | None = None
        self._prev_met_g: float | None = None
        self._prev_sit: str = ""
        self._prev_speed: float | None = None
        self._prev_horiz: float | None = None
        self._prev_alt: float | None = None
        self._prev_heading: float | None = None
        self._landed: bool = False

    def close(self) -> None:
        for stream in self._streams.values():
            try:
                stream.remove()
            except Exception:
                pass
        self._streams.clear()
        self._flight = None
        self._kin = None
        self._orbit = None
        self._body = None
        self._vessel = None
        self._met_was = None
        self._prev_v_vert = None
        self._prev_met_g = None

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
        self._kin = self._flight
        try:
            rf = getattr(self._body, "reference_frame", None)
            if rf is not None:
                self._kin = vessel.flight(rf)
        except TypeError:
            self._kin = self._flight
        except Exception:
            self._kin = self._flight
        add_stream: Callable[..., Any] = self.session.add_stream
        for group, prop in _STREAM_PROPS:
            obj = self._flight if group == "flight" else self._orbit
            self._streams[f"{group}.{prop}"] = add_stream(getattr, obj, prop)
        for prop in ("speed", "horizontal_speed", "heading", "vertical_speed"):
            self._streams[f"kin.{prop}"] = add_stream(getattr, self._kin, prop)
        for prop in ("pitch", "angle_of_attack"):
            self._streams[f"att.{prop}"] = add_stream(getattr, self._flight, prop)

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
            _maybe_shot(snap)
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
        speed = self._stream("kin.speed")
        horiz = self._stream("kin.horizontal_speed")
        v_vert = self._stream("kin.vertical_speed")
        heading = self._stream("kin.heading")
        pitch = self._stream("att.pitch")
        aoa = self._stream("att.angle_of_attack")
        biome = str(getattr(vessel, "biome", "") or "")
        if not math.isfinite(speed) or speed <= 0.05:
            if math.isfinite(horiz) and abs(horiz) > 0.05:
                speed = abs(horiz)
        met = _finite(getattr(vessel, "met", float("nan")))
        wreck = sit in {"wrecked", "wreck"} or (
            math.isfinite(alt) and alt < -10.0
        )
        if (
            not wreck
            and sit in {"flying", "sub_orbital", "suborbital"}
            and math.isfinite(q)
            and q <= 0.0
            and math.isfinite(alt)
            and 0.0 <= alt <= 250.0
            and self._met_was is not None
            and math.isfinite(met)
            and abs(met - self._met_was) < 0.2
        ):
            wreck = True
        if math.isfinite(met):
            self._met_was = met
        g_load = float("nan")
        if (
            self._prev_v_vert is not None
            and self._prev_met_g is not None
            and math.isfinite(v_vert)
            and math.isfinite(met)
        ):
            dt_g = met - self._prev_met_g
            if dt_g > 0.02:
                g_load = (v_vert - self._prev_v_vert) / dt_g / G0
        if math.isfinite(v_vert) and math.isfinite(met):
            self._prev_v_vert = v_vert
            self._prev_met_g = met
        landing = ""
        if sit in _DOWN and not self._landed:
            impact = impact_speed(
                v_vert=v_vert,
                speed=self._prev_speed if self._prev_speed is not None else speed,
                horiz=self._prev_horiz if self._prev_horiz is not None else horiz,
            )
            landing = classify_impact(impact)
            self._landed = True
            self.events.emit(
                "landing",
                landing=landing,
                impact_ms=impact,
                v_vert=self._prev_v_vert if self._prev_v_vert is not None else v_vert,
                speed=self._prev_speed if self._prev_speed is not None else speed,
                horiz=self._prev_horiz if self._prev_horiz is not None else horiz,
                alt_before=self._prev_alt,
                heading=self._prev_heading if self._prev_heading is not None else heading,
                sit=sit,
                met=met,
                biome=biome,
            )
        elif sit in _AIR:
            self._landed = False
        broken = reliability_broken(vessel)
        stage = None
        try:
            stage = int(getattr(vessel.control, "current_stage"))
        except (TypeError, ValueError, AttributeError):
            stage = None
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
            horiz=horiz,
            v_vert=v_vert,
            g=g_load,
            landing=landing,
            heading=heading,
            pitch=pitch,
            aoa=aoa,
            biome=biome,
            met=met,
            ec=ec,
            fuel=fuel,
            lf=fuel,
            broken=broken,
            stage=stage,
            resources=resources,
        )
        reasons = gates(snap)
        snap.flags = tuple(reasons)
        self.events.emit("snapshot", **snap.as_dict())
        for reason in reasons:
            self.events.emit("gate", reason=reason)
        if snap.ec is not None and snap.ec <= 0:
            self.events.emit("resource_low", resource="ElectricCharge", amount=snap.ec)
        if sit in _AIR:
            self._prev_sit = sit
            if math.isfinite(speed):
                self._prev_speed = speed
            if math.isfinite(horiz):
                self._prev_horiz = horiz
            if math.isfinite(alt):
                self._prev_alt = alt
            if math.isfinite(heading):
                self._prev_heading = heading
        _record_run(self.session, snap)
        _maybe_shot(snap)
        return snap


def _maybe_shot(snap: Snapshot) -> None:
    try:
        from screenshot import mission_observe

        mission_observe(snap)
    except Exception:
        log.debug("mission shot observe failed", exc_info=True)


def _record_run(session: Any, snap: Snapshot) -> None:
    """Write this pulse to the seated jsonl. No-op if flight has not started."""
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
        if snap.landing:
            from flightlog import event

            event(
                "landing",
                format_landing(
                    {
                        "landing": snap.landing,
                        "impact_ms": impact_speed(
                            v_vert=snap.v_vert, speed=snap.speed, horiz=snap.horiz
                        ),
                        "heading": snap.heading,
                        "sit": snap.situation,
                    }
                ),
                landing=snap.landing,
                v_vert=snap.v_vert,
                speed=snap.speed,
                horiz=snap.horiz,
                heading=snap.heading,
                sit=snap.situation,
                met=snap.met,
                biome=snap.biome,
            )
    except Exception:
        log.debug("flightlog record failed", exc_info=True)


def read_snapshot(session: Any, *, scene: str = "?", events: EventLog | None = None) -> Snapshot:
    with Telem(session, events=events, scene=scene) as telem:
        return telem.read()
