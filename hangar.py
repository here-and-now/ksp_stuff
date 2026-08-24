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


def _launch_rpc_hung(exc: BaseException) -> bool:
    """launch_vessel RPC never returned; the Session connection is poisoned."""
    return "hung on pre-flight" in _exc_text(exc)


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


def craft_basename(name: str) -> str:
    """Craft token for Hangar refuse: lowercased, no ``@…``, no `` Debris``."""
    low = (name or "").strip().lower()
    if "@" in low:
        low = low.split("@", 1)[0]
    if low.endswith(" debris"):
        low = low[: -len(" debris")].rstrip()
    return low


def name_is_refused(name: str, refuse: tuple[str, ...]) -> str | None:
    """Exact basename match against ``refuse``. Not a substring (I-013)."""
    token = craft_basename(name)
    if not token:
        return None
    for tag in refuse:
        if craft_basename(tag) == token:
            return tag
    return None


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

    Pad and hop both call this. ``refuse`` is exact craft basename
    (hop: ``kspstuff-pad-pbc`` / ``kspstuff-geiger-pbc``), not a substring.
    """
    token = (name or "").strip()
    if not token:
        raise SessionError("install_signed: empty craft name")
    hit = name_is_refused(token, refuse)
    if hit is not None:
        raise SessionError(f"Hangar refused {token} ({hit})")
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


OVERLAY_LAST = Path(__file__).resolve().parent / "docs" / "program" / "overlay.last"
UNRECOVERABLE_LAST = (
    Path(__file__).resolve().parent / "docs" / "program" / "unrecoverable.last"
)
_SKIP_LEFTOVER_TYPES = frozenset(
    {"spaceobject", "flag", "eva", "debris", "asteroid", "unknown"}
)


_RECOVER_SITS = frozenset({"landed", "splashed", "pre_launch", "prelaunch"})
_WRECK_SITS = frozenset({"landed", "splashed"})
_AIR_SITS = frozenset({"flying", "sub_orbital", "suborbital"})
_SKY_SITS = _AIR_SITS | frozenset({"orbiting", "escaping"})
_LEFTOVER_LAND_MET_S = 900.0
_UNRECOVERABLE: set[str] = set()


def leftover_ship(vessel: Any) -> bool:
    """Living craft we walk home. Asteroids, debris, EVA, flags, dead GUID are not.

    Crash-UI wreck (landed/splashed, recoverable=0) is not pad occupancy.
    Os will not click Recover. A GUID we already Closed stays out after
    Space Center lists it as SUB_ORBITAL again. Airborne leftovers are
    still listed; they do not occupy the pad (``leftover_occupies_pad``).
    """
    try:
        name = str(getattr(vessel, "name", "") or "").strip()
    except Exception:
        return False
    if not name:
        return False
    low = name.lower()
    if low.endswith(" debris"):
        return False
    if low.startswith("ast.") or "asteroid" in low or "xrl-" in low:
        return False
    typ = _status_name(getattr(vessel, "type", None))
    if typ in _SKIP_LEFTOVER_TYPES:
        return False
    vid = _vessel_id(vessel)
    if vid and vid in _load_unrecoverable():
        return False
    return True


def leftover_ships(session: Any) -> list[Any]:
    try:
        pool = list(getattr(session.space_center, "vessels", []) or [])
    except Exception:
        return []
    out: list[Any] = []
    for vessel in pool:
        try:
            if leftover_ship(vessel):
                out.append(vessel)
        except Exception:
            continue
    return out


def leftover_occupies_pad(vessel: Any) -> bool:
    """Ground leftover blocks Hangar. Airborne does not (Os)."""
    if not leftover_ship(vessel):
        return False
    return _vessel_sit(vessel) not in _SKY_SITS


def leftover_pad_ships(session: Any) -> list[Any]:
    """Pad occupancy. Tracking leftovers in the sky are not a Hangar veto."""
    return [vessel for vessel in leftover_ships(session) if leftover_occupies_pad(vessel)]


def _vessel_id(vessel: Any) -> str:
    """kRPC 0.6 Vessel has no ``.id``. ``_object_id`` is stable across clients."""
    for attr in ("id", "_object_id"):
        try:
            raw = getattr(vessel, attr, None)
        except Exception:
            continue
        if raw is None:
            continue
        text = str(raw).strip()
        if text and text not in {"None"}:
            return text
    return ""


def _overlay_unrecoverable() -> set[str]:
    out: set[str] = set()
    try:
        text = OVERLAY_LAST.read_text(encoding="utf-8")
    except Exception:
        return out
    for line in text.splitlines():
        if not line.startswith("unrecoverable:"):
            continue
        raw = line.split(":", 1)[1]
        for tok in raw.replace(",", " ").split():
            if tok:
                out.add(tok)
    return out


def _load_unrecoverable() -> set[str]:
    ids = set(_UNRECOVERABLE)
    ids |= _overlay_unrecoverable()
    try:
        text = UNRECOVERABLE_LAST.read_text(encoding="utf-8")
    except Exception:
        text = ""
    for line in text.splitlines():
        tok = line.strip()
        if tok and not tok.startswith("#"):
            ids.add(tok)
    return ids


def _persist_unrecoverable() -> None:
    ids = _load_unrecoverable()
    UNRECOVERABLE_LAST.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(sorted(ids))
    UNRECOVERABLE_LAST.write_text(body + ("\n" if body else ""), encoding="utf-8")


def remember_unrecoverable(vessel: Any) -> None:
    """Crash-UI rec=0 wreck we Closed. Disk so the next process skips it."""
    vid = _vessel_id(vessel)
    if not vid:
        log.warning(
            "walk home unrecoverable %s sit=%s has no object id",
            _vessel_name(vessel),
            _vessel_sit(vessel),
        )
        return
    _UNRECOVERABLE.add(vid)
    _persist_unrecoverable()
    log.info(
        "walk home unrecoverable %s id=%s sit=%s — not pad occupancy",
        _vessel_name(vessel),
        vid,
        _vessel_sit(vessel),
    )


def _vessel_name(vessel: Any) -> str:
    try:
        return str(getattr(vessel, "name", "") or "").strip() or "?"
    except Exception:
        return "?"


def _vessel_sit(vessel: Any) -> str:
    try:
        return _status_name(getattr(vessel, "situation", None))
    except Exception:
        return "?"


def _vessel_recoverable(vessel: Any) -> bool:
    try:
        return bool(vessel.recoverable)
    except Exception:
        return False


def _vessel_met(vessel: Any) -> float | None:
    try:
        met = float(getattr(vessel, "met", float("nan")))
    except (TypeError, ValueError):
        return None
    if met != met:  # NaN
        return None
    return met


def leftover_will_land(vessel: Any) -> bool:
    """SUB_ORBITAL / flying leftover will hit the ground. Orbiting will not."""
    return _vessel_sit(vessel) in _RECOVER_SITS or _vessel_sit(vessel) in _AIR_SITS


def _wait_leftover_land(
    session: Session, vessel: Any, *, budget: float | None = None
) -> bool:
    """Wait a living leftover to land, then Recover. MET clock. Never revert.

    Close on a flying leftover leaves it in the list (19-09-12Z parts=20).
    Crash-UI MET freeze: stop waiting, do not revert.
    """
    from physics_warp import set_rate, timeout_hit, unpause_clock

    cap = _LEFTOVER_LAND_MET_S if budget is None else float(budget)
    if cap <= 0:
        return _vessel_recoverable(vessel)
    unpause_clock(session)
    met0 = _vessel_met(vessel)
    prev = met0
    still = 0
    log.info(
        "walk home wait land %s sit=%s met=%s",
        _vessel_name(vessel),
        _vessel_sit(vessel),
        met0,
    )
    while True:
        rec = _vessel_recoverable(vessel)
        sit = _vessel_sit(vessel)
        down = sit in _RECOVER_SITS
        if rec:
            set_rate(session, 1)
            return True
        met = _vessel_met(vessel)
        if timeout_hit(met=met, met0=met0, budget=cap, down=down):
            set_rate(session, 1)
            return False
        if met is not None and prev is not None and abs(met - prev) < 0.05:
            still += 1
        else:
            still = 0
            prev = met
        if still > 40:
            set_rate(session, 1)
            log.info(
                "walk home wait land MET frozen sit=%s rec=%s — Close",
                sit,
                int(rec),
            )
            return rec
        alt = None
        try:
            alt = float(vessel.flight().mean_altitude)
        except Exception:
            alt = None
        if sit in _AIR_SITS and (alt is None or alt > 5000):
            set_rate(session, 4)
        else:
            set_rate(session, 1)
        time.sleep(0.3)


def _wait_recovered(session: Any, name: str, *, timeout: float = 20.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        names = []
        for vessel in leftover_pad_ships(session):
            try:
                names.append(str(getattr(vessel, "name", "") or ""))
            except Exception:
                continue
        if name not in names:
            return True
        time.sleep(0.3)
    return False


def _recover_wait(session: Session, vessel: Any, name: str) -> bool:
    try:
        run_physics(session)
    except Exception:
        pass
    try:
        log.info("walk home recover() %s sit=%s", name, _vessel_sit(vessel))
        vessel.recover()
    except Exception as exc:
        log.warning("walk home recover %s: %s", name, exc)
        return False
    if _wait_recovered(session, name):
        return True
    log.warning("walk home %s still in vessel list after recover()", name)
    return False


def walk_home(session: Session) -> int:
    """Recover leftover ships, then Close. Never revert. Never leftover-ksc.

    rec=yes at Space Center: ``recover()`` there. Do **not** ``go_flight``
    a rec=0 wreck to Close — switching a tracking ghost loads stale
    persistent and can drop ``SpaceCenter.ut`` (21-21-27Z). Airborne
    rec=0 is not pad occupancy: leave it in the sky. Already in Flight:
    wait land on the MET clock if it will, then recover(). Crash-UI
    (landed/splashed rec=0): remember vessel.id. Close skips the scene
    setter when already at KSC (re-set rewinds). From Flight: persist
    RAM then scene; save fail stays Flight; rewind is failure.
    ``reload_save=False``. Never revert.
    """
    session.require_connected()
    n = 0
    recovered_names: list[str] = []
    for vessel in leftover_ships(session):
        name = _vessel_name(vessel)
        started_in_flight = game_scene(session) == "flight"
        rec = _vessel_recoverable(vessel)
        sit = _vessel_sit(vessel)
        if not rec and not started_in_flight:
            # Rec=0 at KSC: never go_flight just to Close (UT rewind).
            if sit in _WRECK_SITS:
                remember_unrecoverable(vessel)
                log.info(
                    "leftover %s sit=%s rec=0 crash UI — not pad occupancy",
                    name,
                    sit,
                )
            else:
                log.info(
                    "leftover %s sit=%s rec=0 — leave in sky, no go_flight",
                    name,
                    sit,
                )
            continue
        if rec:
            recovered_names.append(name)
            if _recover_wait(session, vessel, name):
                n += 1
            continue
        if not rec and sit in _RECOVER_SITS:
            try:
                run_physics(session)
            except Exception:
                pass
            time.sleep(1.0)
            rec = _vessel_recoverable(vessel)
            sit = _vessel_sit(vessel)
        if not rec and sit in _AIR_SITS and leftover_will_land(vessel):
            rec = _wait_leftover_land(session, vessel)
            sit = _vessel_sit(vessel)
        if rec:
            recovered_names.append(name)
            if _recover_wait(session, vessel, name):
                n += 1
        elif started_in_flight:
            recovered_names.append(name)
            if _wait_recovered(session, name):
                n += 1
            elif _vessel_recoverable(vessel) and _recover_wait(session, vessel, name):
                n += 1
            elif sit in _WRECK_SITS:
                remember_unrecoverable(vessel)
                log.info(
                    "leftover %s sit=%s rec=0 crash UI — not pad occupancy",
                    name,
                    sit,
                )
            else:
                log.info(
                    "leftover %s sit=%s not recoverable — Close, no save/load",
                    name,
                    sit,
                )
        elif sit in _WRECK_SITS:
            if _recover_wait(session, vessel, name):
                recovered_names.append(name)
                n += 1
            else:
                remember_unrecoverable(vessel)
                log.info(
                    "leftover %s sit=%s rec=0 crash UI — not pad occupancy",
                    name,
                    sit,
                )
        else:
            log.info(
                "leftover %s sit=%s not recoverable — Close, no save/load",
                name,
                sit,
            )
    _close_to_ksc(session, reload_save=False)
    try:
        session.space_center = session.conn.space_center
    except Exception:
        pass
    for name in recovered_names:
        _wait_recovered(session, name)
    return n


def overlay_painted(session: Any) -> bool:
    """Flight Results still up. Reverting may be disabled — can_revert is not enough.

    Space Center + pad leftover n=0 is the overview: leftover
    ``can_revert`` after walk-home is not an overlay (07-50 screenshot).
    Airborne leftovers are not overlay and not a Hangar veto.
    """
    scene = game_scene(session).lower().replace(" ", "_")
    if scene == "space_center" and not leftover_pad_ships(session):
        return False
    return _can_revert(session)


def go_ksc(session: Any, *, timeout: float = 45.0) -> str:
    """Walk leftover ships home and Close to KSC. No named save/load.

    Scene-only is not enough: ground leftover ships block Hangar.
    Airborne leftovers do not. Overlay is Close (``game_scene``), not
    leftover-ksc. Never rewind UT. Never revert.
    """
    walk_home(session)
    go_space_center(session, timeout=timeout, reload_save=False)
    dismiss_flight_results(session)
    ok, why = ksc_ready(session)
    write_overlay_last(session, ready=ok)
    if not ok:
        raise SessionError(
            f"ksc not ready ({why}). recover-probe --space-center; never revert"
        )
    return "ksc"


def write_overlay_last(session: Any, *, ready: bool | None = None) -> None:
    """Disk sit for ops leftover_sit. No click. Never revert."""
    try:
        ok, _ = ksc_ready(session) if ready is None else (ready, "")
        revert = _can_revert(session)
        painted = overlay_painted(session)
        n = 0
        try:
            n = len(list(getattr(session.space_center, "vessels", []) or []))
        except Exception:
            n = 0
        OVERLAY_LAST.parent.mkdir(parents=True, exist_ok=True)
        ships = leftover_pad_ships(session)
        wrecks = sorted(_load_unrecoverable())
        wreck_line = ",".join(wrecks)
        OVERLAY_LAST.write_text(
            (
                f"scene: {game_scene(session)}\n"
                f"ksc_ready: {str(bool(ok)).lower()}\n"
                f"can_revert: {str(bool(revert)).lower()}\n"
                f"overlay: {str(bool(painted)).lower()}\n"
                f"vessels: {n}\n"
                f"ships: {len(ships)}\n"
                f"unrecoverable: {wreck_line}\n"
            ),
            encoding="utf-8",
        )
    except Exception:
        log.debug("overlay.last write failed", exc_info=True)


def dismiss_flight_results(session: Session) -> str:
    """Close Flight Results. Save RAM from Flight, then scene. No leftover-ksc.

    Live probe (KSC, kRPC 0.6 UI): ``UI.clear`` removes *client* widgets
    only; ``stock_canvas`` has no Flight Results buttons. There is no
    kRPC Close click. ``load_space_center`` / named save+load is a reload
    (Os: voodoo). Crash Close is ``reload_save=False``.
    """
    _close_to_ksc(session, reload_save=False)
    try:
        session.space_center = session.conn.space_center
    except Exception:
        pass
    scene = game_scene(session)
    if scene == "flight":
        _close_to_ksc(session, reload_save=False)
        try:
            session.space_center = session.conn.space_center
        except Exception:
            pass
    return f"scene {game_scene(session)}"


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
    if slug.lower() in {"leftover-ksc", "leftover_ksc"}:
        raise SessionError(
            "load_save: refuse leftover-ksc — walk leftover ships home "
            "and Close (game_scene). Never a named reload to dismiss GUI"
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


_TRACKING = frozenset({"tracking_station", "trackingstation", "tracking"})
_REVERT_PROBES = ("can_revert_to_launch", "can_revert")


def _can_revert(session: Any) -> bool:
    """Flight Results still has Revert to Launch. Read only — never revert."""
    sc = getattr(session, "space_center", None)
    if sc is None:
        return False
    for name in _REVERT_PROBES:
        fn = getattr(sc, name, None)
        try:
            if callable(fn):
                if bool(fn()):
                    return True
            elif fn is not None and bool(fn):
                return True
        except Exception:
            continue
    return False


def ksc_ready(session: Any) -> tuple[bool, str]:
    """KSC overview, ground leftover gone, overlay not painted.

    Asteroids/debris are not leftover ships. Airborne leftovers are
    not a Hangar veto (Os). ``can_revert`` on a clean Space Center
    after walk-home is leftover, not Flight Results. Empty Tracking
    is not KSC. Never leftover-ksc. Never revert.
    """
    scene = game_scene(session).lower().replace(" ", "_")
    if scene in _TRACKING:
        return False, "tracking (empty Tracking is not KSC)"
    if scene != "space_center":
        return False, f"scene {scene}"
    ships = leftover_pad_ships(session)
    if ships:
        names = []
        for vessel in ships[:4]:
            try:
                names.append(str(getattr(vessel, "name", "?") or "?"))
            except Exception:
                names.append("?")
        return False, f"leftover ships n={len(ships)} ({', '.join(names)})"
    if overlay_painted(session):
        return False, "flight results overlay"
    return True, "ksc"


def _space_center_ut(session: Any) -> float | None:
    try:
        ut = float(getattr(session.space_center, "ut", float("nan")))
    except (TypeError, ValueError, AttributeError):
        return None
    if ut != ut:  # NaN
        return None
    return ut


def _ut_rewound(before: float | None, after: float | None) -> bool:
    if before is None or after is None:
        return False
    return after < before - 0.5


def _persist_ram(session: Session) -> None:
    """Write RAM to disk so Flight→KSC loads this clock. Not a load.

    ``save('persistent')`` is not ``load('persistent')`` (F-014). Never
    leftover-ksc. Named ``hop-exit-<stamp>`` is also legal; last SaveGame
    must be current RAM.
    """
    sc = getattr(session, "space_center", None)
    fn = getattr(sc, "save", None) if sc is not None else None
    if not callable(fn):
        raise SessionError("SpaceCenter.save missing")
    fn("persistent")


def _krpc_scene(session: Session, name: str) -> Any:
    krpc = getattr(getattr(session, "conn", None), "krpc", None)
    gs = getattr(krpc, "GameScene", None) if krpc is not None else None
    if gs is None:
        return None
    return getattr(gs, name, None)


def _set_game_scene(session: Session, name: str) -> None:
    """HighLogic.LoadScene via kRPC. Never revert, never leftover-ksc.

    From Flight, Space Center is the overlay Space Center *button* (launch
    SaveGame, pad MET 0). Tracking is the wreck exit. Any UT drop after a
    scene change is Close failure — do not Hangar.
    """
    krpc = getattr(getattr(session, "conn", None), "krpc", None)
    target = _krpc_scene(session, name)
    if krpc is None or target is None:
        raise SessionError(f"kRPC GameScene.{name} missing")
    ut0 = _space_center_ut(session)
    try:
        krpc.game_scene = target
    except Exception as exc:
        log.warning("game_scene %s failed (%s)", name, exc)
        raise SessionError(f"game_scene {name} failed ({exc})") from exc
    for _ in range(8):
        try:
            session.space_center = session.conn.space_center
        except Exception:
            pass
        ut1 = _space_center_ut(session)
        if _ut_rewound(ut0, ut1):
            log.error(
                "Close rewound UT %.3f → %.3f — entropy is one-way; no save/load",
                ut0,
                ut1,
            )
            raise SessionError(
                f"Close rewound UT {ut0:.3f} → {ut1:.3f} — entropy is one-way"
            )
        if game_scene(session) == name:
            return
        time.sleep(0.2)
    log.warning("game_scene still %s after %s", game_scene(session), name)


def _close_to_ksc(session: Session, *, reload_save: bool = False) -> None:
    """Leave Flight via Tracking, then KSC. Never revert or leftover-ksc.

    ``StartWithNewLaunch`` writes persistent before the hop. Space Center
    from Flight loads that file (pad MET 0). Tracking is KSP's wreck
    ``onLeavingFlight``. Persist RAM first so the clock on disk is *this*
    flight. Save fail: stay Flight. ``reload_save=True`` is refused.
    """
    if reload_save:
        log.warning("load_space_center refused — Close is scene setter only")
    scene = game_scene(session)
    if scene == "space_center":
        return
    if scene == "flight":
        try:
            from ra_align import align_live

            align_live(session)
        except Exception as exc:
            log.warning("RA align before Close (%s)", exc)
        try:
            _persist_ram(session)
        except Exception as exc:
            log.warning("Close save persistent failed (%s) — not setting scene", exc)
            raise SessionError(
                f"Close refused: save RAM failed ({exc}); staying in Flight"
            ) from exc
        _set_game_scene(session, "tracking_station")
        scene = game_scene(session)
    if scene in _TRACKING:
        _set_game_scene(session, "space_center")


def go_space_center(
    session: Session, *, timeout: float = 45.0, reload_save: bool = False
) -> None:
    """Leave flight/editor for the KSC overview. Close, no named load.

    From Flight: persist RAM, Tracking (wreck exit), then KSC. Never
    leftover-ksc. Never ``load_space_center``. Never rewind UT. Never
    revert. Rewind is a Hangar veto.
    """
    session.require_connected()
    log.info("scene %s → space_center", game_scene(session))
    _close_to_ksc(session, reload_save=False)
    deadline = time.monotonic() + timeout
    last = game_scene(session)
    while time.monotonic() < deadline:
        try:
            session.space_center = session.conn.space_center
        except Exception:
            pass
        ok, last = ksc_ready(session)
        if ok:
            time.sleep(1.0)
            return
        scene = game_scene(session)
        if scene == "space_center":
            if leftover_pad_ships(session):
                return
            dismiss_flight_results(session)
            time.sleep(1.0)
            return
        time.sleep(0.3)
    raise SessionError(
        f"timed out waiting for KSC (still {last}; walk leftover ships home)"
    )


def _reload_space_center(session: Session, *, timeout: float = 45.0) -> None:
    """After SaveGame NRE: Close (scene setter). Not load_space_center."""
    session.require_connected()
    log.info("Close space_center after SaveGame failure (no load_space_center)")
    _close_to_ksc(session, reload_save=False)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if game_scene(session) == "space_center":
            session.space_center = session.conn.space_center
            time.sleep(1.5)
            return
        time.sleep(0.3)
    log.warning("reload space_center still %s", game_scene(session))


def _abort_preflight_hang(
    settings: ConnectionSettings, timeout: float = 8.0
) -> None:
    """Second kRPC client: hung launch_vessel yields; this one changes scene.

    Connect and ``game_scene`` run on a daemon: Unity stuck in
    ``LaunchConfiguredVessel`` (SaveGame NRE after pre-flight PASS) will
    not answer. Do not issue more RPCs on the hop Session after that hang —
    the in-flight ``launch_vessel`` holds the client lock.
    """
    try:
        import krpc
    except ImportError:
        return

    def _run() -> None:
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

    thread = threading.Thread(target=_run, daemon=True, name="abort-preflight")
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        log.warning("abort client hung %.0fs", timeout)


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

        Close until KSC has no ground leftover before ``launch_vessel``
        (14-52-25Z Flight Results over Tracking is not KSC). Airborne
        leftovers are not a veto. Never rewind UT. Never revert.
        Probes: ``uncrewed=True`` (empty crew list). Do not seat a kerbal
        in a Stayputnik (L-017 is Mk1-only).
        """
        session.require_connected()
        if site is None:
            site = "LaunchPad" if facility.upper() == "VAB" else "Runway"
        try:
            walk_home(session)
            go_space_center(session)
        except Exception as exc:
            log.warning("go_space_center: %s", exc)
            raise SessionError(
                f"Hangar waits: KSC not clean ({exc}). "
                "Close until KSC, no revert, no launch_vessel"
            ) from exc
        ok, why = ksc_ready(session)
        if not ok:
            raise SessionError(
                f"Hangar waits: {why}. Close until KSC, no revert, no launch_vessel"
            )
        run_physics(session)
        try:
            from flightlog import event, publish_hangar_radio

            publish_hangar_radio(vessel=name, why="preflight")
            event("hangar", f"launch {name}", site=site)
        except Exception:
            log.debug("hangar radio/event failed", exc_info=True)
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
                if _launch_rpc_hung(exc):
                    raise SessionError(
                        f"launch_vessel hung on pre-flight (session poisoned): {exc}"
                    ) from exc
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
        flight_grace: float = 90.0,
    ) -> None:
        """launch_vessel on a side client so the hop Session can poll scene.

        A 25 s KSC stall is a pre-flight dialog — abort to space center.
        Scene already ``flight`` is Kopernicus/Parallax loading the pad;
        do **not** yank that back to KSC (T-137).
        """
        box: dict[str, Any] = {"exc": None, "ok": False}
        settings = session.settings

        def _run() -> None:
            conn = None
            try:
                import krpc

                conn = krpc.connect(
                    name="kspstuff-launch",
                    address=settings.address,
                    rpc_port=settings.rpc_port,
                    stream_port=settings.stream_port,
                )
                conn.space_center.launch_vessel(
                    facility, name, site, crew_list, recover
                )
                box["ok"] = True
            except Exception as exc:
                box["exc"] = exc
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass

        thread = threading.Thread(target=_run, daemon=True, name="launch_vessel")
        thread.start()
        deadline = time.monotonic() + timeout
        saw_flight = False
        while thread.is_alive() and time.monotonic() < deadline:
            if game_scene(session) == "flight":
                saw_flight = True
                break
            time.sleep(0.2)
        if thread.is_alive() and saw_flight:
            log.info("launch_vessel: scene flight — waiting %.0fs for vessel", flight_grace)
            try:
                from flightlog import event

                event("hangar", "scene flight", site=site)
            except Exception:
                pass
            thread.join(flight_grace)
        if thread.is_alive() and not saw_flight and game_scene(session) != "flight":
            log.warning("launch_vessel hung %.0fs at KSC — aborting to space center", timeout)
            try:
                from flightlog import event

                event("hangar", "abort preflight", site=site)
            except Exception:
                pass
            _abort_preflight_hang(settings)
            thread.join(2.0)
            raise SessionError("launch_vessel hung on pre-flight (dialog?)")
        if thread.is_alive():
            raise SessionError("launch_vessel hung after Flight scene")
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
