"""Relay constellations: layers, resonant dump, phasing, CommNet commission.

Deploy from one launcher still uses a resonant orbit (``n-1 : n``). After
that the object is a *layer* (MEO VHF, GEO, polar Walker), not a RemoteTech
triangle of dishes. ``setup_comms`` deploys RA/stock antennas and reads
coverage; it only runs the old RT targeting loop if RemoteTech is actually
loaded and an antenna plan is set.
"""

from __future__ import annotations

import logging
import math
import operator
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from comms import AntennaPlan, commission_network, find_constellation, setup_network
from geometry import angle_delta_deg, geosynchronous_altitude, resonance_for_count, walker_slots, wrap_degrees
from nodes import _make_nodes, execute_node
from orientation import apply_smartass, orientate_vessel
from parts import (
    control_from_command_pod,
    deploy_antennas,
    deploy_solar,
    enable_engines,
    enable_rcs_fore_by_throttle,
    retract_solar,
)
from session import Session
from vessels import VesselSnapshot, snapshot

log = logging.getLogger("kspstuff")


@dataclass(frozen=True, slots=True)
class NetworkLayer:
    """A named relay shell. Geometry, not a targeting plan.

    Early RP-1 is VHF/UHF omnis in MEO. Later you add GEO dishes on S/X
    that default-aim at Earth. CommNet routes; we just put the birds in
    the right slots.
    """

    key: str
    title: str
    count: int
    planes: int
    altitude: float | None
    geosync: bool
    inclination_deg: float
    band: str
    notes: str


LAYERS: dict[str, NetworkLayer] = {
    "meo4": NetworkLayer(
        key="meo4",
        title="Earth MEO ×4 VHF (early RP-1)",
        count=4,
        planes=1,
        altitude=3_400_000,
        geosync=False,
        inclination_deg=28.6,
        band="VHF",
        notes="RA wiki example: ~3400 km, omnis, no dish pointing. Covers LEO.",
    ),
    "geo3": NetworkLayer(
        key="geo3",
        title="Earth GEO ×3",
        count=3,
        planes=1,
        altitude=None,
        geosync=True,
        inclination_deg=0.0,
        band="S",
        notes="120° slots, sidereal-day period. Dishes default to Earth centre.",
    ),
    "polar6": NetworkLayer(
        key="polar6",
        title="Polar LEO 6/3 Walker",
        count=6,
        planes=3,
        altitude=800_000,
        geosync=False,
        inclination_deg=90.0,
        band="UHF",
        notes="Two sats per plane. Fill one plane per launch in career.",
    ),
}


@dataclass(slots=True)
class ConstellationConfig:
    name: str = ""
    satellite_count: int = 3
    resonance_numerator: int = 2
    resonance_denominator: int = 3
    release_spacing_s: float = 5.0
    home_antenna_parts: tuple[str, ...] = (
        "restock-relay-radial-2.v2",
        "RTLongAntenna2",
        "HighGainAntenna",
    )
    antenna_plan: AntennaPlan = field(default_factory=dict)
    layer: str = "meo4"


def apply_layer(config: ConstellationConfig, layer: NetworkLayer) -> None:
    config.satellite_count = layer.count
    config.resonance_numerator, config.resonance_denominator = resonance_for_count(
        layer.count
    )
    config.layer = layer.key


class Constellation:
    def __init__(
        self,
        session: Session,
        config: ConstellationConfig | None = None,
        *,
        on_log: Callable[[str], None] | None = None,
        abort: Callable[[], bool] | None = None,
    ) -> None:
        self.session = session
        self.config = config or ConstellationConfig()
        self.on_log = on_log or (lambda msg: log.info(msg))
        self.abort = abort or (lambda: False)
        self.vessels: list[Any] = []

    def _say(self, message: str) -> None:
        log.info(message)
        self.on_log(message)

    def use_active(self) -> None:
        self.vessels = [self.session.active_vessel]
        if not self.config.name:
            self.config.name = self.vessels[0].name

    def load_existing(self, name: str | None = None, *, exact: bool = False) -> list[Any]:
        needle = name or self.config.name
        if not needle:
            raise ValueError("Constellation name is empty")
        self.config.name = needle
        self.vessels = find_constellation(self.session, needle, exact=exact)
        self._say(f"{len(self.vessels)} vessels matching {needle!r}")
        return self.vessels

    def snapshots(self) -> list[tuple[Any, VesselSnapshot]]:
        return [(v, snapshot(self.session, v)) for v in self.vessels]

    def resonant_orbit(self) -> None:
        mj = self.session.require_mechjeb()
        op = mj.maneuver_planner.operation_resonant_orbit
        op.resonance_numerator = self.config.resonance_numerator
        op.resonance_denominator = self.config.resonance_denominator
        op.time_selector.time_reference = mj.TimeReference.x_from_now
        op.time_selector.lead_time = 30
        _make_nodes(op)
        self._say(
            f"Resonant orbit {self.config.resonance_numerator}:"
            f"{self.config.resonance_denominator}"
        )
        execute_node(self.session, all_nodes=True, abort=self.abort)

    def release_all(self, count: int | None = None, spacing: float | None = None) -> list[Any]:
        session = self.session
        mothership = session.active_vessel
        n = count if count is not None else self.config.satellite_count
        gap = spacing if spacing is not None else self.config.release_spacing_s
        retract_solar(mothership)
        try:
            apply_smartass(session, "normal_minus")
        except Exception:
            log.debug("SmartASS anti-normal failed", exc_info=True)
        time.sleep(gap)
        released: list[Any] = []
        for i in range(n):
            if self.abort():
                break
            spawned = mothership.control.activate_next_stage()
            if spawned:
                released.append(spawned[0])
                self._say(f"Released {spawned[0].name} ({i + 1}/{n})")
            time.sleep(gap)
        self._say("Waiting for a clean separation")
        time.sleep(max(10.0, gap * 2))
        self.vessels = released
        self.prepare_vessels(released)
        return released

    def prepare_vessels(self, vessels: Sequence[Any] | None = None) -> None:
        session = self.session
        home = session.home_body
        for vessel in vessels if vessels is not None else self.vessels:
            if self.abort():
                return
            session.switch_to(vessel)
            control_from_command_pod(vessel)
            enable_engines(vessel)
            deploy_antennas(vessel)
            deploy_solar(vessel)
            if session.remote_tech is not None:
                for part_name in self.config.home_antenna_parts:
                    for part in vessel.parts.with_name(part_name):
                        try:
                            session.remote_tech.antenna(part).target_body = home
                        except Exception:
                            continue
            try:
                apply_smartass(session, "node")
            except Exception:
                pass
            self._say(f"Prepared {vessel.name}")

    def recircularize_staggered(self) -> None:
        session = self.session
        mj = session.require_mechjeb()
        recirc = mj.maneuver_planner.operation_circularize
        if self.config.resonance_numerator > self.config.resonance_denominator:
            recirc.time_selector.time_reference = mj.TimeReference.periapsis
        else:
            recirc.time_selector.time_reference = mj.TimeReference.apoapsis

        for i, vessel in enumerate(self.vessels):
            session.switch_to(vessel)
            nodes = _make_nodes(recirc)
            if nodes:
                nodes[0].ut = nodes[0].ut + vessel.orbit.period * i

        ordered = sorted(self.vessels, key=lambda v: _next_node_time(v))
        for vessel in ordered:
            try:
                apply_smartass(session, "node")
            except Exception:
                pass
        for vessel in ordered:
            if self.abort():
                return
            session.switch_to(vessel)
            self._say(f"Circularizing {vessel.name}")
            self._exec_burn(vessel)

    def _exec_burn(self, vessel: Any) -> None:
        engines = [e for e in vessel.parts.engines if e.active]
        if not engines:
            enable_rcs_fore_by_throttle(vessel)
            self._say(f"RCS burn on {vessel.name}")
        execute_node(self.session, vessel, abort=self.abort)

    def fine_tune_period(self, deadband: float = 0.05, timeout: float = 120.0) -> None:
        """RCS nudge each sat toward the constellation mean period."""
        session = self.session
        if len(self.vessels) < 2:
            raise RuntimeError("Need at least two satellites to match periods")
        mean = sum(v.orbit.period for v in self.vessels) / len(self.vessels)
        self._say(f"Mean period {mean:.3f} s")

        for vessel in self.vessels:
            session.switch_to(vessel)
            vessel.control.rcs = False
            if vessel.orbit.period < mean:
                mode, direction, cmp = "prograde", "prograde", operator.lt
            else:
                mode, direction, cmp = "retrograde", "retrograde", operator.gt
            try:
                apply_smartass(session, mode, force_roll=True)
            except Exception:
                pass
            orientate_vessel(session, vessel, direction, accuracy=1e-3, timeout=30)

        for vessel in self.vessels:
            if self.abort():
                return
            session.switch_to(vessel)
            before = vessel.orbit.period
            if before < mean:
                cmp = operator.lt
            else:
                cmp = operator.gt
            deadline = time.monotonic() + timeout
            while cmp(vessel.orbit.period, mean) and time.monotonic() < deadline:
                if abs(vessel.orbit.period - mean) <= deadband:
                    break
                vessel.control.rcs = True
                vessel.control.throttle = 0.01
                time.sleep(0.05)
            vessel.control.rcs = False
            vessel.control.throttle = 0.0
            self._say(
                f"{vessel.name}: period {before:.4f} → {vessel.orbit.period:.4f} s"
            )

    def setup_comms(self, plan: AntennaPlan | None = None) -> None:
        plan = plan if plan is not None else self.config.antenna_plan
        if self.session.remote_tech is not None and plan:
            setup_network(self.session, self.vessels, plan)
            return
        commission_network(self.session, self.vessels, on_log=self._say)

    def layer_altitude(self, layer: NetworkLayer) -> float:
        if not layer.geosync:
            return float(layer.altitude or 0.0)
        body = self.session.home_body
        return geosynchronous_altitude(
            body.gravitational_parameter,
            body.equatorial_radius,
            body.rotational_period,
        )

    def spacing_report(self, layer: NetworkLayer | None = None) -> list[str]:
        """How far the current birds are from the ideal Walker / GEO slots."""
        layer = layer or LAYERS.get(self.config.layer)
        if layer is None:
            return ["No layer selected"]
        if not self.vessels:
            return ["No vessels loaded"]
        try:
            slots = walker_slots(layer.count, layer.planes)
        except ValueError as exc:
            return [str(exc)]
        lines = [
            f"{layer.title}: {layer.count} slots, {layer.planes} plane(s), "
            f"band {layer.band}, {layer.notes}"
        ]
        if layer.geosync:
            alt = self.layer_altitude(layer)
            lines.append(f"Geosync altitude ≈ {alt/1000:.0f} km")
        occupied: list[tuple[float, float, str]] = []
        for vessel in self.vessels:
            try:
                orbit = vessel.orbit
                raan = wrap_degrees(orbit.longitude_of_ascending_node * 180.0 / math.pi)
                ma = wrap_degrees(orbit.mean_anomaly * 180.0 / math.pi)
                occupied.append((raan, ma, vessel.name))
            except Exception:
                continue
        used: set[int] = set()
        for raan, ma, name in occupied:
            best_i, best = 0, 1e9
            for i, (s_raan, s_ma) in enumerate(slots):
                if i in used:
                    continue
                err = abs(angle_delta_deg(raan, s_raan)) + abs(angle_delta_deg(ma, s_ma))
                if err < best:
                    best_i, best = i, err
            used.add(best_i)
            s_raan, s_ma = slots[best_i]
            lines.append(
                f"{name}: slot {best_i + 1}  ΔRAAN {angle_delta_deg(raan, s_raan):+.1f}°  "
                f"ΔM {angle_delta_deg(ma, s_ma):+.1f}°"
            )
        empty = [i for i in range(len(slots)) if i not in used]
        if empty:
            lines.append(
                "Empty slots: "
                + ", ".join(f"{i + 1} (Ω={slots[i][0]:.0f}° M={slots[i][1]:.0f}°)" for i in empty)
            )
        return lines


def _next_node_time(vessel: Any) -> float:
    nodes = vessel.control.nodes
    if not nodes:
        return float("inf")
    return float(nodes[0].time_to)
