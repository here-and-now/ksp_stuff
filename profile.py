"""Stock vs RSS game profiles.

Body names, fuels, default ascent numbers, and launch-site latitudes live
here so nothing else has to hardcode Kerbin.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Realism Overhaul resource names that show up in tanks. Staging treats any
# of these hitting zero (with a non-zero capacity) as "this stage is done".
RO_FUELS: tuple[str, ...] = (
    "LiquidFuel",
    "Oxidizer",
    "LqdHydrogen",
    "LqdOxygen",
    "LqdMethane",
    "Kerosene",
    "UDMH",
    "MMH",
    "Hydrazine",
    "Aerozine50",
    "NTO",
    "IRFNA-III",
    "HTP",
    "Aniline",
    "Ethanol",
    "Ammonia",
    "SolidFuel",
    "HTPB",
    "PBAN",
    "NGNC",
    "MonoPropellant",
)

STOCK_FUELS: tuple[str, ...] = (
    "LiquidFuel",
    "Oxidizer",
    "LqdHydrogen",
    "MonoPropellant",
    "SolidFuel",
)


@dataclass(frozen=True, slots=True)
class LaunchSite:
    """Named pad used for inertial-azimuth estimates."""

    name: str
    latitude_deg: float
    body: str
    notes: str = ""


# RSS pads. Stock KSC is on the equator; latitude is still useful if a
# Kopernicus install moves it.
LAUNCH_SITES: dict[str, tuple[LaunchSite, ...]] = {
    "Kerbin": (
        LaunchSite("KSC", 0.102, "Kerbin", "Stock Kerbal Space Center"),
    ),
    "Earth": (
        LaunchSite("Cape Canaveral", 28.608, "Earth", "KSC / LC-39 analog"),
        LaunchSite("Vandenberg", 34.742, "Earth"),
        LaunchSite("Wallops", 37.940, "Earth"),
        LaunchSite("Kourou", 5.232, "Earth"),
        LaunchSite("Baikonur", 45.965, "Earth"),
        LaunchSite("Mahia", -39.261, "Earth", "Rocket Lab"),
    ),
}


@dataclass(frozen=True, slots=True)
class GameProfile:
    name: str
    display_name: str
    home_body_candidates: tuple[str, ...]
    fuels: tuple[str, ...]
    default_target_altitude: float
    default_turn_start: float
    default_turn_end: float
    default_max_q: float
    default_max_twr: float | None
    altitude_range: tuple[float, float]
    notes: str = ""
    comms_prefers_remotetech: bool = True
    launch_sites: tuple[LaunchSite, ...] = field(default_factory=tuple)

    def resolve_home_body(self, bodies: dict) -> object:
        """Return the kRPC CelestialBody for this profile."""
        for name in self.home_body_candidates:
            if name in bodies:
                return bodies[name]
        raise LookupError(
            f"None of {self.home_body_candidates} exist in this save. "
            f"Bodies: {sorted(bodies)}"
        )

    def home_body_name(self, bodies: dict) -> str:
        return self.resolve_home_body(bodies).name


STOCK = GameProfile(
    name="stock",
    display_name="Stock (Kerbin)",
    home_body_candidates=("Kerbin",),
    fuels=STOCK_FUELS,
    default_target_altitude=150_000,
    default_turn_start=2_500,
    default_turn_end=70_000,
    default_max_q=20_000,
    default_max_twr=None,
    altitude_range=(70_000, 1_000_000),
    notes="Original scripts assumed Kerbin + RemoteTech + MechJeb.",
    comms_prefers_remotetech=True,
    launch_sites=LAUNCH_SITES["Kerbin"],
)

RSS_RP1 = GameProfile(
    name="rss",
    display_name="RSS (Kerbalism Default)",
    home_body_candidates=("Earth",),
    fuels=RO_FUELS,
    default_target_altitude=200_000,
    default_turn_start=250,
    default_turn_end=120_000,
    default_max_q=25_000,
    default_max_twr=2.2,
    altitude_range=(160_000, 2_000_000),
    notes=(
        "Real solar system, science sandbox. Kerbalism Default + RealAntennas "
        "on CommNet. Not RO/RP-1. Not MechJeb. Live body.atmosphere_depth wins; "
        "these numbers are only connect-time defaults."
    ),
    comms_prefers_remotetech=False,
    launch_sites=LAUNCH_SITES["Earth"],
)

PROFILES: dict[str, GameProfile] = {
    "stock": STOCK,
    "rss": RSS_RP1,
    "rss_rp1": RSS_RP1,
}


def launch_sites(body_name: str) -> tuple[LaunchSite, ...]:
    return LAUNCH_SITES.get(body_name, ())


def detect_profile(bodies: dict | None) -> GameProfile:
    """Pick RSS when Earth exists, otherwise stock Kerbin."""
    if not bodies:
        return STOCK
    names = set(bodies)
    if "Earth" in names:
        return RSS_RP1
    return STOCK
