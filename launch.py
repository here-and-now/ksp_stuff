"""Ascent: gravity turn, max-Q PID, staging, fairings, circularize.

The old launcher used APScheduler plus a busy-wait. This is a single loop
on a worker thread so the UI can abort and plot.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable

from geometry import heading_from_inclination, inertial_launch_azimuth, quadratic_pitch
from nodes import (
    execute_node,
    in_atmosphere,
    plan_and_execute_mj_circularize,
    plan_circularize_at_apoapsis,
)
from orientation import set_autopilot
from parts import deploy_solar, jettison_fairings, manipulate_engines, should_stage
from pid import PID
from session import Session
from watch import FlightWatch, MissionAbort, apply_hold, recover_periapsis

log = logging.getLogger("kspstuff")


@dataclass(slots=True)
class AscentConfig:
    target_altitude: float = 150_000
    turn_start_altitude: float = 2_500
    turn_end_altitude: float = 70_000
    end_stage: int = 0
    inclination: float = 0.0
    roll: float = 90.0
    max_q: float = 20_000
    max_twr: float | None = None
    latitude_deg: float | None = None
    northerly: bool = True
    staging_options: dict[int, dict[str, dict[str, Any]]] | None = None
    circularize: bool = True
    energy_cap: float = 1.4


@dataclass(slots=True)
class TelemetrySample:
    met: float
    altitude: float
    apoapsis: float
    periapsis: float
    dynamic_pressure: float
    throttle: float
    pitch: float


class Ascent:
    def __init__(
        self,
        session: Session,
        config: AscentConfig,
        *,
        on_log: Callable[[str], None] | None = None,
        on_telemetry: Callable[[TelemetrySample], None] | None = None,
        abort: Callable[[], bool] | None = None,
        watch: FlightWatch | None = None,
    ) -> None:
        self.session = session
        self.config = config
        self.on_log = on_log or (lambda msg: log.info(msg))
        self.on_telemetry = on_telemetry
        self.abort = abort or (lambda: False)
        self._watch = watch
        self.finished = False
        self.samples: list[TelemetrySample] = []
        self.heading = 90.0

    def run(self) -> None:
        session = self.session
        session.require_connected()
        cfg = self.config
        vessel = session.active_vessel
        body = vessel.orbit.body
        flight = vessel.flight(body.non_rotating_reference_frame)

        self.heading = self._heading(vessel)
        self._say(f"Ascent heading {self.heading:.1f}°  target apo {cfg.target_altitude:.0f} m")

        pid = PID(kp=0.001, ki=0.0001, kd=0.01, i_limit=1.0, out_min=0.0, out_max=1.0)
        pid.reset(cfg.max_q)

        ap = vessel.auto_pilot
        set_autopilot(ap, True)
        ap.target_roll = cfg.roll
        ap.target_heading = self.heading
        ap.target_pitch = 90.0
        vessel.control.sas = False
        vessel.control.throttle = 1.0
        try:
            situation = vessel.situation.name
        except Exception:
            situation = ""
        if situation in ("pre_launch", "prelaunch"):
            vessel.control.activate_next_stage()
            self._say("Ignition")

        solar_done = False
        fairing_done = False
        staging_done_for_stage = False
        last_stage_check = 0.0
        last_telem = 0.0
        atmosphere = float(body.atmosphere_depth)
        apo_cap = cfg.target_altitude * cfg.energy_cap
        surface_frame = vessel.surface_reference_frame

        watch = self._watch
        own_watch = watch is None
        if own_watch:
            watch = FlightWatch(session, extra=5_000.0, on_log=self.on_log, uplink=True)
        try:
            while not self.abort():
                state = watch.pulse("asc ")
                from uplink import holding

                if holding():
                    apply_hold(session)
                    continue
                altitude = state.alt
                apo = state.apo
                q = state.q
                now = time.monotonic()

                if state.flameout:
                    if not watch.relight(end_stage=cfg.end_stage):
                        if not cfg.circularize:
                            vessel.control.throttle = 0.0
                            self._say("Flameout — hop coast")
                            break
                        if apo >= cfg.target_altitude and not state.in_atmo:
                            self._say("Flameout after apo — coasting")
                            break
                        raise MissionAbort(
                            f"flameout no next stage (end_stage={cfg.end_stage})"
                        )

                # Do not use ecc while still in atmosphere — a suborbital
                # hop reports ecc≈1. Cap on apo overshoot, or escape once
                # already above the air.
                if apo > apo_cap or (
                    (not state.in_atmo) and state.escaping
                ):
                    vessel.control.throttle = 0.0
                    self._say(
                        f"Ascent energy cap ecc={state.ecc:.3f} apo={apo:.0f}"
                    )
                    break

                apo_done = apo >= cfg.target_altitude
                # Once apo is in hand, coast. Burning prograde in the air
                # after that sends apo to the Mun (L-015). Only thrust if
                # we are already falling toward a peri that will reenter.
                falling_in = state.heading_to_peri and (
                    state.dipping or (state.in_atmo and apo_done)
                )
                if falling_in:
                    ap.reference_frame = vessel.orbital_reference_frame
                    ap.target_direction = (0.0, 1.0, 0.0)
                    vessel.control.throttle = 1.0
                elif apo_done:
                    vessel.control.throttle = 0.0
                    if not state.in_atmo or not state.heading_to_peri:
                        self._say("Target apoapsis reached")
                        break
                else:
                    ap.reference_frame = surface_frame
                    ap.target_heading = self.heading
                    ap.target_roll = cfg.roll
                    if altitude >= cfg.turn_start_altitude:
                        span = max(cfg.turn_end_altitude - cfg.turn_start_altitude, 1.0)
                        frac = (altitude - cfg.turn_start_altitude) / span
                        ap.target_pitch = quadratic_pitch(frac)
                    else:
                        ap.target_pitch = 90.0
                    throttle = pid.update(q)
                    throttle = self._limit_twr(vessel, throttle)
                    vessel.control.throttle = throttle

                if now - last_stage_check >= 1.0:
                    last_stage_check = now
                    current = vessel.control.current_stage
                    if (
                        not staging_done_for_stage
                        and cfg.staging_options
                        and current in cfg.staging_options
                    ):
                        for engine_name, actions in cfg.staging_options[current].items():
                            manipulate_engines(vessel, engine_name, actions)
                        staging_done_for_stage = True
                    if should_stage(vessel, session.profile.fuels, cfg.end_stage):
                        vessel.control.activate_next_stage()
                        staging_done_for_stage = False
                        self._say(f"Staged  now {vessel.control.current_stage}")

                if (
                    not fairing_done
                    and not solar_done
                    and altitude > atmosphere
                ):
                    n = jettison_fairings(vessel)
                    fairing_done = True
                    self._say(f"Fairings jettisoned ({n})")
                    n = deploy_solar(vessel)
                    solar_done = True
                    self._say(f"Solar deployed ({n})")

                if now - last_telem >= 0.25:
                    last_telem = now
                    sample = TelemetrySample(
                        met=float(vessel.met),
                        altitude=altitude,
                        apoapsis=apo,
                        periapsis=state.peri,
                        dynamic_pressure=q,
                        throttle=vessel.control.throttle,
                        pitch=ap.target_pitch,
                    )
                    self.samples.append(sample)
                    if self.on_telemetry:
                        self.on_telemetry(sample)

            vessel.control.throttle = 0.0
            set_autopilot(ap, False)
            if self.abort():
                self._say("Ascent aborted")
                return
            state = watch.snapshot()
            # Near peri in the air, prograde raises apo not peri (L-016).
            # Circularize-at-apo is the right burn; recover only if unbound.
            # Sounding (circularize=False) coasts in air — do not recover.
            if cfg.circularize and state.escaping:
                self._say("Post-ascent recover (escaping)")
                recover_periapsis(
                    session,
                    extra=5_000.0,
                    on_log=self.on_log,
                    abort=self.abort,
                    watch=watch,
                )
            if cfg.circularize:
                self._circularize(vessel, watch=watch)
            self.finished = True
            self._say("Launch finished")
        except Exception:
            vessel.control.throttle = 0.0
            try:
                set_autopilot(vessel.auto_pilot, False)
            except Exception:
                pass
            raise
        finally:
            if own_watch and watch is not None:
                watch.close()

    def _circularize(self, vessel: Any, *, watch: Any | None = None) -> None:
        self._raise_periapsis(vessel, watch=watch)
        self._say("Planning circularization")
        if self.session.mech_jeb is not None:
            plan_and_execute_mj_circularize(
                self.session, at_apoapsis=True, abort=self.abort
            )
            return
        plan_circularize_at_apoapsis(self.session, vessel)
        execute_node(
            self.session, vessel, abort=self.abort, on_log=self.on_log, watch=watch
        )

    def _raise_periapsis(self, vessel: Any, *, watch: Any | None = None) -> None:
        """Climb out of atmosphere on the way *to apo*.

        Prograde at peri raises apo, not peri (L-016/L-019). If we are
        heading to peri, or apo is already at target, coast — circularize
        at apo is the burn that raises peri. Do not thrust through peri
        in the air.
        """
        body = vessel.orbit.body
        try:
            floor = float(body.atmosphere_depth) + 5_000.0
        except Exception:
            return
        peri = float(vessel.orbit.periapsis_altitude)
        apo = float(vessel.orbit.apoapsis_altitude)
        target = self.config.target_altitude
        if peri >= floor and not in_atmosphere(vessel):
            return
        heading_to_peri = False
        try:
            heading_to_peri = (
                float(vessel.orbit.time_to_periapsis)
                < float(vessel.orbit.time_to_apoapsis)
            )
        except Exception:
            pass
        # Vis-viva: never burn toward/through peri to "raise peri".
        if apo >= target or heading_to_peri:
            self._say("Coasting to apo — circularize will raise peri")
            return
        if not in_atmosphere(vessel) and peri < floor:
            self._say("Coasting to apo — circularize will raise peri")
            return
        self._say("Raising periapsis / climbing out of atmosphere")
        ap = vessel.auto_pilot
        ap.reference_frame = vessel.orbital_reference_frame
        set_autopilot(ap, True)
        vessel.control.sas = False
        own = watch is None
        if own:
            watch = FlightWatch(self.session, extra=5_000.0, on_log=self.on_log, uplink=True)
        try:
            while not self.abort():
                state = watch.pulse("raise ")
                if not state.in_atmo and state.peri >= floor:
                    break
                if not state.in_atmo and not state.heading_to_peri:
                    break
                # Apo in hand, or falling toward peri: coast. Circularize
                # at apo raises peri; thrusting here only pumps apo.
                if state.apo >= target or state.heading_to_peri:
                    vessel.control.throttle = 0.0
                    break
                if state.thrust <= 0:
                    if not watch.relight(end_stage=self.config.end_stage):
                        self._say("No thrust while raising periapsis")
                        break
                if state.in_atmo and state.alt < 10_000:
                    self._say("Too low to raise periapsis")
                    break
                ap.target_direction = (0.0, 1.0, 0.0)
                vessel.control.throttle = 1.0
        finally:
            vessel.control.throttle = 0.0
            set_autopilot(ap, False)
            if own:
                watch.close()
        self._say(
            f"Periapsis now {vessel.orbit.periapsis_altitude:.0f} m  "
            f"apo {vessel.orbit.apoapsis_altitude:.0f} m"
        )

    def _heading(self, vessel: Any) -> float:
        cfg = self.config
        lat = cfg.latitude_deg
        if lat is None:
            try:
                lat = vessel.flight().latitude
            except Exception:
                lat = 0.0
        if abs(lat) < 0.5:
            return heading_from_inclination(cfg.inclination)
        try:
            return inertial_launch_azimuth(
                lat, cfg.inclination, northerly=cfg.northerly
            )
        except Exception:
            return heading_from_inclination(cfg.inclination)

    def _limit_twr(self, vessel: Any, throttle: float) -> float:
        cap = self.config.max_twr
        if cap is None or cap <= 0:
            return throttle
        g = vessel.orbit.body.surface_gravity
        max_thrust = vessel.max_thrust
        mass = vessel.mass
        if max_thrust <= 0 or mass <= 0 or g <= 0:
            return throttle
        twr_at_full = max_thrust / (mass * g)
        if twr_at_full <= 0:
            return throttle
        return min(throttle, cap / twr_at_full)

    def _say(self, message: str) -> None:
        log.info(message)
        self.on_log(message)
