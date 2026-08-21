"""One disk snapshot for Gene / Linus / Gus / Lars packets. No kRPC."""

from __future__ import annotations

import json
from pathlib import Path

from missions import (
    hangar_craft_name,
    seated_craft_path,
    seated_id,
    seated_logs_dir,
    seated_science_path,
    vab_kv,
)
from world import (
    World,
    _instrument_parts,
    craft_part_names,
    format_stack,
    load_world,
)

LAST_FLIGHT = Path("docs/last-flight.md")
LOCK = Path("docs/program/flight.lock")
HELM_TECH = Path("docs/program/helm-tech.md")
DESK_JSON = Path("docs/program/desk.json")
DESK_MD = Path("docs/program/desk.md")
HELM_CARD = Path("docs/program/helm-card.json")


def lock_state() -> str:
    return "live" if LOCK.is_file() else "free"


def leftover_decision(
    *,
    vessels: tuple,
    lock: str,
) -> tuple[str, str]:
    """Hangar call from the save. Disk cannot see crash UI (scene unknown)."""
    ships = list(vessels)
    active = ships[0].name if ships else "none"
    if lock == "live":
        return "hangar-blocked", active
    if not ships:
        return "none", "none"
    names = ", ".join(v.name for v in ships[:3])
    return f"recover {names}", active


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


def card_experiments(text: str) -> list[str]:
    ids: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("- experiment:"):
            token = line.split(":", 1)[1].strip()
            if token:
                ids.append(token)
        elif line.startswith("experiment_id:"):
            token = line.split(":", 1)[1].strip().strip("`")
            if token and token not in ids:
                ids.append(token)
    return ids


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


def experiment_budget(world: World, eid: str) -> str:
    cfg = world.catalog.experiments.get(eid)
    if cfg is None:
        return f"{eid}  (no ExperimentCfg)"
    dur = ""
    if (
        cfg.size_mb
        and cfg.size_mb < 20
        and cfg.data_rate
        and cfg.data_rate > 0
    ):
        dur = f" duration_s={cfg.size_mb / cfg.data_rate:.0f}"
    ec = f" ec_rate={cfg.ec_rate:g}" if cfg.ec_rate else ""
    mb = f" size_mb={cfg.size_mb:g}" if cfg.size_mb and cfg.size_mb < 20 else ""
    return f"{eid:28}{dur}{ec}{mb}".rstrip()


def leftover_lines(world: World, *, limit: int = 12) -> list[str]:
    lines = ["# leftover science (cap − sci). Missing id = unstarted."]
    open_n = 0
    for sub in world.research.subjects:
        left = sub.leftover
        mark = "capped" if left < 0.02 else f"left={left:.3f}"
        if left < 0.02:
            continue
        open_n += 1
        if open_n <= limit:
            lines.append(
                f"  {sub.id:44} sci={sub.sci:.3f}/{sub.cap:.3f} {mark}"
            )
    if open_n == 0:
        lines.append("  (none open in save — unstarted not listed)")
    return lines


def vessel_lines(world: World) -> list[str]:
    ships = [v for v in world.vessels]
    lines = [
        f"# leftover vessels (F-006; skip SpaceObject) n={len(ships)}"
    ]
    if not ships:
        lines.append("  (none — KSC empty of ships; asteroids omitted)")
        return lines
    for v in ships[:12]:
        land = " landed" if v.landed else ""
        lines.append(f"  {v.name}  sit={v.sit} type={v.type}{land}")
    return lines


def f013_record(world: World, eid: str, stack: list[str]) -> dict[str, str]:
    unlocked = set(world.research.unlocked)
    on = set(stack)
    inst = _instrument_parts(world, eid)
    if inst:
        p = inst[0]
        return {
            "instrument": p.name,
            "tech": p.tech or "none",
            "unlocked": "yes" if p.tech in unlocked else "no",
            "on_craft": "yes" if p.name in on else "no",
            "host": "none",
        }
    host_name = "none"
    for n in stack:
        part = world.catalog.get(n)
        if part and eid in (part.experiments or []):
            host_name = n
            break
    return {
        "instrument": "none",
        "tech": "none",
        "unlocked": "n/a",
        "on_craft": "yes" if host_name != "none" else "no",
        "host": host_name if host_name != "none" else "PAW",
    }


def f013_block(world: World, eids: list[str], stack: list[str]) -> list[str]:
    if not eids:
        return [
            "f013:",
            "  instrument: none",
            "  tech: none",
            "  unlocked: n/a",
            "  on_craft: no",
            "  host: none",
        ]
    rec = f013_record(world, eids[0], stack)
    lines = [
        "f013:",
        f"  instrument: {rec['instrument']}",
        f"  tech: {rec['tech']}",
        f"  unlocked: {rec['unlocked']}",
        f"  on_craft: {rec['on_craft']}",
        f"  host: {rec['host']}",
        "# f013 all bound ids (instrument vs host)",
    ]
    for eid in eids:
        r = f013_record(world, eid, stack)
        lines.append(
            f"  {eid}  part={r['instrument']} tech={r['tech']} "
            f"unlocked={r['unlocked']} on_craft={r['on_craft']} host={r['host']}"
        )
    return lines


def sci_delta(world: World) -> str:
    now = world.research.science
    if now is None:
        return "none"
    prev = None
    if DESK_JSON.is_file():
        try:
            prev = json.loads(DESK_JSON.read_text(encoding="utf-8")).get("sci")
        except (OSError, json.JSONDecodeError, TypeError):
            prev = None
    if prev is None:
        return f"{now:.4f} (no prior desk.json)"
    try:
        before = float(prev)
    except (TypeError, ValueError):
        return f"{now:.4f}"
    return f"{before:.4f} → {now:.4f} ({now - before:+.4f})"


def write_desk_json(world: World) -> None:
    DESK_JSON.parent.mkdir(parents=True, exist_ok=True)
    DESK_JSON.write_text(
        json.dumps({"sci": world.research.science}, indent=2) + "\n",
        encoding="utf-8",
    )


def write_desk_md(text: str) -> None:
    DESK_MD.parent.mkdir(parents=True, exist_ok=True)
    DESK_MD.write_text(text, encoding="utf-8")


def format_desk(world: World | None = None) -> str:
    world = world or load_world()
    sci = world.research.science
    sci_s = f"{sci:.4f}" if sci is not None else "?"
    unlocked = ",".join(world.research.unlocked) or "(none)"
    vab = vab_kv()
    capable = vab.get("capable", "?")
    try:
        craft = hangar_craft_name()
    except Exception:
        craft = vab.get("craft", "") or "(none)"
    sci_path = seated_science_path()
    card_text = sci_path.read_text(encoding="utf-8") if sci_path.is_file() else ""
    eids = card_experiments(card_text)
    last = {"command": "", "exit": "", "abort": ""}
    if LAST_FLIGHT.is_file():
        last = parse_last_flight(LAST_FLIGHT.read_text(encoding="utf-8"))
    helm = ""
    if HELM_TECH.is_file():
        notes = [
            ln.strip()
            for ln in HELM_TECH.read_text(encoding="utf-8").splitlines()
            if ln.startswith("- ")
        ]
        helm = notes[-1][2:] if notes else ""
    review = latest_review()
    craft_md = seated_craft_path()
    names = (
        craft_part_names(craft_md.read_text(encoding="utf-8"))
        if craft_md.is_file()
        else []
    )

    lock = lock_state()
    leftover, active = leftover_decision(vessels=world.vessels, lock=lock)
    lines = [
        f"lock: {lock}",
        "scene: unknown",
        f"active_vessel: {active}",
        f"leftover: {leftover}",
        f"seat: {seated_id()}",
        f"sci: {sci_s}",
        f"sci_delta: {sci_delta(world)}",
        f"unlocked: {unlocked}",
        f"capable: {capable}",
        f"craft: {craft}",
        f"card: {','.join(eids) if eids else 'none'}",
        (
            f"last: command={last['command'] or '?'} "
            f"exit={last['exit'] or '?'} abort={last['abort'] or 'none'}"
        ),
        f"review: {review.as_posix() if review else 'none'}",
    ]
    if helm:
        lines.append(f"helm-tech: {helm}")
    lines.extend(vessel_lines(world))
    lines.extend(leftover_lines(world))
    lines.append("# experiment budgets (catalog, not napkin)")
    seen: set[str] = set()
    for eid in list(eids) + [
        "geigerCounter",
        "kerbalism_TELEMETRY",
        "temperatureScan",
        "mysteryGoo",
    ]:
        if eid in seen:
            continue
        seen.add(eid)
        lines.append(f"  {experiment_budget(world, eid)}")
    lines.extend(f013_block(world, eids, names))
    if names:
        lines.append(format_stack(world, names, label=f"seated {seated_id()}").rstrip())
    from science_scan import format_science_scan

    lines.append(format_science_scan(world).rstrip())
    write_desk_json(world)
    text = "\n".join(lines) + "\n"
    write_desk_md(text)
    return text


def helm_card(world: World | None = None) -> dict:
    """Slots for the seated card + stack. Helm loop, not Gene's plan."""
    world = world or load_world()
    try:
        craft = hangar_craft_name()
    except Exception:
        craft = vab_kv().get("craft", "")
    path = seated_science_path()
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    eids = card_experiments(text)
    craft_md = seated_craft_path()
    names = (
        craft_part_names(craft_md.read_text(encoding="utf-8"))
        if craft_md.is_file()
        else []
    )
    unlocked = set(world.research.unlocked)
    slots = []
    do_not: list[str] = []
    for eid in eids:
        inst = _instrument_parts(world, eid)
        part = inst[0].name if inst else "PAW"
        cfg = world.catalog.experiments.get(eid)
        hang = None
        if cfg and cfg.size_mb and cfg.data_rate and cfg.data_rate > 0:
            hang = round(cfg.size_mb / cfg.data_rate, 1)
        on = (inst[0].name in names) if inst else True
        slots.append(
            {
                "eid": eid,
                "part": part,
                "hang_s": hang,
                "on_craft": on,
                "unlocked": (inst[0].tech in unlocked) if inst else True,
            }
        )
        if inst and inst[0].name not in names:
            do_not.append(f"{eid} missing {inst[0].name}")
    if not eids:
        do_not.append("empty card — do not pad goo+thermo fallback")
    card = {
        "craft": craft,
        "hangar": True,
        "slots": slots,
        "do_not_toggle": do_not,
        "wait": "run=1 or UT+=hang_s — rem=0 is not a file (file=recording)",
    }
    HELM_CARD.parent.mkdir(parents=True, exist_ok=True)
    HELM_CARD.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    return card
