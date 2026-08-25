"""Render live dumps from the ticket bus + desk. Not a second sit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tickets import (
    fly_fields,
    list_tickets,
    science_is_catalog,
    seated_fly_ticket,
    show_ticket,
)
from world import TechNode, parse_tech_tree

DESK = Path("docs/program/desk.md")
SLATE = Path("docs/program/slate.md")
SCIENCE = Path("docs/program/science.md")
SEATED_SCIENCE = Path("docs/missions/jebediah/science.md")
PLAN = Path("docs/missions/jebediah/plan.md")
BRIEFING = Path("docs/missions/jebediah/briefing.md")
_FALLBACK_STABILITY = ("stability", 18.0, ("engineering101", "basicRocketry"))
_FALLBACK_GENERAL = ("generalRocketry", 20.0, ("basicRocketry",))
_TREE_CANDIDATES = (
    Path("GameData") / "HideEmptyTechTreeNodes" / "Resources" / "HETTN.TechTree",
    Path("GameData") / "ModuleManager.TechTree",
    Path("GameData") / "Squad" / "Resources" / "TechTree.cfg",
)


def desk_kv(text: str | None = None) -> dict[str, str]:
    raw = text if text is not None else (
        DESK.read_text(encoding="utf-8") if DESK.is_file() else ""
    )
    out: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line or line.startswith("#") or line.startswith(" "):
            continue
        k, _, v = line.partition(":")
        key = k.strip().lower()
        if key:
            out[key] = v.strip()
    return out


def _unlocked_set(desk: dict[str, str]) -> set[str]:
    owned = {"start"}
    for tok in (desk.get("unlocked") or "").split(","):
        nid = tok.strip()
        if nid and nid not in {"?", "(none)"}:
            owned.add(nid)
    return owned


def _game_tree() -> dict[str, TechNode]:
    """GameData RDNode list. Not persistent.sfs (hop may be flying)."""
    try:
        from hangar import discover_ksp

        root = discover_ksp()
    except Exception:
        return {}
    if root is None:
        return {}
    for rel in _TREE_CANDIDATES:
        path = root / rel
        try:
            if path.is_file():
                return parse_tech_tree(path)
        except Exception:
            continue
    return {}


def _cost_s(cost: float) -> str:
    if cost == int(cost):
        return str(int(cost))
    return f"{cost:g}"


def next_ctt(
    desk: dict[str, str] | None = None,
    *,
    tree: dict[str, TechNode] | None = None,
) -> tuple[str, float, tuple[str, ...]]:
    """Cheapest locked node whose parents are owned. Disk tree, not kRPC."""
    d = desk if desk is not None else desk_kv()
    owned = _unlocked_set(d)
    nodes = tree if tree is not None else _game_tree()
    best: tuple[str, float, tuple[str, ...]] | None = None
    for node in nodes.values():
        nid = (getattr(node, "id", None) or "").strip()
        if not nid or nid in owned:
            continue
        try:
            cost = float(getattr(node, "cost", 0) or 0)
        except (TypeError, ValueError):
            continue
        if cost <= 0:
            continue
        parents = tuple(p for p in (getattr(node, "parents", ()) or ()) if p)
        if parents and not all(p in owned for p in parents):
            continue
        cand = (nid, cost, parents)
        if best is None or (cost, nid) < (best[1], best[0]):
            best = cand
    if best is not None:
        return best
    if "stability" in owned:
        return _FALLBACK_GENERAL
    return _FALLBACK_STABILITY


def _ctt_need(desk: dict[str, str], cost: float) -> str:
    try:
        bank = float(desk.get("sci") or "")
    except ValueError:
        return "?"
    return f"{max(0.0, cost - bank):.2f}"


def _open_science() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bound: list[dict[str, Any]] = []
    catalog: list[dict[str, Any]] = []
    for t in list_tickets(open_only=True):
        if t.get("type") != "science" and t.get("category") != "science_opportunity":
            continue
        if science_is_catalog(t):
            catalog.append(t)
        else:
            bound.append(t)
    return bound, catalog


def _sci_row(t: dict[str, Any]) -> str:
    pl = t.get("payload") or {}
    eid = pl.get("experiment_id") or ""
    sit = pl.get("situation") or ""
    biome = pl.get("biome") or ""
    part = pl.get("part") or ""
    dur = pl.get("duration_s") or ""
    rate = pl.get("ec_rate") or ""
    est = pl.get("est") or ""
    rec = pl.get("recover_banks") or "yes"
    return (
        f"| **{t['id']}** | `{eid}` | {sit} | {biome} | `{part}` | "
        f"{dur} | {rate} | {est} | {rec} |"
    )


def format_science_dump(
    *,
    desk: dict[str, str] | None = None,
    tree: dict[str, TechNode] | None = None,
) -> str:
    d = desk if desk is not None else desk_kv()
    bound, catalog = _open_science()
    sci = d.get("sci") or "?"
    craft = d.get("craft") or "?"
    unlocked = d.get("unlocked") or "?"
    node, cost, _parents = next_ctt(d, tree=tree)
    need_s = _ctt_need(d, cost)
    lines = [
        "# Linus board — science dump",
        "",
        "Dump of **science tickets**, not dispatch. Bind is ticket payload.",
        "Catalog (`unbound`) is the shelf. This-hop work is **bound**.",
        "",
        f"Craft `{craft}`. Tree `{unlocked}`. Bank **{sci}**. Next CTT",
        f"`{node}` {_cost_s(cost)} → need ~**{need_s}**. Recover banks for hops; "
        "transmit is a radio (rate on `comms`), not the hop path. F-013:",
        "instrument part, never Stayputnik PAW as Geiger.",
        "",
        "```bash",
        "python main.py science-scan",
        "python main.py comms",
        "python main.py tickets list --type science",
        "```",
        "",
        "---",
        "",
        "## Bound (this hop)",
        "",
        "| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    if not bound:
        lines.append("| _(none)_ | | | | | | | | |")
    else:
        for t in bound:
            lines.append(_sci_row(t))
    lines.extend(
        [
            "",
            "## Catalog (unbound shelf — not `ops next` / not hop bind)",
            "",
            "| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    if not catalog:
        lines.append("| _(none)_ | | | | | | | | |")
    else:
        for t in catalog:
            lines.append(_sci_row(t))
    leftover = d.get("leftover") or "0"
    lines.extend(["", f"Desk leftover vessels n={leftover}. Query desk leftover-science.", ""])
    return "\n".join(lines)


def format_seated_science(*, desk: dict[str, str] | None = None) -> str:
    d = desk if desk is not None else desk_kv()
    bound, _ = _open_science()
    fly = seated_fly_ticket() or {}
    ff = fly_fields(fly)
    ids = ",".join(ff.get("science_ids") or []) or ",".join(
        str((t.get("payload") or {}).get("experiment_id") or "")
        for t in bound
        if (t.get("payload") or {}).get("experiment_id")
    )
    lines = [
        "# jebediah science dump (tickets)",
        "",
        "science: tickets",
        f"flight: {d.get('seat') or 'jebediah'}",
        f"craft: {d.get('craft') or ''}",
        "recover_banks: yes",
        f"notes: dump of bound tickets + fly `science_ids`. Retired splash hang is not live.",
        f"  fly: {fly.get('id') or 'none'} cli={ff.get('cli') or 'none'}",
        f"  science_ids: {ids or 'none'}",
        "",
        "## Flying",
        "",
    ]
    for t in bound:
        pl = t.get("payload") or {}
        eid = pl.get("experiment_id") or "none"
        lines.extend(
            [
                f"- experiment: {eid}",
                f"  situation: {pl.get('situation') or 'FlyingLow'}",
                f"  experiment_id: {eid}",
                f"  part: {pl.get('part') or 'none'}",
                f"  duration_s: {pl.get('duration_s') or 0}",
                f"  ec_rate: {pl.get('ec_rate') or 0}",
                "  recover_banks: yes",
                f"  ticket: {t['id']}",
            ]
        )
    if not bound:
        lines.append("- experiment: none")
    lines.append("")
    return "\n".join(lines)


def render_plan(path: Path | None = None) -> str:
    target = path or PLAN
    fly = seated_fly_ticket() or {}
    ff = fly_fields(fly)
    raw = target.read_text(encoding="utf-8") if target.is_file() else ""
    kv: dict[str, str] = {}
    header: list[str] = []
    for line in raw.splitlines():
        if line.startswith("#"):
            header.append(line)
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        key = k.strip()
        if key.lower() == "recommended":
            continue
        kv[key] = v.strip()
    if ff.get("phase"):
        kv["phase"] = ff["phase"]
    if ff.get("go"):
        kv["go"] = ff["go"]
    if ff.get("cli"):
        kv["cli"] = ff["cli"]
    if ff.get("campaign"):
        kv["campaign"] = ff["campaign"]
    ids = ff.get("science_ids") or []
    if ids:
        kv["science_ids"] = ",".join(ids) if isinstance(ids, (list, tuple)) else str(ids)
    craft = (fly.get("craft") or (fly.get("payload") or {}).get("craft") or "")
    if craft:
        kv["craft"] = str(craft)
    order = [
        "mun_pe",
        "suicide_start",
        "parking_apo",
        "parking_peri",
        "suicide_throttle",
        "landing_pe",
        "phase",
        "next",
        "expect_body",
        "expect_peri_min",
        "expect_apo_max",
        "craft",
        "hop_apo",
        "go",
        "cli",
        "campaign",
        "science_ids",
        "emergencies",
    ]
    lines = header or ["# Gene's plan. `python main.py phase` runs `phase:`."]
    seen = set()
    out = [lines[0]]
    for key in order:
        if key in kv:
            out.append(f"{key}: {kv[key]}")
            seen.add(key)
    for key, val in kv.items():
        if key not in seen:
            out.append(f"{key}: {val}")
    return "\n".join(out) + "\n"


def render_briefing(*, desk: dict[str, str] | None = None) -> str:
    d = desk if desk is not None else desk_kv()
    fly = seated_fly_ticket() or {}
    ff = fly_fields(fly)
    pl = fly.get("payload") or {}
    land = pl.get("landing") or {}
    bound, _ = _open_science()
    binds = ", ".join(
        f"{t['id']} {(t.get('payload') or {}).get('experiment_id')}"
        for t in bound
    ) or "none"
    where = ""
    if land:
        where = (
            f"Last landing: {land.get('landing') or '?'} impact={land.get('speed') or '?'} "
            f"biome={land.get('biome') or '?'} down={land.get('downrange') or '?'} km "
            f"run={land.get('run') or '?'}."
        )
    return (
        f"# Briefing — Gene → {d.get('seat') or 'jebediah'}\n"
        "\n"
        f"Earth. PBC. `{fly.get('id') or 'none'}`. go: **{ff.get('go') or 'wait'}**. "
        f"campaign: **{ff.get('campaign') or 'none'}**.\n"
        f"Helm **`{ff.get('cli') or 'none'}`**. Craft **`{d.get('craft') or '?'}`**.\n"
        "Dump of the fly ticket + last landing. Do not Hangar "
        "`proc-tank-pbc`.\n"
        "\n"
        f"{where}\n"
        "\n"
        f"Bound this hop: {binds}.\n"
        f"science_ids: {','.join(ff.get('science_ids') or []) or 'ticket-bound'}.\n"
        f"f013: copy desk.md. hangar **{d.get('hangar') or 'none'}**. leftover **n={d.get('leftover') or 0}**.\n"
        "\n"
        "emergencies: hold, cut, no_warp, stage, recover, science, abort_pad\n"
    )


def render_slate(
    text: str | None = None,
    *,
    desk: dict[str, str] | None = None,
    tree: dict[str, TechNode] | None = None,
) -> str:
    raw = text if text is not None else (
        SLATE.read_text(encoding="utf-8") if SLATE.is_file() else "# Slate\n"
    )
    d = desk if desk is not None else desk_kv()
    sci = d.get("sci") or "0"
    unlocked = d.get("unlocked") or "start"
    last = d.get("last") or ""
    node, cost, parents = next_ctt(d, tree=tree)
    need_s = _ctt_need(d, cost)
    parent_s = "+".join(parents) if parents else "start"
    fly = seated_fly_ticket() or {}
    run = ((fly.get("payload") or {}).get("landing") or {}).get("run") or ""
    biome = ((fly.get("payload") or {}).get("landing") or {}).get("biome") or ""
    lines = raw.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("**Bank:**"):
            out.append(
                f"**Bank:** desk **sci {sci}**. Tree **{unlocked}**. "
                f"`{node}` ({_cost_s(cost)}) LOCKED — need ~**{need_s}**. "
                f"`load persistent` is forbidden (F-014)."
            )
            i += 1
            while i < len(lines) and not lines[i].startswith("**"):
                i += 1
            continue
        if line.startswith("**Next (Os"):
            out.append(
                f"**Next:** bank `{node}` **{_cost_s(cost)}** (need **~{need_s}**; "
                f"parents {parent_s} owned). Pad occupancy until then. "
                f"Last hop `{run or last}` biome **{biome or '?'}**. "
                "`campaign: uncrewed`. Idle pad is a sin."
            )
            i += 1
            while i < len(lines) and not lines[i].startswith("**") and not lines[i].startswith("#"):
                i += 1
            continue
        if "Bank crumbs **1.47**" in line or "sci 1.4716835" in line:
            line = line.replace("Bank crumbs **1.47**", f"Bank **{sci}**").replace(
                "sci 1.4716835", f"sci {sci}"
            )
        out.append(line)
        i += 1
    body = "\n".join(out)
    if "1.4716835" in body:
        body = body.replace("1.4716835", sci)
    if "**1.47**" in body and sci != "1.47":
        body = body.replace("Bank crumbs **1.47**", f"Bank **{sci}**")
    return body if body.endswith("\n") else body + "\n"


def render_all() -> list[str]:
    written: list[str] = []
    sci = format_science_dump()
    SCIENCE.write_text(sci if sci.endswith("\n") else sci + "\n", encoding="utf-8")
    written.append(str(SCIENCE))
    seated = format_seated_science()
    SEATED_SCIENCE.parent.mkdir(parents=True, exist_ok=True)
    SEATED_SCIENCE.write_text(seated if seated.endswith("\n") else seated + "\n", encoding="utf-8")
    written.append(str(SEATED_SCIENCE))
    if PLAN.parent.is_dir():
        PLAN.write_text(render_plan(), encoding="utf-8")
        written.append(str(PLAN))
    if BRIEFING.parent.is_dir():
        BRIEFING.write_text(render_briefing(), encoding="utf-8")
        written.append(str(BRIEFING))
    if SLATE.is_file() or True:
        SLATE.parent.mkdir(parents=True, exist_ok=True)
        SLATE.write_text(render_slate(), encoding="utf-8")
        written.append(str(SLATE))
    return written
