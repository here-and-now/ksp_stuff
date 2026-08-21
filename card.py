"""Linus science.md card. Empty is not a sit."""

from __future__ import annotations

from dataclasses import dataclass

# Test fixtures only — never fly defaults.
PAD_EXPERIMENTS = ("mysteryGoo", "temperatureScan")
HOP_EXPERIMENTS = ("kerbalism_TELEMETRY", "temperatureScan")
SPLASH_EXPERIMENTS = ("mysteryGoo",)

NO_BOUND_CARD = "no bound card"

_FLYING_SIT = frozenset(
    {
        "flying",
        "flyinglow",
        "flyinghigh",
        "inspace",
        "inspacelow",
        "inspacehigh",
    }
)
_SPLASH_SIT = frozenset(
    {
        "srfsplashed",
        "splashed",
        "splash",
        "srflanded",
        "landed",
        "srf",
    }
)
_PAD_SIT = frozenset(
    {
        "srflanded",
        "landed",
        "prelaunch",
        "pre_launch",
    }
)
_EID_KEYS = frozenset({"experiment", "experiment_id"})


@dataclass(frozen=True, slots=True)
class CardRow:
    eid: str
    section: str
    situation: str


def _norm(text: str) -> str:
    return text.lower().replace(" ", "").replace("_", "")


def parse_card(text: str) -> tuple[CardRow, ...]:
    """Dashed experiment blocks plus bare ``experiment_id:`` lines."""
    rows: list[CardRow] = []
    seen: set[str] = set()
    section = ""
    current_eid: str | None = None
    current_sit = ""

    def flush() -> None:
        nonlocal current_eid, current_sit
        if current_eid and current_eid not in seen:
            seen.add(current_eid)
            rows.append(
                CardRow(eid=current_eid, section=section, situation=current_sit)
            )
        current_eid = None
        current_sit = ""

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            flush()
            section = line.lstrip("#").strip()
            continue
        if line.startswith("-"):
            flush()
            rest = line.lstrip("-").strip()
            key, sep, val = rest.partition(":")
            if sep and key.strip().lower() in _EID_KEYS:
                eid = val.strip().split()[0] if val.strip() else ""
                current_eid = eid or None
            continue
        if line.lower().startswith("experiment_id:"):
            flush()
            eid = line.split(":", 1)[1].strip().strip("`").split()[0]
            if eid and eid not in seen:
                seen.add(eid)
                rows.append(CardRow(eid=eid, section=section, situation=""))
            continue
        if current_eid and ":" in line:
            key, _, val = line.partition(":")
            if key.strip().lower() == "situation":
                current_sit = val.strip().split()[0] if val.strip() else ""
            continue
    flush()
    return tuple(rows)


def card_experiments(text: str) -> list[str]:
    """Every bound id, order preserved. Empty text → []."""
    return [row.eid for row in parse_card(text)]


def _take(row: CardRow, kind: str) -> bool:
    sec = row.section.lower()
    sit = _norm(row.situation)
    splash_sec = any(w in sec for w in ("splash", "water"))
    flying_sec = any(w in sec for w in ("fly", "space"))
    pad_sec = any(w in sec for w in ("pad", "landed", "cape", "shore"))
    splash_sit = sit in {"srfsplashed", "splashed", "splash"} or sit.startswith(
        "srfsplash"
    )
    flying_sit = sit in _FLYING_SIT or sit.startswith("flying") or sit.startswith(
        "inspace"
    )
    pad_sit = sit in _PAD_SIT or sit.startswith("srfland")
    if kind == "all":
        return True
    if kind == "flying":
        land_sec = any(w in sec for w in ("splash", "landed", "surface", "water"))
        fly_sec = flying_sec or not sec
        land_sit = sit in _SPLASH_SIT or sit.startswith("srf")
        if land_sit or land_sec:
            return False
        return flying_sit or fly_sec
    if kind == "splash":
        return splash_sit or splash_sec
    if kind == "pad":
        take = (pad_sec or pad_sit) and not splash_sec and not flying_sec
        if splash_sit or flying_sit:
            return False
        return take
    raise ValueError(f"unknown card kind {kind}")


def card_ids(text: str, kind: str) -> tuple[str, ...]:
    return tuple(row.eid for row in parse_card(text) if _take(row, kind))


def card_pad_ids(text: str) -> tuple[str, ...]:
    return card_ids(text, "pad")


def card_flying_ids(text: str) -> tuple[str, ...]:
    return card_ids(text, "flying")


def card_splash_ids(text: str) -> tuple[str, ...]:
    return card_ids(text, "splash")


def card_experiment_ids(text: str) -> tuple[str, ...]:
    """All dashed/id lines. Empty → (). Not a hop default."""
    return tuple(card_experiments(text))
