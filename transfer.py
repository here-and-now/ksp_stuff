"""Mun transfer: TLI search, SOI wait, capture (phases tli/soi/capture)."""

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
from watch import FlightWatch, MissionAbort, apply_hold, check_alive

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
                apply_hold(session)
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
            apply_hold(session)
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
                apply_hold(session)
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


