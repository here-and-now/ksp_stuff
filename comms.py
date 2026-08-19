"""Communications: CommNet + RealAntennas first, RemoteTech as a leftover.

RA does not expose a kRPC service. Routing is stock CommNet
(``vessel.comms``). Antenna RF lives on ``ModuleRealAntenna`` PAW fields.
Dish *pointing* is a nested ConfigNode we can read as a string, not set.

The old RemoteTech loop (aim dish 0 at Kerbin, 1–2 at nearest mates) is
the wrong model here: CommNet picks the best link itself. Automation is
orbit geometry, deploy/enable, coverage, and a dish-aim checklist.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np

from parts import deploy_antennas
from realantennas import RealAntenna, commission, dish_policy_report, inspect
from session import Session
from vessels import list_vessels, snapshot

log = logging.getLogger("kspstuff")

# Legacy RT plan: part name → "setup_network" | list of targets.
AntennaPlan = dict[str, str | Sequence[str]]


@dataclass(slots=True)
class AntennaInfo:
    part_name: str
    title: str
    module: str
    target: str
    state: str
    band: str = ""
    gain: str = ""
    tx_dbm: str = ""
    tech_level: str = ""
    has_connection: bool | None = None


@dataclass(slots=True)
class NetworkRow:
    vessel_name: str
    body: str
    inclination_deg: float
    apoapsis: float
    periapsis: float
    period: float
    antennas: list[AntennaInfo]
    comms: str
    path: str = ""
    can_communicate: bool | None = None
    signal_strength: float | None = None


@dataclass(slots=True)
class CoverageReport:
    rows: list[NetworkRow]
    linked: int
    dark: int
    notes: list[str] = field(default_factory=list)


def current_distance(a: Any, b: Any) -> float:
    frame = a.orbit.body.non_rotating_reference_frame
    pa = np.array(a.position(frame))
    pb = np.array(b.position(frame))
    return float(np.linalg.norm(pa - pb))


def comm_path(vessel: Any) -> str:
    try:
        hops = []
        for link in vessel.comms.control_path:
            end = getattr(link.end, "name", None) or str(link.end)
            hops.append(end)
        return " → ".join(hops) if hops else "—"
    except Exception:
        return "—"


def comm_status(vessel: Any) -> tuple[bool | None, float | None, str]:
    try:
        comms = vessel.comms
        ok = bool(comms.can_communicate)
        strength = float(comms.signal_strength)
        return ok, strength, comm_path(vessel)
    except Exception:
        return None, None, "—"


def _rt_target_name(session: Session, antenna: Any) -> str:
    rt = session.remote_tech
    if rt is None:
        return ""
    try:
        target = antenna.target
        if target == rt.Target.none:
            return "none"
        if target == rt.Target.celestial_body:
            return antenna.target_body.name
        if target == rt.Target.vessel:
            return antenna.target_vessel.name
        if target == rt.Target.ground_station:
            return str(antenna.target_ground_station)
        if target == rt.Target.active_vessel:
            return "active_vessel"
    except Exception:
        return "error"
    return "unknown"


def _from_ra(ant: RealAntenna) -> AntennaInfo:
    return AntennaInfo(
        part_name=ant.part_name,
        title=ant.title,
        module="ModuleRealAntenna",
        target=ant.target or ("omni" if not ant.is_dish else "default"),
        state=ant.condition,
        band=ant.band,
        gain=ant.gain_dbi,
        tx_dbm=ant.tx_dbm,
        tech_level=ant.tech_level,
        has_connection=None,
    )


def inspect_antennas(session: Session, vessel: Any) -> list[AntennaInfo]:
    ra = inspect(vessel)
    if ra:
        return [_from_ra(a) for a in ra]

    info: list[AntennaInfo] = []
    rt = session.remote_tech
    try:
        stock = list(vessel.parts.antennas)
    except Exception:
        stock = []
    if stock:
        for ant in stock:
            part = ant.part
            target = ""
            connected = None
            if rt is not None:
                try:
                    rt_ant = rt.antenna(part)
                    target = _rt_target_name(session, rt_ant)
                    connected = bool(rt_ant.has_connection)
                except Exception:
                    pass
            deployed = ""
            try:
                deployed = "deployed" if ant.deployed else "stowed"
            except Exception:
                deployed = "n/a"
            info.append(
                AntennaInfo(
                    part_name=part.name,
                    title=getattr(part, "title", part.name),
                    module="Antenna",
                    target=target or "—",
                    state=deployed,
                    has_connection=connected,
                )
            )
        return info

    # Last resort: name heuristic (old RT scripts).
    for part in vessel.parts.all:
        blob = f"{part.name} {getattr(part, 'title', '')}".lower()
        if not any(w in blob for w in ("antenna", "dish", "relay")):
            continue
        info.append(
            AntennaInfo(
                part_name=part.name,
                title=getattr(part, "title", part.name),
                module="?",
                target="—",
                state="n/a",
            )
        )
    return info


def network_report(
    session: Session,
    vessels: Iterable[Any],
    *,
    switch: bool = False,
) -> list[NetworkRow]:
    rows: list[NetworkRow] = []
    for vessel in vessels:
        if switch:
            session.switch_to(vessel)
        snap = snapshot(session, vessel)
        ok, strength, path = comm_status(vessel)
        rows.append(
            NetworkRow(
                vessel_name=snap.name,
                body=snap.body,
                inclination_deg=snap.inclination_deg,
                apoapsis=snap.apoapsis,
                periapsis=snap.periapsis,
                period=snap.period,
                antennas=inspect_antennas(session, vessel),
                comms=snap.comms,
                path=path,
                can_communicate=ok,
                signal_strength=strength,
            )
        )
    return rows


def coverage_report(
    session: Session,
    vessels: Sequence[Any],
    *,
    switch: bool = False,
) -> CoverageReport:
    rows = network_report(session, vessels, switch=switch)
    linked = sum(1 for r in rows if r.can_communicate is True)
    dark = sum(1 for r in rows if r.can_communicate is False)
    notes: list[str] = []
    ra_like = [a for row in rows for a in row.antennas if a.module == "ModuleRealAntenna"]
    if ra_like:
        notes.extend(
            dish_policy_report(
                [
                    RealAntenna(
                        part_name=a.part_name,
                        title=a.title,
                        condition=a.state,
                        band=a.band,
                        gain_dbi=a.gain,
                        tx_dbm=a.tx_dbm,
                        tech_level=a.tech_level,
                        target=a.target,
                        idle_power="",
                        active_power="",
                        deployable=False,
                        deployed=True,
                        is_dish="omni" not in a.target.lower(),
                    )
                    for a in ra_like
                ],
                home_body=session.home_body.name,
            )
        )
    elif session.remote_tech is not None:
        notes.append("RemoteTech is loaded. RP-1 wants RealAntennas; this path is legacy.")
    else:
        notes.append("Stock CommNet. RealAntennas is not on these craft.")
    if dark:
        notes.append(f"{dark} vessel(s) cannot talk to KSC right now.")
    return CoverageReport(rows=rows, linked=linked, dark=dark, notes=notes)


def two_nearest(vessel: Any, others: Sequence[Any]) -> list[Any]:
    ranked = sorted(
        (current_distance(vessel, other), other) for other in others if other != vessel
    )
    return [item[1] for item in ranked[:2]]


def set_rt_target(
    session: Session,
    antenna: Any,
    spec: str,
    *,
    vessels_by_name: dict[str, Any],
) -> None:
    rt = session.require_remotetech()
    spec_l = spec.strip()
    if spec_l in ("active_vessel", "active vessel"):
        antenna.target = rt.Target.active_vessel
        return
    if spec_l in session.bodies:
        antenna.target_body = session.bodies[spec_l]
        return
    if spec_l in vessels_by_name:
        antenna.target_vessel = vessels_by_name[spec_l]
        return
    log.warning("Unknown antenna target %r", spec)


def setup_network(
    session: Session,
    vessels: Sequence[Any],
    plan: AntennaPlan,
    *,
    home_body: str | None = None,
) -> None:
    """Legacy RemoteTech targeting. Prefer :func:`commission_network` on RP-1."""
    if session.remote_tech is None:
        commission_network(session, vessels)
        return
    session.require_connected()
    if not vessels:
        return
    home = home_body or session.home_body.name
    vessels_by_name = {v.name: v for v in session.space_center.vessels}

    for vessel in vessels:
        session.switch_to(vessel)
        deploy_antennas(vessel)
        nearest = two_nearest(vessel, vessels)
        for part_name, targets in plan.items():
            parts = list(vessel.parts.with_name(part_name))
            if not parts:
                log.warning("%s has no part named %s", vessel.name, part_name)
                continue
            if targets == "setup_network":
                for i, part in enumerate(parts):
                    _aim_setup(session, part, i, home, nearest)
            else:
                for i, part in enumerate(parts):
                    if i >= len(targets):
                        break
                    antenna = session.require_remotetech().antenna(part)
                    set_rt_target(
                        session, antenna, str(targets[i]), vessels_by_name=vessels_by_name
                    )


def commission_network(
    session: Session,
    vessels: Sequence[Any],
    *,
    on_log: Any | None = None,
) -> CoverageReport:
    """Deploy, inventory RA, read CommNet coverage. No RT targeting."""
    say = on_log or (lambda msg: log.info(msg))
    commission(session, vessels, on_log=say)
    return coverage_report(session, vessels, switch=True)


def _aim_setup(
    session: Session,
    part: Any,
    index: int,
    home: str,
    nearest: Sequence[Any],
) -> None:
    rt = session.require_remotetech()
    antenna = rt.antenna(part)
    if index == 0:
        antenna.target_body = session.bodies[home]
        return
    mate = nearest[index - 1] if index - 1 < len(nearest) else None
    if mate is None:
        log.warning("No neighbour for antenna %s on %s", part.name, part.vessel.name)
        return
    antenna.target_vessel = mate


def find_constellation(session: Session, name: str, *, exact: bool = False) -> list[Any]:
    return [v for v, _s in list_vessels(session, name=name, exact=exact)]
