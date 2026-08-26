"""Ticket bus. Source of truth for Hank. Disk, no kRPC."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TICKET_DIR = ROOT / "docs" / "program" / "tickets"
BOARD = TICKET_DIR / "board.jsonl"
HEAD = TICKET_DIR / "head.json"
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
# Prefix is the id, not a TYPE. Global N; existing T- science/fly/vehicle keep history.
ID_PREFIX = {
    "science": "S",
    "fly": "M",
    "vehicle": "C",
}
_TID_RE = re.compile(r"^([TSMC])-(\d+)$")
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
    "katherine",
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
    "rsi": "mortimer",
    "ctt": "mortimer",
    "recover": "hank",
    "press": "verena",
    "ops": "hank",
}

# Spawn thinking budget. Never xhigh.
# Token tax lifted (Os): low only for speech-only; high for org/RSI/S1.
REASONING = ("low", "medium", "high")
DESK_REASONING = {
    "walt": "low",
    "mortimer": "high",
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


_FP_STEM_MAX = 48
_FP_ABORT = 80
_LAST_RSI_ID = ""
_FP_REQUIRED = frozenset({"control", "systems"})
SCI_UNCHANGED_FP = "sci-unchanged-recovered"
# RSS Earth FlyingLow / FlyingHigh split. Disk envelope law — not hop.py.
FLYING_HIGH_LID_M = 50_000.0
# Timestamp-prefixed / hop-<digits> novels do not count toward ×3.
_FP_NOVEL_RE = re.compile(
    r"^(?:\d{4}-\d{2}-\d{2}(?:t\d{2}-\d{2}-\d{2}z?)?|\d{2}-\d{2}-\d{2}z?|hop-\d+)"
    r"(?:-|$)",
    re.I,
)


def normalize_fingerprint(fp: str) -> str:
    """Short stem for RSI. Abort/timestamp/hop-N novels do not count toward ×3."""
    raw = str(fp or "").strip()
    if not raw or len(raw) > _FP_ABORT:
        return ""
    stem = _norm_tag(raw)[:_FP_STEM_MAX]
    if not stem or _FP_NOVEL_RE.match(stem):
        return ""
    return stem


def fingerprint_required(typ: str, tags: list[str] | None) -> bool:
    """control / systems / ops --tag feedback. legacy-twin seed is exempt."""
    tags_n = _norm_tags(tags)
    if "legacy-twin" in tags_n:
        return False
    if typ in _FP_REQUIRED:
        return True
    return typ == "ops" and "feedback" in tags_n


def alias_fingerprint(
    fp: str, existing: dict[str, int] | None = None
) -> str:
    """Reuse the shortest existing kebab prefix (flyinghigh-lid-18km-hop → flyinghigh-lid)."""
    stem = normalize_fingerprint(fp)
    if not stem:
        return ""
    fps = existing if existing is not None else (load_head().get("fingerprints") or {})
    best = stem
    best_parts = len([p for p in stem.split("-") if p])
    for other in fps:
        if not other:
            continue
        parts = len([p for p in other.split("-") if p])
        if parts < 2:
            continue
        if stem == other or stem.startswith(other + "-"):
            if parts < best_parts:
                best = other
                best_parts = parts
    return best


def format_fp_catalog(*, limit: int = 12) -> str:
    """reuse (count): stem (n), … plus a copy line. Empty board is valid."""
    fps = load_head().get("fingerprints") or {}
    rows = sorted(
        ((int(n), s) for s, n in fps.items() if s and int(n) > 0),
        reverse=True,
    )
    if not rows:
        return "reuse (count): (none)\ncopy: --fingerprint <stem>"
    parts = [f"{s} ({n})" for n, s in rows[:limit]]
    return (
        "reuse (count): " + ", ".join(parts) + "\n"
        f"copy: --fingerprint {rows[0][1]}"
    )


def _fp_required_error(typ: str) -> TicketError:
    extra = " --tag feedback" if typ == "ops" else ""
    return TicketError(
        f"fingerprint required for {typ}{extra} (empty/novel rejected)\n"
        + format_fp_catalog()
    )


def science_is_catalog(t: dict[str, Any]) -> bool:
    """Leftover biome shelf — not this-hop bind / not Linus ops-next work."""
    if t.get("type") != "science" and t.get("category") != "science_opportunity":
        return False
    tags = set(t.get("tags") or [])
    if "unbound" in tags:
        return True
    bound = str((t.get("payload") or {}).get("bound") or "").strip().lower()
    return bound in {"no", "false", "0"}


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
            prev_fp = tickets[tid].get("fingerprint") or ""
            tickets[tid] = {**tickets[tid], **ev.get("fields", {})}
            tickets[tid]["updated"] = ev.get("at") or tickets[tid].get("updated")
            new_fp = tickets[tid].get("fingerprint") or ""
            if new_fp and not prev_fp:
                fps[new_fp] = fps.get(new_fp, 0) + 1
        elif kind == "fp":
            fp = ev.get("fp") or ""
            if fp:
                fps[fp] = fps.get(fp, 0) + 1
    head = {"tickets": tickets, "fingerprints": fps, "updated": _now()}
    HEAD.write_text(json.dumps(head, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FINGERPRINTS.write_text(json.dumps(fps, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return head


def load_head() -> dict[str, Any]:
    if HEAD.is_file():
        return json.loads(HEAD.read_text(encoding="utf-8"))
    return _rebuild()


def parse_ticket_id(tid: str) -> tuple[str, int] | None:
    m = _TID_RE.match(str(tid or "").strip())
    if not m:
        return None
    return m.group(1), int(m.group(2))


def is_ticket_id(tid: str) -> bool:
    return parse_ticket_id(tid) is not None


def id_prefix_for(typ: str) -> str:
    return ID_PREFIX.get(typ, "T")


def _next_id(tickets: dict[str, Any], typ: str = "") -> str:
    n = 0
    for tid in tickets:
        got = parse_ticket_id(tid)
        if got is not None:
            n = max(n, got[1])
    return f"{id_prefix_for(typ)}-{n + 1:03d}"


def reasoning_for(ticket: dict[str, Any], desk: str | None = None) -> str:
    """Hank spawn thinking budget. Never xhigh.

    Walt is speech (low). Mortimer is org (high). Else: rsi/org/ctt or
    S1 → high; S4 hygiene → low; everything else medium.
    """
    d = (desk or ticket.get("desk") or "").lower()
    if d in DESK_REASONING:
        return DESK_REASONING[d]
    typ = str(ticket.get("type") or "")
    if typ in {"rsi", "org", "ctt"}:
        return "high"
    s = str(ticket.get("severity") or "S3")
    if s == "S1":
        return "high"
    if s == "S4":
        return "low"
    return "medium"


def batch_reasoning(rows: list[dict[str, Any]], desk: str) -> str:
    if desk in DESK_REASONING:
        return DESK_REASONING[desk]
    order = {"low": 0, "medium": 1, "high": 2}
    lvl = "medium"
    for t in rows:
        r = reasoning_for(t, desk)
        if r not in order:
            r = "medium"
        if order[r] > order[lvl]:
            lvl = r
    return lvl if rows else "medium"


def ticket_craft(t: dict[str, Any] | None) -> str:
    """payload.craft, top-level craft, or crafts/*.craft evidence stem."""
    if not t:
        return ""
    pl = t.get("payload") if isinstance(t.get("payload"), dict) else {}
    raw = (
        (pl or {}).get("craft")
        or (pl or {}).get("vehicle")
        or t.get("craft")
        or t.get("payload.craft")
        or ""
    )
    name = str(raw).strip()
    if not name or name.startswith("("):
        for ev in t.get("evidence") or []:
            sp = str(ev).replace("\\", "/")
            if sp.endswith(".craft"):
                name = sp.rsplit("/", 1)[-1]
                break
    if name.endswith(".craft"):
        name = name[: -len(".craft")]
    if "/" in name:
        name = name.rsplit("/", 1)[-1]
    if not name or name.startswith("("):
        return ""
    return name


def ticket_capable(t: dict[str, Any] | None) -> str:
    if not t:
        return ""
    pl = t.get("payload") if isinstance(t.get("payload"), dict) else {}
    return str(t.get("capable") or (pl or {}).get("capable") or "").strip().lower()


def capable_hangar(*, prefer: str = "") -> tuple[str, str]:
    """Open vehicle ticket with capable:yes and a craft name. Recover alts skip."""
    want = str(prefer or "").strip()
    if want.endswith(".craft"):
        want = want[: -len(".craft")]
    if not want:
        fly = seated_fly_ticket()
        pl = fly.get("payload") if isinstance((fly or {}).get("payload"), dict) else {}
        waste = (pl or {}).get("waste") if isinstance((pl or {}).get("waste"), dict) else {}
        want = str((pl or {}).get("craft") or (waste or {}).get("craft") or "").strip()
        if want.endswith(".craft"):
            want = want[: -len(".craft")]
    rows: list[dict[str, Any]] = []
    for t in (load_head().get("tickets") or {}).values():
        if t.get("type") != "vehicle":
            continue
        if t.get("status") in {"done", "wont"}:
            continue
        if ticket_capable(t) != "yes":
            continue
        if not ticket_craft(t):
            continue
        rows.append(t)
    if not rows:
        return "no", ""
    if want:
        matched = [t for t in rows if ticket_craft(t) == want]
        if matched:
            rows = matched
    hang = [
        t
        for t in rows
        if "recover" not in _norm_tags(t.get("tags"))
    ]
    if hang:
        rows = hang
    rows.sort(key=lambda t: (str(t.get("updated") or ""), str(t.get("id") or "")))
    chosen = rows[-1]
    return "yes", ticket_craft(chosen)


def _tape_jsonl(t: dict[str, Any] | None) -> str:
    """payload.telem_run, else an existing docs/missions/*/logs file. Never invent a seat."""
    if not t:
        return ""
    payload = t.get("payload") if isinstance(t.get("payload"), dict) else {}
    path = str((payload or {}).get("telem_run") or "").strip()
    if path:
        return path
    live = str((payload or {}).get("live_run") or "").strip()
    if not live:
        return ""
    p = Path(live)
    if p.suffix.lower() != ".jsonl":
        p = Path(str(p) + ".jsonl")
    posix = str(p).replace("\\", "/")
    if p.is_file():
        return posix
    name = p.name
    logs = ROOT / "docs" / "missions"
    if logs.is_dir() and name:
        hits = sorted(logs.glob(f"*/logs/{name}"))
        if hits:
            return str(hits[0]).replace("\\", "/")
    return ""


def infer_links(t: dict[str, Any]) -> dict[str, Any]:
    """Skim is always desk+BRIEF. Jsonl is tape CLI only — never a read_file."""
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
        from docs_inventory import skim_mentions_forbidden

        if skim_mentions_forbidden(str(path)):
            return
        seen.add(path)
        bucket.append({"kind": kind, "path": path, "why": why})

    add(skim, "desk", "docs/program/desk.md", "sit")
    add(skim, "brief", "docs/program/tickets/BRIEF.md", "how")
    typ = t.get("type")
    craft = ticket_craft(t)
    if craft and not str(craft).endswith(".craft"):
        craft_path = f"crafts/{craft}.craft"
    else:
        craft_path = str(craft)
    run = _tape_jsonl(t)
    if typ == "fly":
        if run:
            add_tape(run)
        if craft_path:
            add(deep, "craft", craft_path, "stack")
        add(deep, "last-flight", "docs/last-flight.md", "last abort")
    elif typ == "vehicle":
        if craft_path:
            add(deep, "craft", craft_path, "stack")
    elif typ == "control":
        add(deep, "last-flight", "docs/last-flight.md", "abort")
        if run:
            add_tape(run)
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
    path = _tape_jsonl(t)
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
        f"type: {t.get('type')} {t.get('severity') or 'S3'} {t.get('priority') or 'P2'} "
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
    findings = finding_rows(t)[:8]
    for row in findings:
        owner = row.get("owner") or "none"
        line = (
            "finding: "
            f"who={row.get('who') or ''} "
            f"owner={owner} "
            f"claim={row.get('claim') or ''}"
        )
        ev = row.get("evidence") or ""
        if ev:
            shown = "telem_run" if str(ev).endswith(".jsonl") else ev
            line += f" evidence={shown}"
        if row.get("real"):
            line += " real"
        lines.append(line)
    lines.append(f'tickets feedback {tid} --claim "…"')
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


_THEM_EMPTY = frozenset({"", "none", "-", "n/a", "na", "nobody"})


def them_desk(them: str) -> str:
    """First token if it is a desk slug. ``none`` is empty."""
    return _finding_owner(them)


def _finding_owner(owner: str) -> str:
    """Desk slug, or empty for none."""
    raw = (owner or "").strip()
    if not raw:
        return ""
    first = raw.split()[0].strip().lower().rstrip(":,.")
    if first in _THEM_EMPTY:
        return ""
    if first in DESKS:
        return first
    return ""


def _as_finding(row: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize a stored row. Legacy {good,self,them} becomes a finding."""
    claim = str(row.get("claim") or "").strip()
    if not claim:
        claim = str(row.get("self") or "").strip() or str(row.get("good") or "").strip()
    if not claim:
        return None
    evidence = str(row.get("evidence") or "").strip()
    owner = _finding_owner(str(row.get("owner") or row.get("them") or ""))
    real = bool(row.get("real")) if row.get("real") is not None else False
    if real and not evidence:
        real = False
    return {
        "who": str(row.get("who") or "hank").strip() or "hank",
        "claim": claim,
        "evidence": evidence,
        "owner": owner or "none",
        "real": real,
        "at": str(row.get("at") or ""),
    }


def _raw_finding_lists(t: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not t:
        return []
    pl = t.get("payload") or {}
    blobs: list[Any] = []
    for key in ("findings", "feedback"):
        raw = pl.get(key)
        if isinstance(raw, list):
            blobs.extend(raw)
        elif isinstance(raw, dict):
            blobs.append(raw)
    return [row for row in blobs if isinstance(row, dict)]


def finding_rows(t: dict[str, Any] | None) -> list[dict[str, Any]]:
    """payload.findings plus legacy payload.feedback as {who,claim,evidence,owner,real,at}."""
    out: list[dict[str, Any]] = []
    for row in _raw_finding_lists(t):
        found = _as_finding(row)
        if found:
            out.append(found)
    return out


def feedback_rows(t: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Alias: findings (legacy trio rows included)."""
    return finding_rows(t)


def last_feedback(t: dict[str, Any] | None) -> dict[str, Any] | None:
    rows = finding_rows(t)
    return rows[-1] if rows else None


def add_feedback(
    tid: str,
    *,
    claim: str,
    evidence: str = "",
    owner: str = "",
    who: str = "hank",
    real: bool = False,
) -> dict[str, Any]:
    """Append one finding on the work ticket. Not a child ticket."""
    c = (claim or "").strip()
    if not c:
        raise TicketError("feedback claim required")
    ev = (evidence or "").strip()
    if real and not ev:
        raise TicketError("feedback --real requires --evidence")
    stored_owner = _finding_owner(owner) or "none"
    cur = show_ticket(tid)
    payload = dict(cur.get("payload") or {})
    raw = payload.get("findings")
    rows: list[Any]
    if isinstance(raw, list):
        rows = list(raw)
    elif isinstance(raw, dict):
        rows = [raw]
    else:
        rows = []
    rows.append(
        {
            "who": (who or "hank").strip() or "hank",
            "claim": c,
            "evidence": ev,
            "owner": stored_owner,
            "real": bool(real) and bool(ev),
            "at": _now(),
        }
    )
    payload["findings"] = rows
    return patch_ticket(tid, {"payload": payload}, who=who)


def close_ticket(tid: str, *, why: str = "", who: str = "hank") -> dict[str, Any]:
    """Harvest nonempty close_why as a finding when empty; refuse if both empty."""
    cur = show_ticket(tid)
    why_s = (why or "").strip()
    if not finding_rows(cur):
        if not why_s:
            raise TicketError(
                f"{tid} close refused: empty findings "
                f"(tickets feedback {tid} --claim …)"
            )
        add_feedback(tid, claim=why_s, who=who)
    fields: dict[str, Any] = {"status": "done"}
    if why_s:
        fields["close_why"] = why_s
    return patch_ticket(tid, fields, who=who)


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
    tid = _next_id(tickets, type)
    now = _now()
    tags_n = _norm_tags(tags)
    fp = alias_fingerprint(fingerprint, head.get("fingerprints") or {})
    if fingerprint_required(type, tags_n) and not fp:
        raise _fp_required_error(type)
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
        "fingerprint": fp,
        "rsi_loop": rsi_loop,
        "category": _norm_category(category, type),
        "tags": tags_n,
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
    global _LAST_RSI_ID
    _LAST_RSI_ID = ""
    if ticket["type"] != "rsi" and ticket["fingerprint"]:
        loop = str(ticket.get("rsi_loop") or "")
        rsi = maybe_open_rsi(
            ticket["fingerprint"],
            rsi_loop=None if loop in {"", "none"} else loop,
        )
        if rsi:
            _LAST_RSI_ID = rsi["id"]
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
    if "fingerprint" in fields:
        fields = {
            **fields,
            "fingerprint": alias_fingerprint(str(fields.get("fingerprint") or "")),
        }
    prev_fp = cur.get("fingerprint") or ""
    now = _now()
    _append({"op": "patch", "at": now, "id": tid, "who": who, "fields": fields})
    out = _rebuild()["tickets"][tid]
    new_fp = out.get("fingerprint") or ""
    if new_fp and not prev_fp and out.get("type") != "rsi":
        loop = str(out.get("rsi_loop") or "")
        maybe_open_rsi(
            new_fp,
            rsi_loop=None if loop in {"", "none"} else loop,
        )
        out = show_ticket(tid)
    return out


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


def commander_for(*, campaign: str = "none", fly: str = "yes") -> str:
    """Who is the abort officer. Uncrewed: none — hop pid is the writer."""
    if fly != "yes":
        return "none"
    camp = (campaign or "none").strip().lower() or "none"
    if camp == "uncrewed":
        return "none"
    return "jebediah"


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
        if science_is_catalog(t):
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


def format_learn_line(row: dict[str, Any] | None) -> str:
    """One-line hop Learn: format_landing + apo + biome + rec + sci run/bank."""
    if not isinstance(row, dict) or not row:
        return ""
    from telem import format_landing

    landing = format_landing(row)
    apo = row.get("apo_max")
    try:
        apo_s = str(int(round(float(apo)))) if apo is not None else "?"
    except (TypeError, ValueError):
        apo_s = "?"
    biome = str(row.get("biome") or "").strip()
    if not biome:
        biomes = [str(b) for b in (row.get("biomes") or []) if b]
        biome = biomes[0] if biomes else "?"
    rec = row.get("recoverable")
    rec_s = "yes" if rec is True else ("no" if rec is False else "?")
    sci_run = row.get("sci_run")
    if sci_run is None:
        run_s = "?"
    else:
        try:
            run_s = "0" if int(sci_run) == 0 else "1"
        except (TypeError, ValueError):
            run_s = "1" if sci_run else "0"
    bank = row.get("sci_bank")
    try:
        bank_s = f"{float(bank):.2f}" if bank is not None else "?"
    except (TypeError, ValueError):
        bank_s = "?"
    rem = row.get("sci_rem")
    rem_s = ""
    if rem is not None:
        try:
            rem_s = f" rem={float(rem):g}"
        except (TypeError, ValueError):
            rem_s = ""
    delta = row.get("sci_delta")
    if delta is None:
        delta_s = " +0" if row.get("sci_paid") is False else ""
    else:
        try:
            d = float(delta)
            delta_s = " +0" if abs(d) < 0.005 else f" {d:+.2f}"
        except (TypeError, ValueError):
            delta_s = ""
    return (
        f"{landing} apo={apo_s} biome={biome} rec={rec_s} "
        f"sci=run={run_s}{rem_s} bank={bank_s}{delta_s}"
    )


def _sci_run_zero(landing: dict[str, Any] | None) -> bool:
    """sci_run=0. Unknown run does not count."""
    if not isinstance(landing, dict):
        return False
    run = landing.get("sci_run")
    if run is None:
        return False
    try:
        return int(run) == 0
    except (TypeError, ValueError):
        return not bool(run)


def _pad_abort_envelope(landing: dict[str, Any] | None) -> bool:
    """Never left the pad. RF/control miss, not science waste (T-472)."""
    if not isinstance(landing, dict):
        return False
    sit = _norm_sit_key(str(landing.get("sit") or ""))
    return sit in {"prelaunch"}


def _sci_unchanged_waste(landing: dict[str, Any] | None) -> bool:
    """Living recover + sci_run=0. Unknown run does not count.

    Pad abort sit=pre_launch never lofted — control miss, not this class
    (T-472). Do not rebind FlyingHigh to a pad card. Wreck rec=no is
    already excluded.
    """
    if not isinstance(landing, dict):
        return False
    if landing.get("recoverable") is not True:
        return False
    if _pad_abort_envelope(landing):
        return False
    return _sci_run_zero(landing)


def _envelope_apo(landing: dict[str, Any] | None) -> float | None:
    if not isinstance(landing, dict):
        return None
    for key in ("apo_max", "apo"):
        raw = landing.get(key)
        if raw is None:
            continue
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return None


sci_unchanged_waste = _sci_unchanged_waste


def _norm_sit_key(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "").replace("_", "")


def _payload_sit_biome(pl: dict[str, Any]) -> tuple[str, str]:
    sit = str(pl.get("situation") or "").strip()
    biome = str(pl.get("biome") or "").strip()
    if not biome and "@" in sit:
        biome = sit.split("@", 1)[1].strip()
    return sit, biome


def _sit_biome_match(
    live_sit: str,
    live_biome: str,
    need_sit: str,
    need_biome: str,
    *,
    apo: float | None = None,
) -> bool:
    """Bound sit/biome/apo vs envelope. FlyingHigh is ≥50 km, not any flying."""
    need = _norm_sit_key(need_sit)
    live = _norm_sit_key(live_sit)
    bio_need = (need_biome or "").strip().lower()
    if not bio_need and "@" in (need_sit or ""):
        bio_need = need_sit.split("@", 1)[1].strip().lower()
    if bio_need in {"global", "none", "any"}:
        bio_need = ""
    bio_live = (live_biome or "").strip().lower()
    if (
        bio_need
        and bio_live
        and bio_need not in bio_live
        and bio_live not in bio_need
    ):
        return False
    if not need:
        return True
    if "flyinghigh" in need:
        if "flying" not in live:
            return False
        return apo is not None and apo >= FLYING_HIGH_LID_M
    if "flying" in need:
        return "flying" in live
    if "splash" in need:
        return "splash" in live
    if "landed" in need or "srfland" in need:
        return "landed" in live
    return True


def _bound_science_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        tickets = list_tickets(open_only=True)
    except Exception:
        return rows
    for t in tickets:
        if t.get("type") != "science" and t.get("category") != "science_opportunity":
            continue
        if science_is_catalog(t):
            continue
        pl = t.get("payload") or {}
        if not isinstance(pl, dict):
            continue
        eid = str(pl.get("experiment_id") or pl.get("eid") or "").strip()
        if not eid:
            continue
        sit, biome = _payload_sit_biome(pl)
        rows.append(
            {
                "id": str(t.get("id") or ""),
                "eid": eid,
                "situation": sit,
                "biome": biome,
                "craft": str(pl.get("craft") or "").strip(),
            }
        )
    rows.sort(key=lambda r: (r.get("id") or "", r.get("eid") or ""))
    return rows


def bind_snapshot(*, craft: str = "") -> dict[str, Any]:
    """Open bound science (eid/sit/biome) plus hang craft. attach_run waste latch."""
    rows = _bound_science_rows()
    crafts = [r["craft"] for r in rows if r.get("craft")]
    bind = [
        {
            "id": r["id"],
            "eid": r["eid"],
            "situation": r["situation"],
            "biome": r["biome"],
        }
        for r in rows
    ]
    return {"bind": bind, "craft": craft or (crafts[0] if crafts else "")}


def _bind_key(snap: dict[str, Any] | None) -> tuple[tuple[str, str, str, str], ...]:
    if not isinstance(snap, dict):
        return ()
    out: list[tuple[str, str, str, str]] = []
    for raw in snap.get("bind") or []:
        if not isinstance(raw, dict):
            continue
        out.append(
            (
                str(raw.get("id") or ""),
                str(raw.get("eid") or ""),
                str(raw.get("situation") or ""),
                str(raw.get("biome") or ""),
            )
        )
    return tuple(out)


def bind_matches_envelope(landing: dict[str, Any] | None) -> bool:
    """True if a bound ticket sit/biome/apo can pay the last envelope."""
    if not isinstance(landing, dict) or not landing:
        return False
    live_sit = str(landing.get("sit") or "").strip()
    live_biome = str(landing.get("biome") or "").strip()
    if not live_sit and not live_biome:
        return False
    apo = _envelope_apo(landing)
    for row in _bound_science_rows():
        need_sit = str(row.get("situation") or "")
        need_biome = str(row.get("biome") or "")
        if not need_sit and not need_biome:
            continue
        if _sit_biome_match(
            live_sit, live_biome, need_sit, need_biome, apo=apo
        ):
            return True
    return False


def hang_or_bind_changed(snap: Any, *, craft: str = "") -> bool:
    """Linus rebound or Gus hang changed since the waste latch. Missing snap is not changed."""
    if not isinstance(snap, dict) or not snap:
        return False
    now = bind_snapshot(craft=craft)
    if _bind_key(now) != _bind_key(snap):
        return True
    prev = str(snap.get("craft") or "").strip()
    cur = str(craft or now.get("craft") or "").strip()
    return bool(prev and cur and prev != cur)


def _bound_loft_only() -> bool:
    """True when every bound card is FlyingHigh/FlyingLow (no surface leftover)."""
    rows = _bound_science_rows()
    if not rows:
        return False
    n_fly = 0
    for row in rows:
        need = _norm_sit_key(str(row.get("situation") or ""))
        if not need:
            continue
        if "flying" in need:
            n_fly += 1
            continue
        return False
    return n_fly > 0


def waste_blocks_refly(
    ticket: dict[str, Any] | None,
    *,
    craft: str = "",
) -> bool:
    """Living +0 is not clean-0 until bind can pay envelope or hang/bind changed.

    Wreck rec=no is a miss — re-fly last cli. Not this latch.
    Pad abort rec=yes sit=pre_launch never lofted — control miss
    (T-472). Re-fly last cli. FlyingHigh still cannot *pay* pad
    (bind_matches_envelope stays false); that does not idle the loft
    or turn High into a pad card.

    Loft bind only (FlyingHigh / FlyingLow, no surface leftover) +
    living +0 short hop — pulse miss of the loft, not unpaid leftover
    (T-475). High cannot pay 655 m landed; that does not idle the
    High loft or turn High into a Surface card. Forest leftover vs
    Shores land still waits (bound is not loft-only).
    """
    if not ticket:
        return False
    pl = ticket.get("payload") or {}
    if not isinstance(pl, dict):
        return False
    landing = pl.get("landing")
    env = landing if isinstance(landing, dict) else None
    if not _sci_unchanged_waste(env):
        return False
    if bind_matches_envelope(env):
        return False
    if hang_or_bind_changed(pl.get("waste"), craft=craft):
        return False
    if _bound_loft_only():
        return False
    return True


def bump_fingerprint(
    fp: str,
    *,
    who: str = "hank",
    source: str = "",
    tid: str = "",
) -> int:
    """Count a miss class without minting a ticket. ×3 still opens type=rsi."""
    stem = normalize_fingerprint(fp)
    if not stem:
        return 0
    _append(
        {
            "op": "fp",
            "at": _now(),
            "fp": stem,
            "who": who,
            "source": source,
            "id": tid,
        }
    )
    _rebuild()
    maybe_open_rsi(stem)
    return fingerprint_count(stem)


def attach_run(tid: str, path: str | Path, *, who: str = "hank") -> dict[str, Any]:
    """Link a telem jsonl onto a ticket. Overwrite payload.learn from the envelope."""
    p = str(path)
    cur = show_ticket(tid)
    prev_run = str((cur.get("payload") or {}).get("telem_run") or "")
    prev_evs = list(cur.get("evidence") or [])
    evs = list(prev_evs)
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
    if cur.get("type") == "fly" and _sci_unchanged_waste(
        landing if isinstance(landing, dict) else None
    ):
        payload["waste"] = bind_snapshot()
    kind = str(landing.get("landing") or "")
    if kind:
        tags = _norm_tags(tags + [kind, "landing"])
    t = patch_ticket(
        tid,
        {"evidence": evs, "payload": payload, "tags": tags},
        who=who,
    )
    learn = format_learn_line(landing if isinstance(landing, dict) else None)
    if learn:
        t = stamp_learn(tid, learn, who="hank")
    t = show_ticket(tid)
    if learn and not finding_rows(t):
        t = add_feedback(tid, claim=learn, evidence=p, who="hank")
    fresh_run = p != prev_run and p not in prev_evs
    t = show_ticket(tid)
    # Bump only when the latch would idle fly_ready (Forest leftover
    # vs Shores). Loft-only High/Low short dud re-flies (T-475) — not
    # another sci-unchanged-recovered RSI. Pad abort already excluded
    # from _sci_unchanged_waste (T-472).
    if fresh_run and cur.get("type") == "fly" and waste_blocks_refly(t):
        bump_fingerprint(SCI_UNCHANGED_FP, who="hank", source=p, tid=tid)
        t = show_ticket(tid)
    return t


def inbox_for(desk: str, *, feedback: bool = False) -> list[dict[str, Any]]:
    """Own desk plus ``ops --tag ask`` addressed with ``payload.to``.

    ``feedback=True``: any finding ``owner=desk`` plus owned tickets with
    zero findings.
    """
    want = (desk or "").strip().lower()
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for t in list_tickets(open_only=True):
        pl = t.get("payload") or {}
        to = str(pl.get("to") or "").strip().lower()
        if feedback:
            owned = t.get("desk") == want
            rows = finding_rows(t)
            missing = owned and not rows
            owners = {_finding_owner(str(row.get("owner") or "")) for row in rows}
            if not missing and want not in owners:
                continue
        elif t.get("desk") != want and to != want:
            continue
        if t["id"] in seen:
            continue
        seen.add(t["id"])
        out.append(t)
    out.sort(key=lambda t: (t.get("severity", "S4"), t.get("priority", "P3"), t["id"]))
    return out


def format_inbox(desk: str, *, feedback: bool = False) -> str:
    rows = inbox_for(desk, feedback=feedback)
    label = f"inbox {desk}" + (" feedback" if feedback else "")
    if not rows:
        return f"{label}: none\n"
    lines = [f"{label}: {len(rows)}"]
    for t in rows:
        cat = t.get("category") or TYPE_CATEGORY.get(t.get("type") or "", "")
        tags = ",".join(t.get("tags") or []) or "-"
        lines.append(
            f"{t['id']} {cat} {t.get('severity') or 'S3'} {t.get('priority') or 'P2'} "
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
    fp = normalize_fingerprint(fp)
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
    desk = "wernher" if loop == "software" else "mortimer"
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
            f"{t['id']} {t.get('type')} {t.get('severity') or 'S3'} {t.get('priority') or 'P2'} "
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
    """Idempotent: skip titles already on the board. Also I/F twins."""
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
        existing.add(spec["title"])
        fp = spec.get("fingerprint") or ""
        if fp:
            maybe_open_rsi(fp)
    opened.extend(migrate_second_bus(who=who))
    return opened


def _title_has_token(titles: list[str], token: str) -> bool:
    """I/F ids match a title prefix so 'if F-005 not capped' is not a twin."""
    from docs_inventory import twin_title_hits

    return twin_title_hits(titles, token) > 0


def migrate_second_bus(*, who: str = "hank") -> list[str]:
    """I-012..I-020, F-001..F-015 twins. Idempotent on title token. No lesson mint."""
    from docs_inventory import IF_TWINS

    titles = [t.get("title") or "" for t in (load_head().get("tickets") or {}).values()]
    opened: list[str] = []
    for spec in IF_TWINS:
        token = spec["token"]
        title = spec["title"]
        if _title_has_token(titles, token) or title in titles:
            continue
        t = open_ticket(
            type=spec["type"],
            title=title,
            reporter=spec["reporter"],
            severity=spec["severity"],
            priority=spec["priority"],
            desk=spec["desk"],
            fingerprint=f"legacy-{token.lower()}",
            rsi_loop="ops",
            tags=["legacy-twin", token.lower()],
        )
        status = spec.get("status") or "inbox"
        fields: dict[str, Any] = {}
        if status != "inbox":
            fields["status"] = status
        why = spec.get("why") or ""
        if why:
            fields["close_why"] = why
            fields["summary"] = why
        if fields:
            t = patch_ticket(t["id"], fields, who=who)
        titles.append(t["title"])
        opened.append(t["id"])
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
    op.add_argument(
        "--fingerprint",
        default="",
        help="required for control/systems/ops --tag feedback; reuse catalog on error",
    )
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
    fb = sub.add_parser("feedback")
    fb.add_argument("id")
    fb.add_argument("--claim", required=True)
    fb.add_argument("--evidence", default="")
    fb.add_argument("--owner", default="")
    fb.add_argument("--who", default="hank")
    fb.add_argument("--real", action="store_true")
    tg = sub.add_parser("tag")
    tg.add_argument("id")
    tg.add_argument("--add", action="append", default=[], dest="tags")
    tg.add_argument("--who", default="hank")
    ib = sub.add_parser("inbox")
    ib.add_argument("--desk", required=True, choices=DESKS)
    ib.add_argument(
        "--feedback",
        action="store_true",
        help="owner=<desk> plus owned tickets with zero findings",
    )
    ld = sub.add_parser("landing")
    ld.add_argument("target", help="ticket id or jsonl path")
    ar = sub.add_parser("attach-run")
    ar.add_argument("id")
    ar.add_argument("--path", required=True)
    ar.add_argument("--who", default="hank")
    sub.add_parser("seed")
    sub.add_parser("dump", help="Rewrite slate (and seated dumps) from tickets")
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
            print(t["id"], t["desk"], t["status"])
            if _LAST_RSI_ID:
                print("rsi", _LAST_RSI_ID)
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
            t = close_ticket(args.id, why=args.why, who=args.who)
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
        if args.act == "feedback":
            t = add_feedback(
                args.id,
                claim=args.claim,
                evidence=args.evidence,
                owner=args.owner,
                who=args.who,
                real=bool(args.real),
            )
            last = last_feedback(t) or {}
            print(t["id"], "feedback", last.get("owner") or "none")
            return 0
        if args.act == "tag":
            t = add_tags(args.id, list(args.tags or []), who=args.who)
            print(t["id"], "tags", ",".join(t.get("tags") or []))
            return 0
        if args.act == "inbox":
            print(
                format_inbox(args.desk, feedback=bool(args.feedback)),
                end="",
            )
            return 0
        if args.act == "landing":
            target = args.target
            path = target
            # T/S/M/C-NNN is a ticket; anything else is a jsonl path.
            if is_ticket_id(target):
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
            learn = (t.get("payload") or {}).get("learn")
            if learn:
                print("learn:", learn)
            return 0
        if args.act == "seed":
            ids = seed_legacy()
            print("seeded", ",".join(ids) if ids else "none")
            return 0
        if args.act == "dump":
            from house_dump import render_all

            paths = render_all()
            print("dump", ",".join(paths))
            return 0
    except TicketError as exc:
        print(str(exc), file=__import__("sys").stderr)
        return 1
    return 2
