"""Sit object for Gene / Linus / Gus / Lars packets.

World/tree/leftover ships stay disk. Banked ``sci:`` is RAM R&D when a
Session can speak (``SpaceCenter.science``); ``persistent.sfs`` lags
until Hangar autosave. No leftover-ksc. No revert. No ``status`` while
``flight.lock`` is live.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from card import card_experiments
from tickets import card_science_ids, list_tickets, seated_fly_ticket
from missions import (
    hangar_craft_name,
    seated_craft_path,
    seated_id,
    seated_logs_dir,
    seated_science_path,
    vab_kv,
)
from session import SessionError
from world import (
    SaveVessel,
    World,
    craft_part_names,
    format_stack,
    instrument_parts,
    is_disk_ship,
    load_world,
)

LAST_FLIGHT = Path("docs/last-flight.md")
LOCK = Path("docs/program/flight.lock")
NOTE_TECH = Path("docs/program/note-tech.md")
_LEGACY_NOTE_TECH = Path("docs/program/helm-tech.md")
DESK_MD = Path("docs/program/desk.md")


@dataclass(frozen=True, slots=True)
class F013:
    eid: str
    instrument: str
    tech: str
    unlocked: str
    on_craft: str
    host: str


@dataclass(frozen=True, slots=True)
class DeskSit:
    lock: str
    hangar: str
    active_vessel: str
    seat: str
    sci: float | None
    sci_delta: str
    unlocked: str
    capable: str
    craft: str
    card: tuple[str, ...]
    last_command: str
    last_exit: str
    last_abort: str
    review: str
    note_tech: str
    f013: tuple[F013, ...]
    stack: tuple[str, ...]
    vessels: tuple[str, ...]
    leftover_science: tuple[str, ...]
    stack_dump: str
    mods: tuple[str, ...]
    bind: str = ""
    hop_apo: str = ""
    sci_src: str = "sfs"
    sci_disk: float | None = None


def lock_state() -> str:
    return "live" if LOCK.is_file() else "free"


_MOD_FOLDERS = (
    ("FerramAerospaceResearch", "FAR"),
    ("RealChute", "RealChute"),
    ("RealHeat", "RealHeat"),
)
_PHASE_SITS = frozenset(
    {
        "prelaunch",
        "landed",
        "srflanded",
        "splashed",
        "srfsplashed",
    }
)


def detect_mods(ksp_root: Path | None) -> tuple[str, ...]:
    if ksp_root is None:
        return ()
    gd = ksp_root / "GameData"
    found: list[str] = []
    for folder, label in _MOD_FOLDERS:
        if (gd / folder).is_dir():
            found.append(label)
    return tuple(found)


def _norm_sit(sit: str) -> str:
    return sit.lower().replace(" ", "").replace("_", "").replace("-", "")


def hangar_call(
    *,
    vessels: tuple[SaveVessel, ...],
    lock: str,
    seated_craft: str = "",
) -> tuple[str, str]:
    """Hangar vs recover from disk *ships*. Debris is not leftover (I-017).

    Disk cannot see crash UI or empty Tracking. FLYING Debris in
    ``persistent.sfs`` is not a hangar job — live leftover is kRPC.
    """
    ships = tuple(v for v in vessels if is_disk_ship(v))
    active = ships[0].name if ships else "none"
    if lock == "live":
        return "blocked", active
    if not ships:
        return "none", "none"
    craft = seated_craft.lower().strip()
    pick = ships[0]
    if craft:
        for v in ships:
            if craft in v.name.lower() or v.name.lower() in craft:
                pick = v
                break
    sit = _norm_sit(pick.sit)
    tag = pick.sit or "?"
    if sit in _PHASE_SITS or pick.landed:
        return f"phase {pick.name} sit={tag}", pick.name
    return f"recover {pick.name} sit={tag}", pick.name


def parse_last_flight(text: str) -> dict[str, str]:
    out = {"command": "", "exit": "", "abort": "", "sci": ""}
    for raw in text.splitlines()[:12]:
        line = raw.strip()
        if line.startswith("command:"):
            out["command"] = line.split(":", 1)[1].strip()
        elif line.startswith("exit:"):
            out["exit"] = line.split(":", 1)[1].strip()
        elif line.startswith("abort:"):
            out["abort"] = line.split(":", 1)[1].strip()
        elif line.startswith("sci:") and "delta" not in line and "src" not in line:
            out["sci"] = line.split(":", 1)[1].strip()
    return out


def _sci_token(raw: str) -> float | None:
    token = (raw or "").strip()
    if not token:
        return None
    try:
        return float(token)
    except ValueError:
        return None


def pick_banked_science(
    disk: float | None,
    *,
    live: float | None = None,
    last_flight: float | None = None,
) -> tuple[float | None, str, float | None]:
    """Banked RD, not leftover canister rem.

    Live kRPC wins. Recover credits RAM; sfs waits for Hangar. last-flight
    ``sci:`` is that RAM sample. Prefer it over a lower disk value.
    """
    lag_eps = 0.01
    if live is not None:
        lag = disk if disk is not None and abs(live - disk) >= lag_eps else None
        return live, "krpc", lag
    if last_flight is not None:
        if disk is None or last_flight - disk >= lag_eps:
            lag = disk if disk is not None else None
            return last_flight, "last-flight", lag
        return disk, "sfs", None
    return disk, "sfs", None


def probe_rd_science() -> float | None:
    """Get-only ``SpaceCenter.science``. Skip while the stick is live."""
    if lock_state() == "live":
        return None
    try:
        from flightlog import live_records, writer_lock_live

        if not live_records() or writer_lock_live():
            return None
    except Exception:
        return None
    try:
        from career import space_center_science
        from session import Session

        session = Session()
        session.connect()
        try:
            return space_center_science(session)
        finally:
            session.close()
    except Exception:
        return None


def latest_review() -> Path | None:
    """Live seated ``*-review.md`` only. Parked archive novels are not the sit."""
    logs = seated_logs_dir()
    if not logs.is_dir():
        return None
    files = [
        p
        for p in logs.glob("*-review.md")
        if p.is_file() and "/archive/" not in p.as_posix().replace("\\", "/")
    ]
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def review_field() -> str:
    """Desk ``review:`` line. Live review.md, else last-flight, else none."""
    path = latest_review()
    if path is not None:
        return path.as_posix()
    if LAST_FLIGHT.is_file():
        return LAST_FLIGHT.as_posix()
    return "none"


def f013_for(world: World, eid: str, stack: list[str]) -> F013:
    unlocked = set(world.research.unlocked)
    on = set(stack)
    inst = instrument_parts(world, eid)
    if inst:
        p = inst[0]
        return F013(
            eid=eid,
            instrument=p.name,
            tech=p.tech or "none",
            unlocked="yes" if p.tech in unlocked else "no",
            on_craft="yes" if p.name in on else "no",
            host="none",
        )
    host_name = "none"
    for n in stack:
        part = world.catalog.get(n)
        if part and eid in (part.experiments or []):
            host_name = n
            break
    return F013(
        eid=eid,
        instrument="none",
        tech="none",
        unlocked="n/a",
        on_craft="yes" if host_name != "none" else "no",
        host=host_name if host_name != "none" else "PAW",
    )


def _empty_f013() -> F013:
    return F013(
        eid="",
        instrument="none",
        tech="none",
        unlocked="n/a",
        on_craft="no",
        host="none",
    )


def prior_sci(text: str) -> float | None:
    for raw in text.splitlines()[:24]:
        if raw.startswith("sci:") and "delta" not in raw:
            token = raw.split(":", 1)[1].strip()
            try:
                return float(token)
            except ValueError:
                return None
    return None


def sci_delta(now: float | None, before: float | None) -> str:
    if now is None:
        return "none"
    if before is None:
        return f"{now:.4f} (no prior desk.md)"
    return f"{before:.4f} → {now:.4f} ({now - before:+.4f})"


def _note_tech_path() -> Path | None:
    if NOTE_TECH.is_file():
        return NOTE_TECH
    if _LEGACY_NOTE_TECH.is_file():
        return _LEGACY_NOTE_TECH
    return None


def _last_note_tech() -> str:
    path = _note_tech_path()
    if path is None:
        return ""
    notes = [
        ln.strip()
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.startswith("- ")
    ]
    return _clip_note(notes[-1][2:] if notes else "")


_NOTE_TECH_MAX = 160


def _clip_note(text: str) -> str:
    one = " ".join(str(text or "").split())
    if len(one) <= _NOTE_TECH_MAX:
        return one
    return one[: _NOTE_TECH_MAX - 1] + "…"


def bind_line() -> str:
    bits: list[str] = []
    try:
        rows = list_tickets(open_only=True)
    except Exception:
        return ""
    for t in rows:
        if t.get("type") != "science":
            continue
        pl = t.get("payload") or {}
        eid = str(pl.get("experiment_id") or pl.get("eid") or "").strip()
        if not eid:
            continue
        dur = pl.get("duration_s", "")
        rate = pl.get("ec_rate", "")
        seq = pl.get("seq", "")
        bits.append(f"{t['id']} {eid} {dur}/{rate} seq{seq}")
        if len(bits) >= 6:
            break
    return "; ".join(bits)


def hop_apo_line() -> str:
    try:
        t = seated_fly_ticket()
    except Exception:
        return ""
    if not t:
        return ""
    pl = t.get("payload") or {}
    return str(pl.get("hop_apo") or "").strip()


def leftover_science_lines(world: World, *, limit: int = 12) -> tuple[str, ...]:
    rows: list[str] = []
    for sub in world.research.subjects:
        if sub.leftover < 0.02:
            continue
        rows.append(
            f"{sub.id:44} sci={sub.sci:.3f}/{sub.cap:.3f} left={sub.leftover:.3f}"
        )
        if len(rows) >= limit:
            break
    return tuple(rows)


def build_sit(world: World | None = None) -> DeskSit:
    world = world or load_world()
    vab = vab_kv()
    capable = vab.get("capable", "?")
    try:
        craft = hangar_craft_name()
    except SessionError:
        craft = vab.get("craft", "") or "(none)"
    sci_path = seated_science_path()
    card_text = sci_path.read_text(encoding="utf-8") if sci_path.is_file() else ""
    eids = card_science_ids(ticket=seated_fly_ticket())
    if not eids:
        eids = tuple(card_experiments(card_text))
    last = {"command": "", "exit": "", "abort": ""}
    if LAST_FLIGHT.is_file():
        last = parse_last_flight(LAST_FLIGHT.read_text(encoding="utf-8"))
    review = review_field()
    craft_md = seated_craft_path()
    names = (
        craft_part_names(craft_md.read_text(encoding="utf-8"))
        if craft_md.is_file()
        else []
    )
    lock = lock_state()
    ships = tuple(v for v in world.vessels if is_disk_ship(v))
    hangar, active = hangar_call(
        vessels=ships,
        lock=lock,
        seated_craft=craft if craft not in {"", "(none)"} else "",
    )
    disk = world.research.science
    last_sci = _sci_token(last.get("sci") or "")
    now, sci_src, sci_disk = pick_banked_science(
        disk,
        live=probe_rd_science(),
        last_flight=last_sci,
    )
    before = prior_sci(DESK_MD.read_text(encoding="utf-8")) if DESK_MD.is_file() else None
    rows = leftover_science_lines(world)
    f013 = tuple(f013_for(world, eid, names) for eid in eids) or (_empty_f013(),)
    return DeskSit(
        lock=lock,
        hangar=hangar,
        active_vessel=active,
        seat=seated_id(),
        sci=now,
        sci_delta=sci_delta(now, before),
        sci_src=sci_src,
        sci_disk=sci_disk,
        unlocked=",".join(world.research.unlocked) or "(none)",
        capable=capable,
        craft=craft,
        card=eids,
        last_command=last["command"],
        last_exit=last["exit"],
        last_abort=last["abort"],
        review=review,
        note_tech=_last_note_tech(),
        f013=f013,
        stack=tuple(names),
        vessels=tuple(v.name for v in ships[:12]),
        leftover_science=rows,
        stack_dump=(
            format_stack(world, names, label=f"seated {seated_id()}").rstrip()
            if names
            else ""
        ),
        mods=detect_mods(world.ksp_root),
        bind=bind_line(),
        hop_apo=hop_apo_line(),
    )


def format_sit(sit: DeskSit) -> str:
    sci_s = f"{sit.sci:.4f}" if sit.sci is not None else "?"
    rec = sit.f013[0]
    mods = ",".join(sit.mods) if sit.mods else "none"
    lines = [
        f"lock: {sit.lock}",
        "scene: unknown (disk)",
        f"active_vessel: {sit.active_vessel}",
        f"hangar: {sit.hangar}",
        f"leftover: {len(sit.vessels)}",
        f"seat: {sit.seat}",
        f"sci: {sci_s}",
        f"sci_delta: {sit.sci_delta}",
        f"sci_src: {sit.sci_src}",
    ]
    if sit.sci_disk is not None:
        lines.append(f"sci_disk: {sit.sci_disk:.4f} (lag)")
    lines.extend(
        [
            f"unlocked: {sit.unlocked}",
            f"capable: {sit.capable}",
            f"craft: {sit.craft}",
            f"mods: {mods}",
            f"card: {','.join(sit.card) if sit.card else 'none'}",
            (
                f"last: command={sit.last_command or '?'} "
                f"exit={sit.last_exit or '?'} abort={sit.last_abort or 'none'}"
            ),
            f"review: {sit.review}",
            "f013:",
        ]
    )
    for row in sit.f013:
        lines.append(
            f"  {row.eid or '(none)'}  part={row.instrument} tech={row.tech} "
            f"unlocked={row.unlocked} on_craft={row.on_craft} host={row.host}"
        )
    lines.extend(
        [
            f"  instrument: {rec.instrument}",
            f"  tech: {rec.tech}",
            f"  unlocked: {rec.unlocked}",
            f"  on_craft: {rec.on_craft}",
            f"  host: {rec.host}",
        ]
    )
    if sit.bind:
        lines.append(f"bind: {sit.bind}")
    if sit.hop_apo:
        lines.append(f"hop_apo: {sit.hop_apo}")
    if sit.note_tech:
        lines.append(f"note-tech: {_clip_note(sit.note_tech)}")
    lines.append(f"# leftover vessels n={len(sit.vessels)}")
    if sit.vessels:
        lines.extend(f"  {name}" for name in sit.vessels)
    else:
        lines.append("  (none — KSC empty of ships; asteroids/debris omitted)")
    lines.append("# leftover science (cap − sci). Missing id = unstarted.")
    if sit.leftover_science:
        lines.extend(f"  {row}" for row in sit.leftover_science)
    else:
        lines.append("  (none open in save — unstarted not listed)")
    if sit.stack_dump:
        lines.append(sit.stack_dump)
    return "\n".join(lines) + "\n"


def write_desk_md(text: str) -> None:
    DESK_MD.parent.mkdir(parents=True, exist_ok=True)
    DESK_MD.write_text(text, encoding="utf-8")


def format_desk(world: World | None = None) -> str:
    sit = build_sit(world)
    text = format_sit(sit)
    write_desk_md(text)
    return text
