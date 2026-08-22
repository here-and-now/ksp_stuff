"""One disk sit for Gene / Linus / Gus / Lars packets. No kRPC."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from card import card_experiments
from tickets import science_ids_for
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
SIT_CARD = Path("docs/program/sit-card.json")


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
    out = {"command": "", "exit": "", "abort": ""}
    for raw in text.splitlines()[:8]:
        line = raw.strip()
        if line.startswith("command:"):
            out["command"] = line.split(":", 1)[1].strip()
        elif line.startswith("exit:"):
            out["exit"] = line.split(":", 1)[1].strip()
        elif line.startswith("abort:"):
            out["abort"] = line.split(":", 1)[1].strip()
    return out


def latest_review() -> Path | None:
    logs = seated_logs_dir()
    if not logs.is_dir():
        return None
    files = sorted(
        logs.glob("*-review.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


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
    return notes[-1][2:] if notes else ""


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
    craft_key = craft if craft not in {"", "(none)"} else ""
    eids = science_ids_for(craft=craft_key)
    if not eids:
        eids = tuple(card_experiments(card_text))
    last = {"command": "", "exit": "", "abort": ""}
    if LAST_FLIGHT.is_file():
        last = parse_last_flight(LAST_FLIGHT.read_text(encoding="utf-8"))
    review = latest_review()
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
    now = world.research.science
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
        unlocked=",".join(world.research.unlocked) or "(none)",
        capable=capable,
        craft=craft,
        card=eids,
        last_command=last["command"],
        last_exit=last["exit"],
        last_abort=last["abort"],
        review=review.as_posix() if review else "none",
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
    if sit.note_tech:
        lines.append(f"note-tech: {sit.note_tech}")
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


def sit_card(world: World | None = None) -> dict:
    """Bound-card slots for the Commander. Same F013 as desk."""
    import json

    world = world or load_world()
    sit = build_sit(world)
    slots = []
    do_not: list[str] = []
    for row in sit.f013:
        if not row.eid:
            continue
        cfg = world.catalog.experiments.get(row.eid)
        hang = None
        if cfg and cfg.size_mb and cfg.data_rate and cfg.data_rate > 0:
            hang = round(cfg.size_mb / cfg.data_rate, 1)
        slots.append(
            {
                "eid": row.eid,
                "part": row.instrument,
                "hang_s": hang,
                "on_craft": row.on_craft == "yes",
                "unlocked": row.unlocked == "yes",
                "host": row.host,
            }
        )
        if row.unlocked == "no" or row.on_craft != "yes":
            do_not.append(
                f"{row.eid} instrument={row.instrument} "
                f"unlocked={row.unlocked} on_craft={row.on_craft} host={row.host}"
            )
    if not sit.card:
        do_not.append("empty card — do not pad a fallback")
    card = {
        "craft": sit.craft,
        "hangar": sit.hangar,
        "slots": slots,
        "do_not_toggle": do_not,
        "wait": "run=1 or UT+=hang_s — rem=0 is not a file (file=recording)",
    }
    SIT_CARD.parent.mkdir(parents=True, exist_ok=True)
    SIT_CARD.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    return card
