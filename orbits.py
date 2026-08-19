"""Orbit helpers kept next to the old Orbit / OrbitManager names."""

from __future__ import annotations

from typing import Any, Sequence

from nodes import set_altitude_and_circularize
from session import Session
from vessels import snapshot

__all__ = ["mean_period", "set_altitude_and_circularize", "period_spread"]


def mean_period(vessels: Sequence[Any]) -> float:
    if not vessels:
        return 0.0
    return sum(v.orbit.period for v in vessels) / len(vessels)


def period_spread(session: Session, vessels: Sequence[Any]) -> list[tuple[str, float, float]]:
    if not vessels:
        return []
    mean = mean_period(vessels)
    rows = []
    for vessel in vessels:
        snap = snapshot(session, vessel)
        rows.append((snap.name, snap.period, snap.period - mean))
    return rows
