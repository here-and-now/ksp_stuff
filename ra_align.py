"""Stamp live RealAntennas TL from the owned tree. Disk catalog is cfg; RAM is GSTL."""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("kspstuff")


def owned_comms_tl(world: Any | None = None) -> int:
    if world is None:
        from world import load_world

        world = load_world()
    from comms_catalog import load_comms_catalog

    return int(load_comms_catalog(world).owned_tl or 0)


def align_live(session: Any, world: Any | None = None) -> bool:
    """Set RA GSTL + difficulty cap to owned comms TL. No-op if kRPC/RA missing."""
    conn = getattr(session, "conn", None)
    ra = getattr(conn, "real_antennas", None) if conn is not None else None
    if ra is None:
        return False
    try:
        if not bool(getattr(ra, "available", False)):
            return False
    except Exception:
        return False
    try:
        tl = owned_comms_tl(world)
    except Exception as exc:
        log.warning("RA align: owned TL (%s)", exc)
        return False
    fn = getattr(ra, "align_tech_level", None)
    if not callable(fn):
        gstl = getattr(ra, "ground_station_tech_level", None)
        if gstl is None:
            return False
        try:
            ra.ground_station_tech_level = tl
            return True
        except Exception as exc:
            log.warning("RA align GSTL (%s)", exc)
            return False
    try:
        fn(tl)
        log.info("RA align tech level %s", tl)
        return True
    except Exception as exc:
        log.warning("RA align_tech_level (%s)", exc)
        return False
