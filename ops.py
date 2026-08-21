"""Hank dispatch. Disk, no kRPC. Pad occupancy first."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tickets import DESKS, list_tickets, load_head

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "docs" / "program" / "flight.lock"
DESK = ROOT / "docs" / "program" / "desk.md"


def lock_live() -> bool:
    return LOCK.is_file()


def parse_desk(text: str | None = None) -> dict[str, str]:
    raw = text if text is not None else (
        DESK.read_text(encoding="utf-8") if DESK.is_file() else ""
    )
    out: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        key = k.strip().lower()
        if key:
            out[key] = v.strip()
    return out


def _open_by_type(*types: str) -> list[dict[str, Any]]:
    rows = []
    for t in list_tickets(open_only=True):
        if t.get("type") in types and t.get("status") not in {"blocked", "inbox"}:
            rows.append(t)
        elif t.get("type") in types and t.get("status") == "inbox":
            rows.append(t)
    return rows


def next_actions(
    *,
    desk: dict[str, str] | None = None,
    locked: bool | None = None,
) -> dict[str, Any]:
    """Who Hank hires this turn. Illegal combos are not emitted."""
    d = desk if desk is not None else parse_desk()
    live = lock_live() if locked is None else locked
    hangar = d.get("hangar", "none")
    fly_tickets = [
        t
        for t in list_tickets(open_only=True)
        if t.get("type") == "fly"
        and t.get("status") not in {"done", "wont", "blocked"}
    ]
    fly_ready = [
        t
        for t in fly_tickets
        if (t.get("payload") or {}).get("go") == "yes"
        or t.get("go") == "yes"
    ]
    recover = [
        t
        for t in list_tickets(open_only=True)
        if t.get("type") == "recover" and t.get("severity") == "S1"
    ]
    hires: list[dict[str, Any]] = []
    pad = "flight" if live else "idle"

    if hangar.startswith("recover ") or hangar.startswith("phase "):
        if not live:
            hires.append(
                {
                    "desk": "jebediah",
                    "tickets": [t["id"] for t in recover]
                    or ["(open recover)"],
                    "why": f"leftover hangar={hangar}",
                }
            )
            return {
                "lock": "live" if live else "free",
                "pad": pad,
                "fly_ready": None,
                "hire": hires,
            }

    if live:
        for desk_name in ("gus", "linus", "wernher", "lars", "verena"):
            batch = [
                t
                for t in list_tickets(open_only=True)
                if t.get("desk") == desk_name
                and t.get("status") in {"inbox", "triage", "ready", "assigned"}
                and t.get("type") not in {"fly", "recover"}
            ]
            if batch:
                hires.append(
                    {
                        "desk": desk_name,
                        "tickets": [t["id"] for t in batch],
                        "why": "lock live — ground only, batched",
                    }
                )
        return {
            "lock": "live",
            "pad": "flight",
            "fly_ready": None,
            "hire": hires,
        }

    if recover:
        hires.append(
            {
                "desk": "jebediah",
                "tickets": [t["id"] for t in recover],
                "why": "S1 recover",
            }
        )
        return {
            "lock": "free",
            "pad": "idle",
            "fly_ready": None,
            "hire": hires,
        }

    if fly_ready:
        t = fly_ready[0]
        cli = (t.get("payload") or {}).get("cli") or t.get("cli") or ""
        hires.append(
            {
                "desk": "jebediah",
                "tickets": [t["id"]],
                "cli": cli,
                "why": "lock free, go yes — pad occupancy",
            }
        )
        for desk_name in ("gus", "linus", "wernher"):
            batch = [
                x
                for x in list_tickets(open_only=True)
                if x.get("desk") == desk_name
                and x.get("type") not in {"fly", "recover"}
                and x.get("status") in {"inbox", "triage", "ready", "assigned"}
            ]
            if batch:
                hires.append(
                    {
                        "desk": desk_name,
                        "tickets": [x["id"] for x in batch],
                        "why": "parallel ground while Commander flies (will be lock live)",
                    }
                )
        return {
            "lock": "free",
            "pad": "idle",
            "fly_ready": t["id"],
            "hire": hires,
        }

    needing_go = [
        t
        for t in fly_tickets
        if (t.get("payload") or {}).get("go") in (None, "", "wait")
        and t.get("go") not in {"yes"}
    ]
    if needing_go:
        t = needing_go[0]
        hires.append(
            {
                "desk": "gene",
                "tickets": [t["id"]],
                "why": "fly ticket needs go stamp",
            }
        )
        veh = [
            x
            for x in list_tickets(open_only=True)
            if x.get("type") == "vehicle"
            and x.get("status") in {"inbox", "triage", "ready", "assigned"}
        ]
        sci = [
            x
            for x in list_tickets(open_only=True)
            if x.get("type") == "science"
            and x.get("status") in {"inbox", "triage", "ready", "assigned"}
        ]
        if veh:
            hires.append(
                {
                    "desk": "gus",
                    "tickets": [x["id"] for x in veh],
                    "why": "batch vehicle tickets (tree/unlock)",
                }
            )
        if sci:
            hires.append(
                {
                    "desk": "linus",
                    "tickets": [x["id"] for x in sci],
                    "why": "batch science tickets (bind still blocked on capable)",
                }
            )
        return {
            "lock": "free",
            "pad": "idle",
            "fly_ready": None,
            "hire": hires,
        }

    for desk_name in DESKS:
        if desk_name in {"jebediah", "gene", "hank", "walt"}:
            continue
        batch = [
            t
            for t in list_tickets(open_only=True)
            if t.get("desk") == desk_name
            and t.get("status") in {"inbox", "triage", "ready", "assigned"}
        ]
        if batch:
            hires.append(
                {
                    "desk": desk_name,
                    "tickets": [t["id"] for t in batch],
                    "why": "ground queue",
                }
            )
    if not hires:
        hires.append(
            {
                "desk": "hank",
                "tickets": [],
                "why": "pad idle — no fly_ready, no leftover, no ground",
            }
        )
    return {
        "lock": "free",
        "pad": "idle",
        "fly_ready": None,
        "hire": hires,
    }


def format_next(actions: dict[str, Any]) -> str:
    lines = [
        f"lock: {actions.get('lock')}",
        f"pad: {actions.get('pad')}",
        f"fly_ready: {actions.get('fly_ready') or 'none'}",
        "hire:",
    ]
    for h in actions.get("hire") or []:
        tickets = ",".join(h.get("tickets") or []) or "none"
        extra = f" cli={h['cli']}" if h.get("cli") else ""
        lines.append(
            f"  - desk: {h.get('desk')} tickets: [{tickets}]{extra}"
        )
        lines.append(f"    why: {h.get('why')}")
    return "\n".join(lines) + "\n"


def fly_gate() -> dict[str, str]:
    """Disk fly gate from tickets, not dual plan.md."""
    act = next_actions()
    fid = act.get("fly_ready")
    if not fid:
        why = "no fly_ready"
        if act.get("hire"):
            why = act["hire"][0].get("why") or why
        return {"fly": "wait", "reason": why, "cli": "none"}
    from tickets import show_ticket

    t = show_ticket(fid)
    cli = (t.get("payload") or {}).get("cli") or t.get("cli") or "none"
    return {"fly": "yes", "reason": "ok", "cli": cli}


def format_fly(g: dict[str, str]) -> str:
    return f"fly: {g['fly']}\nreason: {g['reason']}\ncli: {g['cli']}\n"


def cmd_ops(argv: list[str] | None = None) -> int:
    verb = (argv or ["next"])[0] if argv else "next"
    if verb == "fly":
        g = fly_gate()
        print(format_fly(g), end="")
        return 0 if g["fly"] == "yes" else 2
    print(format_next(next_actions()), end="")
    return 0
