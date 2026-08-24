"""Disk fly gate and return-block parse. Parent asks before the Commander."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from card import card_flying_ids, card_pad_ids, card_splash_ids
from phases import NAMES as PHASE_NAMES
from tickets import commander_for, fly_fields, seated_fly_ticket, waste_blocks_refly

SCHEMAS: dict[str, tuple[str, ...]] = {
    "gene": ("go", "recommended", "phase", "f013"),
    "gus": ("capable", "craft", "f013"),
    "linus": ("science", "f013"),
    "lars": ("stack", "lesson", "f013"),
    "mortimer": ("org", "goal"),
    "wernher": ("ready_to_fly", "files"),
    "verena": ("story", "shot"),
    "katherine": ("model", "ask", "tickets"),
    "pilot": ("result", "exit", "handoff"),
}

_HANGAR_PHASES = frozenset({"pad", "hop"})


@dataclass(frozen=True, slots=True)
class ParseResult:
    desk: str
    fields: dict[str, str]
    missing: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FlyGate:
    fly: str
    reason: str
    cli: str
    campaign: str = "none"
    commander: str = "none"
    writer: str = "hop-pid"


def parse_kv(text: str) -> dict[str, str]:
    """Last fenced block if present, else whole text. Header kv only."""
    body = text
    if "```" in text:
        parts = text.split("```")
        # Prefer a fenced block that looks like a return (has a colon line).
        for chunk in reversed(parts):
            if ":" in chunk and not chunk.strip().startswith("bash"):
                body = chunk
                break
    out: dict[str, str] = {}
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line == "```":
            continue
        if line.startswith("- "):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        if key:
            out[key] = val.strip()
    return out


def parse_return(text: str, desk: str) -> ParseResult:
    slug = desk.strip().lower()
    if slug not in SCHEMAS:
        raise ValueError(f"unknown desk {desk}")
    fields = parse_kv(text)
    if slug == "gene" and fields.get("cli") and not fields.get("recommended"):
        fields["recommended"] = fields["cli"]
    missing = tuple(k for k in SCHEMAS[slug] if k not in fields or not fields[k])
    return ParseResult(desk=slug, fields=fields, missing=missing)


def _plan_kv(path: Path | None = None) -> dict[str, str]:
    from missions import seated_plan_path

    dest = path or seated_plan_path()
    if not dest.is_file():
        return {}
    return parse_kv(dest.read_text(encoding="utf-8"))


_PHASE_SIT = {
    "pad": "landed",
    "hop": "flying",
    "splash": "splash",
}


def _card_ids(phase: str, science_text: str) -> tuple[str, ...]:
    if phase == "pad":
        return card_pad_ids(science_text)
    if phase == "hop":
        return card_flying_ids(science_text)
    if phase == "splash":
        return card_splash_ids(science_text)
    return ()


def _bound_ids(ticket, sit, phase: str, science_text: str) -> tuple[str, ...]:
    sit_key = _PHASE_SIT.get(phase, "")
    ids: tuple[str, ...] = ()
    try:
        from tickets import card_science_ids

        ids = card_science_ids(situation=sit_key, ticket=ticket)
    except Exception:
        ids = tuple(fly_fields(ticket).get("science_ids") or ())
    if ids:
        return ids
    return _card_ids(phase, science_text)


def fly_gate(
    *,
    sit,
    plan: dict[str, str],
    science_text: str = "",
    phase_names: tuple[str, ...] | None = None,
    ticket=None,
) -> FlyGate:
    names = phase_names or PHASE_NAMES
    t = ticket if ticket is not None else seated_fly_ticket()
    ff = fly_fields(t)
    go = (ff.get("go") or plan.get("go") or "").lower()
    phase = (ff.get("phase") or plan.get("phase") or "").lower()
    rec = (ff.get("cli") or plan.get("recommended") or plan.get("cli") or "").strip()
    campaign = (ff.get("campaign") or plan.get("campaign") or "none").strip() or "none"

    def _out(fly: str, reason: str, cli: str) -> FlyGate:
        return FlyGate(
            fly,
            reason,
            cli,
            campaign,
            commander_for(campaign=campaign, fly=fly),
            "hop-pid",
        )

    if go != "yes":
        return _out("wait", "missing go: yes", rec)
    if sit.lock == "live":
        return _out("wait", "lock live", rec)
    hangar = str(sit.hangar)
    if hangar == "blocked":
        return _out("wait", "hangar blocked", rec)
    if hangar.startswith("recover "):
        return _out("wait", f"leftover {hangar}", rec)
    vessels = getattr(sit, "vessels", ()) or ()
    if vessels:
        return _out("wait", "leftover", rec)
    leftover = getattr(sit, "leftover", None)
    if leftover is not None:
        try:
            n = int(str(leftover).strip().lstrip("n=").split()[0])
        except ValueError:
            n = 0
        if n > 0:
            return _out("wait", "leftover", rec)
    if phase not in names:
        return _out("wait", f"phase {phase or '(none)'} not in blocks", rec)

    def _card(phase_name: str, cli: str) -> FlyGate:
        gate = _f013_and_card(sit, science_text, phase_name, cli, campaign, t)
        if gate.fly == "yes" and waste_blocks_refly(
            t, craft=str(getattr(sit, "craft", "") or "")
        ):
            return _out(
                "wait",
                "sci-unchanged-recovered bind cannot pay envelope",
                rec,
            )
        return gate

    if hangar.startswith("phase "):
        cli = rec or f"python main.py phase {phase}"
        return _card(phase, cli)
    if phase in _HANGAR_PHASES:
        if str(sit.capable).lower() != "yes":
            return _out("wait", "capable is not yes", rec)
        cli = rec or f"python main.py {phase}"
        return _card(phase, cli)
    cli = rec or f"python main.py phase {phase}"
    return _card(phase, cli)


def _f013_and_card(
    sit, science_text: str, phase: str, cli: str, campaign: str, ticket=None
) -> FlyGate:
    ids = _bound_ids(ticket, sit, phase, science_text)
    if phase in {"pad", "hop", "splash"} and not ids:
        return FlyGate(
            "wait",
            "no bound card",
            cli,
            campaign,
            commander_for(campaign=campaign, fly="wait"),
            "hop-pid",
        )
    blocked = [
        row
        for row in sit.f013
        if row.eid and (row.unlocked == "no" or row.on_craft != "yes")
    ]
    if blocked:
        row = blocked[0]
        return FlyGate(
            "wait",
            f"f013 {row.eid} unlocked={row.unlocked} on_craft={row.on_craft}",
            cli,
            campaign,
            commander_for(campaign=campaign, fly="wait"),
            "hop-pid",
        )
    return FlyGate(
        "yes",
        "ok",
        cli,
        campaign,
        commander_for(campaign=campaign, fly="yes"),
        "hop-pid",
    )


def format_gate(gate: FlyGate) -> str:
    return (
        f"fly: {gate.fly}\n"
        f"reason: {gate.reason}\n"
        f"cli: {gate.cli or 'none'}\n"
        f"campaign: {gate.campaign or 'none'}\n"
        f"writer: {gate.writer or 'hop-pid'}\n"
        f"commander: {gate.commander or 'none'}\n"
    )


def cmd_protocol(argv: list[str]) -> int:
    """``protocol fly`` | ``protocol parse --desk gene``."""
    import sys

    if not argv:
        print("protocol fly | protocol parse --desk <slug>", file=sys.stderr)
        return 2
    verb = argv[0]
    if verb == "fly":
        from desk import build_sit
        from missions import seated_science_path
        from world import WorldError

        try:
            sit = build_sit()
        except WorldError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        sci = seated_science_path()
        text = sci.read_text(encoding="utf-8") if sci.is_file() else ""
        gate = fly_gate(
            sit=sit,
            plan=_plan_kv(),
            science_text=text,
            ticket=seated_fly_ticket(),
        )
        print(format_gate(gate), end="")
        return 0 if gate.fly == "yes" else 2
    if verb == "parse":
        desk = "gene"
        if "--desk" in argv:
            i = argv.index("--desk")
            if i + 1 < len(argv):
                desk = argv[i + 1]
        raw = sys.stdin.read()
        result = parse_return(raw, desk)
        print(f"desk: {result.desk}")
        if result.missing:
            print("missing: " + ",".join(result.missing))
            return 2
        print("missing: none")
        return 0
    print(f"unknown protocol verb {verb}", file=sys.stderr)
    return 2
