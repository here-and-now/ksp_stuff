"""RSS / KSCSwitcher launch sites from disk. No kRPC."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

# RSS Earth mean radius. Live telem prefers body.equatorial_radius.
EARTH_R_M = 6_371_000.0


@dataclass(frozen=True, slots=True)
class Site:
    name: str
    latitude: float
    longitude: float
    display: str = ""


# Stock KSC — only if no RSS site file exists.
STOCK_PAD = Site("ksc", -0.0972, -74.5577, "Stock Kerbal Space Center")
CAPE = Site("us_cape_canaveral", 28.608389, -80.604333, "US - Cape Canaveral")


def parse_launch_sites(text: str) -> tuple[str, dict[str, Site]]:
    """Return (default_name, sites) from a KSCSwitcher / RSS LaunchSites.cfg."""
    default = ""
    sites: dict[str, Site] = {}
    in_site = False
    name = display = ""
    lat = lon = None
    for raw in text.splitlines():
        s = raw.strip()
        if s.startswith("%DefaultSite") or s.startswith("DefaultSite"):
            if "=" in s:
                default = s.split("=", 1)[1].strip()
            continue
        if s == "Site":
            if in_site and name and lat is not None and lon is not None:
                sites[name] = Site(name, lat, lon, display)
            in_site = True
            name = display = ""
            lat = lon = None
            continue
        if not in_site:
            continue
        if s == "}" and name and lat is not None and lon is not None:
            # closing a nested block is common; commit only when we already
            # have lat/lon and see a later Site or EOF.
            continue
        if "=" not in s:
            continue
        key, _, rest = s.partition("=")
        key = key.strip()
        value = rest.strip()
        if key == "name" and not name:
            name = value
        elif key == "displayName" and not display:
            display = value.split("//", 1)[-1].strip() if "//" in value else value
        elif key == "latitude" and lat is None:
            try:
                lat = float(value)
            except ValueError:
                pass
        elif key == "longitude" and lon is None:
            try:
                lon = float(value)
            except ValueError:
                pass
    if in_site and name and lat is not None and lon is not None:
        sites[name] = Site(name, lat, lon, display)
    if not default and sites:
        default = next(iter(sites))
    return default, sites


def load_launch_sites(ksp_root: str | Path) -> tuple[str, dict[str, Site]]:
    root = Path(ksp_root)
    candidates = (
        root / "GameData" / "RealSolarSystem" / "LaunchSites.cfg",
        root / "GameData" / "KSCSwitcher" / "LaunchSites.cfg",
    )
    for path in candidates:
        if path.is_file():
            return parse_launch_sites(
                path.read_text(encoding="utf-8", errors="replace")
            )
    return "ksc", {"ksc": STOCK_PAD}


def default_pad_ll(ksp_root: str | Path) -> tuple[float, float]:
    """Latitude, longitude of the default pad (Cape under RSS)."""
    default, sites = load_launch_sites(ksp_root)
    site = sites.get(default) or sites.get("us_cape_canaveral")
    if site is None:
        return STOCK_PAD.latitude, STOCK_PAD.longitude
    return site.latitude, site.longitude


def downrange_km(
    lat: float,
    lon: float,
    pad_lat: float,
    pad_lon: float,
    radius_m: float = EARTH_R_M,
) -> float:
    """Great-circle km from pad to (lat, lon). NaN if any input is not finite."""
    try:
        lat_f = float(lat)
        lon_f = float(lon)
        plat = float(pad_lat)
        plon = float(pad_lon)
        radius = float(radius_m)
    except (TypeError, ValueError):
        return float("nan")
    if not all(math.isfinite(x) for x in (lat_f, lon_f, plat, plon, radius)):
        return float("nan")
    if radius <= 0.0:
        return float("nan")
    rlat1 = math.radians(lat_f)
    rlat2 = math.radians(plat)
    dlat = math.radians(plat - lat_f)
    dlon = math.radians(plon - lon_f)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2.0) ** 2
    )
    a = min(1.0, max(0.0, a))
    return (radius * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))) / 1000.0
