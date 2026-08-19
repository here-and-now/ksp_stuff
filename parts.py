"""Part-module helpers: engines, staging, fairings, solar, antennas."""

from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping

log = logging.getLogger("kspstuff")

# Events tried in order when kRPC's high-level property is missing.
_ANTENNA_ACTIONS: tuple[tuple[str, str], ...] = (
    ("ModuleRTAntenna", "Activate"),
    ("ModuleDeployableAntenna", "Extend Antenna"),
    ("ModuleDeployableAntenna", "Extend"),
)
_FAIRING_EVENTS = ("Jettison Fairing", "Jettison")


def manipulate_engines(
    vessel: Any,
    engine_name: str,
    actions: Mapping[str, Any] | None = None,
) -> list[Any]:
    """Toggle / limit engines whose ``part.name`` matches ``engine_name``."""
    matched: list[Any] = []
    actions = actions or {}
    for engine in vessel.parts.engines:
        if engine.part.name != engine_name:
            continue
        if "active" in actions:
            engine.active = bool(actions["active"])
        if "thrust_limit" in actions:
            engine.thrust_limit = float(actions["thrust_limit"])
        if "gimbal_limit" in actions:
            engine.gimbal_limit = float(actions["gimbal_limit"])
        matched.append(engine)
        log.info("Engine %s active=%s", engine.part.name, engine.active)
    return matched


def decouple_by_name(vessel: Any, decoupler_name: str) -> list[Any]:
    fired: list[Any] = []
    for decoupler in vessel.parts.decouplers:
        if decoupler.part.name == decoupler_name:
            decoupler.decouple()
            fired.append(decoupler)
            log.info("Decoupled %s on %s", decoupler.part.name, vessel.name)
    return fired


def deploy_solar(vessel: Any) -> int:
    n = 0
    for panel in vessel.parts.solar_panels:
        try:
            if not panel.deployed:
                panel.deployed = True
                n += 1
        except Exception:
            log.debug("Solar deploy failed on %s", panel, exc_info=True)
    return n


def retract_solar(vessel: Any) -> int:
    n = 0
    for panel in vessel.parts.solar_panels:
        try:
            if panel.deployed:
                panel.deployed = False
                n += 1
        except Exception:
            log.debug("Solar retract failed on %s", panel, exc_info=True)
    return n


def jettison_fairings(vessel: Any) -> int:
    n = 0
    for fairing in vessel.parts.fairings:
        try:
            fairing.jettison()
            n += 1
            continue
        except Exception:
            pass
        for module in fairing.part.modules:
            for event in _FAIRING_EVENTS:
                try:
                    if module.has_event(event):
                        module.trigger_event(event)
                        n += 1
                        break
                except Exception:
                    continue
    return n


def deploy_antennas(vessel: Any) -> int:
    """Stock/CommNet deploy plus RemoteTech module actions."""
    n = 0
    try:
        for antenna in vessel.parts.antennas:
            if getattr(antenna, "deployable", False) and not antenna.deployed:
                antenna.deployed = True
                n += 1
    except Exception:
        log.debug("vessel.parts.antennas failed", exc_info=True)

    for part in vessel.parts.all:
        for module in part.modules:
            for module_name, action in _ANTENNA_ACTIONS:
                if module.name != module_name:
                    continue
                try:
                    module.set_action(action)
                    n += 1
                except Exception:
                    try:
                        if module.has_event(action):
                            module.trigger_event(action)
                            n += 1
                    except Exception:
                        continue
    return n


def control_from_command_pod(vessel: Any) -> bool:
    try:
        parts = vessel.parts.with_module("ModuleCommand")
    except Exception:
        return False
    for part in parts:
        for module in part.modules:
            if module.name != "ModuleCommand":
                continue
            try:
                if module.has_event("Control From Here"):
                    module.trigger_event("Control From Here")
                    return True
            except Exception:
                continue
    return False


def enable_engines(vessel: Any) -> None:
    for engine in vessel.parts.engines:
        try:
            engine.active = True
        except Exception:
            continue


def enable_rcs_fore_by_throttle(vessel: Any) -> None:
    """RO/probe trick: RCS translation follows the throttle axis."""
    vessel.control.rcs = True
    for rcs in vessel.parts.rcs:
        try:
            rcs.enabled = True
            rcs.fore_by_throttle = True
        except Exception:
            continue


def ullage(vessel: Any, seconds: float = 2.0) -> None:
    """RO engines often need a ullage pulse before ignition. Best-effort."""
    enable_rcs_fore_by_throttle(vessel)
    vessel.control.throttle = 0.05
    import time

    time.sleep(max(0.0, seconds))
    vessel.control.throttle = 0.0


def stage_resources(vessel: Any, decouple_stage: int) -> Any | None:
    """Resources dumped by the next decouple. Prefers kRPC 0.6 Stage API."""
    try:
        stage = vessel.decouple_stage_at(decouple_stage)
        return stage.resources()
    except Exception:
        pass
    try:
        return vessel.resources_in_decouple_stage(decouple_stage, cumulative=False)
    except Exception:
        log.debug("Could not read decouple-stage resources", exc_info=True)
        return None


def should_stage(
    vessel: Any,
    fuels: Iterable[str],
    end_stage: int,
) -> bool:
    """True when the current decouple stage is dry or is an empty interstage."""
    current = vessel.control.current_stage
    if current <= end_stage:
        return False
    resources = stage_resources(vessel, current - 1)
    if resources is None:
        return False

    fuel_list = list(fuels)
    amounts: list[tuple[float, float]] = []
    for name in fuel_list:
        try:
            amounts.append((resources.amount(name), resources.max(name)))
        except Exception:
            continue

    if not amounts:
        return False
    # Ignore fuels the stage cannot hold. A parachute-only stage reports
    # amount=0/max=0 and must not count as "dry tanks".
    carried = [(amount, maximum) for amount, maximum in amounts if maximum > 0]
    if not carried:
        return False
    return all(amount < 1 for amount, _maximum in carried)


def print_parts(vessel: Any, kind: str = "all") -> None:
    if kind in ("all", "parts"):
        for part in vessel.parts.all:
            print(part.name)
    if kind in ("all", "engines"):
        for engine in vessel.parts.engines:
            print(f"engine {engine.part.name} active={engine.active}")
    if kind in ("all", "resources"):
        for resource in vessel.resources.all:
            print(resource.name)
