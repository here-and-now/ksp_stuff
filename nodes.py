"""Maneuver nodes: MechJeb executor with a kRPC autopilot fallback."""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Callable

from geometry import burn_time, circularize_delta_v
from orientation import set_autopilot
from parts import enable_rcs_fore_by_throttle
from session import Session
from warp import in_atmosphere, warp_to_ut

log = logging.getLogger("kspstuff")


@dataclass(slots=True)
class NodeSnapshot:
    ut: float
    time_to: float
    remaining_dv: float
    prograde: float
    normal: float
    radial: float


def list_nodes(vessel: Any) -> list[Any]:
    return list(vessel.control.nodes)


def snapshot_node(node: Any) -> NodeSnapshot:
    return NodeSnapshot(
        ut=float(node.ut),
        time_to=float(node.time_to),
        remaining_dv=float(node.remaining_delta_v),
        prograde=float(node.prograde),
        normal=float(node.normal),
        radial=float(node.radial),
    )


def plan_circularize_at_apoapsis(session: Session, vessel: Any | None = None) -> Any:
    """Vis-viva circularization node. Works without MechJeb."""
    session.require_connected()
    vessel = vessel or session.active_vessel
    orbit = vessel.orbit
    delta_v = circularize_delta_v(
        orbit.body.gravitational_parameter,
        orbit.apoapsis,
        orbit.semi_major_axis,
    )
    node = vessel.control.add_node(
        session.space_center.ut + orbit.time_to_apoapsis,
        prograde=delta_v,
    )
    log.info("Circularize node Δv=%.2f m/s", delta_v)
    return node


def plan_circularize_at_periapsis(session: Session, vessel: Any | None = None) -> Any:
    """Vis-viva circularization at periapsis (capture burns)."""
    session.require_connected()
    vessel = vessel or session.active_vessel
    orbit = vessel.orbit
    delta_v = circularize_delta_v(
        orbit.body.gravitational_parameter,
        orbit.periapsis,
        orbit.semi_major_axis,
    )
    node = vessel.control.add_node(
        session.space_center.ut + orbit.time_to_periapsis,
        prograde=delta_v,
    )
    log.info("Circularize@Pe node Δv=%.2f m/s", delta_v)
    return node


def estimate_burn_time(vessel: Any, delta_v: float) -> float:
    return burn_time(
        delta_v,
        vessel.available_thrust,
        vessel.specific_impulse,
        vessel.mass,
    )


def execute_node(
    session: Session,
    vessel: Any | None = None,
    *,
    tolerance: float = 0.01,
    lead_time: float = 5.0,
    all_nodes: bool = False,
    abort: Callable[[], bool] | None = None,
    on_log: Callable[[str], None] | None = None,
    watch: Any | None = None,
    stop_if: Callable[[], bool] | None = None,
) -> None:
    """MechJeb node executor when present, otherwise a simple burn loop."""
    session.require_connected()
    vessel = vessel or session.active_vessel
    if session.mech_jeb is not None:
        _execute_mechjeb(
            session,
            tolerance=tolerance,
            lead_time=lead_time,
            all_nodes=all_nodes,
            abort=abort,
        )
        return
    _execute_fallback(
        session,
        vessel,
        lead_time=lead_time,
        abort=abort,
        on_log=on_log,
        watch=watch,
        stop_if=stop_if,
    )


def _execute_mechjeb(
    session: Session,
    *,
    tolerance: float,
    lead_time: float,
    all_nodes: bool,
    abort: Callable[[], bool] | None,
) -> None:
    executor = session.mech_jeb.node_executor
    executor.tolerance = tolerance
    executor.lead_time = lead_time
    if all_nodes:
        executor.execute_all_nodes()
    else:
        executor.execute_one_node()
    enabled = session.conn.stream(getattr, executor, "enabled")
    enabled.rate = 2
    try:
        with enabled.condition:
            while enabled():
                if abort and abort():
                    try:
                        executor.abort()
                    except Exception:
                        pass
                    raise RuntimeError("Node execution aborted")
                enabled.wait(timeout=0.5)
    finally:
        try:
            enabled.remove()
        except Exception:
            pass


def _execute_fallback(
    session: Session,
    vessel: Any,
    *,
    lead_time: float,
    abort: Callable[[], bool] | None,
    on_log: Callable[[str], None] | None = None,
    watch: Any | None = None,
    stop_if: Callable[[], bool] | None = None,
) -> None:
    from watch import FlightWatch, heartbeat

    nodes = vessel.control.nodes
    if not nodes:
        raise RuntimeError("No maneuver node to execute")
    node = nodes[0]
    remaining = node.remaining_delta_v
    duration = estimate_burn_time(vessel, remaining)
    warp_ut = node.ut - duration / 2.0 - lead_time
    time_to = float(node.time_to)
    own = watch is None
    if own:
        watch = FlightWatch(session, on_log=on_log, uplink=True)
    try:
        if time_to > max(duration / 2.0, 30.0) + lead_time:
            # Rails illegal in atmo (L-005/L-012). Coast at 1x until out,
            # then warp to the node — aborting wastes a circularize-at-apo
            # that is still minutes away (L-019).
            while in_atmosphere(vessel):
                if abort and abort():
                    raise RuntimeError("Node execution aborted")
                heartbeat(session, tag="node-atmo ", on_log=on_log, watch=watch)
                time.sleep(1.0)
            warp_to_ut(
                session,
                max(warp_ut, session.space_center.ut + 1.0),
                abort=abort,
                watch=watch,
                stop_if=stop_if,
            )

        ap = vessel.auto_pilot
        ap.reference_frame = vessel.orbital_reference_frame
        set_autopilot(ap, True)
        ap.target_direction = node.remaining_burn_vector(vessel.orbital_reference_frame)
        try:
            ap.wait()
        except Exception:
            time.sleep(2.0)

        engines = [e for e in vessel.parts.engines if e.active]
        if not engines:
            enable_rcs_fore_by_throttle(vessel)

        last_remaining = remaining
        vessel.control.throttle = 1.0
        while node.remaining_delta_v > 0.5:
            if abort and abort():
                break
            state = watch.pulse("node ")
            from uplink import holding

            if holding():
                from watch import apply_hold

                apply_hold(session)
                continue
            if float(getattr(vessel, "available_thrust", 0) or 0) <= 0:
                if watch.relight(end_stage=0):
                    vessel.control.throttle = 1.0
                    continue
                bound = (
                    (not state.escaping)
                    and math.isfinite(state.peri)
                    and state.peri >= 12_000
                )
                fueled = state.lf > 0 or state.ox > 0
                if bound and fueled:
                    log.info("node flame — bound, stopping for relight")
                    vessel.control.throttle = 0.0
                    watch.pulse("node-flame ", force_log=True)
                    break
                from watch import MissionAbort

                raise MissionAbort("no thrust during node")
            remaining = node.remaining_delta_v
            if remaining > last_remaining + 5.0:
                log.info("node remaining Δv rose (%.1f → %.1f) — stopping", last_remaining, remaining)
                break
            last_remaining = remaining
            # Overburn into an escape on a circularize/capture.
            if state.escaping and remaining < 20.0:
                log.info("node stopped — escaping with %.1f m/s left", remaining)
                break
            twr = vessel.max_thrust / max(vessel.mass, 1.0)
            if remaining < twr / 3:
                vessel.control.throttle = 0.05
            elif remaining < twr / 2:
                vessel.control.throttle = 0.1
            elif remaining < twr:
                vessel.control.throttle = 0.25
            else:
                vessel.control.throttle = 1.0
            try:
                ap.target_direction = node.remaining_burn_vector(
                    vessel.orbital_reference_frame
                )
            except Exception:
                pass
        vessel.control.throttle = 0.0
        set_autopilot(ap, False)
        try:
            node.remove()
        except Exception:
            pass
        watch.pulse("node-done ", force_log=True)
    finally:
        if own:
            watch.close()


def plan_and_execute_mj_circularize(
    session: Session,
    *,
    at_apoapsis: bool = True,
    abort: Callable[[], bool] | None = None,
) -> None:
    mj = session.require_mechjeb()
    op = mj.maneuver_planner.operation_circularize
    op.time_selector.time_reference = (
        mj.TimeReference.apoapsis if at_apoapsis else mj.TimeReference.periapsis
    )
    _make_nodes(op)
    execute_node(session, abort=abort)


def _make_nodes(operation: Any) -> list[Any]:
    if hasattr(operation, "make_nodes"):
        return list(operation.make_nodes())
    node = operation.make_node()
    return [node]


def mj_change_inclination(session: Session, degrees: float) -> None:
    mj = session.require_mechjeb()
    op = mj.maneuver_planner.operation_inclination
    op.new_inclination = degrees
    _make_nodes(op)
    execute_node(session)


def mj_set_apoapsis(session: Session, altitude: float) -> None:
    mj = session.require_mechjeb()
    op = mj.maneuver_planner.operation_apoapsis
    op.new_apoapsis = altitude
    _make_nodes(op)
    execute_node(session)


def set_altitude_and_circularize(
    session: Session,
    desired_inclination: float,
    desired_altitude: float,
    vessel: Any | None = None,
) -> None:
    """Old Orbit.set_altitude_and_circularize, without a new connection."""
    session.require_connected()
    vessel = vessel or session.active_vessel
    orbit = vessel.orbit
    inc_deg = orbit.inclination * (180.0 / math.pi)
    if abs(inc_deg - desired_inclination) > 0.05:
        mj_change_inclination(session, desired_inclination)
    if orbit.apoapsis_altitude < desired_altitude:
        mj_set_apoapsis(session, desired_altitude)
    if orbit.eccentricity > 0.001:
        plan_and_execute_mj_circularize(session, at_apoapsis=True)
