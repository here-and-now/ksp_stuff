"""One kRPC connection shared by every manager.

The old repo opened a new ``krpc.connect()`` in almost every class. That
fought RemoteTech and leaked streams. Call :meth:`Session.connect`
explicitly. One Session per process.

One **control** writer (``name=kspstuff``). GET readers
(``name=kspstuff-read``, ``readonly=True``) are legal while
``flight.lock`` is live. Readers must not write Control, scene,
``active_vessel``, jsonl, ``ship.md``, or last-flight. They
``stream.remove()`` on close.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

from profile import STOCK, GameProfile, detect_profile

log = logging.getLogger("kspstuff")

WRITE_CLIENT = "kspstuff"
READ_CLIENT = "kspstuff-read"
_SC_WRITE_METHODS = frozenset(
    {
        "launch_vessel",
        "save",
        "load",
        "warp_to",
        "create_kerbal",
        "transfer_crew",
        "launch_vessel_from_vab",
        "launch_vessel_from_sph",
    }
)
_SC_WRITE_ATTRS = frozenset(
    {
        "active_vessel",
        "rails_warp_factor",
        "physics_warp_factor",
        "target_body",
        "target_vessel",
        "target_docking_port",
        "ut",
    }
)
_CTRL_WRITE_METHODS = frozenset(
    {
        "activate_next_stage",
        "set_action_group",
        "toggle_action_group",
        "set_throttle",
    }
)
_CTRL_WRITE_ATTRS = frozenset(
    {
        "throttle",
        "sas",
        "rcs",
        "gear",
        "lights",
        "brakes",
        "abort",
        "pitch",
        "yaw",
        "roll",
        "forward",
        "up",
        "right",
        "wheel_steer",
        "wheel_throttle",
        "current_stage",
        "input_mode",
        "sas_mode",
        "speed_mode",
    }
)
_AP_WRITE_METHODS = frozenset({"engage", "disengage", "wait", "target_pitch_and_heading"})
_AP_WRITE_ATTRS = frozenset(
    {
        "engaged",
        "target_pitch",
        "target_heading",
        "target_roll",
        "target_direction",
        "target_pitch_and_heading",
        "reference_frame",
        "stopping_time",
        "deceleration_time",
        "attenuation_angle",
        "auto_tune",
        "time_to_peak",
        "overshoot",
        "pitch_pid_gains",
        "roll_pid_gains",
        "yaw_pid_gains",
    }
)


class SessionError(RuntimeError):
    """Connection, missing service, or wrong-scene failure."""


class ReadOnlyError(SessionError):
    """Reader Session refused a Control / scene / active_vessel write."""


def _krpc_service_names(conn: Any) -> tuple[str, ...]:
    """``get_services()`` is a protobuf ``Services`` message (L-040)."""
    try:
        raw = conn.krpc.get_services()
    except Exception:
        log.debug("Could not list kRPC services", exc_info=True)
        return ()
    items = getattr(raw, "services", None)
    if items is None:
        if isinstance(raw, (list, tuple)):
            items = raw
        else:
            return ()
    names: list[str] = []
    for svc in items:
        n = getattr(svc, "name", None)
        if n:
            names.append(str(n))
    return tuple(names)


def _refuse(what: str) -> None:
    raise ReadOnlyError(f"read-only Session refused {what}")


class _ReadProxy:
    """GET-through proxy. Setters and named write methods raise."""

    __slots__ = ("_inner", "_methods", "_setters", "_label")

    def __init__(
        self,
        inner: Any,
        *,
        methods: frozenset[str],
        setters: frozenset[str],
        label: str,
    ) -> None:
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "_methods", methods)
        object.__setattr__(self, "_setters", setters)
        object.__setattr__(self, "_label", label)

    def __getattr__(self, name: str) -> Any:
        if name in object.__getattribute__(self, "_methods"):
            label = object.__getattribute__(self, "_label")

            def _blocked(*_a: Any, **_k: Any) -> Any:
                _refuse(f"{label}.{name}")

            return _blocked
        return getattr(object.__getattribute__(self, "_inner"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in object.__getattribute__(self, "_setters"):
            _refuse(f"{object.__getattribute__(self, '_label')}.{name}")
        setattr(object.__getattribute__(self, "_inner"), name, value)


class _ReadOnlyControl(_ReadProxy):
    def __init__(self, inner: Any) -> None:
        super().__init__(
            inner, methods=_CTRL_WRITE_METHODS, setters=_CTRL_WRITE_ATTRS, label="control"
        )


class _ReadOnlyAutopilot(_ReadProxy):
    def __init__(self, inner: Any) -> None:
        super().__init__(
            inner, methods=_AP_WRITE_METHODS, setters=_AP_WRITE_ATTRS, label="auto_pilot"
        )


class _ReadOnlyVessel:
    __slots__ = ("_inner",)

    def __init__(self, inner: Any) -> None:
        object.__setattr__(self, "_inner", inner)

    def __getattr__(self, name: str) -> Any:
        if name == "control":
            return _ReadOnlyControl(getattr(object.__getattribute__(self, "_inner"), "control"))
        if name == "auto_pilot":
            return _ReadOnlyAutopilot(
                getattr(object.__getattribute__(self, "_inner"), "auto_pilot")
            )
        if name == "recover":

            def _blocked(*_a: Any, **_k: Any) -> Any:
                _refuse("vessel.recover")

            return _blocked
        return getattr(object.__getattribute__(self, "_inner"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        _refuse(f"vessel.{name}")


class _ReadOnlySpaceCenter(_ReadProxy):
    def __init__(self, inner: Any) -> None:
        super().__init__(
            inner, methods=_SC_WRITE_METHODS, setters=_SC_WRITE_ATTRS, label="space_center"
        )

    def __getattr__(self, name: str) -> Any:
        if name == "vessels":
            raw = getattr(object.__getattribute__(self, "_inner"), "vessels")
            try:
                return [_ReadOnlyVessel(v) for v in (raw or [])]
            except TypeError:
                return raw
        if name == "active_vessel":
            raw = getattr(object.__getattribute__(self, "_inner"), "active_vessel")
            return None if raw is None else _ReadOnlyVessel(raw)
        return super().__getattr__(name)


class _ReadOnlyKrpc(_ReadProxy):
    def __init__(self, inner: Any) -> None:
        super().__init__(
            inner,
            methods=frozenset(),
            setters=frozenset({"game_scene", "paused"}),
            label="krpc",
        )


@dataclass(slots=True)
class ConnectionSettings:
    name: str = WRITE_CLIENT
    address: str = "127.0.0.1"
    rpc_port: int = 50000
    stream_port: int = 50001


@dataclass(slots=True)
class ServiceStatus:
    krpc_version: str = ""
    services: tuple[str, ...] = ()
    mechjeb: bool = False
    remotetech: bool = False
    far: bool = False
    commnet: bool = False
    realantennas: bool = False


class Session:
    """Thin wrapper around a kRPC client plus the active game profile."""

    def __init__(
        self,
        settings: ConnectionSettings | None = None,
        profile: GameProfile | None = None,
        *,
        readonly: bool = False,
    ) -> None:
        self.readonly = bool(readonly)
        base = settings or ConnectionSettings()
        if self.readonly:
            self.settings = ConnectionSettings(
                name=READ_CLIENT,
                address=base.address,
                rpc_port=base.rpc_port,
                stream_port=base.stream_port,
            )
        else:
            self.settings = base
        self._profile_explicit = profile is not None
        self.profile = profile or STOCK
        self.conn: Any = None
        self.space_center: Any = None
        self.mech_jeb: Any = None
        self.remote_tech: Any = None
        self.status = ServiceStatus()
        self._lock = threading.RLock()
        self._streams: list[Any] = []
        self.switch_settle_s = 1.5

    @property
    def connected(self) -> bool:
        return self.conn is not None

    def connect(self, profile: GameProfile | str | None = None) -> None:
        try:
            import krpc
        except ImportError as exc:
            raise SessionError(
                "The krpc package is not installed. Use the project venv:\n"
                "  source .venv/bin/activate"
            ) from exc

        self.close()
        try:
            self.conn = krpc.connect(
                name=self.settings.name,
                address=self.settings.address,
                rpc_port=self.settings.rpc_port,
                stream_port=self.settings.stream_port,
            )
        except SessionError:
            raise
        except Exception as exc:
            raise SessionError(
                f"Could not reach kRPC at {self.settings.address}:"
                f"{self.settings.rpc_port}. Is KSP running with kRPC? ({exc})"
            ) from exc

        self.space_center = self.conn.space_center
        if self.readonly:
            self._wrap_readonly()
        try:
            self._probe_services()
            if profile is not None:
                self._apply_profile(profile)
            elif self._profile_explicit:
                self._apply_profile(self.profile)
            else:
                self._apply_profile("auto")
            self.profile.resolve_home_body(self.space_center.bodies)
        except SessionError:
            self.close()
            raise
        except LookupError as exc:
            self.close()
            raise SessionError(str(exc)) from exc
        except Exception:
            self.close()
            raise
        log.info(
            "Connected to kRPC %s  profile=%s  services=%s",
            self.status.krpc_version,
            self.profile.name,
            ", ".join(self.status.services) or "(none)",
        )

    def close(self) -> None:
        conn = self.conn
        streams = list(self._streams)
        self._streams.clear()
        self.conn = None
        self.space_center = None
        self.mech_jeb = None
        self.remote_tech = None
        self.status = ServiceStatus()
        if conn is None and not streams:
            return

        def _close() -> None:
            for stream in streams:
                try:
                    stream.remove()
                except Exception:
                    log.debug("kRPC stream.remove failed", exc_info=True)
            if conn is None:
                return
            try:
                conn.close()
            except Exception:
                log.debug("kRPC close failed", exc_info=True)

        thread = threading.Thread(target=_close, daemon=True, name="krpc-close")
        thread.start()
        thread.join(5.0)
        if thread.is_alive():
            log.warning("kRPC close hung 5s — abandoning connection")

    def __enter__(self) -> Session:
        if not self.connected:
            self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def require_connected(self) -> None:
        if self.conn is None or self.space_center is None:
            raise SessionError("Not connected to kRPC.")

    def require_write(self, what: str = "control") -> None:
        if self.readonly:
            _refuse(what)

    def _wrap_readonly(self) -> None:
        sc = self.space_center
        if sc is not None and not isinstance(sc, _ReadOnlySpaceCenter):
            self.space_center = _ReadOnlySpaceCenter(sc)
        conn = self.conn
        krpc = getattr(conn, "krpc", None) if conn is not None else None
        if krpc is not None and not isinstance(krpc, _ReadOnlyKrpc):
            try:
                conn.krpc = _ReadOnlyKrpc(krpc)
            except Exception:
                log.debug("could not wrap krpc for read-only", exc_info=True)

    @property
    def active_vessel(self) -> Any:
        self.require_connected()
        vessel = self.space_center.active_vessel
        if self.readonly and vessel is not None and not isinstance(vessel, _ReadOnlyVessel):
            return _ReadOnlyVessel(vessel)
        return vessel

    @property
    def bodies(self) -> dict:
        self.require_connected()
        return self.space_center.bodies

    @property
    def home_body(self) -> Any:
        return self.profile.resolve_home_body(self.bodies)

    def switch_to(self, vessel: Any, settle: float | None = None) -> None:
        """Make ``vessel`` active and wait for KSP to load it."""
        self.require_write("active_vessel")
        self.require_connected()
        sc = self.space_center
        inner = getattr(vessel, "_inner", vessel)
        with self._lock:
            if sc.active_vessel != inner and sc.active_vessel != vessel:
                sc.active_vessel = inner
                time.sleep(self.switch_settle_s if settle is None else settle)

    def add_stream(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """``conn.add_stream``. Properties must use ``getattr`` form.

        ``add_stream(getattr, flight, "mean_altitude")`` is correct.
        ``add_stream(flight.mean_altitude)`` already ran the RPC and
        passes a float. Setters cannot be streamed. Keep the target
        object alive until ``stream.remove()``.
        """
        self.require_connected()
        stream = self.conn.add_stream(func, *args, **kwargs)
        self._streams.append(stream)
        return stream

    def _probe_services(self) -> None:
        conn = self.conn
        assert conn is not None
        version = ""
        try:
            version = conn.krpc.get_status().version
        except Exception:
            log.debug("Could not read kRPC version", exc_info=True)

        names = list(_krpc_service_names(conn))

        def grab(attr: str) -> Any:
            try:
                return getattr(conn, attr)
            except Exception:
                return None

        # RemoteTech.dll ships *inside* GameData/kRPC: getattr is a stub, not
        # "the mod is installed". ``status.services`` is the protobuf inventory.
        # MechJeb / RemoteTech **require** helpers were 2022 stock-Mun; letsgrok
        # does not install them. Probe flags only — do not raise if missing.
        self.mech_jeb = grab("mech_jeb")
        self.remote_tech = grab("remote_tech")

        far = False
        commnet = False
        realantennas = False
        sc = self.space_center
        try:
            far = bool(sc.far_available)
        except Exception:
            pass
        try:
            vessel = sc.active_vessel
            _ = vessel.comms.can_communicate
            commnet = True
            realantennas = bool(vessel.parts.with_module("ModuleRealAntenna"))
        except Exception:
            commnet = False

        self.status = ServiceStatus(
            krpc_version=version,
            services=tuple(names),
            mechjeb=self.mech_jeb is not None,
            remotetech=self.remote_tech is not None,
            far=far,
            commnet=commnet,
            realantennas=realantennas,
        )

    def _apply_profile(self, profile: GameProfile | str | None) -> None:
        if profile is None:
            return
        if isinstance(profile, GameProfile):
            self.profile = profile
            return
        if profile == "auto":
            self.profile = detect_profile(self.space_center.bodies)
            return
        from profile import PROFILES

        if profile not in PROFILES:
            raise SessionError(f"Unknown profile {profile!r}")
        self.profile = PROFILES[profile]
