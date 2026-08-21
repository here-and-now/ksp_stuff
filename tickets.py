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


class TicketError(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
        "| id | type | S | P | status | desk | title |",
        "|---|---|---|---|---|---|---|",
    ]
    for t in open_t:
        title = (t.get("title") or "").replace("|", "/")
        lines.append(
            f"| {t['id']} | {t.get('type')} | {t.get('severity')} | "
            f"{t.get('priority')} | {t.get('status')} | {t.get('desk')} | {title} |"
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
    now = _now()
    _append({"op": "patch", "at": now, "id": tid, "who": who, "fields": fields})
    return _rebuild()["tickets"][tid]


def list_tickets(
    *,
    status: str | None = None,
    desk: str | None = None,
    open_only: bool = True,
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
        out.append(t)
    out.sort(key=lambda t: (t.get("severity", "S4"), t.get("priority", "P3"), t["id"]))
    return out


def show_ticket(tid: str) -> dict[str, Any]:
    tickets = load_head().get("tickets") or {}
    if tid not in tickets:
        raise TicketError(f"no ticket {tid}")
    return tickets[tid]


def fingerprint_count(fp: str) -> int:
    fps = load_head().get("fingerprints") or {}
    return int(fps.get(fp, 0))


def maybe_open_rsi(fp: str, *, reporter: str = "Hank Grokman, COO") -> dict[str, Any] | None:
    """At 3 hits, open an RSI ticket if none open for this fingerprint."""
    if not fp:
        return None
    n = fingerprint_count(fp)
    if n < 3:
        return None
    for t in list_tickets(open_only=True):
        if t.get("type") == "rsi" and t.get("fingerprint") == fp:
            return None
    return open_ticket(
        type="rsi",
        title=f"RSI {fp} ×{n}",
        reporter=reporter,
        severity="S2",
        priority="P1",
        desk="hank",
        fingerprint=fp,
        rsi_loop="ops",
        payload={"count": n},
    )


def format_list(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "tickets: none\n"
    lines = [f"tickets: {len(rows)}"]
    for t in rows:
        lines.append(
            f"{t['id']} {t.get('type')} {t.get('severity')}{t.get('priority')} "
            f"{t.get('status')} desk={t.get('desk')} {t.get('title')}"
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
    ls = sub.add_parser("list")
    ls.add_argument("--status", default="", choices=("",) + STATUS)
    ls.add_argument("--desk", default="", choices=("",) + DESKS)
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
            t = patch_ticket(args.id, {args.field: args.value}, who=args.who)
            print(t["id"], args.field, args.value)
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
