"""Mission heartbeat, gates, and intervention.

Every control loop holds a :class:`FlightWatch`. Streams cover the hot
orbit numbers; resources/warp refresh at 1 Hz. :meth:`FlightWatch.pulse`
waits for a stream batch, logs one line a second, and returns a
:class:`FlightState` the loop can act on (atmosphere, escape, flameout,
wreck). Do not construct a second watch in the same process.

``heartbeat()`` is the one-shot used by ``python main.py status``.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from orientation import set_autopilot, wait_aligned
from session import Session

log = logging.getLogger("kspstuff")

# Hot path only. Resources / warp / engines stay 1 Hz RPC.
_STREAM_PROPS: tuple[tuple[str, str], ...] = (
    ("flight", "mean_altitude"),
    ("flight", "dynamic_pressure"),
    ("flight", "surface_altitude"),
    ("orbit", "apoapsis_altitude"),
    ("orbit", "periapsis_altitude"),
    ("orbit", "eccentricity"),
    ("orbit", "semi_major_axis"),
    ("orbit", "time_to_periapsis"),
    ("orbit", "time_to_apoapsis"),
)
_LANDING_PROPS: tuple[str, ...] = ("speed", "vertical_speed")


class MissionAbort(RuntimeError):
    """Predicted lithobrake, wreck, empty tanks with leftover speed, or a gate."""


def _say(msg: str, on_log: Callable[[str], None] | None) -> None:
    log.info(msg)
    if on_log:
        on_log(msg)


def _enum_name(value: Any, default: str = "?") -> str:
    if value is None:
        return default
    name = getattr(value, "name", None)
    if isinstance(name, str):
        return name
    text = str(value)
    return text.rsplit(".", 1)[-1] if "." in text else text


def _finite(value: Any, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except Exception:
        return default
    return out if math.isfinite(out) else default


@dataclass(slots=True)
class FlightState:
    """One snapshot a control loop can branch on."""

    body: str = "?"
    situation: str = "?"
    alt: float = float("nan")
    peri: float = float("nan")
    apo: float = float("nan")
    ecc: float = float("nan")
    sma: float = float("nan")
    q: float = float("nan")
    lf: float = -1.0
    ox: float = -1.0
    stage: int = -1
    throttle: float = -1.0
    thrust: float = -1.0
    max_thrust: float = -1.0
    parts: int = -1
    warp: float = 0.0
    rails: int = 0
    rmax: int = 0
    t_pe: float = float("nan")
    t_ap: float = float("nan")
    atm_depth: float = float("nan")
    in_atmo: bool = False
    dipping: bool = False
    escaping: bool = False
    flameout: bool = False
    wreck: bool = False
    heading_to_peri: bool = False
    surf: float = float("nan")
    spd: float = float("nan")
    vs: float = float("nan")
    flags: tuple[str, ...] = field(default_factory=tuple)

    def line(self, tag: str = "") -> str:
        flag = (" [" + " ".join(self.flags) + "]") if self.flags else ""
        tpe = f" tpe={self.t_pe:.0f}" if math.isfinite(self.t_pe) else ""
        return (
            f"{tag}{self.body} {self.situation} "
            f"alt={self.alt:.0f} peri={self.peri:.0f} apo={self.apo:.0f} "
            f"ecc={self.ecc:.3f} LF={self.lf:.0f} stg={self.stage} "
            f"thr={self.throttle:.2f} F={self.thrust:.0f}N "
            f"parts={self.parts} warp={self.warp:.0f}x{tpe}{flag}"
        )

    def danger(self) -> str | None:
        if self.wreck:
            return "wreck"
        if (
            math.isfinite(self.peri)
            and self.peri < 0.0
            and not self.in_atmo
            and math.isfinite(self.alt)
            and self.alt < 50_000
        ):
            return f"lithobrake peri={self.peri:.0f} alt={self.alt:.0f}"
        if self.in_atmo and self.dipping:
            return f"in atmosphere alt={self.alt:.0f} peri={self.peri:.0f}"
        if self.dipping:
            return f"periapsis {self.peri:.0f} below atmosphere {self.atm_depth:.0f}"
        if self.escaping:
            return f"escaping ecc={self.ecc:.3f} apo={self.apo:.0f}"
        return None


class FlightWatch:
    """Subscribe once; :meth:`pulse` every control-loop iteration."""

    def __init__(
        self,
        session: Session,
        *,
        extra: float = 10_000.0,
        on_log: Callable[[str], None] | None = None,
        stream_rate: float = 10.0,
        uplink: bool = False,
    ) -> None:
        self.session = session
        self.extra = extra
        self.on_log = on_log
        self.stream_rate = stream_rate
        self._uplink = uplink
        self._vessel: Any = None
        self._vid: Any = None
        self._flight: Any = None
        self._orbit: Any = None
        self._body: Any = None
        self._body_flight: Any = None
        self._streams: dict[str, Any] = {}
        self._slow: dict[str, Any] = {}
        self._slow_t = 0.0
        self._last_log = 0.0
        self._landing = False
        self._bind()

    def __enter__(self) -> FlightWatch:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        self._drop_streams()
        self._flight = None
        self._orbit = None
        self._body = None
        self._body_flight = None
        self._vessel = None
        self._vid = None
        self._landing = False

    def _drop_streams(self) -> None:
        for stream in self._streams.values():
            try:
                if stream is not None:
                    stream.remove()
            except Exception:
                pass
        self._streams.clear()

    def _vessel_id(self, vessel: Any) -> Any:
        try:
            return vessel.id
        except Exception:
            return id(vessel)

    def _add_stream(self, obj: Any, name: str) -> None:
        conn = self.session.conn
        try:
            stream = conn.add_stream(getattr, obj, name)
            stream.rate = self.stream_rate
            self._streams[name] = stream
        except Exception:
            log.debug("stream %s failed", name, exc_info=True)
            self._streams[name] = None

    def _bind(self) -> None:
        self._drop_streams()
        session = self.session
        vessel = session.active_vessel
        if vessel is None:
            raise MissionAbort("no active vessel")
        self._vessel = vessel
        self._vid = self._vessel_id(vessel)
        self._flight = vessel.flight()
        self._orbit = vessel.orbit
        self._body = vessel.orbit.body
        self._body_flight = vessel.flight(self._body.reference_frame)
        self._streams = {}
        for kind, name in _STREAM_PROPS:
            obj = self._flight if kind == "flight" else self._orbit
            self._add_stream(obj, name)
        if self._landing:
            for name in _LANDING_PROPS:
                self._add_stream(self._body_flight, name)
        self._slow = {}
        self._slow_t = 0.0

    def enable_landing(self) -> None:
        """Extra body-frame speed streams for suicide. Same watch, no second bind of the core set."""
        if self._landing:
            return
        self._landing = True
        self._ensure_bound()
        for name in _LANDING_PROPS:
            if name not in self._streams:
                self._add_stream(self._body_flight, name)

    def wait(self, timeout: float = 0.08) -> None:
        """Block until the stream socket pushes, or ``timeout``. One wake is a batch."""
        conn = self.session.conn
        try:
            with conn.stream_update_condition:
                conn.wait_for_stream_update(timeout=timeout)
        except Exception:
            time.sleep(timeout)

    def _ensure_bound(self) -> Any:
        vessel = self.session.active_vessel
        if vessel is None:
            raise MissionAbort("no active vessel")
        if self._vessel is None or self._vid != self._vessel_id(vessel):
            self._bind()
            vessel = self._vessel
        return vessel

    def _stream(self, name: str, fallback: Callable[[], float]) -> float:
        stream = self._streams.get(name)
        if stream is not None:
            try:
                return _finite(stream())
            except Exception:
                pass
        try:
            return _finite(fallback())
        except Exception:
            return float("nan")

    def _refresh_slow(self, vessel: Any, sc: Any) -> None:
        def grab(fn: Callable[[], Any], default: Any) -> Any:
            try:
                return fn()
            except Exception:
                return default

        self._slow = {
            "lf": grab(lambda: float(vessel.resources.amount("LiquidFuel")), -1.0),
            "ox": grab(lambda: float(vessel.resources.amount("Oxidizer")), -1.0),
            "stage": grab(lambda: int(vessel.control.current_stage), -1),
            "parts": grab(lambda: len(vessel.parts.all), -1),
            "warp": grab(lambda: float(sc.warp_rate), 0.0),
            "rails": grab(lambda: int(sc.rails_warp_factor), 0),
            "rmax": grab(lambda: int(sc.maximum_rails_warp_factor), 0),
            "throttle": grab(lambda: float(vessel.control.throttle), -1.0),
            "thrust": grab(lambda: float(vessel.available_thrust), float("nan")),
            "max_thrust": grab(lambda: float(vessel.max_thrust), float("nan")),
            "sit": _enum_name(grab(lambda: vessel.situation, None)),
            "flameout_eng": False,
        }
        try:
            for engine in vessel.parts.engines:
                if engine.active and not engine.has_fuel:
                    self._slow["flameout_eng"] = True
                    break
        except Exception:
            pass

    def snapshot(self) -> FlightState:
        vessel = self._ensure_bound()
        sc = self.session.space_center
        flight = self._flight
        orbit = self._orbit
        now = time.monotonic()
        if now - self._slow_t >= 1.0 or not self._slow:
            self._slow_t = now
            self._refresh_slow(vessel, sc)
        slow = self._slow

        alt = self._stream("mean_altitude", lambda: float(flight.mean_altitude))
        peri = self._stream("periapsis_altitude", lambda: float(orbit.periapsis_altitude))
        apo = self._stream("apoapsis_altitude", lambda: float(orbit.apoapsis_altitude))
        ecc = self._stream("eccentricity", lambda: float(orbit.eccentricity))
        sma = self._stream("semi_major_axis", lambda: float(orbit.semi_major_axis))
        q = self._stream("dynamic_pressure", lambda: float(flight.dynamic_pressure))
        t_pe = self._stream("time_to_periapsis", lambda: float(orbit.time_to_periapsis))
        t_ap = self._stream("time_to_apoapsis", lambda: float(orbit.time_to_apoapsis))
        surf = self._stream(
            "surface_altitude", lambda: float(flight.surface_altitude)
        )
        body_flight = self._body_flight
        spd = self._stream("speed", lambda: float(body_flight.speed))
        vs = self._stream("vertical_speed", lambda: float(body_flight.vertical_speed))
        heading_to_peri = (
            math.isfinite(t_pe) and math.isfinite(t_ap) and t_pe < t_ap
        )

        def grab(fn: Callable[[], Any], default: Any) -> Any:
            try:
                return fn()
            except Exception:
                return default

        body = self._body
        body_name = grab(lambda: body.name, "?")
        sit = str(slow.get("sit") or "?")
        thrust = _finite(slow.get("thrust"), float("nan"))
        max_thrust = _finite(slow.get("max_thrust"), float("nan"))
        throttle = _finite(slow.get("throttle"), float("nan"))

        has_atm = bool(grab(lambda: bool(body.has_atmosphere), False))
        atm_depth = (
            _finite(grab(lambda: float(body.atmosphere_depth), float("nan")))
            if has_atm
            else float("nan")
        )
        in_atmo = bool(
            has_atm and math.isfinite(alt) and math.isfinite(atm_depth) and alt < atm_depth
        )
        floor = (atm_depth + self.extra) if has_atm and math.isfinite(atm_depth) else None
        # Peri is *always* underground on the pad. DIP means we already have
        # an apo above the air and will come back through it.
        apo_above_air = bool(
            has_atm and math.isfinite(apo) and math.isfinite(atm_depth) and apo > atm_depth
        )
        dipping = bool(
            floor is not None
            and math.isfinite(peri)
            and peri < floor
            and apo_above_air
        )
        # ecc≈1 on the pad is a suborbital hop, not an escape. Energy
        # flags only count once we are out of the atmosphere (or apo is).
        energy_escape = bool(
            (math.isfinite(sma) and sma < 0.0)
            or (math.isfinite(ecc) and ecc >= 0.98)
        )
        escaping = bool(energy_escape and (not in_atmo or apo_above_air))
        parts = int(slow.get("parts", -1) or -1)
        lf = float(slow.get("lf", -1.0))
        # Thrust 0 with fuel still in this stage is a tip-over or ullage,
        # not a reason to dump the booster. Only active-dry engines.
        flameout = bool(slow.get("flameout_eng"))
        wreck = parts == 0
        if math.isfinite(surf) and surf < -2.0 and math.isfinite(spd) and spd > 15.0:
            wreck = True

        flags: list[str] = []
        if in_atmo:
            flags.append("ATMO")
        if dipping:
            flags.append("DIP")
        if escaping:
            flags.append("ESC")
        if flameout:
            flags.append("FLAME")
        if wreck:
            flags.append("WRECK")

        return FlightState(
            body=body_name,
            situation=sit,
            alt=alt,
            peri=peri,
            apo=apo,
            ecc=ecc,
            sma=sma,
            q=q,
            lf=lf,
            ox=float(slow.get("ox", -1.0)),
            stage=int(slow.get("stage", -1) or -1),
            throttle=throttle,
            thrust=thrust,
            max_thrust=max_thrust,
            parts=parts,
            warp=float(slow.get("warp", 0.0)),
            rails=int(slow.get("rails", 0) or 0),
            rmax=int(slow.get("rmax", 0) or 0),
            t_pe=t_pe,
            t_ap=t_ap,
            atm_depth=atm_depth,
            in_atmo=in_atmo,
            dipping=dipping,
            escaping=escaping,
            flameout=flameout,
            wreck=wreck,
            heading_to_peri=heading_to_peri,
            surf=surf,
            spd=spd,
            vs=vs,
            flags=tuple(flags),
        )

    def _apply_uplink(self, state: FlightState) -> None:
        """Gene's file. ``status`` watches leave ``uplink=False`` so they do not steal."""
        from uplink import desk, take

        cmd = take()
        if cmd is None:
            if desk.hold:
                freeze(self.session)
            return
        if cmd.verb in {"abort", "freeze", "hold"} and _pad_radio_off(state):
            desk.hold = False
            log.info("uplink ignored on pad: %s", cmd.raw)
            try:
                from flightlog import event

                event("uplink", f"ignored on pad {cmd.raw}")
            except Exception:
                pass
            return
        if cmd.verb in {"abort", "freeze", "hold"}:
            freeze(self.session)
        if cmd.verb == "abort":
            reason = cmd.arg or cmd.raw
            raise MissionAbort(f"uplink abort {reason}".strip())

    def pulse(self, tag: str = "", *, force_log: bool = False) -> FlightState:
        """Wait for a stream batch, read state, log at 1 Hz, abort on wreck."""
        self.wait()
        state = self.snapshot()
        now = time.monotonic()
        if force_log or now - self._last_log >= 1.0:
            self._last_log = now
            _say(state.line(tag), self.on_log)
        try:
            from flightlog import record

            ut = None
            try:
                ut = float(self.session.space_center.ut)
            except Exception:
                ut = None
            record(state, tag, ut=ut)
        except Exception:
            pass
        if state.wreck:
            raise MissionAbort(state.line(tag) or "wreck")
        if self._uplink:
            self._apply_uplink(state)
        return state

    def relight(self, *, end_stage: int = 0) -> bool:
        """Stage or enable engines until there is thrust, or give up."""
        from parts import enable_engines

        vessel = self._ensure_bound()
        if vessel.available_thrust > 0:
            return True
        dry = bool(self._slow.get("flameout_eng"))
        if (not dry) and vessel.control.current_stage > end_stage:
            from parts import should_stage

            try:
                dry = should_stage(
                    vessel, self.session.profile.fuels, end_stage
                )
            except Exception:
                dry = False
        if dry and vessel.control.current_stage > end_stage:
            before = vessel.control.current_stage
            vessel.control.activate_next_stage()
            time.sleep(0.4)
            _say(f"relight staged {before} → {vessel.control.current_stage}", self.on_log)
        if vessel.available_thrust > 0:
            return True
        enable_engines(vessel)
        time.sleep(0.2)
        if vessel.available_thrust > 0:
            return True
        # Twin Terriers: one dry+active, one fueled+idle (Grok 4761 Mun).
        try:
            for eng in vessel.parts.engines:
                try:
                    if eng.has_fuel:
                        eng.active = True
                    elif eng.active:
                        eng.active = False
                except Exception:
                    continue
        except Exception:
            pass
        time.sleep(0.2)
        return vessel.available_thrust > 0


def heartbeat(
    session: Session,
    on_log: Callable[[str], None] | None = None,
    tag: str = "",
    watch: FlightWatch | None = None,
) -> str:
    """One compact line. Reuse ``watch`` when the process already has one."""
    if watch is not None:
        state = watch.pulse(tag, force_log=True)
        return state.line(tag)
    created = FlightWatch(session, on_log=on_log)
    try:
        state = created.pulse(tag, force_log=True)
        return state.line(tag)
    finally:
        created.close()


def check_alive(
    session: Session,
    *,
    need_thrust: bool = False,
    watch: FlightWatch | None = None,
) -> None:
    """Raise :class:`MissionAbort` if the vessel is a wreck or a lithobrake."""
    if watch is not None:
        state = watch.snapshot()
    else:
        created = FlightWatch(session)
        try:
            state = created.snapshot()
        finally:
            created.close()
    if state.wreck:
        raise MissionAbort(state.line() or "wreck")
    if (
        math.isfinite(state.peri)
        and state.peri < 0.0
        and math.isfinite(state.alt)
        and state.alt < 25_000
        and not state.in_atmo
    ):
        raise MissionAbort(f"lithobrake peri={state.peri:.0f} alt={state.alt:.0f}")
    if need_thrust and state.thrust <= 0 and state.alt < 20_000:
        raise MissionAbort(f"no thrust at alt={state.alt:.0f}")


def atmosphere_floor(body: Any, extra: float = 10_000.0) -> float | None:
    """Periapsis that still dips into atmosphere. None if the body has no air."""
    try:
        if not body.has_atmosphere:
            return None
        return float(body.atmosphere_depth) + extra
    except Exception:
        return None


def atmosphere_danger(session: Session, extra: float = 10_000.0) -> str | None:
    """If we are in atmosphere *or* peri will take us there, return a reason."""
    watch = FlightWatch(session, extra=extra)
    try:
        return watch.snapshot().danger()
    finally:
        watch.close()


def require_parking(
    state: FlightState,
    *,
    min_peri: float,
    max_apo: float | None = None,
    max_ecc: float | None = 0.25,
) -> None:
    """Abort unless this looks like a bound parking orbit."""
    if state.escaping:
        raise MissionAbort(f"not parked — escaping {state.line()}")
    if not math.isfinite(state.peri) or state.peri < min_peri:
        raise MissionAbort(
            f"not parked — peri={state.peri:.0f} < {min_peri:.0f} {state.line()}"
        )
    if max_apo is not None and math.isfinite(state.apo) and state.apo > max_apo:
        raise MissionAbort(
            f"not parked — apo={state.apo:.0f} > {max_apo:.0f} {state.line()}"
        )
    if max_ecc is not None and math.isfinite(state.ecc) and state.ecc > max_ecc:
        raise MissionAbort(
            f"not parked — ecc={state.ecc:.3f} {state.line()}"
        )


def recover_periapsis(
    session: Session,
    *,
    extra: float = 10_000.0,
    on_log: Callable[[str], None] | None = None,
    abort: Callable[[], bool] | None = None,
    apo_limit: float = 500_000.0,
    watch: FlightWatch | None = None,
) -> None:
    """Get bound, then raise peri above atmosphere + extra.

    Prograde *at peri* raises apo, not peri (L-016). Climb only while
    actually in atmosphere and apo is still modest; otherwise coast to
    apo and burn prograde there. Retrograde only when unbound and above
    the air. Hold a mode until AP is aligned; do not flip every tick.
    """
    from warp import warp_to_ut

    v = session.active_vessel
    body = v.orbit.body
    floor = atmosphere_floor(body, extra)
    if floor is None:
        return
    freeze(session, throttle=True)
    _say(f"recover periapsis → {floor:.0f} m", on_log)
    ap = v.auto_pilot
    ap.reference_frame = v.orbital_reference_frame
    set_autopilot(ap, True)
    v.control.sas = False
    pointed: str | None = None

    def _point(want: str) -> None:
        nonlocal pointed
        if want == pointed:
            return
        v.control.throttle = 0.0
        ap.target_direction = (0.0, 1.0, 0.0) if want == "prograde" else (0.0, -1.0, 0.0)
        aligned = wait_aligned(ap, timeout=10.0, max_error=20.0)
        err = None
        try:
            from orientation import autopilot_error

            err = autopilot_error(ap)
        except Exception:
            pass
        _say(
            f"AP {want} aligned={aligned} err={err if err is not None else '?'}",
            on_log,
        )
        pointed = want

    own = watch is None
    if own:
        watch = FlightWatch(session, extra=extra, on_log=on_log, uplink=True)
    try:
        try:
            while True:
                if abort and abort():
                    raise MissionAbort("recover aborted")
                state = watch.pulse("recover ")
                from uplink import holding

                if holding():
                    continue
                if (not state.escaping) and state.peri >= floor and not state.in_atmo:
                    break
                if state.apo > apo_limit * 4 and state.peri < floor:
                    raise MissionAbort(
                        f"recover apo runaway {state.apo:.0f} peri={state.peri:.0f}"
                    )

                if state.escaping and not state.in_atmo:
                    want, throttle = "retrograde", 1.0
                elif state.in_atmo and state.apo < apo_limit:
                    want, throttle = "prograde", 1.0
                elif state.dipping and not state.heading_to_peri:
                    want, throttle = "prograde", 1.0
                else:
                    # At/toward peri, or apo already huge: coast. Warp to
                    # apo once we are out of the air.
                    want, throttle = "prograde", 0.0
                    if (
                        not state.in_atmo
                        and state.dipping
                        and state.heading_to_peri
                        and math.isfinite(state.t_ap)
                        and state.t_ap > 40.0
                    ):
                        v.control.throttle = 0.0
                        try:
                            warp_to_ut(
                                session,
                                session.space_center.ut + min(state.t_ap - 20.0, 600.0),
                                abort=abort,
                                watch=watch,
                            )
                        except Exception:
                            pass
                        continue

                _point(want)
                if throttle > 0 and not watch.relight(end_stage=0):
                    raise MissionAbort("no thrust while recovering")
                v.control.throttle = throttle

            state = watch.snapshot()
            if state.escaping or state.peri < floor:
                raise MissionAbort(f"recover unfinished {state.line()}")
        finally:
            try:
                v.control.throttle = 0.0
                set_autopilot(ap, False)
            except Exception:
                pass
        watch.pulse("recover-done ", force_log=True)
    finally:
        if own:
            watch.close()


def _pad_radio_off(state: FlightState) -> bool:
    """Stale ESC abort of a wreck must not kill a Kerbin pad start (L-026)."""
    sit = (state.situation or "").lower().replace("-", "_")
    if sit in {"pre_launch", "prelaunch"}:
        return True
    if not math.isfinite(state.alt) or state.alt >= 200.0:
        return False
    if sit in {"landed", "splashed"}:
        return True
    return (state.body or "").lower() == "kerbin"


def freeze(session: Session, *, throttle: bool = True) -> None:
    """Cut rails. Do not cut throttle on a lithobrake (L-035)."""
    from warp import drop_warp

    drop_warp(session)
    keep_throttle = False
    try:
        v = session.active_vessel
        peri = float(v.orbit.periapsis_altitude)
        alt = float(v.flight().mean_altitude)
        keep_throttle = peri < 0 and alt < 30_000
        if keep_throttle:
            v.control.throttle = 1.0
            log.info("freeze: lithobrake — throttle 1, not 0")
    except Exception:
        pass
    if throttle and not keep_throttle:
        try:
            session.active_vessel.control.throttle = 0.0
        except Exception:
            pass
