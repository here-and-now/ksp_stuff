"""Where ``.craft`` files live, and how kRPC launches them.

kRPC never opens the VAB parts list. ``launch_vessel('VAB', name, ...)``
loads ``saves/<save>/Ships/VAB/<name>.craft`` onto a pad. So the pipeline
is: write a craft file here → copy into that folder → launch.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from craft import Craft
from session import ConnectionSettings, Session, SessionError

log = logging.getLogger("kspstuff")

SKIP_SAVES = {"training", "scenarios", "missions"}
STEAM_KSP = Path.home() / ".steam/steam/steamapps/common/Kerbal Space Program"

# Empty Mk1/Mk1-3 pods are not probes. KSP then shows "No Control" and
# kRPC WaitForVesselPreFlightChecks sits on Launch anyway / Cancel (L-017).
# Assigned/missing kerbals also launch empty (L-018).
STOCK_CREW: tuple[str, ...] = (
    "Jebediah Kerman",
    "Valentina Kerman",
    "Bill Kerman",
    "Bob Kerman",
)
_CREATED_PILOT = "Grok Kerman"


def _status_name(value: Any) -> str:
    name = getattr(value, "name", None)
    if isinstance(name, str):
        return name.lower()
    text = str(value)
    return text.rsplit(".", 1)[-1].lower()


def _kerbal_available(kerbal: Any) -> bool:
    try:
        if bool(kerbal.on_mission):
            return False
    except Exception:
        pass
    return _status_name(getattr(kerbal, "roster_status", None)) == "available"


def default_crew(session: Session, seats: int = 1) -> list[str]:
    """Kerbal(s) currently *available* — never assigned/missing/dead."""
    n = max(1, seats)
    sc = session.space_center
    picked: list[str] = []
    for name in STOCK_CREW + (_CREATED_PILOT,):
        try:
            kerbal = sc.get_kerbal(name)
        except Exception:
            continue
        if kerbal is not None and _kerbal_available(kerbal):
            picked.append(kerbal.name)
            if len(picked) >= n:
                break
    while len(picked) < n:
        name = _CREATED_PILOT if _CREATED_PILOT not in picked else f"Grok Kerman {int(time.time()) % 10000}"
        try:
            existing = sc.get_kerbal(name)
        except Exception:
            existing = None
        if existing is None:
            log.info("create_kerbal %s Pilot", name)
            sc.create_kerbal(name, "Pilot", True)
            time.sleep(0.2)
            picked.append(name)
        elif _kerbal_available(existing):
            picked.append(existing.name)
        else:
            name = f"Grok Kerman {int(time.time()) % 10000}"
            sc.create_kerbal(name, "Pilot", True)
            picked.append(name)
    log.info("Launch crew: %s", ", ".join(picked[:n]))
    return picked[:n]


def ensure_kerbal(session: Session, name: str, *, trait: str = "Pilot") -> str | None:
    """Roster that exact kerbal: create if missing, seat if available."""
    sc = session.space_center
    try:
        kerbal = sc.get_kerbal(name)
    except Exception:
        kerbal = None
    if kerbal is None:
        log.info("create_kerbal %s %s", name, trait)
        try:
            sc.create_kerbal(name, trait, True)
            time.sleep(0.2)
            kerbal = sc.get_kerbal(name)
        except Exception:
            log.warning("create_kerbal %s failed", name, exc_info=True)
            return None
    if kerbal is not None and _kerbal_available(kerbal):
        return kerbal.name
    if kerbal is not None:
        log.warning("kerbal %s not available (status=%s)", name, getattr(kerbal, "roster_status", "?"))
    return None


def resolve_crew(session: Session, wanted: list[str] | None, seats: int = 1) -> list[str]:
    """Named seat from current.md: create the kerbal if they are not on the roster."""
    n = max(1, seats)
    picked: list[str] = []
    if wanted:
        for name in wanted:
            seated = ensure_kerbal(session, name)
            if seated and seated not in picked:
                picked.append(seated)
            if len(picked) >= n:
                log.info("Launch crew: %s", ", ".join(picked))
                return picked
    if len(picked) < n:
        picked.extend(x for x in default_crew(session, seats=n) if x not in picked)
    log.info("Launch crew: %s", ", ".join(picked[:n]))
    return picked[:n]


def _exc_text(exc: BaseException) -> str:
    parts = [str(exc)]
    cause = exc.__cause__ or exc.__context__
    if cause is not None:
        parts.append(str(cause))
    return "\n".join(parts).lower()


def _savegame_nre(exc: BaseException) -> bool:
    """launch_vessel(recover=True) SaveGame NRE on a dirty leftover (L-022)."""
    text = _exc_text(exc)
    return (
        "object reference not set" in text
        or "nullreference" in text
        or "savegame" in text
        or "flightstate" in text
    )


def _site_not_clear(exc: BaseException) -> bool:
    """KSP pre-flight: leftover craft still occupying the pad (L-027)."""
    text = _exc_text(exc)
    return "launch site not clear" in text or "site not clear" in text


# Stock KSC. Used when biome is missing (packed flying leftover).
_SITE_LL: dict[str, tuple[float, float]] = {
    "LaunchPad": (-0.0972, -74.5577),
    "Runway": (-0.0486, -74.7246),
}
_PAD_SITS = frozenset({"pre_launch", "prelaunch", "landed", "splashed", "flying"})


def _near_site(lat: float, lon: float, site: str) -> bool:
    want = _SITE_LL.get(site)
    if want is None:
        return False
    dlat = abs(lat - want[0])
    dlon = abs((lon - want[1] + 180.0) % 360.0 - 180.0)
    return dlat < 0.05 and dlon < 0.05


def _on_launch_site(session: Session, vessel: Any, site: str) -> bool:
    sit = _status_name(getattr(vessel, "situation", None))
    if sit not in _PAD_SITS:
        return False
    home = "kerbin"
    try:
        home = session.home_body.name.lower()
    except Exception:
        pass
    try:
        body = vessel.orbit.body.name.lower()
    except Exception:
        body = ""
    if body and body != home:
        return False
    biome = ""
    try:
        biome = (getattr(vessel, "biome", None) or "").lower().replace(" ", "")
    except Exception:
        pass
    site_key = site.lower().replace(" ", "")
    if site_key and site_key in biome:
        return True
    try:
        if bool(vessel.recoverable) and sit in (
            "pre_launch",
            "prelaunch",
            "landed",
            "splashed",
        ):
            return True
    except Exception:
        pass
    if sit != "flying":
        return False
    try:
        flt = vessel.flight()
        if float(flt.mean_altitude) > 200:
            return False
        return _near_site(float(flt.latitude), float(flt.longitude), site)
    except Exception:
        return False


def _recover_one(session: Session, vessel: Any) -> bool:
    name = "?"
    try:
        name = vessel.name
    except Exception:
        pass
    rec = False
    try:
        rec = bool(vessel.recoverable)
    except Exception:
        rec = False
    if not rec:
        # Abort leftover can still be flying at 82 m; recover() needs landed.
        log.info("pad occupant %s not recoverable yet — switch and wait", name)
        try:
            session.switch_to(vessel)
            try:
                vessel.control.throttle = 0.0
            except Exception:
                pass
            deadline = time.monotonic() + 15.0
            while time.monotonic() < deadline:
                try:
                    rec = bool(vessel.recoverable)
                except Exception:
                    rec = False
                if rec:
                    break
                time.sleep(0.4)
        except Exception as exc:
            log.warning("switch to pad occupant %s: %s", name, exc)
            return False
    if not rec:
        log.warning("pad occupant %s still not recoverable", name)
        return False
    try:
        log.info("recover pad occupant %s", name)
        vessel.recover()
        time.sleep(1.0)
        return True
    except Exception as exc:
        log.warning("vessel.recover %s: %s", name, exc)
        return False


def clear_launch_site(session: Session, site: str = "LaunchPad") -> int:
    """Recover craft occupying the pad. No Recover click (L-027)."""
    session.require_connected()
    try:
        pool = list(session.space_center.vessels)
    except Exception as exc:
        log.warning("vessels for pad clear: %s", exc)
        return 0
    n = 0
    for vessel in pool:
        try:
            if not _on_launch_site(session, vessel, site):
                continue
        except Exception:
            continue
        if _recover_one(session, vessel):
            n += 1
    if n:
        log.info("cleared %s occupant(s) from %s", n, site)
        try:
            go_space_center(session)
        except Exception as exc:
            log.warning("go_space_center after pad clear: %s", exc)
        time.sleep(1.0)
    return n


def go_space_center(session: Session, *, timeout: float = 45.0) -> None:
    """Leave flight/editor/dialogs for the KSC overview. No human click.

    Always apply the scene setter. A leftover dirty flight can still
    report ``game_scene == space_center`` (L-022).
    """
    session.require_connected()
    krpc = session.conn.krpc
    log.info("scene %s → space_center", game_scene(session))
    try:
        krpc.game_scene = krpc.GameScene.space_center
    except Exception as exc:
        log.warning("game_scene setter failed (%s); load_space_center", exc)
        session.space_center.load_space_center()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if game_scene(session) == "space_center":
            session.space_center = session.conn.space_center
            time.sleep(1.0)
            return
        time.sleep(0.3)
    raise SessionError(
        f"timed out waiting for space_center (still {game_scene(session)})"
    )


def _reload_space_center(session: Session, *, timeout: float = 45.0) -> None:
    """Force a KSC reload after SaveGame NRE. No Recover click (L-022)."""
    session.require_connected()
    log.info("reload space_center after SaveGame failure")
    try:
        session.space_center.load_space_center()
    except Exception as exc:
        log.warning("load_space_center: %s; game_scene setter", exc)
        try:
            krpc = session.conn.krpc
            krpc.game_scene = krpc.GameScene.space_center
        except Exception:
            _abort_preflight_hang(session.settings)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if game_scene(session) == "space_center":
            session.space_center = session.conn.space_center
            time.sleep(1.5)
            return
        time.sleep(0.3)
    log.warning("reload space_center still %s", game_scene(session))


def _abort_preflight_hang(settings: ConnectionSettings) -> None:
    """Second kRPC client: hung launch_vessel yields; this one changes scene."""
    try:
        import krpc
    except ImportError:
        return
    conn = None
    try:
        conn = krpc.connect(
            name="kspstuff-abort",
            address=settings.address,
            rpc_port=settings.rpc_port,
            stream_port=settings.stream_port,
        )
        conn.krpc.game_scene = conn.krpc.GameScene.space_center
        log.info("abort client set game_scene=space_center")
        time.sleep(2.0)
    except Exception:
        log.debug("abort client failed", exc_info=True)
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


@dataclass(slots=True)
class CraftInfo:
    name: str
    facility: str
    path: Path
    parts: int | None = None
    description: str = ""


@dataclass
class Hangar:
    ksp_root: Path
    save: str

    @property
    def save_dir(self) -> Path:
        return self.ksp_root / "saves" / self.save

    def ships(self, facility: str = "VAB") -> Path:
        return self.save_dir / "Ships" / facility

    def subassemblies(self) -> Path:
        return self.save_dir / "Subassemblies"

    def list_saves(self) -> list[str]:
        root = self.ksp_root / "saves"
        if not root.is_dir():
            return []
        names = []
        for p in sorted(root.iterdir()):
            if p.is_dir() and p.name not in SKIP_SAVES and not p.name.startswith("."):
                names.append(p.name)
        return names

    def list_crafts(self, facility: str = "VAB") -> list[CraftInfo]:
        folder = self.ships(facility)
        if not folder.is_dir():
            return []
        out: list[CraftInfo] = []
        for path in sorted(folder.glob("*.craft")):
            parts = None
            desc = ""
            try:
                craft = Craft.load(path)
                parts = len(craft.parts)
                desc = craft.description
            except Exception:
                log.debug("Could not parse %s", path, exc_info=True)
            out.append(
                CraftInfo(
                    name=path.stem,
                    facility=facility,
                    path=path,
                    parts=parts,
                    description=desc,
                )
            )
        return out

    def install(
        self,
        craft: Craft,
        *,
        facility: str = "VAB",
        overwrite: bool = False,
    ) -> Path:
        folder = self.ships(facility)
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / f"{craft.name}.craft"
        if dest.exists() and not overwrite:
            raise FileExistsError(dest)
        craft.kind = facility
        craft.save(dest)
        log.info("Installed %s → %s", craft.name, dest)
        return dest

    def load_craft(self, name: str, facility: str = "VAB") -> Craft:
        path = self.ships(facility) / f"{name}.craft"
        return Craft.load(path)

    def launch(
        self,
        session: Session,
        name: str,
        *,
        facility: str = "VAB",
        site: str | None = None,
        recover: bool = True,
        crew: list[str] | None = None,
    ) -> None:
        """Launch from KSC. Recovers junk flights and pre-flight dialogs itself."""
        session.require_connected()
        if site is None:
            site = "LaunchPad" if facility.upper() == "VAB" else "Runway"
        try:
            go_space_center(session)
        except Exception as exc:
            log.warning("go_space_center: %s", exc)
        # Recover pad leftover before seating crew — assigned kerbals
        # on that stack are not available until it is gone (L-027).
        clear_launch_site(session, site)
        last_exc: Exception | None = None
        use_recover = recover
        for attempt in range(3):
            crew_list = resolve_crew(session, crew)
            try:
                self._launch_watched(
                    session,
                    facility,
                    name,
                    site,
                    crew_list,
                    use_recover,
                )
                return
            except Exception as exc:
                last_exc = exc
                log.warning("launch attempt %s failed: %s", attempt + 1, exc)
                if _site_not_clear(exc):
                    clear_launch_site(session, site)
                    use_recover = True
                elif _savegame_nre(exc):
                    _reload_space_center(session)
                    use_recover = False
                else:
                    use_recover = False
                    try:
                        go_space_center(session)
                    except Exception:
                        _abort_preflight_hang(session.settings)
                        try:
                            go_space_center(session)
                        except Exception:
                            pass
                time.sleep(2.0)
        raise SessionError(
            f"Could not launch {name!r} from {facility} onto {site}: {last_exc}"
        ) from last_exc

    def _launch_watched(
        self,
        session: Session,
        facility: str,
        name: str,
        site: str,
        crew_list: list[str],
        recover: bool,
        timeout: float = 25.0,
    ) -> None:
        box: dict[str, Any] = {"exc": None, "ok": False}

        def _run() -> None:
            try:
                session.space_center.launch_vessel(
                    facility, name, site, crew_list, recover
                )
                box["ok"] = True
            except Exception as exc:
                box["exc"] = exc

        thread = threading.Thread(target=_run, daemon=True, name="launch_vessel")
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            log.warning("launch_vessel hung %.0fs — aborting to space center", timeout)
            _abort_preflight_hang(session.settings)
            thread.join(20.0)
            if thread.is_alive():
                raise SessionError("launch_vessel hung on pre-flight (dialog?)")
        if box["exc"] is not None:
            raise box["exc"]
        if not box["ok"]:
            raise SessionError("launch_vessel returned without success")

    def launchable(self, session: Session, facility: str = "VAB") -> list[str]:
        session.require_connected()
        try:
            return list(session.space_center.launchable_vessels(facility))
        except Exception as exc:
            raise SessionError(f"launchable_vessels({facility}): {exc}") from exc


def discover_ksp() -> Path | None:
    env = os.environ.get("KSPSTUFF_KSP")
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p
    if STEAM_KSP.is_dir():
        return STEAM_KSP
    return None


def discover_hangar(save: str | None = None) -> Hangar | None:
    root = discover_ksp()
    if root is None:
        return None
    hangar = Hangar(ksp_root=root, save=save or os.environ.get("KSPSTUFF_SAVE") or "")
    saves = hangar.list_saves()
    if hangar.save and hangar.save in saves:
        return hangar
    if len(saves) == 1:
        hangar.save = saves[0]
        return hangar
    hangar.save = saves[0] if saves else ""
    return hangar


def game_scene(session: Session) -> str:
    session.require_connected()
    try:
        return session.conn.krpc.game_scene.name
    except Exception:
        return "?"
