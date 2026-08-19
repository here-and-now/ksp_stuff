"""Vessel snapshots and name search. No pandas — a list of dataclasses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from session import Session


@dataclass(slots=True)
class VesselSnapshot:
    name: str
    type: str
    situation: str
    body: str
    apoapsis: float
    periapsis: float
    inclination_deg: float
    eccentricity: float
    period: float
    crew: int
    loaded: bool
    comms: str
    met: float

    def as_row(self) -> tuple[object, ...]:
        return (
            self.name,
            self.type,
            self.situation,
            self.body,
            round(self.apoapsis),
            round(self.periapsis),
            round(self.inclination_deg, 3),
            f"{self.eccentricity:.5f}",
            round(self.period, 2),
            self.crew,
            self.comms,
        )


COLUMNS = (
    "Name",
    "Type",
    "Situation",
    "Body",
    "Apoapsis",
    "Periapsis",
    "Incl °",
    "Ecc",
    "Period s",
    "Crew",
    "Comms",
)


def _enum_name(value: Any) -> str:
    return getattr(value, "name", str(value))


def _comms_summary(session: Session, vessel: Any) -> str:
    try:
        comms = vessel.comms
        if comms.can_communicate:
            return f"CN {comms.signal_strength:.2f}"
        return "CN no link"
    except Exception:
        pass
    if session.remote_tech is not None:
        try:
            comms = session.remote_tech.comms(vessel)
            if comms.has_connection:
                return f"RT delay {comms.signal_delay:.2f}s"
            return "RT no link"
        except Exception:
            pass
    return "—"


def snapshot(session: Session, vessel: Any) -> VesselSnapshot:
    orbit = vessel.orbit
    try:
        body = orbit.body.name
    except Exception:
        body = "?"
    try:
        inc = orbit.inclination * (180.0 / 3.141592653589793)
    except Exception:
        inc = 0.0
    return VesselSnapshot(
        name=vessel.name,
        type=_enum_name(vessel.type),
        situation=_enum_name(vessel.situation),
        body=body,
        apoapsis=float(orbit.apoapsis_altitude),
        periapsis=float(orbit.periapsis_altitude),
        inclination_deg=inc,
        eccentricity=float(orbit.eccentricity),
        period=float(orbit.period),
        crew=int(getattr(vessel, "crew_count", 0) or 0),
        loaded=bool(getattr(vessel, "loaded", False)),
        comms=_comms_summary(session, vessel),
        met=float(getattr(vessel, "met", 0.0) or 0.0),
    )


_CLUTTER_TYPES = {"debris", "flag", "dropped_part", "space_object"}


def list_vessels(
    session: Session,
    name: str | None = None,
    *,
    exact: bool = False,
    vessels: Iterable[Any] | None = None,
    skip_clutter: bool = True,
) -> list[tuple[Any, VesselSnapshot]]:
    session.require_connected()
    pool = list(vessels) if vessels is not None else list(session.space_center.vessels)
    if name:
        if exact:
            pool = [v for v in pool if v.name == name]
        else:
            needle = name.lower()
            pool = [v for v in pool if needle in v.name.lower()]
    out: list[tuple[Any, VesselSnapshot]] = []
    for vessel in pool:
        try:
            snap = snapshot(session, vessel)
        except Exception:
            continue
        if skip_clutter and snap.type.lower() in _CLUTTER_TYPES:
            continue
        out.append((vessel, snap))
    return out


def find_by_name(session: Session, name: str, *, exact: bool = True) -> list[Any]:
    rows = list_vessels(session, name=name, exact=exact)
    return [vessel for vessel, _snap in rows]
