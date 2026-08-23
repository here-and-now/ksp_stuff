"""Hank dispatch. Disk, no kRPC. Pad occupancy first."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tickets import (
    DESKS,
    batch_reasoning,
    fly_fields,
    list_tickets,
    load_head,
    needs_learn,
    packet_cmd,
    show_ticket,
)

ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "docs" / "program" / "flight.lock"
DESK = ROOT / "docs" / "program" / "desk.md"
OVERLAY = ROOT / "docs" / "program" / "overlay.last"
_OVERLAY_KEYS = frozenset({"can_revert", "overlay", "ksc_ready"})


def lock_live() -> bool:
    return LOCK.is_file()


def parse_desk(text: str | None = None) -> dict[str, str]:
    raw = text if text is not None else (
        DESK.read_text(encoding="utf-8") if DESK.is_file() else ""
    )
    out: dict[str, str] = {}
    leftover_n = ""
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("# leftover vessels n="):
            leftover_n = stripped.split("n=", 1)[1].strip()
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        key = k.strip().lower()
        if key:
            out[key] = v.strip()
    if leftover_n and "leftover" not in out:
        out["leftover"] = leftover_n
    if text is None and OVERLAY.is_file():
        try:
            overlay_txt = OVERLAY.read_text(encoding="utf-8")
        except OSError:
            overlay_txt = ""
        for line in overlay_txt.splitlines():
            if ":" not in line:
                continue
            k, _, v = line.partition(":")
            key = k.strip().lower()
            if key in _OVERLAY_KEYS and v.strip():
                out[key] = v.strip()
    return out


def leftover_n(desk: dict[str, str]) -> int:
    raw = (desk.get("leftover") or "0").strip().lower()
    if raw.startswith("n="):
        raw = raw[2:].strip()
    token = raw.split()[0] if raw else "0"
    try:
        return int(token)
    except ValueError:
        if token in {"", "0", "none", "no"}:
            return 0
        return 1


def leftover_cli(desk: dict[str, str]) -> str:
    hangar = (desk.get("hangar") or "none").strip().lower()
    rec = (desk.get("recoverable") or "").strip().lower()
    overlay = (desk.get("can_revert") or desk.get("overlay") or "").strip().lower()
    if overlay in {"true", "yes", "1"}:
        return "python main.py recover-probe --space-center"
    if rec in {"no", "false", "0"}:
        return "python main.py recover-probe --space-center"
    if hangar.startswith("recover "):
        return "python main.py recover-probe --space-center"
    return "python main.py recover-probe --recover"


def leftover_sit(desk: dict[str, str]) -> bool:
    hangar = desk.get("hangar") or "none"
    n = leftover_n(desk)
    ready = (desk.get("ksc_ready") or "").strip().lower()
    if n == 0 and ready in {"true", "yes", "1"}:
        return False
    overlay = (desk.get("can_revert") or desk.get("overlay") or "").strip().lower()
    if overlay in {"true", "yes", "1"}:
        return True
    if hangar.startswith("recover ") or hangar.startswith("phase "):
        return True
    return n > 0


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
    fly_ready = [t for t in fly_tickets if fly_fields(t).get("go") == "yes"]
    recover = [
        t
        for t in list_tickets(open_only=True)
        if t.get("type") == "recover" and t.get("severity") == "S1"
    ]
    recover_any = [
        t
        for t in list_tickets(open_only=True)
        if t.get("type") == "recover"
    ]
    hires: list[dict[str, Any]] = []
    pad = "flight" if live else "idle"

    def _hire(desk: str, rows: list[dict[str, Any]], why: str, cli: str = "") -> None:
        tids = [t["id"] for t in rows]
        reasoning = batch_reasoning(rows, desk) if rows else (
            "high" if desk == "mortimer" else "medium"
        )
        item: dict[str, Any] = {
            "desk": desk,
            "tickets": tids,
            "reasoning": reasoning,
            "packet": packet_cmd(tids, reasoning),
            "why": why,
        }
        if cli:
            item["cli"] = cli
        hires.append(item)

    if leftover_sit(d) and not live:
        rows = recover_any or recover or [
            {
                "id": "",
                "desk": "hank",
                "type": "recover",
                "severity": "S2",
                "priority": "P0",
            }
        ]
        call = leftover_cli(d)
        _hire("hank", rows, f"leftover hangar={hangar}", cli=call)
        return {
            "lock": "free",
            "pad": pad,
            "fly_ready": None,
            "hire": hires,
            "ksc": "leftover",
            "call": call,
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
                _hire(desk_name, batch, "lock live — ground only, batched")
        return {
            "lock": "live",
            "pad": "flight",
            "fly_ready": None,
            "hire": hires,
        }

    if recover:
        call = leftover_cli(d)
        _hire("hank", recover, "S1 recover", cli=call)
        return {
            "lock": "free",
            "pad": "idle",
            "fly_ready": None,
            "hire": hires,
            "ksc": "leftover",
            "call": call,
        }

    if fly_ready:
        t = fly_ready[0]
        cli = fly_fields(t).get("cli") or ""
        _hire("jebediah", [t], "lock free, go yes — pad occupancy", cli=cli)
        for desk_name in ("gus", "linus", "wernher", "lars"):
            batch = [
                x
                for x in list_tickets(open_only=True)
                if x.get("desk") == desk_name
                and x.get("type") not in {"fly", "recover"}
                and x.get("status") in {"inbox", "triage", "ready", "assigned"}
            ]
            if batch:
                _hire(
                    desk_name,
                    batch,
                    "parallel ground while Commander flies (will be lock live)",
                )
        return {
            "lock": "free",
            "pad": "idle",
            "fly_ready": t["id"],
            "hire": hires,
        }

    needing_go = [t for t in fly_tickets if fly_fields(t).get("go") != "yes"]
    if needing_go:
        t = needing_go[0]
        why = (
            "campaign stop — batch Learn"
            if needs_learn(t)
            else "fly ticket needs go stamp"
        )
        _hire("gene", [t], why)
        ready = {"inbox", "triage", "ready", "assigned"}

        def _typed(*types: str) -> list[dict[str, Any]]:
            return [
                x
                for x in list_tickets(open_only=True)
                if x.get("type") in types and x.get("status") in ready
            ]

        veh = _typed("vehicle")
        sci = _typed("science")
        ctrl = _typed("control")
        seen = {x["id"] for x in veh + sci + ctrl}
        sys_rows = [
            x
            for x in list_tickets(open_only=True)
            if x["id"] not in seen
            and x.get("status") in ready
            and x.get("type") not in {"fly", "recover"}
            and (x.get("type") == "systems" or x.get("desk") == "wernher")
        ]
        if veh:
            _hire("gus", veh, "batch vehicle tickets (tree/unlock)")
        if sci:
            _hire("linus", sci, "batch science tickets (bind still blocked on capable)")
        if ctrl:
            _hire("lars", ctrl, "batch control tickets (miss/fingerprint)")
        if sys_rows:
            _hire("wernher", sys_rows, "batch systems tickets")
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
            _hire(desk_name, batch, "ground queue")
    if not hires:
        _hire("hank", [], "pad idle — no fly_ready, no leftover, no ground")
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
    ]
    if actions.get("ksc"):
        lines.append(f"ksc: {actions['ksc']}")
    if actions.get("call"):
        lines.append(f"call: {actions['call']}")
    lines.append("hire:")
    for h in actions.get("hire") or []:
        tickets = ",".join(h.get("tickets") or []) or "none"
        extra = f" cli={h['cli']}" if h.get("cli") else ""
        lines.append(
            f"  - desk: {h.get('desk')} tickets: [{tickets}] "
            f"reasoning={h.get('reasoning', 'medium')}{extra}"
        )
        if h.get("packet"):
            lines.append(f"    packet: {h.get('packet')}")
        lines.append(f"    why: {h.get('why')}")
    return "\n".join(lines) + "\n"


def fly_gate(
    *,
    desk: dict[str, str] | None = None,
    locked: bool | None = None,
) -> dict[str, str]:
    """Disk fly gate from tickets, not dual plan.md."""
    act = next_actions(desk=desk, locked=locked)
    fid = act.get("fly_ready")
    if not fid:
        why = "no fly_ready"
        if act.get("hire"):
            why = act["hire"][0].get("why") or why
        return {"fly": "wait", "reason": why, "cli": "none"}
    from tickets import show_ticket

    t = show_ticket(fid)
    ff = fly_fields(t)
    return {
        "fly": "yes",
        "reason": "ok",
        "cli": ff.get("cli") or "none",
        "campaign": ff.get("campaign") or "none",
    }


def format_fly(g: dict[str, str]) -> str:
    lines = [
        f"fly: {g['fly']}",
        f"reason: {g['reason']}",
        f"cli: {g['cli']}",
    ]
    if g.get("campaign"):
        lines.append(f"campaign: {g['campaign']}")
    return "\n".join(lines) + "\n"


def cmd_ops(argv: list[str] | None = None) -> int:
    verb = (argv or ["next"])[0] if argv else "next"
    if verb == "fly":
        g = fly_gate()
        print(format_fly(g), end="")
        return 0 if g["fly"] == "yes" else 2
    print(format_next(next_actions()), end="")
    return 0
