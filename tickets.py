"""Ticket bus. Source of truth for Hank. Disk, no kRPC."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TICKET_DIR = ROOT / "docs" / "program" / "tickets"
BOARD = TICKET_DIR / "board.jsonl"
HEAD = TICKET_DIR / "head.json"
PRINT = TICKET_DIR / "BOARD.md"
FINGERPRINTS = TICKET_DIR / "fingerprints.json"

TYPES = (
    "fly",
    "science",
    "vehicle",
    "control",
    "systems",
    "org",
    "rsi",
    "ctt",
    "recover",
    "press",
    "ops",
)
CATEGORIES = (
    "craft",
    "science_opportunity",
    "bug",
    "improvement",
    "flight",
    "recover",
    "org",
    "control",
    "systems",
    "press",
    "ops",
)
TYPE_CATEGORY = {
    "fly": "flight",
    "science": "science_opportunity",
    "vehicle": "craft",
    "control": "bug",
    "systems": "bug",
    "org": "org",
    "rsi": "improvement",
    "ctt": "org",
    "recover": "recover",
    "press": "press",
    "ops": "ops",
}
SEVERITY = ("S1", "S2", "S3", "S4")
PRIORITY = ("P0", "P1", "P2", "P3")
STATUS = (
    "inbox",
    "triage",
    "ready",
    "assigned",
    "in_progress",
    "blocked",
    "verify",
    "done",
    "wont",
)
DESKS = (
    "hank",
    "mortimer",
    "gene",
    "gus",
    "linus",
    "lars",
    "wernher",
    "jebediah",
    "verena",
    "walt",
)
GO_STAMP_DESK = "gene"
STAMP_RULES = {
    "go": "gene",
    "capable": "gus",
    "science_payload": "linus",
    "lesson": "lars",
    "systems": "wernher",
    "org": "mortimer",
}
DEFAULT_ROUTE = {
    "fly": "gene",
    "science": "linus",
    "vehicle": "gus",
    "control": "lars",
    "systems": "wernher",
    "org": "mortimer",
    "rsi": "hank",
    "ctt": "mortimer",
    "recover": "jebediah",
    "press": "verena",
    "ops": "hank",
}

# Spawn thinking budget. Never xhigh.
# Os 2026-08-23 Sunday token tax: desk floors, not severity inflation.
REASONING = ("low", "medium", "high")
DESK_REASONING = {
    "jebediah": "low",
    "lars": "low",
    "walt": "low",
    "wernher": "medium",
    "mortimer": "medium",
    "hank": "medium",
    "gene": "medium",
    "gus": "medium",
    "linus": "medium",
    "verena": "medium",
}
NEED_MAP = {
    "need_stack": ("control", "lars"),
    "need_builder": ("vehicle", "gus"),
    "need_science": ("science", "linus"),
    "need_pr": ("press", "verena"),
    "need_mortimer": ("org", "mortimer"),
    "need_qol": ("systems", "wernher"),
    "need_os": ("org", "mortimer"),
    "need_gene": ("fly", "gene"),
}


class TicketError(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_tag(tag: str) -> str:
    return "-".join(str(tag).strip().lower().replace("_", "-").split())


def _norm_tags(tags: Any) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in tags or []:
        t = _norm_tag(raw)
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _norm_category(category: str | None, typ: str) -> str:
    cat = (category or "").strip().lower()
    if cat in CATEGORIES:
        return cat
    return TYPE_CATEGORY.get(typ, "ops")


def _load_events() -> list[dict[str, Any]]:
    if not BOARD.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in BOARD.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def _append(event: dict[str, Any]) -> None:
    TICKET_DIR.mkdir(parents=True, exist_ok=True)
    with BOARD.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def _rebuild() -> dict[str, Any]:
    tickets: dict[str, dict[str, Any]] = {}
    fps: dict[str, int] = {}
    for ev in _load_events():
        kind = ev.get("op")
        if kind == "open":
            t = dict(ev["ticket"])
            tickets[t["id"]] = t
            fp = t.get("fingerprint") or ""
            if fp:
                fps[fp] = fps.get(fp, 0) + 1
        elif kind == "patch":
            tid = ev["id"]
            if tid not in tickets:
                continue
            tickets[tid] = {**tickets[tid], **ev.get("fields", {})}
            tickets[tid]["updated"] = ev.get("at") or tickets[tid].get("updated")
    head = {"tickets": tickets, "fingerprints": fps, "updated": _now()}
    HEAD.write_text(json.dumps(head, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FINGERPRINTS.write_text(json.dumps(fps, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_board_md(tickets)
    return head


def load_head() -> dict[str, Any]:
    if HEAD.is_file():
        return json.loads(HEAD.read_text(encoding="utf-8"))
    return _rebuild()


def _next_id(tickets: dict[str, Any]) -> str:
    n = 0
    for tid in tickets:
        if tid.startswith("T-"):
            try:
                n = max(n, int(tid[2:]))
            except ValueError:
                continue
    return f"T-{n + 1:03d}"


def reasoning_for(ticket: dict[str, Any], desk: str | None = None) -> str:
    """Hank spawn thinking budget. Never xhigh. Desk floor (Os 2026-08-23)."""
    d = (desk or ticket.get("desk") or "").lower()
    if d in DESK_REASONING:
        return DESK_REASONING[d]
    s = ticket.get("severity") or "S3"
    if s == "S4":
        return "low"
    return "medium"


def batch_reasoning(rows: list[dict[str, Any]], desk: str) -> str:
    if desk in DESK_REASONING:
        return DESK_REASONING[desk]
    order = {"low": 0, "medium": 1, "high": 2}
    lvl = "low"
    for t in rows:
        r = reasoning_for(t, desk)
        if r not in order:
            r = "medium"
        if order[r] > order[lvl]:
            lvl = r
    return lvl


def infer_links(t: dict[str, Any]) -> dict[str, Any]:
    """Skim vs deep paths. Jsonl is tape CLI only — never a read_file."""
    skim: list[dict[str, str]] = []
    deep: list[dict[str, str]] = []
    tape: list[str] = []
    seen: set[str] = set()
    seen_tape: set[str] = set()

    def add_tape(path: str) -> None:
        p = str(path or "")
        if not p or p in seen_tape:
            return
        seen_tape.add(p)
        tape.append(p)

    def add(bucket: list[dict[str, str]], kind: str, path: str, why: str) -> None:
        if not path or path in seen:
            return
        seen.add(path)
        bucket.append({"kind": kind, "path": path, "why": why})

    add(skim, "desk", "docs/program/desk.md", "sit")
    add(skim, "brief", "docs/program/tickets/BRIEF.md", "how")
    payload = t.get("payload") or {}
    typ = t.get("type")
    craft = payload.get("craft") or payload.get("vehicle") or ""
    if craft and not str(craft).endswith(".craft"):
        craft_path = f"crafts/{craft}.craft"
    else:
        craft_path = str(craft)
    if typ == "fly":
        add(skim, "briefing", "docs/missions/jebediah/briefing.md", "brief")
        telem = payload.get("telem_run") or ""
        if telem:
            add_tape(str(telem))
        if craft_path:
            add(deep, "craft", craft_path, "stack")
        add(deep, "last-flight", "docs/last-flight.md", "last abort")
    elif typ == "science" or t.get("category") == "science_opportunity":
        add(skim, "science", "docs/program/science.md", "opportunities")
    elif typ == "vehicle":
        add(skim, "vab", "docs/program/vab.md", "VAB")
        if craft_path:
            add(deep, "craft", craft_path, "stack")
    elif typ == "control":
        add(skim, "blocks", "docs/program/blocks.md", "catalog")
        add(deep, "last-flight", "docs/last-flight.md", "abort")
        live = payload.get("live_run") or ""
        if live:
            add(
                deep,
                "review",
                f"docs/missions/jebediah/logs/{live}-review.md",
                "review",
            )
            add_tape(f"docs/missions/jebediah/logs/{live}.jsonl")
    elif typ == "systems":
        add(deep, "agent-notes", "docs/agent-notes.md", "kRPC")
    elif typ == "recover":
        add(deep, "last-flight", "docs/last-flight.md", "abort")
    elif typ == "org" or typ == "rsi":
        add(skim, "ops", "docs/program/OPS.md", "ops kernel")
    for p in t.get("evidence") or []:
        sp = str(p)
        if sp.endswith(".jsonl"):
            add_tape(sp)
        elif sp.endswith(".png"):
            add(deep, "png", sp, "stuck still")
        else:
            add(deep, "evidence", sp, "evidence")
    related: list[str] = []
    fp = t.get("fingerprint") or ""
    if fp:
        for other in (load_head().get("tickets") or {}).values():
            if other.get("id") != t.get("id") and other.get("fingerprint") == fp:
                related.append(other["id"])
    for extra in list(t.get("blockers") or []) + list(t.get("related") or []):
        if extra not in related:
            related.append(extra)
    return {"skim": skim, "deep": deep, "tape": tape, "related": related}


def _packet_envelope(t: dict[str, Any]) -> dict[str, Any] | None:
    """Landing/eyes from disk tape, else stored payload. Never jsonl rows."""
    payload = t.get("payload") or {}
    path = payload.get("telem_run") or ""
    if not path:
        live = payload.get("live_run") or ""
        if live:
            path = f"docs/missions/jebediah/logs/{live}.jsonl"
    if not path:
        evs = [e for e in (t.get("evidence") or []) if str(e).endswith(".jsonl")]
        path = evs[-1] if evs else ""
    if path:
        src = Path(path)
        if src.is_file():
            try:
                from tape import envelope

                return envelope(src)
            except Exception:
                pass
    landing = payload.get("landing")
    if isinstance(landing, dict) and landing:
        return landing
    return None


def format_packet(tid: str, *, deep: bool = False) -> str:
    t = show_ticket(tid)
    links = infer_links(t)
    lvl = reasoning_for(t)
    lines = [
        f"ticket: {t['id']}",
        f"type: {t.get('type')} {t.get('severity')}{t.get('priority')} "
        f"{t.get('status')} desk={t.get('desk')}",
        f"category: {t.get('category') or TYPE_CATEGORY.get(t.get('type') or '', 'ops')}",
        f"title: {t.get('title')}",
        f"reasoning: {lvl}",
        f"fingerprint: {t.get('fingerprint') or 'none'}",
        f"inbox: python main.py tickets inbox --desk {t.get('desk') or 'hank'}",
    ]
    tags = t.get("tags") or []
    if tags:
        lines.append("tags: " + ",".join(tags))
    env = _packet_envelope(t)
    if env:
        try:
            from tape import format_envelope

            lines.append(format_envelope(env))
        except Exception:
            from telem import format_landing

            lines.append(format_landing(env))
    if t.get("summary"):
        lines.append(f"summary: {t['summary']}")
    lines.append("read:")
    for item in links["skim"]:
        lines.append(f"  - {item['path']}  # {item['why']}")
    if deep:
        lines.append("deep:")
        for item in links["deep"]:
            lines.append(f"  - {item['path']}  # {item['why']}")
        for p in links.get("tape") or []:
            lines.append(f"  tape: python main.py telem {p}  # query; do not read jsonl")
        if not links["deep"] and not (links.get("tape") or []):
            lines.append("  (none)")
    else:
        lines.append(f"deep: python main.py tickets packet {tid} --deep")
    if links["related"]:
        lines.append("related: " + ",".join(links["related"]))
    payload = t.get("payload") or {}
    if payload.get("cli"):
        lines.append(f"cli: {payload['cli']}")
    go = t.get("go") or payload.get("go")
    if go:
        lines.append(f"go: {go}")
    learn = payload.get("learn") or payload.get("learned") or t.get("learn")
    if learn:
        lines.append(f"learn: {learn}")
    return "\n".join(lines) + "\n"


def packet_cmd(tids: list[str], reasoning: str) -> str:
    if not tids:
        return ""
    tid = str(tids[0])
    if not tid or tid.startswith("("):
        return ""
    _ = reasoning  # skim envelope is enough; --deep is opt-in (PNG/craft)
    return f"python main.py tickets packet {tid}"


def from_need(
    need: str,
    *,
    title: str,
    reporter: str,
    severity: str = "S2",
    priority: str = "P1",
) -> dict[str, Any]:
    key = need.strip().lstrip("+").split(":")[0].lower()
    if key not in NEED_MAP:
        raise TicketError(f"unknown need {need}")
    typ, desk = NEED_MAP[key]
    return open_ticket(
        type=typ,
        title=title,
        reporter=reporter,
        severity=severity,
        priority=priority,
        desk=desk,
        fingerprint=key.replace("need_", ""),
        rsi_loop="ops",
    )


def _write_board_md(tickets: dict[str, dict[str, Any]]) -> None:
    open_t = [
        t
        for t in tickets.values()
        if t.get("status") not in {"done", "wont"}
    ]
    open_t.sort(key=lambda t: (t.get("severity", "S4"), t.get("priority", "P3"), t["id"]))
    lines = [
        "# Ticket board",
        "",
        f"open: {len(open_t)} / {len(tickets)}",
        "",
        "| id | type | cat | S | P | R | status | desk | tags | title |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for t in open_t:
        title = (t.get("title") or "").replace("|", "/")
        cat = t.get("category") or TYPE_CATEGORY.get(t.get("type") or "", "")
        tags = ",".join(t.get("tags") or [])
        lines.append(
            f"| {t['id']} | {t.get('type')} | {cat} | {t.get('severity')} | "
            f"{t.get('priority')} | {reasoning_for(t)} | {t.get('status')} | "
            f"{t.get('desk')} | {tags} | {title} |"
        )
    lines.append("")
    PRINT.write_text("\n".join(lines), encoding="utf-8")


def open_ticket(
    *,
    type: str,
    title: str,
    reporter: str,
    severity: str = "S3",
    priority: str = "P2",
    desk: str | None = None,
    fingerprint: str = "",
    rsi_loop: str = "none",
    payload: dict[str, Any] | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    if type not in TYPES:
        raise TicketError(f"bad type {type}")
    if severity not in SEVERITY:
        raise TicketError(f"bad severity {severity}")
    if priority not in PRIORITY:
        raise TicketError(f"bad priority {priority}")
    head = load_head()
    tickets = head.get("tickets") or {}
    tid = _next_id(tickets)
    now = _now()
    ticket = {
        "id": tid,
        "type": type,
        "title": title.strip(),
        "reporter": reporter.strip(),
        "desk": desk or DEFAULT_ROUTE.get(type, "hank"),
        "assignee": "",
        "severity": severity,
        "priority": priority,
        "status": "inbox",
        "blockers": [],
        "fingerprint": fingerprint.strip(),
        "rsi_loop": rsi_loop,
        "category": _norm_category(category, type),
        "tags": _norm_tags(tags),
        "payload": payload or {},
        "evidence": [],
        "sci_expect": None,
        "created": now,
        "updated": now,
        "sla_s": None,
    }
    if ticket["desk"] not in DESKS:
        raise TicketError(f"bad desk {ticket['desk']}")
    _append({"op": "open", "at": now, "ticket": ticket})
    _rebuild()
    return ticket


def patch_ticket(tid: str, fields: dict[str, Any], *, who: str) -> dict[str, Any]:
    head = load_head()
    tickets = head.get("tickets") or {}
    if tid not in tickets:
        raise TicketError(f"no ticket {tid}")
    cur = tickets[tid]
    if "go" in fields and who != "gene":
        raise TicketError("only Gene stamps go")
    if "capable" in fields and who != "gus":
        raise TicketError("only Gus stamps capable")
    if "status" in fields and fields["status"] not in STATUS:
        raise TicketError(f"bad status {fields['status']}")
    if "desk" in fields and fields["desk"] not in DESKS:
        raise TicketError(f"bad desk {fields['desk']}")
    if "severity" in fields and fields["severity"] not in SEVERITY:
        raise TicketError("bad severity")
    if "priority" in fields and fields["priority"] not in PRIORITY:
        raise TicketError("bad priority")
    if "category" in fields:
        fields = {
            **fields,
            "category": _norm_category(str(fields.get("category") or ""), cur.get("type") or "ops"),
        }
    if "tags" in fields:
        fields = {**fields, "tags": _norm_tags(fields.get("tags"))}
    now = _now()
    _append({"op": "patch", "at": now, "id": tid, "who": who, "fields": fields})
    return _rebuild()["tickets"][tid]


def list_tickets(
    *,
    status: str | None = None,
    desk: str | None = None,
    open_only: bool = True,
    category: str | None = None,
    tag: str | None = None,
) -> list[dict[str, Any]]:
    tickets = (load_head().get("tickets") or {}).values()
    out = []
    for t in tickets:
        if open_only and t.get("status") in {"done", "wont"}:
            continue
        if status and t.get("status") != status:
            continue
        if desk and t.get("desk") != desk:
            continue
        if category and (t.get("category") or TYPE_CATEGORY.get(t.get("type") or "", "")) != category:
            continue
        if tag and _norm_tag(tag) not in (t.get("tags") or []):
            continue
        out.append(t)
    out.sort(key=lambda t: (t.get("severity", "S4"), t.get("priority", "P3"), t["id"]))
    return out


_FLY_DEAD = frozenset({"done", "wont", "blocked"})
_FLY_PREF = ("verify", "in_progress", "assigned", "ready")
_FLY_PAYLOAD = frozenset(
    {"cli", "campaign", "phase", "science_ids", "recommended", "learn", "learned"}
)


def fly_fields(t: dict[str, Any] | None) -> dict[str, Any]:
    """go / cli / campaign / phase / science_ids / learn. go is t.go or payload.go."""
    empty: dict[str, Any] = {
        "go": "",
        "cli": "",
        "campaign": "",
        "phase": "",
        "science_ids": (),
        "learn": "",
    }
    if not t:
        return empty
    pl = t.get("payload") or {}
    if not isinstance(pl, dict):
        pl = {}
    go = str(t.get("go") or pl.get("go") or "").strip()
    cli = str(pl.get("cli") or pl.get("recommended") or t.get("cli") or "").strip()
    campaign = str(pl.get("campaign") or t.get("campaign") or "").strip()
    phase = str(pl.get("phase") or t.get("phase") or "").strip()
    learn = str(pl.get("learn") or pl.get("learned") or t.get("learn") or "").strip()
    raw = pl.get("science_ids") or ()
    if isinstance(raw, str):
        ids = tuple(p.strip() for p in raw.split(",") if p.strip())
    else:
        ids = tuple(str(x) for x in raw if x)
    return {
        "go": go,
        "cli": cli,
        "campaign": campaign,
        "phase": phase,
        "science_ids": ids,
        "learn": learn,
    }


def needs_learn(t: dict[str, Any] | None) -> bool:
    """Empty Learn on a stopped campaign (not uncrewed hops)."""
    ff = fly_fields(t)
    if ff.get("learn"):
        return False
    camp = (ff.get("campaign") or "none").strip() or "none"
    return camp != "uncrewed"


def stamp_learn(tid: str, text: str, *, who: str = "gene") -> dict[str, Any]:
    return patch_fly_payload(tid, {"learn": str(text).strip()}, who=who)


def seated_fly_ticket() -> dict[str, Any] | None:
    """Open type=fly, not done/wont/blocked. Prefer go=yes in active statuses."""
    if not HEAD.is_file():
        return None
    try:
        tickets = load_head().get("tickets") or {}
    except Exception:
        return None
    rows = [
        t
        for t in tickets.values()
        if t.get("type") == "fly" and t.get("status") not in _FLY_DEAD
    ]
    if not rows:
        return None

    def _rank(t: dict[str, Any]) -> tuple[int, int, str]:
        go_yes = 0 if fly_fields(t).get("go") == "yes" else 1
        st = t.get("status") or ""
        try:
            pref = _FLY_PREF.index(st)
        except ValueError:
            pref = len(_FLY_PREF)
        return (go_yes, pref, str(t.get("id") or ""))

    rows.sort(key=_rank)
    return rows[0]


def patch_fly_payload(tid: str, fields: dict[str, Any], *, who: str) -> dict[str, Any]:
    """Merge payload.cli / campaign / phase / science_ids. Keeps top-level go."""
    cur = show_ticket(tid)
    payload = dict(cur.get("payload") or {})
    top: dict[str, Any] = {}
    for k, v in fields.items():
        if k == "go":
            top["go"] = v
            continue
        key = k[8:] if k.startswith("payload.") else k
        if key in _FLY_PAYLOAD:
            if key == "science_ids" and isinstance(v, str):
                payload[key] = [p.strip() for p in v.split(",") if p.strip()]
            else:
                payload[key] = v
        else:
            top[k] = v
    top["payload"] = payload
    return patch_ticket(tid, top, who=who)


def science_ids_for(*, situation: str = "", craft: str = "") -> tuple[str, ...]:
    """Bound experiment ids from science tickets. Empty → caller falls back to card."""
    want = situation.lower().replace(" ", "").replace("_", "")
    craft_l = craft.strip().lower()
    found: list[tuple[int, str, str]] = []
    for t in list_tickets(open_only=True):
        if t.get("type") != "science" and t.get("category") != "science_opportunity":
            continue
        pl = t.get("payload") or {}
        eid = str(pl.get("experiment_id") or pl.get("eid") or "").strip()
        if not eid:
            continue
        if craft_l:
            got = str(pl.get("craft") or "").strip().lower()
            if got and got != craft_l:
                continue
        if want:
            sit = str(pl.get("situation") or "").lower().replace(" ", "").replace("_", "")
            if sit and want not in sit and sit not in want:
                continue
        try:
            seq = int(pl.get("seq", 100))
        except (TypeError, ValueError):
            seq = 100
        found.append((seq, t["id"], eid))
    found.sort()
    out: list[str] = []
    for _, _, eid in found:
        if eid not in out:
            out.append(eid)
    return tuple(out)


def union_science_ids(*groups: object) -> tuple[str, ...]:
    """Stable unique concat. Later groups cannot drop earlier ids."""
    out: list[str] = []
    for group in groups:
        if not group:
            continue
        if isinstance(group, str):
            items = [p.strip() for p in group.split(",") if p.strip()]
        else:
            try:
                items = list(group)
            except TypeError:
                continue
        for raw in items:
            eid = str(raw).strip()
            if eid and eid not in out:
                out.append(eid)
    return tuple(out)


def card_science_ids(
    *,
    situation: str = "",
    craft: str = "",
    ticket: dict[str, Any] | None = None,
) -> tuple[str, ...]:
    """Bound science tickets union fly payload.science_ids. Fly cannot hide binds."""
    bound = science_ids_for(situation=situation, craft=craft)
    fly = tuple(fly_fields(ticket).get("science_ids") or ())
    return union_science_ids(bound, fly)


def attach_run(tid: str, path: str | Path, *, who: str = "hank") -> dict[str, Any]:
    """Link a telem jsonl onto a ticket. Merge payload; do not blank top-level go."""
    p = str(path)
    cur = show_ticket(tid)
    evs = list(cur.get("evidence") or [])
    if p not in evs:
        evs.append(p)
    payload = dict(cur.get("payload") or {})
    payload["telem_run"] = p
    try:
        from tape import envelope

        payload["landing"] = envelope(Path(p))
    except Exception:
        pass
    tags = list(cur.get("tags") or [])
    landing = payload.get("landing") or {}
    kind = str(landing.get("landing") or "")
    if kind:
        tags = _norm_tags(tags + [kind, "landing"])
    return patch_ticket(
        tid,
        {"evidence": evs, "payload": payload, "tags": tags},
        who=who,
    )


def inbox_for(desk: str) -> list[dict[str, Any]]:
    return list_tickets(desk=desk, open_only=True)


def format_inbox(desk: str) -> str:
    rows = inbox_for(desk)
    if not rows:
        return f"inbox {desk}: none\n"
    lines = [f"inbox {desk}: {len(rows)}"]
    for t in rows:
        cat = t.get("category") or TYPE_CATEGORY.get(t.get("type") or "", "")
        tags = ",".join(t.get("tags") or []) or "-"
        lines.append(
            f"{t['id']} {cat} {t.get('severity')}{t.get('priority')} "
            f"{t.get('status')} tags={tags} {t.get('title')}"
        )
    return "\n".join(lines) + "\n"


def add_tags(tid: str, tags: list[str], *, who: str = "hank") -> dict[str, Any]:
    cur = show_ticket(tid)
    merged = _norm_tags(list(cur.get("tags") or []) + list(tags))
    return patch_ticket(tid, {"tags": merged}, who=who)


def show_ticket(tid: str) -> dict[str, Any]:
    tickets = load_head().get("tickets") or {}
    if tid not in tickets:
        raise TicketError(f"no ticket {tid}")
    return tickets[tid]


def fingerprint_count(fp: str) -> int:
    fps = load_head().get("fingerprints") or {}
    return int(fps.get(fp, 0))


def maybe_open_rsi(
    fp: str,
    *,
    reporter: str = "Hank Grokman, COO",
    rsi_loop: str | None = None,
) -> dict[str, Any] | None:
    """At 3 hits, open an RSI ticket if none open for this fingerprint."""
    if not fp:
        return None
    n = fingerprint_count(fp)
    if n < 3:
        return None
    for t in list_tickets(open_only=True):
        if t.get("type") == "rsi" and t.get("fingerprint") == fp:
            return None
    loop = (rsi_loop or "").strip()
    if not loop:
        loop = "ops"
        for t in (load_head().get("tickets") or {}).values():
            got = str(t.get("rsi_loop") or "")
            if t.get("fingerprint") == fp and got:
                loop = got
                if got == "software":
                    break
    desk = "wernher" if loop == "software" else "hank"
    return open_ticket(
        type="rsi",
        title=f"RSI {fp} ×{n}",
        reporter=reporter,
        severity="S2",
        priority="P1",
        desk=desk,
        fingerprint=fp,
        rsi_loop=loop,
        payload={"count": n},
    )


def format_list(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "tickets: none\n"
    lines = [f"tickets: {len(rows)}"]
    for t in rows:
        cat = t.get("category") or TYPE_CATEGORY.get(t.get("type") or "", "")
        tags = ",".join(t.get("tags") or [])
        extra = f" {cat}"
        if tags:
            extra += f" [{tags}]"
        lines.append(
            f"{t['id']} {t.get('type')} {t.get('severity')}{t.get('priority')} "
            f"{t.get('status')} desk={t.get('desk')}{extra} {t.get('title')}"
        )
    return "\n".join(lines) + "\n"


SEED = (
    {
        "type": "systems",
        "title": "I-013 hop Hangar substring geiger-pbc",
        "reporter": "Gus Grokman, Vehicle Engineering Lead",
        "severity": "S3",
        "priority": "P2",
        "desk": "wernher",
        "fingerprint": "hangar-geiger-pbc-substring",
        "rsi_loop": "software",
    },
    {
        "type": "systems",
        "title": "I-017 desk leftover vs live Tracking",
        "reporter": "Lars Grokman, Vehicle Systems Engineer",
        "severity": "S2",
        "priority": "P1",
        "desk": "wernher",
        "fingerprint": "desk-leftover-vs-krpc",
        "rsi_loop": "software",
    },
    {
        "type": "science",
        "title": "I-018 leftover-science hides unstarted REACH",
        "reporter": "Linus Grokman, Director of Research",
        "severity": "S3",
        "priority": "P1",
        "desk": "linus",
        "fingerprint": "leftover-hides-unstarted",
        "rsi_loop": "science",
    },
    {
        "type": "control",
        "title": "I-019 leftover hop-flea vs seated craft",
        "reporter": "Gene Grokman, Flight Director",
        "severity": "S2",
        "priority": "P1",
        "desk": "lars",
        "fingerprint": "leftover-prelaunch-ghost",
        "rsi_loop": "vehicle",
    },
    {
        "type": "control",
        "title": "ec=0 after loft before splash dwell",
        "reporter": "Jebediah Grokman, Commander",
        "severity": "S2",
        "priority": "P1",
        "desk": "lars",
        "fingerprint": "ec=0-after-loft",
        "rsi_loop": "vehicle",
    },
    {
        "type": "control",
        "title": "heading never holds 090 (Water dead)",
        "reporter": "Jebediah Grokman, Commander",
        "severity": "S3",
        "priority": "P2",
        "desk": "lars",
        "fingerprint": "heading-never-090",
        "rsi_loop": "vehicle",
    },
    {
        "type": "fly",
        "title": "hop-splash t7 toward 15 sci",
        "reporter": "Hank Grokman, COO",
        "severity": "S2",
        "priority": "P0",
        "desk": "gene",
        "fingerprint": "hop-splash-15sci",
        "rsi_loop": "none",
        "payload": {
            "cli": "python main.py hop-splash",
            "phase": "hop-splash",
            "campaign": "uncrewed",
            "go": "",
        },
    },
)


def seed_legacy(*, who: str = "hank") -> list[str]:
    """Idempotent: skip titles already on the board."""
    existing = {
        t.get("title") for t in (load_head().get("tickets") or {}).values()
    }
    opened: list[str] = []
    for spec in SEED:
        if spec["title"] in existing:
            continue
        kw = dict(spec)
        payload = kw.pop("payload", None)
        t = open_ticket(**kw, payload=payload)
        opened.append(t["id"])
        fp = spec.get("fingerprint") or ""
        if fp:
            maybe_open_rsi(fp)
    return opened


def cmd_tickets(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tickets")
    sub = p.add_subparsers(dest="act", required=True)
    op = sub.add_parser("open")
    op.add_argument("--type", required=True, choices=TYPES)
    op.add_argument("--title", required=True)
    op.add_argument("--reporter", default="Hank Grokman, COO")
    op.add_argument("--severity", default="S3", choices=SEVERITY)
    op.add_argument("--priority", default="P2", choices=PRIORITY)
    op.add_argument("--desk", default="", choices=("",) + DESKS)
    op.add_argument("--fingerprint", default="")
    op.add_argument("--rsi-loop", default="none")
    op.add_argument("--category", default="", choices=("",) + CATEGORIES)
    op.add_argument("--tag", action="append", default=[])
    ls = sub.add_parser("list")
    ls.add_argument("--status", default="", choices=("",) + STATUS)
    ls.add_argument("--desk", default="", choices=("",) + DESKS)
    ls.add_argument("--category", default="", choices=("",) + CATEGORIES)
    ls.add_argument("--tag", default="")
    ls.add_argument("--all", action="store_true")
    sh = sub.add_parser("show")
    sh.add_argument("id")
    asg = sub.add_parser("assign")
    asg.add_argument("id")
    asg.add_argument("--desk", required=True, choices=DESKS)
    asg.add_argument("--who", default="hank")
    cl = sub.add_parser("close")
    cl.add_argument("id")
    cl.add_argument("--why", default="")
    cl.add_argument("--who", default="hank")
    ev = sub.add_parser("evidence")
    ev.add_argument("id")
    ev.add_argument("--path", required=True)
    ev.add_argument("--who", default="hank")
    st = sub.add_parser("stamp")
    st.add_argument("id")
    st.add_argument("--field", required=True)
    st.add_argument("--value", required=True)
    st.add_argument("--who", required=True)
    pk = sub.add_parser("packet")
    pk.add_argument("id")
    pk.add_argument("--deep", action="store_true")
    fn = sub.add_parser("from-need")
    fn.add_argument("--need", required=True)
    fn.add_argument("--title", required=True)
    fn.add_argument("--reporter", default="Gene Grokman, Flight Director")
    fn.add_argument("--severity", default="S2", choices=SEVERITY)
    fn.add_argument("--priority", default="P1", choices=PRIORITY)
    tg = sub.add_parser("tag")
    tg.add_argument("id")
    tg.add_argument("--add", action="append", default=[], dest="tags")
    tg.add_argument("--who", default="hank")
    ib = sub.add_parser("inbox")
    ib.add_argument("--desk", required=True, choices=DESKS)
    ld = sub.add_parser("landing")
    ld.add_argument("target", help="ticket id or jsonl path")
    ar = sub.add_parser("attach-run")
    ar.add_argument("id")
    ar.add_argument("--path", required=True)
    ar.add_argument("--who", default="hank")
    sub.add_parser("board")
    sub.add_parser("seed")
    args = p.parse_args(argv)
    try:
        if args.act == "open":
            t = open_ticket(
                type=args.type,
                title=args.title,
                reporter=args.reporter,
                severity=args.severity,
                priority=args.priority,
                desk=args.desk or None,
                fingerprint=args.fingerprint,
                rsi_loop=args.rsi_loop,
                category=args.category or None,
                tags=list(args.tag or []),
            )
            rsi = maybe_open_rsi(args.fingerprint)
            print(t["id"], t["desk"], t["status"])
            if rsi:
                print("rsi", rsi["id"])
            return 0
        if args.act == "list":
            rows = list_tickets(
                status=args.status or None,
                desk=args.desk or None,
                open_only=not args.all,
                category=args.category or None,
                tag=args.tag or None,
            )
            print(format_list(rows), end="")
            return 0
        if args.act == "show":
            print(json.dumps(show_ticket(args.id), indent=2, sort_keys=True))
            return 0
        if args.act == "assign":
            t = patch_ticket(
                args.id,
                {"desk": args.desk, "assignee": args.desk, "status": "assigned"},
                who=args.who,
            )
            print(t["id"], t["desk"], t["status"])
            return 0
        if args.act == "close":
            fields: dict[str, Any] = {"status": "done"}
            if args.why:
                fields["close_why"] = args.why
            t = patch_ticket(args.id, fields, who=args.who)
            print(t["id"], t["status"])
            return 0
        if args.act == "evidence":
            cur = show_ticket(args.id)
            evs = list(cur.get("evidence") or [])
            evs.append(args.path)
            t = patch_ticket(args.id, {"evidence": evs}, who=args.who)
            print(t["id"], "evidence", len(t.get("evidence") or []))
            return 0
        if args.act == "stamp":
            if args.field in _FLY_PAYLOAD or str(args.field).startswith("payload."):
                t = patch_fly_payload(
                    args.id, {args.field: args.value}, who=args.who
                )
            else:
                t = patch_ticket(args.id, {args.field: args.value}, who=args.who)
            print(t["id"], args.field, args.value)
            return 0
        if args.act == "packet":
            print(format_packet(args.id, deep=bool(args.deep)), end="")
            return 0
        if args.act == "from-need":
            t = from_need(
                args.need,
                title=args.title,
                reporter=args.reporter,
                severity=args.severity,
                priority=args.priority,
            )
            print(t["id"], t["type"], t["desk"])
            return 0
        if args.act == "tag":
            t = add_tags(args.id, list(args.tags or []), who=args.who)
            print(t["id"], "tags", ",".join(t.get("tags") or []))
            return 0
        if args.act == "inbox":
            print(format_inbox(args.desk), end="")
            return 0
        if args.act == "landing":
            target = args.target
            path = target
            if target.startswith("T-"):
                cur = show_ticket(target)
                path = (cur.get("payload") or {}).get("telem_run") or ""
                if not path:
                    evs = [e for e in (cur.get("evidence") or []) if str(e).endswith(".jsonl")]
                    path = evs[-1] if evs else ""
                if not path:
                    raise TicketError(f"{target} has no telem run")
            from tape import envelope, format_envelope

            row = envelope(path)
            print(format_envelope(row))
            print(json.dumps(row, indent=2, sort_keys=True))
            return 0
        if args.act == "attach-run":
            t = attach_run(args.id, args.path, who=args.who)
            print(t["id"], "telem", (t.get("payload") or {}).get("telem_run"))
            return 0
        if args.act == "board":
            _rebuild()
            print(PRINT.read_text(encoding="utf-8"), end="")
            return 0
        if args.act == "seed":
            ids = seed_legacy()
            print("seeded", ",".join(ids) if ids else "none")
            return 0
    except TicketError as exc:
        print(str(exc), file=__import__("sys").stderr)
        return 1
    return 2
