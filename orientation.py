"""Wait until the vessel is pointing at a named flight vector."""

from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

log = logging.getLogger("kspstuff")


def set_autopilot(ap: Any, engaged: bool) -> None:
    """kRPC 0.6 uses ``engaged``; 0.5 used ``engage()`` / ``disengage()``."""
    if hasattr(ap, "engage"):
        if engaged:
            ap.engage()
        else:
            ap.disengage()
        return
    ap.engaged = engaged


def autopilot_error(ap: Any) -> float | None:
    """Attitude error in degrees, or None if the autopilot is not engaged.

    kRPC raises ``RuntimeError: The auto-pilot is not engaged`` on
    ``error`` / ``pitch_error`` / ``heading_error`` (and the ``current_*``
    variants) while ``engaged`` is false.
    """
    try:
        if not ap.engaged:
            return None
        return float(ap.error)
    except Exception:
        return None


def wait_aligned(ap: Any, *, timeout: float = 8.0, max_error: float = 20.0) -> bool:
    """Block until AP error is under ``max_error`` degrees. False on timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        err = autopilot_error(ap)
        if err is not None and err <= max_error:
            return True
        time.sleep(0.05)
    return False

SAS_MODES = {
    "prograde": "prograde",
    "retrograde": "retrograde",
    "normal": "normal",
    "anti_normal": "anti_normal",
    "anti-normal": "anti_normal",
    "normal_minus": "anti_normal",
    "radial": "radial",
    "anti_radial": "anti_radial",
    "anti-radial": "anti_radial",
    "target": "target",
    "node": "maneuver",
    "maneuver": "maneuver",
}

SMARTASS = {
    "prograde": "prograde",
    "retrograde": "retrograde",
    "normal": "normal",
    "normal_plus": "normal_plus",
    "anti_normal": "normal_minus",
    "anti-normal": "normal_minus",
    "normal_minus": "normal_minus",
    "radial": "radial_plus",
    "radial_plus": "radial_plus",
    "anti_radial": "radial_minus",
    "radial_minus": "radial_minus",
    "node": "node",
    "target": "target_plus",
}


def apply_smartass(session: Any, mode: str, force_roll: bool = False) -> None:
    mj = session.require_mechjeb()
    attr = SMARTASS.get(mode, mode)
    mj.smart_ass.autopilot_mode = getattr(mj.SmartASSAutopilotMode, attr)
    mj.smart_ass.force_roll = force_roll
    mj.smart_ass.update(False)


def orientate_vessel(
    session: Any,
    vessel: Any,
    orientation: str,
    accuracy: float = 1e-2,
    timeout: float = 60.0,
    *,
    use_sas: bool = False,
) -> bool:
    """Block until ``vessel.flight().direction`` matches the named vector."""
    conn = session.conn
    sc = session.space_center
    if use_sas:
        sas_attr = SAS_MODES.get(orientation)
        if sas_attr is None:
            raise ValueError(f"Unknown SAS orientation {orientation!r}")
        vessel.control.sas = True
        vessel.control.sas_mode = getattr(sc.SASMode, sas_attr)

    if orientation in ("node", "maneuver"):
        nodes = vessel.control.nodes
        if not nodes:
            raise RuntimeError("No maneuver node to point at")
        frame = vessel.reference_frame
        direction = conn.add_stream(vessel.direction, frame)
        target = conn.add_stream(nodes[0].remaining_burn_vector, frame)
    else:
        attr = {
            "anti_normal": "anti_normal",
            "anti-normal": "anti_normal",
            "normal_minus": "anti_normal",
        }.get(orientation, orientation)
        flight = vessel.flight()
        direction = conn.add_stream(getattr, flight, "direction")
        target = conn.add_stream(getattr, flight, attr)

    deadline = time.monotonic() + timeout
    aligned = False
    try:
        while time.monotonic() < deadline:
            delta = np.abs(np.subtract(direction(), target()))
            if bool(np.all(delta < accuracy)):
                aligned = True
                break
            time.sleep(0.05)
    finally:
        try:
            direction.remove()
        except Exception:
            pass
        try:
            target.remove()
        except Exception:
            pass
    if not aligned:
        log.warning("Orientation %s timed out on %s", orientation, vessel.name)
    return aligned
