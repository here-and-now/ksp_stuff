"""Kerbin → Mun transfer, capture, and a surface suicide burn.

No MechJeb. Nodes are vis-viva + a search over ``node.ut`` for a Mun
encounter. Landing is surface-retrograde with a constant-accel estimate.
"""

from __future__ import annotations

import logging
import math
import time
from typing import Any, Callable

from geometry import vis_viva
from nodes import execute_node, plan_circularize_at_periapsis
from orientation import set_autopilot, wait_aligned
from session import Session
from uplink import (
    clear_capture,
    desk,
    holding,
    load_plan,
    no_warp_pe,
    skip_warp,
    want_capture,
)
from warp import warp_to_ut
from watch import (
    FlightWatch,
    MissionAbort,
    check_alive,
    freeze,
    heartbeat,
    require_parking,
)

log = logging.getLogger("kspstuff")

MUN_NAME = "Mun"
_ENCOUNTER_PE_MIN = 12_000.0
_ENCOUNTER_PE_MAX = 50_000.0
_ENCOUNTER_PE_AIM = 25_000.0
# apoapsis_altitude past this with no Mun patch is a miss (L-028).
_MUN_APO_PAST = 12_000_000.0


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def _clear_nodes(vessel: Any) -> None:
    for node in list(vessel.control.nodes):
        try:
            node.remove()
        except Exception:
            pass


def _next_body(orbit: Any) -> str | None:
    try:
        nxt = orbit.next_orbit
    except Exception:
        return None
    if nxt is None:
        return None
    try:
        return nxt.body.name
    except Exception:
        return None


def _next_pe(orbit: Any) -> float | None:
    try:
        nxt = orbit.next_orbit
        if nxt is None:
            return None
        return float(nxt.periapsis_altitude)
    except Exception:
        return None


def _encounter_pe(vessel: Any, body: str = MUN_NAME) -> float | None:
    try:
        if vessel.orbit.body.name == body:
            return float(vessel.orbit.periapsis_altitude)
    except Exception:
        return None
    return _next_pe(vessel.orbit)


def _time_to_soi(vessel: Any, body: str) -> float:
    """``time_to_soi_change`` is NaN when the patch is missing or flickering."""
    try:
        tts = float(vessel.orbit.time_to_soi_change)
        if math.isfinite(tts) and tts > 0.0:
            return tts
    except Exception:
        pass
    if _next_body(vessel.orbit) == body:
        try:
            tap = float(vessel.orbit.time_to_apoapsis)
            if math.isfinite(tap) and tap > 0.0:
                return tap
        except Exception:
            pass
    return float("nan")


def _tli_patch(vessel: Any) -> tuple[str | None, float | None]:
    return _next_body(vessel.orbit), _next_pe(vessel.orbit)


def _tli_good(nxt: str | None, pe: float | None) -> bool:
    return (
        nxt == MUN_NAME
        and pe is not None
        and _ENCOUNTER_PE_MIN <= pe <= _ENCOUNTER_PE_MAX
    )


def _tli_litho(nxt: str | None, pe: float | None) -> bool:
    return nxt == MUN_NAME and pe is not None and pe < _ENCOUNTER_PE_MIN


def _tli_escaped_miss(state: Any, nxt: str | None) -> bool:
    """Hyperbola or apo past Mun with no SOI — not a short Hohmann (L-028)."""
    if nxt == MUN_NAME or not state.escaping:
        return False
    return (
        not math.isfinite(state.apo)
        or state.apo < 0.0
        or state.apo >= _MUN_APO_PAST
    )


def _abort_bad_tli(state: Any, nxt: str | None, pe: float | None) -> None:
    if _tli_litho(nxt, pe):
        raise MissionAbort(f"TLI Mun Pe {pe:.0f} below {_ENCOUNTER_PE_MIN:.0f}")
    if _tli_escaped_miss(state, nxt):
        raise MissionAbort(
            f"TLI escaped Kerbin with no Mun SOI apo={state.apo:.0f}"
        )
    if state.in_atmo or (state.dipping and state.body != MUN_NAME):
        raise MissionAbort(f"TLI left a bad orbit {state.line()}")


def _raise_tli_apo(
    session: Session,
    vessel: Any,
    *,
    watch: FlightWatch,
    abort: Callable[[], bool] | None,
    on_log: Callable[[str], None] | None,
    band: float,
) -> None:
    """Prograde until a Mun patch appears or apo reaches the Mun band."""
    ap = vessel.auto_pilot
    ap.reference_frame = vessel.orbital_reference_frame
    set_autopilot(ap, True)
    ap.target_direction = (0.0, 1.0, 0.0)
    vessel.control.sas = False
    wait_aligned(ap, timeout=10.0, max_error=20.0)
    try:
        t0 = time.monotonic()
        while time.monotonic() - t0 < 90.0:
            if abort and abort():
                raise MissionAbort("TLI raise aborted")
            state = watch.pulse("tli+ ")
            if holding():
                vessel.control.throttle = 0.0
                continue
            check_alive(session, watch=watch)
            nxt, pe = _tli_patch(vessel)
            if nxt == MUN_NAME and pe is not None:
                vessel.control.throttle = 0.0
                if pe < _ENCOUNTER_PE_MIN:
                    raise MissionAbort(
                        f"TLI Mun Pe {pe:.0f} below {_ENCOUNTER_PE_MIN:.0f}"
                    )
                _say(f"TLI encounter after raise Pe={pe:.0f}", on_log)
                return
            if _tli_escaped_miss(state, nxt):
                vessel.control.throttle = 0.0
                return
            if math.isfinite(state.apo) and state.apo >= band:
                vessel.control.throttle = 0.0
                _say(
                    f"TLI apo {state.apo:.0f} in Mun band, Pe={pe}",
                    on_log,
                )
                return
            if not watch.relight(end_stage=0):
                raise MissionAbort("no thrust during TLI raise")
            vessel.control.throttle = 1.0
        vessel.control.throttle = 0.0
    finally:
        try:
            vessel.control.throttle = 0.0
            set_autopilot(ap, False)
        except Exception:
            pass


def _finish_tli(
    session: Session,
    vessel: Any,
    *,
    watch: FlightWatch,
    abort: Callable[[], bool] | None,
    on_log: Callable[[str], None] | None,
) -> None:
    """After the TLI node: Pe=None is not a lost encounter while apo is short.

    L-023 still: do not warp until Pe is 12–50 km; abort a subsurface Mun Pe
    or an escape past ~12 Mm with no SOI (L-028).
    """
    mun = session.bodies[MUN_NAME]
    band = float(mun.orbit.semi_major_axis) - float(
        vessel.orbit.body.equatorial_radius
    )

    def _tick() -> tuple[Any, str | None, float | None]:
        st = watch.pulse("tli ", force_log=True)
        nxt, pe = _tli_patch(vessel)
        return st, nxt, pe

    state, nxt, pe = _tick()
    for _ in range(4):
        if nxt == MUN_NAME:
            break
        time.sleep(0.25)
        state, nxt, pe = _tick()

    _abort_bad_tli(state, nxt, pe)
    if _tli_good(nxt, pe):
        return

    if nxt != MUN_NAME and math.isfinite(state.apo) and state.apo < band:
        _say(
            f"TLI apo {state.apo:.0f} short of Mun {band:.0f} — raising",
            on_log,
        )
        _raise_tli_apo(
            session, vessel, watch=watch, abort=abort, on_log=on_log, band=band
        )
        state, nxt, pe = _tick()
        _abort_bad_tli(state, nxt, pe)
        if _tli_good(nxt, pe):
            return

    if not _tli_good(nxt, pe):
        _say("TLI has no Mun patch in 12–50 km — re-planning", on_log)
        try:
            plan_mun_encounter(session, vessel, on_log=on_log)
        except MissionAbort as exc:
            # L-030: a 12–50 km Pe planner miss is not "leave Grok in the ellipse".
            _say(f"replan missed 12–50 km Pe ({exc}) — coast apo/SOI", on_log)
            return
        execute_node(session, vessel, abort=abort, on_log=on_log, watch=watch)
        state, nxt, pe = _tick()
        _abort_bad_tli(state, nxt, pe)
        if _tli_good(nxt, pe):
            return

    if _tli_good(nxt, pe):
        return
    if (
        not state.escaping
        and math.isfinite(state.peri)
        and state.peri >= 70_000
    ):
        _say(f"no 12–50 km Pe yet (Pe={pe}) — coast apo/SOI anyway", on_log)
        return
    raise MissionAbort(f"TLI lost Mun encounter Pe={pe}")


def hohmann_transfer_dv(orbit: Any, target_sma: float) -> float:
    mu = float(orbit.body.gravitational_parameter)
    r = float(orbit.semi_major_axis)
    a_t = 0.5 * (r + target_sma)
    v0 = vis_viva(mu, r, r)
    vt = vis_viva(mu, r, a_t)
    return vt - v0


def plan_mun_encounter(
    session: Session,
    vessel: Any | None = None,
    *,
    on_log: Callable[[str], None] | None = None,
) -> Any:
    """Search one Mun period. Only accept Pe in 12–50 km."""
    session.require_connected()
    vessel = vessel or session.active_vessel
    mun = session.bodies[MUN_NAME]
    _clear_nodes(vessel)
    dv0 = hohmann_transfer_dv(vessel.orbit, float(mun.orbit.semi_major_axis))
    ut0 = float(session.space_center.ut) + 30.0
    node = vessel.control.add_node(ut0, prograde=dv0)
    period = float(vessel.orbit.period)
    mun_period = float(mun.orbit.period)
    step = max(period / 6.0, 30.0)
    best: tuple[float, float, float, float] | None = None
    for dv in (dv0, dv0 - 15.0, dv0 + 15.0, dv0 - 30.0, dv0 + 30.0):
        t = ut0
        end = ut0 + mun_period
        while t < end:
            node.ut = t
            node.prograde = dv
            if _next_body(node.orbit) == MUN_NAME:
                pe = _next_pe(node.orbit)
                if pe is not None and _ENCOUNTER_PE_MIN <= pe <= _ENCOUNTER_PE_MAX:
                    score = abs(pe - _ENCOUNTER_PE_AIM)
                    if best is None or score < best[0]:
                        best = (score, t, dv, pe)
                        if score < 5_000:
                            break
            t += step
        if best is not None and best[0] < 8_000:
            break

    if best is None:
        node.remove()
        raise MissionAbort(
            "No Mun encounter with Pe in 12–50 km. Refusing a high flyby."
        )

    load_plan()
    aim = desk.plan["mun_pe"]
    pe_min, pe_max = _ENCOUNTER_PE_MIN, _ENCOUNTER_PE_MAX
    _score, t_best, dv, pe = best
    node.ut = t_best
    node.prograde = dv
    last_good = dv
    for delta in (10.0, 5.0, 2.0, 1.0):
        pe_now = _next_pe(node.orbit)
        if pe_now is None or _next_body(node.orbit) != MUN_NAME:
            node.prograde = last_good
            break
        if not (pe_min <= pe_now <= pe_max):
            node.prograde = last_good
            break
        last_good = node.prograde
        if abs(pe_now - aim) < 3_000:
            break
        node.prograde = node.prograde + (
            delta if pe_now > aim else -delta
        )
    pe = _next_pe(node.orbit)
    if pe is None or pe > pe_max:
        node.remove()
        raise MissionAbort(f"Encounter Pe still unusable ({pe})")
    _say(
        f"Mun encounter  UT+{node.ut - session.space_center.ut:.0f}s  "
        f"Δv={node.prograde:.1f} m/s  Pe={pe:.0f} m",
        on_log,
    )
    return node


def warp_to_soi(
    session: Session,
    vessel: Any | None = None,
    *,
    lead: float = 30.0,
    body: str = MUN_NAME,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    watch: FlightWatch | None = None,
) -> None:
    session.require_connected()
    vessel = vessel or session.active_vessel
    # L-032: Gene abort is the way out. A wall-clock timeout leaves Groks.

    def _arrived_or_impact() -> bool:
        try:
            if vessel.orbit.body.name == body:
                return True
        except Exception:
            return False
        pe = _encounter_pe(vessel, body)
        return pe is not None and pe < _ENCOUNTER_PE_MIN

    while True:
        heartbeat(session, on_log, tag="soi ", watch=watch)
        check_alive(session, watch=watch)
        if abort and abort():
            raise MissionAbort("aborted waiting for SOI")
        if holding():
            time.sleep(0.5)
            continue
        if vessel.orbit.body.name == body:
            _say(f"SOI {body}", on_log)
            return
        pe = _encounter_pe(vessel, body)
        if pe is not None and pe < _ENCOUNTER_PE_MIN:
            raise MissionAbort(
                f"Mun Pe {pe:.0f} m below {_ENCOUNTER_PE_MIN:.0f} before SOI"
            )
        tts = _time_to_soi(vessel, body)
        if skip_warp():
            time.sleep(0.5)
            continue
        if math.isfinite(tts) and tts > lead + 5.0:
            warp_to_ut(
                session,
                session.space_center.ut + tts - lead,
                abort=abort,
                watch=watch,
                stop_if=_arrived_or_impact,
            )
            continue
        # No patched SOI yet (L-031): rails toward apo, never sit 1× until
        # a wall-clock timeout abandons a Grok.
        try:
            tap = float(vessel.orbit.time_to_apoapsis)
        except Exception:
            tap = float("nan")
        if math.isfinite(tap) and tap > 45.0:
            warp_to_ut(
                session,
                session.space_center.ut + tap - 30.0,
                abort=abort,
                watch=watch,
                stop_if=_arrived_or_impact,
            )
        else:
            time.sleep(0.5)


def _capture_now(
    session: Session,
    vessel: Any,
    *,
    on_log: Callable[[str], None] | None,
    abort: Callable[[], bool] | None,
    watch: FlightWatch,
    min_pe: float = _ENCOUNTER_PE_MIN,
) -> None:
    """Retrograde now. Do not warp to a subsurface peri (L-023)."""
    ap = vessel.auto_pilot
    ap.reference_frame = vessel.orbital_reference_frame
    set_autopilot(ap, True)
    ap.target_direction = (0.0, -1.0, 0.0)
    vessel.control.sas = False
    wait_aligned(ap, timeout=10.0, max_error=20.0)
    try:
        t0 = time.monotonic()
        while time.monotonic() - t0 < 90.0:
            if abort and abort():
                raise MissionAbort("capture aborted")
            state = watch.pulse("cap ")
            if holding():
                vessel.control.throttle = 0.0
                continue
            check_alive(session, watch=watch)
            if state.alt < 25_000 and (
                (math.isfinite(state.peri) and state.peri < min_pe) or state.escaping
            ):
                raise MissionAbort(
                    f"lithobrake peri={state.peri:.0f} alt={state.alt:.0f}"
                )
            if not state.escaping:
                vessel.control.throttle = 0.0
                if math.isfinite(state.peri) and state.peri < 0.0:
                    raise MissionAbort(f"captured into lithobrake peri={state.peri:.0f}")
                _say(
                    f"Capture now peri={state.peri:.0f} ecc={state.ecc:.3f}",
                    on_log,
                )
                return
            if not watch.relight(end_stage=0):
                raise MissionAbort("no thrust during capture")
            vessel.control.throttle = 1.0
        raise MissionAbort("capture-now timed out")
    finally:
        try:
            vessel.control.throttle = 0.0
            set_autopilot(ap, False)
        except Exception:
            pass


def capture_at_periapsis(
    session: Session,
    vessel: Any | None = None,
    *,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    watch: FlightWatch | None = None,
) -> None:
    session.require_connected()
    vessel = vessel or session.active_vessel
    peri = float(vessel.orbit.periapsis_altitude)
    try:
        alt = float(vessel.flight().mean_altitude)
    except Exception:
        alt = float("nan")
    own = watch is None
    if own:
        watch = FlightWatch(session, on_log=on_log, uplink=True)
    try:
        if want_capture() or no_warp_pe() or peri < _ENCOUNTER_PE_MIN:
            if math.isfinite(alt) and alt < 25_000:
                raise MissionAbort(f"lithobrake peri={peri:.0f} alt={alt:.0f}")
            _say(f"Mun Pe {peri:.0f} — capturing now (uplink/L-023)", on_log)
            _capture_now(
                session, vessel, on_log=on_log, abort=abort, watch=watch
            )
            clear_capture()
            return
        _clear_nodes(vessel)
        node = plan_circularize_at_periapsis(session, vessel)
        _say(f"Capture node Δv={node.prograde:.1f} m/s", on_log)

        def _pe_unsafe() -> bool:
            try:
                return float(vessel.orbit.periapsis_altitude) < _ENCOUNTER_PE_MIN
            except Exception:
                return False

        execute_node(
            session,
            vessel,
            abort=abort,
            on_log=on_log,
            watch=watch,
            stop_if=_pe_unsafe,
        )
    finally:
        if own:
            watch.close()


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
    try:
        t0 = time.monotonic()
        while time.monotonic() - t0 < 1_800.0:
            if abort and abort():
                raise MissionAbort("suicide aborted")
            state = watch.pulse("land ")
            if holding():
                vessel.control.throttle = 0.0
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
                _say(f"Touchdown  alt={alt:.1f} m  spd={spd:.2f} m/s", on_log)
                return

            # Never cut in the air while still fast, or if peri is underground.
            peri_bad = math.isfinite(state.peri) and state.peri < 0
            if peri_bad or burn_d > alt - 20.0 or (math.isfinite(spd) and spd > 12.0 and alt < 8_000):
                vessel.control.throttle = 1.0
            elif math.isfinite(spd) and spd > 6.0:
                vessel.control.throttle = 0.4
            else:
                vessel.control.throttle = 0.05
            if peri_bad:
                t0 = time.monotonic()  # L-035: do not timeout while peri is underground
        raise MissionAbort("suicide burn timed out")
    finally:
        try:
            vessel.control.throttle = 0.0
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
) -> None:
    """Parking orbit, or an already-raised transfer (from_orbit). Then Mun."""
    vessel = session.active_vessel
    with FlightWatch(session, on_log=on_log, uplink=True) as watch:
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
            if peri > 20_000:
                lower_periapsis(
                    session, 18_000, vessel, on_log=on_log, abort=abort, watch=watch
                )
            start = load_plan().get("suicide_start", suicide_start_alt)
            while True:
                state = watch.pulse("desc ")
                check_alive(session, watch=watch)
                if abort and abort():
                    raise MissionAbort("aborted before landing")
                if holding():
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
        if peri > 14_000:
            lower_periapsis(
                session, 10_000, vessel, on_log=on_log, abort=abort, watch=watch
            )

        # Start the suicide with altitude still tens of km, not at Pe.
        start = load_plan().get("suicide_start", suicide_start_alt)
        while True:
            state = watch.pulse("desc ")
            check_alive(session, watch=watch)
            if abort and abort():
                raise MissionAbort("aborted before landing")
            if holding():
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


def run_mission(
    session: Session,
    *,
    recover: bool = True,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    from_orbit: bool = False,
) -> None:
    """Pad → LKO → Mun, or continue the active vessel (from_orbit)."""
    from craft import mun_lander
    from crew import apply_ascent, current_pilot
    from hangar import Hangar, discover_ksp
    from launch import Ascent, AscentConfig

    person = current_pilot()
    style = person.style
    _say(f"Crew {person.name}  apo={style.target_altitude:.0f} cap={style.energy_cap}", on_log)
    from uplink import desk as _desk, save_plan

    _desk.plan["suicide_start"] = style.suicide_start_alt
    _desk.plan["parking_apo"] = style.target_altitude
    save_plan()

    if from_orbit:
        if session.active_vessel is None:
            raise MissionAbort("from-orbit: no active vessel")
        _say(f"Continue from orbit as {person.name}", on_log)
        heartbeat(session, on_log, tag="cont ")
        try:
            run_from_lko(
                session,
                on_log=on_log,
                abort=abort,
                suicide_start_alt=style.suicide_start_alt,
                from_orbit=True,
            )
        except MissionAbort:
            freeze(session)
            heartbeat(session, on_log, tag="abort ")
            raise
        return

    root = discover_ksp()
    if root is None:
        raise MissionAbort("KSP install not found (KSPSTUFF_KSP / Steam path)")
    hangar = Hangar(ksp_root=root, save="Grok")
    craft = mun_lander()
    hangar.install(craft, overwrite=True)
    _say(f"Installed {craft.name} ({len(craft.parts)} parts)", on_log)
    seats = [person.kerbal] if person.kerbal else None
    hangar.launch(session, craft.name, recover=recover, crew=seats)
    time.sleep(2.0)
    heartbeat(session, on_log, tag="pad ")

    cfg = apply_ascent(
        AscentConfig(
            target_altitude=style.target_altitude,
            turn_start_altitude=style.turn_start_altitude,
            turn_end_altitude=style.turn_end_altitude,
            end_stage=1,
            circularize=True,
            max_q=style.max_q,
            energy_cap=style.energy_cap,
        ),
        style,
    )
    Ascent(session, cfg, on_log=on_log, abort=abort or (lambda: False)).run()
    try:
        run_from_lko(
            session,
            on_log=on_log,
            abort=abort,
            suicide_start_alt=style.suicide_start_alt,
        )
    except MissionAbort:
        freeze(session)
        heartbeat(session, on_log, tag="abort ")
        raise

