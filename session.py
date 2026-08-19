"""One kRPC connection shared by every manager.

The old repo opened a new ``krpc.connect()`` in almost every class. That
fought RemoteTech and leaked streams. Call :meth:`Session.connect`
explicitly. One Session per process.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

from profile import STOCK, GameProfile, detect_profile

log = logging.getLogger("kspstuff")


class SessionError(RuntimeError):
    """Connection, missing service, or wrong-scene failure."""


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


@dataclass(slots=True)
class ConnectionSettings:
    name: str = "kspstuff"
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
    ) -> None:
        self.settings = settings or ConnectionSettings()
        self._profile_explicit = profile is not None
        self.profile = profile or STOCK
        self.conn: Any = None
        self.space_center: Any = None
        self.mech_jeb: Any = None
        self.remote_tech: Any = None
        self.status = ServiceStatus()
        self._lock = threading.RLock()
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
        self.conn = None
        self.space_center = None
        self.mech_jeb = None
        self.remote_tech = None
        self.status = ServiceStatus()
        if conn is not None:
            try:
                conn.close()
            except Exception:
                log.debug("kRPC close failed", exc_info=True)

    def __enter__(self) -> Session:
        if not self.connected:
            self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def require_connected(self) -> None:
        if self.conn is None or self.space_center is None:
            raise SessionError("Not connected to kRPC.")

    def require_mechjeb(self) -> Any:
        self.require_connected()
        if self.mech_jeb is None:
            raise SessionError(
                "MechJeb kRPC service is missing. Install MechJeb2 and KRPC.MechJeb."
            )
        return self.mech_jeb

    def require_remotetech(self) -> Any:
        self.require_connected()
        if self.remote_tech is None:
            raise SessionError(
                "RemoteTech kRPC service is missing. For RP-1 use CommNet/RealAntennas."
            )
        return self.remote_tech

    @property
    def active_vessel(self) -> Any:
        self.require_connected()
        return self.space_center.active_vessel

    @property
    def bodies(self) -> dict:
        self.require_connected()
        return self.space_center.bodies

    @property
    def home_body(self) -> Any:
        return self.profile.resolve_home_body(self.bodies)

    def switch_to(self, vessel: Any, settle: float | None = None) -> None:
        """Make ``vessel`` active and wait for KSP to load it."""
        self.require_connected()
        sc = self.space_center
        with self._lock:
            if sc.active_vessel != vessel:
                sc.active_vessel = vessel
                time.sleep(self.switch_settle_s if settle is None else settle)

    def add_stream(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """``conn.add_stream``. Properties must use ``getattr`` form.

        ``add_stream(getattr, flight, "mean_altitude")`` is correct.
        ``add_stream(flight.mean_altitude)`` already ran the RPC and
        passes a float. Setters cannot be streamed. Keep the target
        object alive until ``stream.remove()``.
        """
        self.require_connected()
        return self.conn.add_stream(func, *args, **kwargs)

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
