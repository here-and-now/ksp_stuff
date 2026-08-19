"""Pure orbital / launch geometry. No kRPC."""

from __future__ import annotations

import math

G0 = 9.80665


def clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def vis_viva(mu: float, radius: float, semi_major_axis: float) -> float:
    return math.sqrt(mu * (2.0 / radius - 1.0 / semi_major_axis))


def circular_speed(mu: float, radius: float) -> float:
    return math.sqrt(mu / radius)


def circularize_delta_v(mu: float, radius: float, semi_major_axis: float) -> float:
    """Prograde Δv to circularize at ``radius`` (typically apoapsis)."""
    return circular_speed(mu, radius) - vis_viva(mu, radius, semi_major_axis)


def burn_time(delta_v: float, thrust: float, isp_seconds: float, mass: float) -> float:
    """Rocket-equation burn duration. ``isp_seconds`` uses g0 = 9.80665."""
    if thrust <= 0 or isp_seconds <= 0 or mass <= 0 or delta_v == 0:
        return 0.0
    exhaust_velocity = isp_seconds * G0
    mass_final = mass / math.exp(abs(delta_v) / exhaust_velocity)
    flow_rate = thrust / exhaust_velocity
    return abs(mass - mass_final) / flow_rate


def heading_from_inclination(inclination_deg: float) -> float:
    """Compass heading for an equatorial launch site (stock KSC)."""
    return (90.0 - inclination_deg) % 360.0


def inertial_launch_azimuth(
    latitude_deg: float,
    inclination_deg: float,
    *,
    northerly: bool = True,
) -> float:
    """Inertial launch azimuth in degrees from north (KSP heading).

    ``sin(azimuth) = cos(i) / cos(φ)``. Inclination cannot be below the
    site latitude. Southbound is ``180° − azimuth``.
    """
    lat = math.radians(latitude_deg)
    inc = math.radians(abs(inclination_deg))
    if abs(math.cos(lat)) < 1e-9:
        return 90.0 if inclination_deg >= 0 else 270.0
    ratio = clamp(math.cos(inc) / math.cos(lat), -1.0, 1.0)
    azimuth = math.degrees(math.asin(ratio))
    if inclination_deg < 0:
        northerly = False
    if not northerly:
        azimuth = 180.0 - azimuth
    return azimuth % 360.0


def rotation_corrected_azimuth(
    inertial_azimuth_deg: float,
    latitude_deg: float,
    orbital_speed: float,
    equatorial_rotation_speed: float,
) -> float:
    """Steer into the rotating atmosphere. Approximate, parking-orbit speed."""
    if orbital_speed <= 0:
        return inertial_azimuth_deg
    az = math.radians(inertial_azimuth_deg)
    v_east = equatorial_rotation_speed * math.cos(math.radians(latitude_deg))
    vx = orbital_speed * math.sin(az) - v_east
    vy = orbital_speed * math.cos(az)
    return math.degrees(math.atan2(vx, vy)) % 360.0


def quadratic_pitch(frac: float) -> float:
    """Pitch 90° → 0° as ``frac`` goes 0 → 1. Same curve as the old launcher."""
    frac = clamp(frac, 0.0, 1.0)
    return 90.0 + 90.0 * frac * (frac - 2.0)


def wrap_degrees(value: float) -> float:
    return value % 360.0


def angle_delta_deg(a: float, b: float) -> float:
    """Signed smallest difference ``a - b`` in (−180, 180]."""
    return (a - b + 180.0) % 360.0 - 180.0


def geosynchronous_altitude(
    gravitational_parameter: float,
    equatorial_radius: float,
    rotational_period: float,
) -> float:
    """Circular altitude whose period matches the body's sidereal day."""
    if rotational_period <= 0:
        return 0.0
    sma = (gravitational_parameter * rotational_period**2 / (4.0 * math.pi**2)) ** (
        1.0 / 3.0
    )
    return sma - equatorial_radius


def resonance_for_count(n: int) -> tuple[int, int]:
    """MechJeb resonant-orbit ratio that spaces ``n`` drops one period apart.

    ``(n-1):n`` is a faster (lower) transfer: release at peri/apo, wait one
    rev, next sat is 360°/n behind. Three sats → 2:3, the old default.
    """
    n = max(2, int(n))
    return n - 1, n


def walker_slots(
    total: int,
    planes: int = 1,
    phasing: int = 0,
) -> list[tuple[float, float]]:
    """Walker-delta slots as ``(RAAN_deg, mean_anomaly_deg)``.

    ``phasing`` is the usual f parameter, 0 … planes-1. One RP-1 launch
    usually fills a single plane; the rest of the slots stay empty until
    later flights.
    """
    total = max(1, int(total))
    planes = max(1, int(planes))
    if total % planes:
        raise ValueError(f"{total} satellites do not divide into {planes} planes")
    per_plane = total // planes
    slots: list[tuple[float, float]] = []
    for plane in range(planes):
        raan = 360.0 * plane / planes
        for i in range(per_plane):
            mean_anomaly = 360.0 * i / per_plane + 360.0 * phasing * plane / total
            slots.append((wrap_degrees(raan), wrap_degrees(mean_anomaly)))
    return slots


def elevation_deg(
    observer: tuple[float, float, float],
    target: tuple[float, float, float],
    up: tuple[float, float, float],
) -> float:
    """Elevation of ``target`` above the local horizon at ``observer``."""
    dx = target[0] - observer[0]
    dy = target[1] - observer[1]
    dz = target[2] - observer[2]
    range_m = math.sqrt(dx * dx + dy * dy + dz * dz)
    if range_m <= 0:
        return 90.0
    up_n = math.sqrt(up[0] ** 2 + up[1] ** 2 + up[2] ** 2) or 1.0
    cos_zenith = (dx * up[0] + dy * up[1] + dz * up[2]) / (range_m * up_n)
    cos_zenith = clamp(cos_zenith, -1.0, 1.0)
    return 90.0 - math.degrees(math.acos(cos_zenith))
