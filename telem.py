"""Structured flight telemetry. Not FlightWatch.

Streams use kRPC 0.6 ``add_stream(getattr, obj, name)``. Gates use the
live body's ``atmosphere_depth``. Each :meth:`Telem.read` writes a
``kind=state`` row to the seated run jsonl (alt, apo, peri, situation,
MET, EC, fuel, surface horiz, heading, pitch, AoA, biome, lat, lon,
downrange km, v_vert).
:class:`EventLog` stays in-memory unless given a path.
``vessel.flight()`` with no frame is the vessel origin — ``speed`` is
always ~0. Surface kinematics use the body's ``reference_frame``.

Cadence is adaptive: cruise ~5 Hz, ~20 Hz below 8 km, while throttled,
or time-to-impact < 8 s so slew-through-burnout and a hard splash are
tape, not three rows 15 s apart. ``read`` must stay cheap (cache part
walks, never ``parts.all`` on the fast path, never grim inside the
timed pulse) or requested Hz is a lie — 16-47-21Z wrote 0.07 Hz
(26 samples / 380 s) because an expensive sci/broken walk *or* a 10 s
grim tick made every pulse >10 s, which re-armed both. Skip those
walks after an expensive read; skip tape ticks if grim was slow.
Each state row may carry requested ``hz``. Agents query ``tape.Tape``
/ ``python main.py telem``; packet skim is the envelope. Jsonl stays
on disk.
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
    ("flight", "g_force"),
    ("flight", "latitude"),
    ("flight", "longitude"),
    ("orbit", "apoapsis_altitude"),
    ("orbit", "periapsis_altitude"),
    ("orbit", "eccentricity"),
    ("orbit", "semi_major_axis"),
    ("orbit", "time_to_periapsis"),
    ("orbit", "time_to_apoapsis"),
)
_CHUTE_RANK = {
    "cut": 4,
    "deployed": 3,
    "semi_deployed": 2,
    "semideployed": 2,
    "armed": 1,
    "stowed": 0,
}

_PAD = frozenset({"pre_launch", "prelaunch", "landed", "splashed"})
_DOWN = frozenset({"landed", "splashed"})
_AIR = frozenset({"flying", "sub_orbital", "suborbital", "escaping", "orbiting"})
CRUISE_HZ = 5.0
NEAR_HZ = 20.0
NEAR_ALT_M = 8000.0
TTI_BURST_S = 8.0
SLOW_RPC_S = 1.0
CHEAP_READ_S = 0.45
BURN_THROTTLE = 0.05
_FAST_FUELS = (
    "ElectricCharge",
    "SolidFuel",
    "LiquidFuel",
    "Oxidizer",
    "Kerosene",
)
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
    lat: float = float("nan")
    lon: float = float("nan")
    downrange: float = float("nan")
    met: float = float("nan")
    ec: float | None = None
    fuel: float | None = None
    lf: float | None = None
    broken: str | None = None
    stage: int | None = None
    hz: float = float("nan")
    recoverable: bool | None = None
    chute: str = ""
    sci_run: bool | None = None
    sci_rem: float | None = None
    sci_bank: float | None = None
    mass: float = float("nan")
    parts_n: int | None = None
    root: str = ""
    debris_n: int | None = None
    shear: bool = False
    available_thrust: float = float("nan")
    link: bool | None = None
    snr: float = float("nan")
    via: str = ""
    rate_bps: float = float("nan")
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
    link_s = ""
    if snap.link is True:
        link_s = " link=yes"
    elif snap.link is False:
        link_s = " link=no"
    rate_s = ""
    if math.isfinite(getattr(snap, "rate_bps", float("nan"))):
        rate_s = f" rate={snap.rate_bps:g}"
    return (
        f"status body={snap.body} sit={snap.situation} "
        f"alt={snap.alt:.1f} peri={snap.peri:.1f} apo={snap.apo:.1f} "
        f"atm={snap.atm_depth:.1f} in_atmo={int(snap.in_atmo)} "
        f"ec={ec} fuel={fuel} wreck={int(snap.wreck)}{link_s}{rate_s} "
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


_TRUE = (True, 1, "1", "True", "true", "yes")


def _module_flag(module: Any, *keys: str) -> str | None:
    """True-ish KSPField flags. Never build ``Module.fields`` unguarded.

    kRPC 0.6 ``Module.fields`` / ``get_field`` are visible PAW gui names and
    raise ``ValueError`` on duplicate keys (OKTO ``ModuleReactionWheel``:
    two gui ``Reaction Wheels``). Walk ``field_list`` / ``get_field_by_id``.
    """
    want = {k.lower(): k for k in keys}

    try:
        flist = list(getattr(module, "field_list", None) or [])
    except Exception:
        flist = []
    for field in flist:
        try:
            fname = str(getattr(field, "name", "") or "")
        except Exception:
            continue
        key = want.get(fname.lower())
        if key is None:
            continue
        try:
            val = getattr(field, "value", None)
        except Exception:
            val = None
        if val in _TRUE:
            return key

    try:
        getter_id = getattr(module, "get_field_by_id", None)
    except Exception:
        getter_id = None
    if callable(getter_id):
        for key in keys:
            try:
                val = getter_id(key)
            except Exception:
                continue
            if val in _TRUE:
                return key

    try:
        by_id = getattr(module, "fields_by_id", None)
    except Exception:
        by_id = None
    if isinstance(by_id, dict):
        for key in keys:
            if key in by_id and by_id[key] in _TRUE:
                return key

    # field_list already walked — do not getattr .fields (OKTO duplicate
    # gui names raise; 36-part hops spent ~13 s/pulse on that path).
    if flist:
        return None

    try:
        fields = getattr(module, "fields", None)
    except Exception:
        fields = None
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
                try:
                    val = getattr(module, key, None)
                except Exception:
                    val = None
        if val in _TRUE:
            return key
    return None


def chute_state(vessel: Any, *, deep: bool = True) -> str:
    """kRPC Parachute.State, else RealChuteModule field_list. ``none`` if no chute.

    ``deep=False`` skips ``parts.all`` (fast pulse). RealChute fallback is
    the slow path.
    """
    best = "none"
    best_rank = -1

    def _consider(label: str) -> None:
        nonlocal best, best_rank
        st = (label or "").lower().replace("-", "_")
        rank = _CHUTE_RANK.get(st, -1)
        if rank > best_rank:
            best_rank = rank
            best = st or "stowed"

    try:
        chutes = list(getattr(getattr(vessel, "parts", None), "parachutes", None) or [])
    except Exception:
        chutes = []
    for ch in chutes:
        st = ""
        try:
            st = _enum_name(getattr(ch, "state", None), "")
        except Exception:
            st = ""
        if not st:
            try:
                if getattr(ch, "deployed", False):
                    st = "deployed"
                elif getattr(ch, "armed", False):
                    st = "armed"
                else:
                    st = "stowed"
            except Exception:
                continue
        _consider(st)
    if best != "none" or not deep:
        return best
    try:
        parts = list(vessel.parts.all)
    except Exception:
        return "none"
    for part in parts:
        try:
            modules = list(part.modules)
        except Exception:
            continue
        for module in modules:
            try:
                mname = str(getattr(module, "name", "") or "").lower()
            except Exception:
                continue
            if "chute" not in mname and "parachute" not in mname:
                continue
            st = ""
            try:
                flist = list(getattr(module, "field_list", None) or [])
            except Exception:
                flist = []
            for field in flist:
                try:
                    fname = str(getattr(field, "name", "") or "").lower()
                    val = getattr(field, "value", None)
                except Exception:
                    continue
                if fname in {"state", "deploymentstate", "chute state"}:
                    st = str(val or "")
                    break
                if fname == "deployed" and val in _TRUE:
                    st = "deployed"
                elif fname == "armed" and val in _TRUE and not st:
                    st = "armed"
            _consider(st or "stowed")
    return best


def science_run_rem(vessel: Any) -> tuple[bool | None, float | None]:
    """Kerbalism/stock experiment running + min remaining. Disk PAW ids, not gui names."""
    try:
        from science import card_run_rem, iter_science_modules
    except Exception:
        return None, None
    try:
        eids = [eid for _p, _m, eid in iter_science_modules(vessel) if eid]
    except Exception:
        return None, None
    if not eids:
        return False, None
    try:
        running, rem = card_run_rem(vessel, eids)
    except Exception:
        return None, None
    return bool(running), rem


def parts_count(vessel: Any) -> int | None:
    try:
        n = len(list(getattr(getattr(vessel, "parts", None), "all", ()) or ()))
    except Exception:
        return None
    return n


def root_part_name(vessel: Any) -> str:
    try:
        root = getattr(getattr(vessel, "parts", None), "root", None)
        name = str(getattr(root, "name", "") or "")
    except Exception:
        return ""
    return name


def debris_count(session: Any) -> int | None:
    try:
        pool = list(getattr(getattr(session, "space_center", None), "vessels", ()) or ())
    except Exception:
        return None
    n = 0
    for other in pool:
        try:
            name = str(getattr(other, "name", "") or "").lower()
        except Exception:
            name = ""
        typ = ""
        try:
            typ = str(getattr(getattr(other, "type", None), "name", "") or "").lower()
        except Exception:
            typ = ""
        if "debris" in name or typ == "debris":
            n += 1
    return n


def stack_shear(prev: Any, cur: Any) -> bool:
    """Aero/attitude shear: stack mass/parts vanish without a stage.

    ``reliability_broken`` is Kerbalism malfunction, not exploded parts.
    Fuel burn is a slow mass bleed; a hop tank+engine leaving the OKTO
    is a one-sample drop (1677→270 kg, stage unchanged).
    """

    def _get(obj: Any, key: str) -> Any:
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)

    p_stage, c_stage = _get(prev, "stage"), _get(cur, "stage")
    try:
        if p_stage is not None and c_stage is not None and int(c_stage) < int(p_stage):
            return False
    except (TypeError, ValueError):
        pass
    p_n, c_n = _get(prev, "parts_n"), _get(cur, "parts_n")
    try:
        if p_n is not None and c_n is not None and int(c_n) < int(p_n):
            return True
    except (TypeError, ValueError):
        pass
    pm, cm = _finite(_get(prev, "mass")), _finite(_get(cur, "mass"))
    if not (pm > 80.0 and cm > 20.0):
        return False
    if cm / pm > 0.50:
        return False
    drop = pm - cm
    pf, cf = _finite(_get(prev, "fuel")), _finite(_get(cur, "fuel"))
    dfuel = 0.0
    if math.isfinite(pf) and math.isfinite(cf) and pf > cf:
        dfuel = pf - cf
    return drop >= max(200.0, dfuel + 150.0)


def _vessel_key(vessel: Any) -> tuple[Any, ...]:
    if vessel is None:
        return ("none",)
    try:
        vid = getattr(vessel, "id", None)
    except Exception:
        vid = None
    if vid is not None and vid != "":
        return ("id", vid)
    return ("py", id(vessel))


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
            try:
                hit = _module_flag(
                    module, "broken", "isBroken", "malfunction", "failed"
                )
            except Exception:
                continue
            if hit:
                mname = getattr(module, "name", "?")
                return f"{pname}:{mname}:{hit}"
    return None


def comms_via(vessel: Any) -> str:
    """Home ``CommNode.Name`` on ``control_path``. Slow RPC; never the 20 Hz path."""
    try:
        comms = getattr(vessel, "comms", None)
        if comms is None:
            return ""
        path = getattr(comms, "control_path", None)
        links = list(path or [])
    except Exception:
        return ""
    home = ""
    end_name = ""
    for link in links:
        for attr in ("end", "start"):
            try:
                node = getattr(link, attr, None)
            except Exception:
                continue
            if node is None:
                continue
            try:
                name = str(getattr(node, "name", "") or "")
            except Exception:
                name = ""
            is_home = False
            try:
                is_home = bool(getattr(node, "is_home", False))
            except Exception:
                is_home = False
            if not is_home:
                try:
                    is_home = bool(getattr(node, "IsHome", False))
                except Exception:
                    is_home = False
            if not name:
                continue
            if is_home:
                home = name
            elif attr == "end":
                end_name = name
    return home or end_name


def comms_rate_bps(vessel: Any) -> float:
    """Live RA RateToHome (bps). Table MaxDataRate is not this. Slow RPC."""
    try:
        client = getattr(vessel, "_client", None)
        ra = getattr(client, "real_antennas", None) if client is not None else None
        if ra is None or not bool(getattr(ra, "available", False)):
            return float("nan")
        comms = ra.comms(vessel)
        return float(comms.rate_to_home)
    except Exception:
        return float("nan")


def gates(snap: Snapshot) -> list[str]:
    """Body-relative gates. No Kerbin DIP/ESC strings."""
    out: list[str] = []
    if snap.wreck:
        out.append("wreck")
    if snap.link is False:
        out.append("deaf")
    if snap.broken:
        out.append(f"reliability {snap.broken}")
    if snap.shear:
        out.append("shear")
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
    """Hop loop nap. Cruise 5 Hz; 20 Hz while throttled, below 8 km, or TTI < 8 s."""
    sit = (snap.situation or "").lower()
    if sit in _PAD and sit not in {"splashed", "landed"}:
        return 1.0 / CRUISE_HZ
    alt = snap.alt
    vz = snap.v_vert
    thr = snap.throttle
    if sit in _DOWN:
        return 1.0 / CRUISE_HZ
    if math.isfinite(thr) and thr > BURN_THROTTLE:
        return 1.0 / NEAR_HZ
    if math.isfinite(alt) and alt < NEAR_ALT_M:
        return 1.0 / NEAR_HZ
    if math.isfinite(vz) and vz < 0 and math.isfinite(alt) and alt > 0:
        tti = alt / max(0.1, -vz)
        if tti < TTI_BURST_S:
            return 1.0 / NEAR_HZ
    return 1.0 / CRUISE_HZ


def _fmt_num(val: Any, spec: str = ".0f") -> str:
    try:
        n = float(val)
    except (TypeError, ValueError):
        return "?"
    if not math.isfinite(n):
        return "?"
    return format(n, spec)


def format_landing(row: dict[str, Any]) -> str:
    landing = row.get("landing") or "unknown"
    sit = row.get("sit") or row.get("situation") or "?"
    synth = ""
    if row.get("landing_synthesized") or row.get("synthesized"):
        synth = " synth"
    return (
        f"landing: {landing} impact={_fmt_num(row.get('impact_ms'))} m/s "
        f"heading={_fmt_num(row.get('heading'))} "
        f"horiz={_fmt_num(row.get('horiz'))} "
        f"pitch={_fmt_num(row.get('pitch'))} sit={sit}{synth}"
    )


def landing_from_jsonl(path: str | Path) -> dict[str, Any]:
    """Disk envelope. Agents query ``tape.Tape``; do not read the jsonl."""
    from tape import envelope

    return envelope(path)


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
        self._prev_pitch: float | None = None
        self._landed: bool = False
        self._prev_recoverable: bool | None = None
        self._prev_mass: float | None = None
        self._prev_fuel: float | None = None
        self._prev_parts: int | None = None
        self._prev_stage: int | None = None
        self._sheared: bool = False
        self._shear_emitted: bool = False
        self._vessel_key: tuple[Any, ...] | None = None
        self._slow_at: float = 0.0
        self._slow_cost_s: float = 0.0
        self._last_read_s: float = 0.0
        self._slow_sci: tuple[bool | None, float | None] = (None, None)
        self._slow_bank: float | None = None
        self._slow_broken: str | None = None
        self._slow_debris: int | None = None
        self._slow_chute: str = ""
        self._slow_parts: int | None = None
        self._slow_root: str = ""
        self._slow_resources: dict[str, float] = {}
        self._slow_via: str = ""
        self._slow_rate_bps: float = float("nan")
        self._pad_ll: tuple[float, float] | None = None
        self._body_r: float = float("nan")

    def _drop_streams(self) -> None:
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
        self._vessel_key = None

    def close(self) -> None:
        self._drop_streams()
        self._met_was = None
        self._prev_v_vert = None
        self._prev_met_g = None
        self._slow_at = 0.0
        self._slow_cost_s = 0.0
        self._last_read_s = 0.0
        self._slow_chute = ""
        self._slow_parts = None
        self._slow_root = ""
        self._slow_resources = {}
        self._slow_via = ""

    def __enter__(self) -> Telem:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _bind(self, vessel: Any) -> None:
        key = _vessel_key(vessel)
        if key == self._vessel_key and self._streams:
            self._vessel = vessel
            return
        # Rebind must not reset cadence — close() zeroes _last_read_s
        # and re-arms the 13 s sci/broken walk (16-47-21Z 0.07 Hz).
        old = self._vessel_key
        self._drop_streams()
        self._vessel = vessel
        self._vessel_key = key
        if old != key:
            self._slow_at = 0.0
            self._slow_cost_s = 0.0
            self._slow_via = ""
            self._slow_rate_bps = float("nan")
        if vessel is None:
            return
        self._flight = vessel.flight()
        self._orbit = vessel.orbit
        self._body = self._orbit.body
        self._body_r = _finite(getattr(self._body, "equatorial_radius", float("nan")))
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
        for prop in ("mass", "met"):
            try:
                self._streams[f"vessel.{prop}"] = add_stream(getattr, vessel, prop)
            except Exception:
                pass
        try:
            ctrl = getattr(vessel, "control", None)
            if ctrl is not None:
                self._streams["ctrl.throttle"] = add_stream(getattr, ctrl, "throttle")
        except Exception:
            pass
        try:
            comms = getattr(vessel, "comms", None)
        except Exception:
            comms = None
        if comms is not None:
            for prop in ("can_communicate", "signal_strength"):
                try:
                    self._streams[f"comms.{prop}"] = add_stream(getattr, comms, prop)
                except Exception:
                    pass

    def _stream(self, key: str, fallback: Any = float("nan")) -> float:
        stream = self._streams.get(key)
        if stream is None:
            return _finite(fallback)
        try:
            return _finite(stream())
        except Exception:
            return _finite(fallback)

    def _stream_bool(self, key: str) -> bool | None:
        stream = self._streams.get(key)
        if stream is None:
            return None
        try:
            val = stream()
        except Exception:
            return None
        if val is None:
            return None
        return bool(val)

    def _downrange_km(self, lat: float, lon: float) -> float:
        if not math.isfinite(lat) or not math.isfinite(lon):
            return float("nan")
        if self._pad_ll is None:
            try:
                from hangar import pad_ll

                self._pad_ll = pad_ll()
            except Exception:
                from sites import CAPE

                self._pad_ll = (CAPE.latitude, CAPE.longitude)
        plat, plon = self._pad_ll
        radius = self._body_r
        if not math.isfinite(radius) or radius <= 0.0:
            from sites import EARTH_R_M

            radius = EARTH_R_M
        from sites import downrange_km

        return downrange_km(lat, lon, plat, plon, radius)

    def read(self) -> Snapshot:
        t0 = time.monotonic()
        snap: Snapshot | None = None
        try:
            snap = self._read_body()
            return snap
        finally:
            self._last_read_s = time.monotonic() - t0
            # grim ticks must not live inside the timed pulse (16-47-21Z).
            if snap is not None and self._last_read_s < CHEAP_READ_S:
                _maybe_shot(snap)

    def _read_body(self) -> Snapshot:
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
        now_m = time.monotonic()
        cheap_enough = 0.0 < self._last_read_s < CHEAP_READ_S
        down_edge = sit in _DOWN and not self._landed
        # An expensive sci/broken walk re-armed every cheap pulse (T-147
        # skip lasted one row). After a slow walk costs ≥ CHEAP_READ_S,
        # stay on streams until sit goes landed/splashed.
        slow = (
            self._slow_at <= 0.0
            or down_edge
            or (
                cheap_enough
                and self._slow_cost_s < CHEAP_READ_S
                and now_m - self._slow_at >= SLOW_RPC_S
            )
        )
        resources: dict[str, float] = dict(self._slow_resources)
        fuel_names = _FUELS if slow else _FAST_FUELS
        for name in fuel_names:
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
        throttle = self._stream(
            "ctrl.throttle",
            getattr(getattr(vessel, "control", None), "throttle", float("nan")),
        )
        link = self._stream_bool("comms.can_communicate")
        snr = self._stream("comms.signal_strength")
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
        lat = self._stream("flight.latitude")
        lon = self._stream("flight.longitude")
        downrange = self._downrange_km(lat, lon)
        if not math.isfinite(speed) or speed <= 0.05:
            if math.isfinite(horiz) and abs(horiz) > 0.05:
                speed = abs(horiz)
        met = self._stream("vessel.met", getattr(vessel, "met", float("nan")))
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
        g_load = self._stream("flight.g_force")
        if not math.isfinite(g_load):
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
        rec: bool | None
        try:
            rec = bool(getattr(vessel, "recoverable", False))
        except Exception:
            rec = None
        rec_edge = False
        if rec is not None:
            if self._prev_recoverable is None:
                rec_edge = bool(rec)
            elif rec != self._prev_recoverable:
                rec_edge = True
            self._prev_recoverable = rec
        if rec_edge:
            self.events.emit(
                "recoverable",
                recoverable=bool(rec),
                sit=sit,
                met=met,
            )
        chute = chute_state(vessel, deep=slow)
        mass = self._stream("vessel.mass", getattr(vessel, "mass", float("nan")))
        mass_drop = (
            self._prev_mass is not None
            and math.isfinite(mass)
            and self._prev_mass > 80.0
            and mass < self._prev_mass * 0.50
        )
        if slow:
            t_slow = time.monotonic()
            parts_n = parts_count(vessel)
            root = root_part_name(vessel)
            self._slow_chute = chute
            self._slow_parts = parts_n
            self._slow_root = root
            self._slow_resources = dict(resources)
            sci_run, sci_rem = science_run_rem(vessel)
            self._slow_sci = (sci_run, sci_rem)
            try:
                from career import space_center_science

                self._slow_bank = space_center_science(self.session)
            except Exception:
                self._slow_bank = None
            try:
                self._slow_broken = reliability_broken(vessel)
            except Exception:
                self._slow_broken = None
            self._slow_debris = debris_count(self.session)
            try:
                self._slow_via = comms_via(vessel)
            except Exception:
                self._slow_via = ""
            try:
                self._slow_rate_bps = comms_rate_bps(vessel)
            except Exception:
                self._slow_rate_bps = float("nan")
            self._slow_at = time.monotonic()
            self._slow_cost_s = self._slow_at - t_slow
        else:
            if mass_drop:
                parts_n = parts_count(vessel)
                root = root_part_name(vessel)
                self._slow_parts = parts_n
                self._slow_root = root
            else:
                parts_n = self._slow_parts
                root = self._slow_root
            if chute in {"", "none"} and self._slow_chute:
                chute = self._slow_chute
            sci_run, sci_rem = self._slow_sci
        sci_bank = self._slow_bank
        debris_n = self._slow_debris
        via = self._slow_via
        rate_bps = self._slow_rate_bps
        avail = _finite(getattr(vessel, "available_thrust", float("nan")))
        landing = ""
        downish = sit in _DOWN or wreck
        if downish and not self._landed:
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
                pitch=self._prev_pitch if self._prev_pitch is not None else pitch,
                sit=sit,
                met=met,
                biome=biome,
                lat=lat,
                lon=lon,
                downrange=downrange,
                wreck=int(wreck),
            )
        elif sit in _AIR and not wreck:
            self._landed = False
        broken = self._slow_broken
        stage = None
        try:
            stage = int(getattr(vessel.control, "current_stage"))
        except (TypeError, ValueError, AttributeError):
            stage = None
        sheared = bool(self._sheared)
        prev_stack = {
            "mass": self._prev_mass,
            "fuel": self._prev_fuel,
            "parts_n": self._prev_parts,
            "stage": self._prev_stage,
        }
        cur_stack = {
            "mass": mass,
            "fuel": fuel,
            "parts_n": parts_n,
            "stage": stage,
        }
        if not sheared and self._prev_mass is not None:
            sheared = stack_shear(prev_stack, cur_stack)
        if sheared:
            self._sheared = True
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
            lat=lat,
            lon=lon,
            downrange=downrange,
            met=met,
            ec=ec,
            fuel=fuel,
            lf=fuel,
            broken=broken,
            stage=stage,
            recoverable=rec,
            chute=chute,
            sci_run=sci_run,
            sci_rem=sci_rem,
            sci_bank=sci_bank,
            mass=mass,
            parts_n=parts_n,
            root=root,
            debris_n=debris_n,
            shear=bool(sheared),
            available_thrust=avail,
            link=link,
            snr=snr,
            via=via,
            rate_bps=rate_bps,
            resources=resources,
        )
        reasons = gates(snap)
        snap.flags = tuple(reasons)
        try:
            snap.hz = round(1.0 / max(pulse_s(snap), 1e-9), 2)
        except Exception:
            snap.hz = float("nan")
        shear_edge = bool(sheared) and not self._shear_emitted
        if shear_edge:
            self._shear_emitted = True
            self.events.emit(
                "shear",
                mass=mass,
                parts_n=parts_n,
                root=root,
                debris_n=debris_n,
                met=met,
                sit=sit,
            )
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
            if math.isfinite(pitch):
                self._prev_pitch = pitch
        if math.isfinite(mass):
            self._prev_mass = mass
        self._prev_fuel = fuel
        self._prev_parts = parts_n
        self._prev_stage = stage
        _record_run(
            self.session, snap, rec_edge=rec_edge, shear_edge=shear_edge
        )
        return snap


def _maybe_shot(snap: Snapshot) -> None:
    try:
        from screenshot import mission_observe

        mission_observe(snap)
    except Exception:
        log.debug("mission shot observe failed", exc_info=True)


def _record_run(
    session: Any,
    snap: Snapshot,
    *,
    rec_edge: bool = False,
    shear_edge: bool = False,
) -> None:
    """Write this pulse to the seated jsonl. No-op if flight has not started."""
    try:
        from flightlog import event, record
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
            event(
                "landing",
                format_landing(
                    {
                        "landing": snap.landing,
                        "impact_ms": impact_speed(
                            v_vert=snap.v_vert, speed=snap.speed, horiz=snap.horiz
                        ),
                        "heading": snap.heading,
                        "horiz": snap.horiz,
                        "pitch": snap.pitch,
                        "sit": snap.situation,
                    }
                ),
                landing=snap.landing,
                v_vert=snap.v_vert,
                speed=snap.speed,
                horiz=snap.horiz,
                heading=snap.heading,
                pitch=snap.pitch,
                sit=snap.situation,
                met=snap.met,
                biome=snap.biome,
                wreck=int(snap.wreck),
            )
        if rec_edge and snap.recoverable is not None:
            rec_s = "yes" if snap.recoverable else "no"
            event(
                "recoverable",
                f"recoverable={rec_s} sit={snap.situation}",
                recoverable=bool(snap.recoverable),
                sit=snap.situation,
                met=snap.met,
                alt=snap.alt,
            )
        if shear_edge:
            event(
                "shear",
                (
                    f"shear mass={snap.mass:g} parts={snap.parts_n} "
                    f"root={snap.root or '?'} debris={snap.debris_n}"
                ),
                mass=snap.mass,
                parts_n=snap.parts_n,
                root=snap.root,
                debris_n=snap.debris_n,
                sit=snap.situation,
                met=snap.met,
                alt=snap.alt,
                q=snap.q,
            )
    except Exception:
        log.debug("flightlog record failed", exc_info=True)


def read_snapshot(session: Any, *, scene: str = "?", events: EventLog | None = None) -> Snapshot:
    with Telem(session, events=events, scene=scene) as telem:
        return telem.read()
