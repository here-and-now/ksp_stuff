"""RSS / KSCSwitcher launch sites from disk. No kRPC."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
