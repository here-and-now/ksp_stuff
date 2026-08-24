"""RA CommNet params, commsTL upgrades, Kopernicus RA stations.

Parse ``ModuleManager.ConfigCache`` last write. No kRPC. No GameData tweak
cfg. Agents look at the dump; this module does not lecture.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_COMMS_TL = re.compile(r"^commsTL(\d+)$")
_TRUE = frozenset({"true", "1", "yes"})


def _cfg_token(value: str) -> str:
    raw = value.split("//", 1)[0].strip() if value else ""
    return raw.split()[0] if raw else ""


def _cfg_float(value: str) -> float | None:
    raw = _cfg_token(value)
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _cfg_int(value: str) -> int | None:
    n = _cfg_float(value)
    if n is None or not math.isfinite(n):
        return None
    return int(n)


def _cfg_true(value: str) -> bool:
    return _cfg_token(value).lower() in _TRUE


def _fmt_rate(n: float | None) -> str:
    if n is None or not math.isfinite(n):
        return "-"
    if float(n).is_integer():
        return str(int(n))
    return f"{n:g}"


@dataclass
class TechLevelRow:
    level: int
    name: str
    rate_bps: float | None = None
    node: str = ""
    live: bool = False


@dataclass
class GroundRow:
    name: str
    lat: float = float("nan")
    lon: float = float("nan")
    band: str = ""
    gain_dbi: float | None = None
    tx_dbm: float | None = None
    need_tl: int = 0
    live: bool = False


@dataclass
class CommsCatalog:
    source: str = ""
    min_relay_tl: int | None = None
    tech_levels: list[TechLevelRow] = field(default_factory=list)
    bands: dict[str, int | None] = field(default_factory=dict)
    upgrades: dict[str, str] = field(default_factory=dict)
    stations: list[GroundRow] = field(default_factory=list)
    owned_tl: int = 0
    owned_node: str = ""


def apply_unlocks(cat: CommsCatalog, unlocked: set[str]) -> None:
    """Owned comms TL = highest commsTLN whose techRequired is unlocked."""
    best_n = -1
    best_node = ""
    for name, tech in cat.upgrades.items():
        m = _COMMS_TL.match(name)
        if not m or not tech or tech not in unlocked:
            continue
        n = int(m.group(1))
        if n > best_n:
            best_n = n
            best_node = tech
    owned = best_n if best_n >= 0 else 0
    cat.owned_tl = owned
    cat.owned_node = best_node
    for tl in cat.tech_levels:
        tl.node = cat.upgrades.get(tl.name, "")
        tl.live = tl.level <= owned
    for row in cat.stations:
        row.live = row.need_tl <= owned


def scan_comms_cache(path: str | Path) -> CommsCatalog:
    """Stream ConfigCache for RA params / PARTUPGRADE commsTL / City2 stations."""
    cache = Path(path)
    cat = CommsCatalog(source=str(cache))
    if not cache.is_file():
        return cat

    stack: list[tuple[str, int]] = []
    depth = 0
    pending = ""
    min_relay: int | None = None
    levels: dict[int, TechLevelRow] = {}
    bands: dict[str, int | None] = {}
    upgrades: dict[str, str] = {}
    by_station: dict[str, list[GroundRow]] = {}

    tl_name = ""
    tl_level: int | None = None
    tl_rate: float | None = None
    band_name = ""
    band_tl: int | None = None
    up_name = ""
    up_tech = ""
    city_name = ""
    city_obj = ""
    city_lat = float("nan")
    city_lon = float("nan")
    city_ra = False
    city_ants: list[tuple[str, float | None, float | None, int]] = []
    ant_band = ""
    ant_gain: float | None = None
    ant_tx: float | None = None
    ant_tl: int | None = None

    def _reset_tl() -> None:
        nonlocal tl_name, tl_level, tl_rate
        tl_name = ""
        tl_level = None
        tl_rate = None

    def _reset_band() -> None:
        nonlocal band_name, band_tl
        band_name = ""
        band_tl = None

    def _reset_up() -> None:
        nonlocal up_name, up_tech
        up_name = ""
        up_tech = ""

    def _reset_city() -> None:
        nonlocal city_name, city_obj, city_lat, city_lon, city_ra, city_ants
        city_name = ""
        city_obj = ""
        city_lat = float("nan")
        city_lon = float("nan")
        city_ra = False
        city_ants = []

    def _reset_ant() -> None:
        nonlocal ant_band, ant_gain, ant_tx, ant_tl
        ant_band = ""
        ant_gain = None
        ant_tx = None
        ant_tl = None

    def _open(kind: str) -> None:
        if kind == "TechLevelInfo":
            _reset_tl()
        elif kind == "BandInfo":
            _reset_band()
        elif kind == "PARTUPGRADE":
            _reset_up()
        elif kind == "City2":
            _reset_city()
        elif kind == "Antenna":
            _reset_ant()

    def _parent() -> str:
        return stack[-2][0] if len(stack) >= 2 else ""

    def _close(kind: str) -> None:
        parent = _parent()
        if kind == "TechLevelInfo" and parent == "RealAntennasCommNetParams":
            level = tl_level
            name = tl_name
            if level is None and name:
                m = _COMMS_TL.match(name)
                if m:
                    level = int(m.group(1))
            if name and level is None:
                return
            if level is None:
                return
            if not name:
                name = f"commsTL{level}"
            levels[level] = TechLevelRow(level=level, name=name, rate_bps=tl_rate)
        elif kind == "BandInfo" and parent == "RealAntennasCommNetParams":
            if band_name:
                bands[band_name] = band_tl
        elif kind == "PARTUPGRADE":
            if _COMMS_TL.match(up_name) and up_tech:
                upgrades[up_name] = up_tech
        elif kind == "Antenna" and parent == "City2":
            city_ants.append((ant_band, ant_gain, ant_tx, ant_tl if ant_tl is not None else 0))
        elif kind == "City2":
            if not city_ra:
                return
            key = city_obj or city_name
            if not key or not city_ants:
                return
            by_station[key] = [
                GroundRow(
                    name=key,
                    lat=city_lat,
                    lon=city_lon,
                    band=band or "-",
                    gain_dbi=gain,
                    tx_dbm=tx,
                    need_tl=need,
                )
                for band, gain, tx, need in city_ants
            ]

    with cache.open(encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            s = raw.strip()
            if not s or s.startswith("//"):
                continue
            if s.endswith("{") and "=" not in s.split("{")[0]:
                kind = s[: s.index("{")].strip() or pending
                pending = ""
                depth += 1
                if kind:
                    stack.append((kind, depth))
                    _open(kind)
                continue
            if s == "{":
                depth += 1
                if pending:
                    stack.append((pending, depth))
                    _open(pending)
                    pending = ""
                continue
            if s == "}":
                if stack and stack[-1][1] == depth:
                    kind = stack[-1][0]
                    _close(kind)
                    stack.pop()
                depth -= 1
                if depth < 0:
                    depth = 0
                continue
            if "=" not in s:
                pending = s
                continue
            pending = ""
            key, _, rest = s.partition("=")
            key = key.strip()
            value = rest.strip()
            kind = stack[-1][0] if stack else ""
            if kind == "RealAntennasCommNetParams":
                if key == "minRelayTL":
                    min_relay = _cfg_int(value)
            elif kind == "TechLevelInfo":
                if key == "name" and not tl_name:
                    tl_name = _cfg_token(value) or value.split("//", 1)[0].strip()
                elif key == "Level":
                    tl_level = _cfg_int(value)
                elif key == "MaxDataRate":
                    tl_rate = _cfg_float(value)
            elif kind == "BandInfo":
                if key == "name" and not band_name:
                    band_name = _cfg_token(value) or value.split("//", 1)[0].strip()
                elif key == "TechLevel":
                    band_tl = _cfg_int(value)
            elif kind == "PARTUPGRADE":
                if key == "name" and not up_name:
                    up_name = _cfg_token(value) or value.split("//", 1)[0].strip()
                elif key == "techRequired" and not up_tech:
                    up_tech = _cfg_token(value) or value.split("//", 1)[0].strip()
            elif kind == "City2":
                if key == "objectName" and not city_obj:
                    city_obj = value.split("//", 1)[0].strip()
                elif key == "name" and not city_name:
                    city_name = value.split("//", 1)[0].strip()
                elif key == "lat":
                    n = _cfg_float(value)
                    if n is not None:
                        city_lat = n
                elif key == "lon":
                    n = _cfg_float(value)
                    if n is not None:
                        city_lon = n
                elif key == "RACommNetStation":
                    city_ra = _cfg_true(value)
            elif kind == "Antenna":
                if key == "RFBand" and not ant_band:
                    ant_band = _cfg_token(value) or value.split("//", 1)[0].strip()
                elif key == "referenceGain":
                    ant_gain = _cfg_float(value)
                elif key == "TxPower":
                    ant_tx = _cfg_float(value)
                elif key == "TechLevel":
                    ant_tl = _cfg_int(value)

    cat.min_relay_tl = min_relay
    cat.tech_levels = [levels[k] for k in sorted(levels)]
    cat.bands = bands
    cat.upgrades = upgrades
    cat.stations = [row for rows in by_station.values() for row in rows]
    return cat


def load_comms_catalog(world: Any) -> CommsCatalog:
    root = Path(getattr(world, "ksp_root", "") or "")
    cache = root / "GameData" / "ModuleManager.ConfigCache"
    src = str(getattr(getattr(world, "catalog", None), "source", "") or "")
    if src.endswith("ConfigCache") and Path(src).is_file():
        cache = Path(src)
    cat = scan_comms_cache(cache)
    unlocked = set(getattr(getattr(world, "research", None), "unlocked", ()) or ())
    apply_unlocks(cat, unlocked)
    return cat


def format_ra_tables(cat: CommsCatalog) -> str:
    node = cat.owned_node or "-"
    relay = "-" if cat.min_relay_tl is None else str(cat.min_relay_tl)
    lines = [
        "# RA ConfigCache last write (cfg spawn gate). Live TL is kRPC GSTL.",
        f"# owned comms TL = {cat.owned_tl} ({node}). sample = recover the can. file = HD.",
        "# python main.py comms",
        "#",
        f"# minRelayTL = {relay}",
        "# TL  node              rate_bps  LIVE",
    ]
    for tl in cat.tech_levels:
        live = "LIVE" if tl.live else ""
        lines.append(
            f"{tl.level:<4} {(tl.node or '-'):18} {_fmt_rate(tl.rate_bps):>8}  {live}".rstrip()
        )
    return "\n".join(lines)


def format_ground(cat: CommsCatalog) -> str:
    lines = ["# ground: name lat lon band gain_dBi Tx_dBm need_TL LIVE|SILENT"]
    rows = sorted(
        cat.stations,
        key=lambda r: (not r.live, r.name.lower(), r.band, r.need_tl),
    )
    for row in rows:
        state = "LIVE" if row.live else "SILENT"
        lat = f"{row.lat:.4f}" if math.isfinite(row.lat) else "-"
        lon = f"{row.lon:.4f}" if math.isfinite(row.lon) else "-"
        gain = "-" if row.gain_dbi is None else f"{row.gain_dbi:g}"
        tx = "-" if row.tx_dbm is None else f"{row.tx_dbm:g}"
        lines.append(
            f"{row.name}  {lat}  {lon}  {row.band or '-'}  {gain}  {tx}  "
            f"{row.need_tl}  {state}"
        )
    return "\n".join(lines)
