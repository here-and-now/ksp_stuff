"""Tape id folders under ``docs/missions/<id>/``.

``current.md`` ``flight:`` is the tape id (uncrewed hops write
``docs/missions/uncrewed/logs/``). Commander dossier stays ``jebediah``.
Uplink / ship / lock stay global.
"""

from __future__ import annotations

import logging
import math
import re
from pathlib import Path
from typing import Any

log = logging.getLogger("kspstuff")

ROOT = Path("docs/missions")
CURRENT_PATH = Path("docs/program/current.md")

_NAMED = {
    "Jebediah Grokman": "jebediah",
    "Jebediah Kerman": "jebediah",
    "Valentina Grokman": "valentina",
    "Valentina Kerman": "valentina",
    "Bill Grokman": "bill",
    "Bill Kerman": "bill",
    "Bob Grokman": "bob",
    "Bob Kerman": "bob",
    "Grok Grokman": "grok",
    "Grok Kerman": "grok",
}

_AIRLESS_PE_MIN = 12_000.0
_LOST = frozenset({"lost", "missing", "gone"})


def flight_slug(roster: str) -> str:
    """Exact roster string → id. ``Grok Grokman 4373`` → ``grok-4373``."""
    text = roster.strip()
    m = re.match(r"^Grok (?:Grokman|Kerman)(?:\s+(\d+))?$", text, re.I)
    if m:
        num = m.group(1)
        return f"grok-{num}" if num else "grok"
    if text in _NAMED:
        return _NAMED[text]
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _parse_kv(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower().replace("-", "_")
        if key:
            out[key] = val.strip()
    return out


def current_kv() -> dict[str, str]:
    return _parse_kv(CURRENT_PATH)


def seated_pilot() -> str:
    kv = current_kv()
    return kv.get("pilot", "Jebediah Grokman")


def seated_id() -> str:
    kv = current_kv()
    fid = kv.get("flight", "").strip().lower()
    if fid:
        return fid
    return flight_slug(seated_pilot())


def dossier(flight_id: str | None = None) -> Path:
    return ROOT / (flight_id or seated_id())


def seated_plan_path(flight_id: str | None = None) -> Path:
    return dossier(flight_id) / "plan.md"


def seated_briefing_path(flight_id: str | None = None) -> Path:
    return dossier(flight_id) / "briefing.md"


def seated_loop_path(flight_id: str | None = None) -> Path:
    return dossier(flight_id) / "loop.md"


def seated_logs_dir(flight_id: str | None = None) -> Path:
    return dossier(flight_id) / "logs"


def seated_craft_path(flight_id: str | None = None) -> Path:
    return dossier(flight_id) / "craft.md"


def seated_science_path(flight_id: str | None = None) -> Path:
    return dossier(flight_id) / "science.md"


def vab_kv() -> dict[str, str]:
    """Program vab.md is archived. Hangar is the capable ticket."""
    return {}


def hangar_craft_name() -> str:
    """Hangar name from vehicle ticket capable:yes + payload.craft. Not vab.md."""
    from session import SessionError
    from tickets import capable_hangar

    prefer = _parse_kv(seated_craft_path()).get("craft", "").strip()
    cap, name = capable_hangar(prefer=prefer)
    if cap != "yes" or not name or name.startswith("("):
        raise SessionError(
            f"vehicle capable={cap or 'missing'} — no Hangar"
        )
    return name


def pad_craft_name() -> str:
    return hangar_craft_name()


def mission_meta(flight_id: str | None = None) -> dict[str, str]:
    return _parse_kv(dossier(flight_id) / "mission.md")


def is_lost(flight_id: str | None = None) -> bool:
    return mission_meta(flight_id).get("status", "").lower() in _LOST


def list_ids() -> list[str]:
    if not ROOT.is_dir():
        return []
    out: list[str] = []
    for path in sorted(ROOT.iterdir()):
        if path.is_dir() and (
            (path / "plan.md").is_file() or (path / "mission.md").is_file()
        ):
            out.append(path.name)
    return out


def lock_held() -> str | None:
    """Return lock text if a flight pid is alive, else None."""
    from flightlog import LOCK, _pid_alive

    if not LOCK.is_file():
        return None
    raw = LOCK.read_text(encoding="utf-8")
    pid = 0
    for line in raw.splitlines():
        if line.startswith("pid="):
            try:
                pid = int(line.split("=", 1)[1].strip())
            except ValueError:
                pid = 0
    if _pid_alive(pid):
        return raw
    return None


def write_current(*, flight: str, pilot: str, capcom: str | None = None) -> None:
    kv = current_kv()
    cap = capcom or kv.get("capcom") or "Walt Grokman"
    CURRENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CURRENT_PATH.write_text(
        f"flight: {flight}\npilot: {pilot}\ncapcom: {cap}\n",
        encoding="utf-8",
    )


def seat(who: str) -> str:
    """Point current.md at a mission. Refuses lost and a live flight."""
    held = lock_held()
    if held:
        raise RuntimeError(f"flight is live — cannot seat\n{held.strip()}")
    text = who.strip()
    if (ROOT / text).is_dir():
        fid = text
    else:
        fid = flight_slug(text)
    meta = mission_meta(fid)
    if not meta and not seated_plan_path(fid).is_file():
        raise FileNotFoundError(f"no mission dossier {fid}")
    if meta.get("status", "").lower() in _LOST:
        raise RuntimeError(f"cannot seat {fid} — status {meta.get('status')}")
    pilot = meta.get("pilot") or seated_pilot()
    write_current(flight=fid, pilot=pilot)
    write_index()
    log.info("seated %s (%s)", fid, pilot)
    return fid


def write_mission_md(flight_id: str, fields: dict[str, str]) -> None:
    path = dossier(flight_id) / "mission.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    order = (
        "id",
        "pilot",
        "status",
        "body",
        "peri",
        "apo",
        "next",
        "notes",
    )
    merged = dict(mission_meta(flight_id))
    merged.update({k: str(v) for k, v in fields.items() if v is not None})
    merged["id"] = flight_id
    lines = [f"# {merged.get('pilot', flight_id)}\n"]
    for key in order:
        if key in merged:
            lines.append(f"{key}: {merged[key]}\n")
    for key, val in merged.items():
        if key not in order:
            lines.append(f"{key}: {val}\n")
    path.write_text("".join(lines), encoding="utf-8")


def write_index() -> Path:
    path = ROOT / "INDEX.md"
    rows = [
        "# Missions\n",
        "\n",
        "Tape id is `current.md` `flight:`. Uncrewed hops write `docs/missions/uncrewed/logs/`.\n",
        "Commander dossier stays `jebediah` (historical logs stay). Seat with `python main.py seat <id>`.\n",
        "Dossier render is `plan.md`; science dump is `science.md`; tape is `logs/*.jsonl`.\n",
        "\n",
        "| Id | Pilot | Status | Next |\n",
        "|---|---|---|---|\n",
    ]
    seated = seated_id()
    cur = current_kv()
    ids = list_ids()
    if seated in ids:
        ids = [seated] + [x for x in ids if x != seated]
    for fid in ids:
        m = dict(mission_meta(fid))
        if fid == "uncrewed":
            m.setdefault("pilot", cur.get("pilot") if fid == seated else "none")
            m.setdefault("status", "tape id")
        elif fid == "jebediah":
            m.setdefault("pilot", "Jebediah Grokman")
            m.setdefault("status", "Commander dossier")
        if fid == seated:
            m.setdefault("pilot", cur.get("pilot") or seated_pilot())
            m.setdefault("status", "available")
        plan = seated_plan_path(fid)
        next_tok = m.get("next") or ""
        if not next_tok and plan.is_file():
            next_tok = _parse_kv(plan).get("phase") or _parse_kv(plan).get("next") or "plan.md"
        mark = " ← seated" if fid == seated else ""
        rows.append(
            "| `{id}`{mark} | {pilot} | {status} | {next} |\n".format(
                id=fid,
                mark=mark,
                pilot=m.get("pilot", ""),
                status=m.get("status", ""),
                next=next_tok,
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(rows), encoding="utf-8")
    return path


def crew_names(vessel: Any) -> list[str]:
    try:
        return [str(c.name) for c in vessel.crew]
    except Exception:
        return []


def find_vessels_by_crew(session: Any, roster: str) -> list[Any]:
    hits: list[Any] = []
    try:
        vessels = list(session.space_center.vessels)
    except Exception:
        return hits
    for vessel in vessels:
        if roster in crew_names(vessel):
            hits.append(vessel)
    return hits


def snapshot_seated(session: Any, flight_id: str | None = None) -> None:
    fid = flight_id or seated_id()
    vessel = session.active_vessel
    if vessel is None:
        return
    fields: dict[str, str] = {}
    try:
        fields["body"] = str(vessel.orbit.body.name)
        fields["peri"] = f"{float(vessel.orbit.periapsis_altitude):.0f}"
        fields["apo"] = f"{float(vessel.orbit.apoapsis_altitude):.0f}"
    except Exception:
        pass
    write_mission_md(fid, fields)


def assert_seated(session: Any) -> str:
    """Active vessel crew must be the seated pilot. Else SESSION."""
    from session import SessionError

    fid = seated_id()
    if not seated_plan_path(fid).is_file():
        raise SessionError(f"no plan for seated mission {fid}")
    if is_lost(fid):
        raise SessionError(f"cannot fly lost mission {fid}")
    roster = seated_pilot()
    vessel = session.active_vessel
    if vessel is None:
        raise SessionError(f"no active vessel (seated {roster} / {fid})")
    names = crew_names(vessel)
    if roster not in names:
        hits = find_vessels_by_crew(session, roster)
        if len(hits) == 1:
            try:
                session.space_center.active_vessel = hits[0]
            except Exception as exc:
                raise SessionError(
                    f"wrong ship: seated {roster} ({fid}); could not focus: {exc}"
                ) from exc
            names = crew_names(session.active_vessel)
        if roster not in names:
            raise SessionError(
                f"wrong ship: seated {roster} ({fid}) "
                f"active crew={names!r} hits={len(hits)}"
            )
    snapshot_seated(session, fid)
    return fid


def pad_kerbal_available(session: Any) -> None:
    """Hangar only if the seated kerbal is not already assigned."""
    from hangar import _kerbal_available
    from session import SessionError

    roster = seated_pilot()
    try:
        kerbal = session.space_center.get_kerbal(roster)
    except Exception:
        kerbal = None
    if kerbal is not None and not _kerbal_available(kerbal):
        raise SessionError(
            f"{roster} is not available (status="
            f"{getattr(kerbal, 'roster_status', '?')}) — do not Hangar; "
            f"use phase on their vessel"
        )


def other_crewed_warp_danger(session: Any) -> str | None:
    """Orbit-only scan of other crewed stacks. Fail closed (L-038)."""
    active = session.active_vessel
    aid = None
    try:
        aid = active.id
    except Exception:
        pass
    try:
        vessels = list(session.space_center.vessels)
    except Exception:
        return "warp blocked — cannot list vessels"
    for vessel in vessels:
        try:
            if aid is not None and vessel.id == aid:
                continue
        except Exception:
            continue
        crew = crew_names(vessel)
        if not crew:
            continue
        label = crew[0]
        try:
            orb = vessel.orbit
            body = orb.body
            peri = float(orb.periapsis_altitude)
            has_atm = bool(getattr(body, "has_atmosphere", False))
            atm = float(getattr(body, "atmosphere_depth", 0) or 0) if has_atm else 0.0
        except Exception:
            return f"warp blocked — {label} orbit unread"
        in_atmo = False
        try:
            alt = float(vessel.flight().mean_altitude)
            in_atmo = has_atm and math.isfinite(alt) and alt < atm
        except Exception:
            in_atmo = False
        if in_atmo:
            return f"warp blocked — {label} in atmosphere"
        if has_atm and math.isfinite(peri) and peri < atm:
            return f"warp blocked — {label} peri in air ({peri:.0f} m)"
        if (not has_atm) and math.isfinite(peri) and peri < _AIRLESS_PE_MIN:
            return f"warp blocked — {label} airless peri {peri:.0f} m"
    return None


def index_text() -> str:
    path = ROOT / "INDEX.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    write_index()
    return path.read_text(encoding="utf-8")
