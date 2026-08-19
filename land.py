"""Mun landing: deorbit, lander stage, suicide burn, continue-from-orbit."""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Callable

from geometry import vis_viva
from nodes import execute_node, plan_circularize_at_periapsis
from orientation import set_autopilot
from session import Session
from transfer import (
    MUN_NAME,
    _clear_nodes,
    _finish_tli,
    _say,
    capture_at_periapsis,
    plan_mun_encounter,
    warp_to_soi,
)
from uplink import desk, holding, load_plan, no_warp_pe, skip_warp
from warp import warp_to_ut
from watch import (
    FlightWatch,
    MissionAbort,
    apply_hold,
    check_alive,
    require_parking,
)

log = logging.getLogger("kspstuff")


def lower_periapsis(
    session: Session,
    altitude: float,
    vessel: Any | None = None,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    watch: FlightWatch | None = None,
) -> None:
    """Retrograde burn at apoapsis to set periapsis altitude."""
    session.require_connected()
    vessel = vessel or session.active_vessel
    orbit = vessel.orbit
    mu = float(orbit.body.gravitational_parameter)
    r_ap = float(orbit.apoapsis)
    r_pe = float(orbit.body.equatorial_radius) + altitude
    a_new = 0.5 * (r_ap + r_pe)
    dv = vis_viva(mu, r_ap, a_new) - vis_viva(mu, r_ap, float(orbit.semi_major_axis))
    _clear_nodes(vessel)
    node = vessel.control.add_node(
        session.space_center.ut + float(orbit.time_to_apoapsis),
        prograde=dv,
    )
    _say(f"Lower Pe to {altitude:.0f} m  Δv={dv:.1f} m/s", on_log)
    execute_node(session, vessel, abort=abort, on_log=on_log, watch=watch)


def stage_to_lander(vessel: Any, on_log: Callable[[str], None] | None = None) -> None:
    """Fire stage 0 if a lander engine is still waiting."""
    if vessel.control.current_stage <= 0:
        return
    before = vessel.control.current_stage
    vessel.control.activate_next_stage()
    time.sleep(0.4)
    _say(f"Lander staged {before} → {vessel.control.current_stage}", on_log)


def suicide_burn(
    session: Session,
    vessel: Any | None = None,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    touchdown_speed: float = 5.0,
    watch: FlightWatch | None = None,
) -> None:
    """Surface-retrograde. Stay at throttle 1 while burn_d > alt.

    Previous attempt chopped throttle when ``alt`` oscillated around
    ``burn_d`` at 4 km / 380 m/s, then ran out of fuel and lithobraked.
    """
    session.require_connected()
    vessel = vessel or session.active_vessel
    body = vessel.orbit.body
    g = float(body.surface_gravity)
    ap = vessel.auto_pilot
    ap.reference_frame = vessel.surface_velocity_reference_frame
    set_autopilot(ap, True)
    ap.target_direction = (0.0, -1.0, 0.0)
    vessel.control.sas = False
    _say(f"Suicide burn on {body.name}  g={g:.2f}", on_log)

    own = watch is None
    if own:
        watch = FlightWatch(session, on_log=on_log, uplink=True)
    watch.enable_landing()
    landed = False
    try:
        t0 = time.monotonic()
        while time.monotonic() - t0 < 1_800.0:
            if abort and abort():
                raise MissionAbort("suicide aborted")
            state = watch.pulse("land ")
            if holding():
                apply_hold(session)
                continue
            alt = state.surf if math.isfinite(state.surf) else state.alt
            spd = state.spd
            vs = state.vs
            thrust = float(vessel.available_thrust)
            mass = float(vessel.mass)
            a = thrust / max(mass, 1.0) - g
            burn_d = (spd * spd) / (2.0 * max(a, 0.2)) if a > 0 and math.isfinite(spd) else 1e9

            if math.isfinite(alt) and alt < -2.0:
                raise MissionAbort(f"lithobrake alt={alt:.0f} spd={spd:.0f}")
            if thrust <= 0 and math.isfinite(spd) and spd > 8.0 and alt < 15_000:
                raise MissionAbort(f"tanks empty spd={spd:.0f} alt={alt:.0f}")
            if alt < 20.0 and math.isfinite(spd) and spd < touchdown_speed:
                vessel.control.throttle = 0.0
                landed = True
                _say(f"Touchdown  alt={alt:.1f} m  spd={spd:.2f} m/s", on_log)
                return

            # Never cut in the air while still fast, or if peri is underground.
            peri_bad = math.isfinite(state.peri) and state.peri < 0
            thr = float(desk.plan.get("suicide_throttle", 1.0))
            if peri_bad or burn_d > alt - 20.0 or (math.isfinite(spd) and spd > 12.0 and alt < 8_000):
                vessel.control.throttle = thr
            elif math.isfinite(spd) and spd > 6.0:
                vessel.control.throttle = 0.4
            else:
                vessel.control.throttle = 0.05
            if peri_bad:
                t0 = time.monotonic()  # L-035: do not timeout while peri is underground
        raise MissionAbort("suicide burn timed out")
    finally:
        try:
            if landed:
                vessel.control.throttle = 0.0
            else:
                apply_hold(session)
            set_autopilot(ap, False)
        except Exception:
            pass
        if own:
            watch.close()


def run_from_lko(
    session: Session,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    suicide_start_alt: float = 25_000.0,
    from_orbit: bool = False,
    watch: FlightWatch | None = None,
) -> None:
    """Parking orbit, or an already-raised transfer (from_orbit). Then Mun."""
    vessel = session.active_vessel
    own = watch is None
    if own:
        watch = FlightWatch(session, on_log=on_log, uplink=True)
    try:
        state = watch.pulse("lko ", force_log=True)
        if from_orbit and state.body == MUN_NAME:
            _say(f"Continue Mun orbit {state.peri:.0f}×{state.apo:.0f} m", on_log)
            if not watch.relight(end_stage=0):
                raise MissionAbort(f"Mun orbit, no thrust {state.line()}")
            peri = float(vessel.orbit.periapsis_altitude)
            if peri > 80_000:
                _say("High Mun orbit — lowering Pe to 30 km then circularizing", on_log)
                lower_periapsis(
                    session, 30_000, vessel, on_log=on_log, abort=abort, watch=watch
                )
                _clear_nodes(vessel)
                plan_circularize_at_periapsis(session, vessel)
                execute_node(session, vessel, abort=abort, on_log=on_log, watch=watch)
                watch.pulse("low ", force_log=True)
            peri = float(vessel.orbit.periapsis_altitude)
            landing_pe = float(desk.plan.get("landing_pe", 18_000.0))
            if peri > landing_pe + 2_000.0:
                lower_periapsis(
                    session, landing_pe, vessel, on_log=on_log, abort=abort, watch=watch
                )
            start = load_plan().get("suicide_start", suicide_start_alt)
            while True:
                state = watch.pulse("desc ")
                check_alive(session, watch=watch)
                if abort and abort():
                    raise MissionAbort("aborted before landing")
                if holding():
                    apply_hold(session)
                    continue
                surf = state.surf if math.isfinite(state.surf) else state.alt
                if surf <= start:
                    break
                if no_warp_pe() or skip_warp():
                    break
                if math.isfinite(state.t_pe) and state.t_pe > 45.0:
                    warp_to_ut(
                        session,
                        session.space_center.ut + min(state.t_pe - 40.0, 600.0),
                        abort=abort,
                        watch=watch,
                    )
                else:
                    break
            stage_to_lander(vessel, on_log=on_log)
            time.sleep(0.5)
            check_alive(session, need_thrust=True, watch=watch)
            suicide_burn(session, vessel, on_log=on_log, abort=abort, watch=watch)
            watch.pulse("end ", force_log=True)
            return
        on_transfer = (
            from_orbit
            and not state.in_atmo
            and math.isfinite(state.peri)
            and state.peri >= 70_000
            and math.isfinite(state.apo)
            and state.apo > 2_000_000
        )
        if on_transfer:
            _say(
                f"Continue transfer {state.peri:.0f}×{state.apo:.0f} m",
                on_log,
            )
            _finish_tli(
                session, vessel, watch=watch, abort=abort, on_log=on_log
            )
        else:
            if from_orbit:
                require_parking(
                    state, min_peri=70_000, max_apo=12_000_000, max_ecc=0.9
                )
            else:
                require_parking(
                    state, min_peri=70_000, max_apo=2_000_000, max_ecc=0.25
                )
            plan_mun_encounter(session, vessel, on_log=on_log)
            execute_node(session, vessel, abort=abort, on_log=on_log, watch=watch)
            _finish_tli(
                session, vessel, watch=watch, abort=abort, on_log=on_log
            )
        _say("TLI done, warping to Mun SOI", on_log)
        warp_to_soi(session, vessel, on_log=on_log, abort=abort, watch=watch)
        capture_at_periapsis(session, vessel, on_log=on_log, abort=abort, watch=watch)
        state = watch.pulse("cap ", force_log=True)
        body = vessel.orbit.body.name
        peri = float(vessel.orbit.periapsis_altitude)
        apo = float(vessel.orbit.apoapsis_altitude)
        _say(f"After capture body={body} apo={apo:.0f} peri={peri:.0f}", on_log)
        if body != MUN_NAME:
            raise MissionAbort(f"Capture left us around {body}, not Mun")
        if state.escaping:
            raise MissionAbort(f"Capture still escaping {state.line()}")

        # Do not drop Pe to 8 km from a 1700 km apo — that is an impact trajectory.
        # Circularize low first, then a small deorbit.
        if peri > 80_000:
            _say("High Mun orbit — lowering Pe to 30 km then circularizing", on_log)
            lower_periapsis(
                session, 30_000, vessel, on_log=on_log, abort=abort, watch=watch
            )
            _clear_nodes(vessel)
            plan_circularize_at_periapsis(session, vessel)
            execute_node(session, vessel, abort=abort, on_log=on_log, watch=watch)
            watch.pulse("low ", force_log=True)
        peri = float(vessel.orbit.periapsis_altitude)
        landing_pe = float(desk.plan.get("landing_pe", 18_000.0))
        if peri > landing_pe + 2_000.0:
            lower_periapsis(
                session, landing_pe, vessel, on_log=on_log, abort=abort, watch=watch
            )

        # Start the suicide with altitude still tens of km, not at Pe.
        start = load_plan().get("suicide_start", suicide_start_alt)
        while True:
            state = watch.pulse("desc ")
            check_alive(session, watch=watch)
            if abort and abort():
                raise MissionAbort("aborted before landing")
            if holding():
                apply_hold(session)
                continue
            surf = state.surf if math.isfinite(state.surf) else state.alt
            if surf <= start:
                break
            if no_warp_pe() or skip_warp():
                break
            if math.isfinite(state.t_pe) and state.t_pe > 45.0:
                warp_to_ut(
                    session,
                    session.space_center.ut + min(state.t_pe - 40.0, 600.0),
                    abort=abort,
                    watch=watch,
                )
            else:
                break

        stage_to_lander(vessel, on_log=on_log)
        time.sleep(0.5)
        check_alive(session, need_thrust=True, watch=watch)
        suicide_burn(session, vessel, on_log=on_log, abort=abort, watch=watch)
        watch.pulse("end ", force_log=True)
    finally:
        if own:
            watch.close()


