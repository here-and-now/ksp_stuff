"""Disk fly gate and return-block parse. Parent asks before the Commander."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from card import card_flying_ids, card_pad_ids, card_splash_ids
from phases import NAMES as PHASE_NAMES

SCHEMAS: dict[str, tuple[str, ...]] = {
    "gene": ("go", "recommended", "phase", "f013"),
    "gus": ("capable", "craft", "f013"),
    "linus": ("science", "card", "f013"),
    "lars": ("stack", "lesson", "f013"),
    "mortimer": ("org", "goal"),
    "wernher": ("ready_to_fly", "files"),
    "verena": ("story", "shot"),
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
    missing = tuple(k for k in SCHEMAS[slug] if k not in fields or not fields[k])
    return ParseResult(desk=slug, fields=fields, missing=missing)


def _plan_kv(path: Path | None = None) -> dict[str, str]:
    from missions import seated_plan_path

    dest = path or seated_plan_path()
    if not dest.is_file():
        return {}
    return parse_kv(dest.read_text(encoding="utf-8"))


def _card_ids(phase: str, science_text: str) -> tuple[str, ...]:
    if phase == "pad":
        return card_pad_ids(science_text)
    if phase == "hop":
        return card_flying_ids(science_text)
    if phase == "splash":
        return card_splash_ids(science_text)
    return ()


def fly_gate(
    *,
    sit,
    plan: dict[str, str],
    science_text: str = "",
    phase_names: tuple[str, ...] | None = None,
) -> FlyGate:
    names = phase_names or PHASE_NAMES
    go = plan.get("go", "").lower()
    phase = (plan.get("phase") or "").lower()
    rec = plan.get("recommended", "").strip()
    if go != "yes":
        return FlyGate("wait", "missing go: yes", rec)
    if sit.lock == "live":
        return FlyGate("wait", "lock live", rec)
    hangar = str(sit.hangar)
    if hangar == "blocked":
        return FlyGate("wait", "hangar blocked", rec)
    if hangar.startswith("recover "):
        return FlyGate("wait", f"leftover {hangar}", rec)
    if phase not in names:
        return FlyGate("wait", f"phase {phase or '(none)'} not in blocks", rec)
    if hangar.startswith("phase "):
        cli = rec or f"python main.py phase {phase}"
        return _f013_and_card(sit, science_text, phase, cli)
    if phase in _HANGAR_PHASES:
        if str(sit.capable).lower() != "yes":
            return FlyGate("wait", "capable is not yes", rec)
        cli = rec or f"python main.py {phase}"
        return _f013_and_card(sit, science_text, phase, cli)
    cli = rec or f"python main.py phase {phase}"
    return _f013_and_card(sit, science_text, phase, cli)


def _f013_and_card(sit, science_text: str, phase: str, cli: str) -> FlyGate:
    ids = _card_ids(phase, science_text)
    if phase in {"pad", "hop", "splash"} and not ids:
        return FlyGate("wait", "no bound card", cli)
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
        )
    return FlyGate("yes", "ok", cli)


def format_gate(gate: FlyGate) -> str:
    return f"fly: {gate.fly}\nreason: {gate.reason}\ncli: {gate.cli or 'none'}\n"


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
        gate = fly_gate(sit=sit, plan=_plan_kv(), science_text=text)
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
