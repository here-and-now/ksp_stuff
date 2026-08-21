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
REPO_CRAFTS = Path(__file__).resolve().parent / "crafts"
STEAM_KSP = Path.home() / ".steam/steam/steamapps/common/Kerbal Space Program"
RSS_KSP = Path.home() / "Games" / "KSP-rss"
RO_KSP = Path.home() / "Games" / "KSP-RO"
DEFAULT_SAVE = "letsgrok"

# Empty Mk1/Mk1-3 pods are not probes. KSP then shows "No Control" and
# kRPC WaitForVesselPreFlightChecks sits on Launch anyway / Cancel (L-017).
# Assigned/missing kerbals also launch empty (L-018).
STOCK_CREW: tuple[str, ...] = (
    "Jebediah Grokman",
    "Valentina Grokman",
    "Bill Grokman",
    "Bob Grokman",
    # Stock save leftover until Hangar recasts them.
    "Jebediah Kerman",
    "Valentina Kerman",
    "Bill Kerman",
    "Bob Kerman",
)
_CREATED_PILOT = "Grok Grokman"


def _roster_aliases(name: str) -> tuple[str, ...]:
    """House Grokman; stock saves may still roster Kerman."""
    names = [name]
    if " Grokman" in name:
        names.append(name.replace(" Grokman", " Kerman"))
        names.append(name.replace(" Grokman", " von Kerman"))
    if "Kerman" in name:
        names.append(name.replace(" von Kerman", " Grokman").replace(" Kerman", " Grokman"))
    return tuple(dict.fromkeys(names))


def _get_kerbal(sc: Any, name: str) -> Any:
    for n in _roster_aliases(name):
        try:
            kerbal = sc.get_kerbal(n)
        except Exception:
            continue
        if kerbal is not None:
            return kerbal
    return None


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
        kerbal = _get_kerbal(sc, name)
        if kerbal is not None and _kerbal_available(kerbal):
            picked.append(kerbal.name)
            if len(picked) >= n:
                break
    while len(picked) < n:
        name = _CREATED_PILOT if _CREATED_PILOT not in picked else f"Grok Grokman {int(time.time()) % 10000}"
        existing = _get_kerbal(sc, name)
        if existing is None:
            log.info("create_kerbal %s Pilot", name)
            sc.create_kerbal(name, "Pilot", True)
            time.sleep(0.2)
            picked.append(name)
        elif _kerbal_available(existing):
            picked.append(existing.name)
        else:
            name = f"Grok Grokman {int(time.time()) % 10000}"
            sc.create_kerbal(name, "Pilot", True)
            picked.append(name)
    log.info("Launch crew: %s", ", ".join(picked[:n]))
    return picked[:n]


def ensure_kerbal(session: Session, name: str, *, trait: str = "Pilot") -> str | None:
    """Roster that exact kerbal: create if missing, seat if available."""
    sc = session.space_center
    kerbal = _get_kerbal(sc, name)
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


_PAD_SITS = frozenset({"pre_launch", "prelaunch", "landed", "splashed", "flying"})


def pad_ll(ksp_root: Path | None = None) -> tuple[float, float]:
    """Default pad lat/lon. RSS Cape, not stock KSC, when RSS sites exist."""
    from sites import STOCK_PAD, default_pad_ll

    root = ksp_root or discover_ksp()
    if root is None:
        return STOCK_PAD.latitude, STOCK_PAD.longitude
    return default_pad_ll(root)


def _near_site(lat: float, lon: float, site: str) -> bool:
    want_lat, want_lon = pad_ll()
    if site.lower() not in {"launchpad", "runway", "ksc", "us_cape_canaveral"}:
        return False
    dlat = abs(lat - want_lat)
    dlon = abs((lon - want_lon + 180.0) % 360.0 - 180.0)
    return dlat < 0.5 and dlon < 0.5


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


def vessel_ready_state(session: Any, vessel: Any = None) -> tuple[bool, str]:
    """kRPC: Flight, active vessel, parts loaded, ``flight()`` callable.

    Do not sleep a wall-clock guess. PRELAUNCH is ready (MET may still be 0).
    """
    try:
        scene = game_scene(session)
    except Exception:
        scene = "?"
    if scene not in {"flight", "?"}:
        return False, f"scene {scene}"
    try:
        v = vessel if vessel is not None else getattr(session, "active_vessel", None)
        if v is None:
            sc = getattr(session, "space_center", None)
            v = getattr(sc, "active_vessel", None) if sc is not None else None
    except Exception as exc:
        return False, f"active_vessel ({exc})"
    if v is None:
        return False, "active_vessel None"
    try:
        parts = list(getattr(getattr(v, "parts", None), "all", ()) or ())
        sit = str(getattr(v, "situation", "") or "?")
        name = str(getattr(v, "name", "") or "?")
    except Exception as exc:
        return False, f"loading ({exc})"
    if not parts:
        return False, "parts empty"
    try:
        v.flight()
    except Exception as exc:
        return False, f"flight() {exc}"
    return True, f"hangar ready {name} sit={sit} parts={len(parts)}"


def wait_vessel_ready(
    session: Any,
    vessel: Any = None,
    *,
    timeout: float = 30.0,
) -> str:
    """Poll kRPC until the vessel is loaded. No 30 s guess."""
    deadline = time.monotonic() + timeout
    last = "no vessel"
    while time.monotonic() < deadline:
        ok, last = vessel_ready_state(session, vessel)
        if ok:
            log.info(last)
            return last
        time.sleep(0.1)
    raise SessionError(f"timed out waiting for vessel ready ({last})")


def install_signed(
    session: Any,
    name: str,
    *,
    hangar: Any,
    recover: bool = True,
    uncrewed: bool = True,
    refuse: tuple[str, ...] = (),
    src: Path | None = None,
) -> str:
    """Byte-copy ``crafts/<name>.craft`` into the save VAB and launch.

    Pad and hop both call this. ``refuse`` substrings abort (hop: pad/geiger).
    """
    token = (name or "").strip()
    if not token:
        raise SessionError("install_signed: empty craft name")
    low = token.lower()
    for tag in refuse:
        if tag.lower() in low:
            raise SessionError(f"Hangar refused {token} ({tag})")
    path = src or (REPO_CRAFTS / f"{token}.craft")
    if not path.is_file():
        raise SessionError(f"missing craft {path}")
    if hangar is None:
        raise SessionError("KSP install not found (KSPSTUFF_KSP or ~/Games/KSP-rss)")
    folder = hangar.ships("VAB")
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"{token}.craft"
    dest.write_bytes(path.read_bytes())
    log.info("Hangar %s uncrewed", token)
    hangar.launch(session, token, recover=recover, uncrewed=uncrewed)
    return token


def go_ksc(session: Any, *, timeout: float = 45.0) -> str:
    """Leave Flight (asteroid, debris, leftover) for Space Center. Not a load."""
    go_space_center(session, timeout=timeout)
    return "ksc"


def load_save(session: Any, name: str = "persistent") -> str:
    """Apply ``name.sfs`` from the current save folder via kRPC.

    Mortimer after an honest RD spend. Not quickload. Not revert-to-launch.
    Os is not asked. ``SpaceCenter.load`` may drop the client — that is
    success if the RPC was issued.
    """
    slug = (name or "").strip()
    if not slug:
        raise SessionError(
            "load_save: need a named sfs (rd-<node>). "
            "load persistent autosaves RAM first and wipes an RD spend"
        )
    if slug.lower() in {"quicksave", "quickload"}:
        raise SessionError("load_save: quicksave/quickload is forbidden")
    if slug.lower() == "persistent":
        raise SessionError(
            "load_save: refuse persistent — kRPC autosaves RAM onto "
            "persistent.sfs before load (F-014). Use rd-<node>"
        )
    sc = getattr(session, "space_center", None)
    fn = getattr(sc, "load", None) if sc is not None else None
    if not callable(fn):
        raise SessionError("SpaceCenter.load missing (cannot apply RD save)")
    log.info("load save %s (apply RD, not revert)", slug)
    try:
        fn(slug)
    except Exception as exc:
        msg = str(exc).lower()
        if "disconnect" in msg or "connection" in msg or "closed" in msg:
            log.info("load save %s: client dropped after load (ok)", slug)
            return f"load {slug}"
        raise SessionError(f"load save {slug}: {exc}") from exc
    return f"load {slug}"


def run_physics(session: Any) -> None:
    """Unpause and 1× physics. Launch / Flight Results often stop the clock.

    Always set ``paused=False`` (kRPC 0.6 ``conn.krpc.paused`` and
    ``space_center.paused`` if present). Do not skip when the flag already
    reads false — Flight Results freeze is not that flag. ``physics_warp_factor``
    0 is 1× (not paused).
    """
    krpc = getattr(getattr(session, "conn", None), "krpc", None)
    sc = getattr(session, "space_center", None)
    for obj in (krpc, sc):
        if obj is None:
            continue
        try:
            obj.paused = False
        except Exception:
            pass
    if sc is None:
        return
    try:
        sc.rails_warp_factor = 0
    except Exception:
        pass
    try:
        sc.physics_warp_factor = 0
    except Exception:
        pass


def go_flight(
    session: Session,
    vessel: Any = None,
    *,
    timeout: float = 45.0,
) -> None:
    """Enter Flight on a leftover from SpaceCenter / tracking. No click.

    ``vessel.flight()`` / control are not available in ``space_center``.
    Setting ``active_vessel`` loads the tracking leftover; ``GameScene.flight``
    is the belt if the switch did not move the scene.
    """
    session.require_connected()
    if vessel is None:
        try:
            vessel = session.active_vessel
        except Exception:
            vessel = None
    if vessel is None:
        raise SessionError("no vessel to enter Flight")
    name = "?"
    try:
        name = str(vessel.name or "?")
    except Exception:
        pass
    scene = game_scene(session)
    if scene == "flight":
        wait_vessel_ready(session, vessel, timeout=min(timeout, 30.0))
        return
    log.info("scene %s → flight (%s)", scene, name)
    try:
        session.switch_to(vessel)
    except Exception as exc:
        log.warning("switch_to leftover %s: %s", name, exc)
        try:
            session.space_center.active_vessel = vessel
        except Exception as exc2:
            log.warning("active_vessel leftover %s: %s", name, exc2)
    try:
        krpc = session.conn.krpc
        flight = getattr(krpc.GameScene, "flight", None)
        if flight is not None:
            krpc.game_scene = flight
    except Exception as exc:
        log.warning("game_scene flight: %s", exc)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if game_scene(session) == "flight":
            session.space_center = session.conn.space_center
            left = max(0.5, deadline - time.monotonic())
            wait_vessel_ready(session, vessel, timeout=left)
            return
        time.sleep(0.1)
    raise SessionError(
        f"timed out waiting for flight (still {game_scene(session)}; leftover {name})"
    )


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
        uncrewed: bool = False,
    ) -> None:
        """Launch from KSC. Recovers junk flights and pre-flight dialogs itself.

        Probes: ``uncrewed=True`` (empty crew list). Do not seat a kerbal
        in a Stayputnik (L-017 is Mk1-only).
        """
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
            crew_list: list[str] = [] if uncrewed else resolve_crew(session, crew)
            try:
                self._launch_watched(
                    session,
                    facility,
                    name,
                    site,
                    crew_list,
                    use_recover,
                )
                run_physics(session)
                wait_vessel_ready(session)
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
    """``KSPSTUFF_KSP`` wins. Else ``~/Games/KSP-rss`` if that tree exists.
    ``KSP-RO`` only when the gym directory is absent. Steam last."""
    env = os.environ.get("KSPSTUFF_KSP")
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p
    rss = RSS_KSP
    if (rss / "GameData" / "RealSolarSystem").is_dir():
        return rss
    if rss.is_dir() and (rss / "GameData").is_dir():
        return rss
    ro = RO_KSP
    if (ro / "GameData" / "RealismOverhaul").is_dir():
        return ro
    if STEAM_KSP.is_dir():
        return STEAM_KSP
    return None


def discover_hangar(save: str | None = None) -> Hangar | None:
    """Default save is ``letsgrok``. Never the alphabetically first folder."""
    root = discover_ksp()
    if root is None:
        return None
    wanted = save or os.environ.get("KSPSTUFF_SAVE") or DEFAULT_SAVE
    return Hangar(ksp_root=root, save=wanted)


def game_scene(session: Session) -> str:
    session.require_connected()
    try:
        return session.conn.krpc.game_scene.name
    except Exception:
        return "?"
