"""Gene → flying script. Last write wins. The mun process is the only consumer.

Files (git-friendly, next to the slate):

- ``docs/program/uplink.md`` — one command. Gene writes; the script
  *takes* it (acks + clears). ``status`` must not take.
- ``docs/program/loop.md`` — one-line notes Gene ↔ pilot/script.
- ``docs/program/plan.md`` — live numbers ``set`` can change.

Gene is not on the stick every tick. He uplinks on gates and when the
*plan* is wrong (hyperbolic Mun Pe, warp stuck). FlightWatch wreck/ESC
gates still abort even if he said nothing. The pilot cannot override
``abort``. mun/recover start with ``clear()`` so a leftover abort cannot
kill the next pad (L-026).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("kspstuff")

UPLINK_PATH = Path("docs/program/uplink.md")
LAST_PATH = Path("docs/program/uplink.last")
LOOP_PATH = Path("docs/program/loop.md")
PLAN_PATH = Path("docs/program/plan.md")
SHIP_PATH = Path("docs/program/ship.md")

_VERBS = (
    "abort",
    "freeze",
    "hold",
    "resume",
    "capture",
    "skip-warp",
    "no-warp-pe",
    "warp-pe",
    "set",
)

_PLAN_CLAMP: dict[str, tuple[float, float]] = {
    "mun_pe": (8_000.0, 80_000.0),
    "suicide_start": (15_000.0, 40_000.0),
    "parking_apo": (80_000.0, 400_000.0),
    "parking_peri": (75_000.0, 400_000.0),
    "suicide_throttle": (0.2, 1.0),
    "landing_pe": (15_000.0, 40_000.0),
}

_PLAN_DEFAULTS: dict[str, float] = {
    "mun_pe": 25_000.0,
    "suicide_start": 25_000.0,
    "parking_apo": 250_000.0,
    "parking_peri": 75_000.0,
    "suicide_throttle": 1.0,
    "landing_pe": 18_000.0,
}

_CLEARED = "# cleared — Gene writes one command; last write wins\n"


@dataclass
class Command:
    verb: str
    arg: str = ""
    raw: str = ""


@dataclass
class Desk:
    """In-process flags. Survive take() until resume / opposite verb."""

    hold: bool = False
    skip_warp: bool = False
    no_warp_pe: bool = False
    capture: bool = False
    plan: dict[str, float] = field(default_factory=lambda: dict(_PLAN_DEFAULTS))


desk = Desk()


def _parse_plan(text: str) -> dict[str, float]:
    out = dict(_PLAN_DEFAULTS)
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower().replace("-", "_")
        if key not in _PLAN_CLAMP:
            continue
        try:
            num = float(val.strip())
        except ValueError:
            continue
        lo, hi = _PLAN_CLAMP[key]
        out[key] = min(hi, max(lo, num))
    return out


def load_plan() -> dict[str, float]:
    if PLAN_PATH.is_file():
        desk.plan = _parse_plan(PLAN_PATH.read_text(encoding="utf-8"))
    else:
        desk.plan = dict(_PLAN_DEFAULTS)
    return desk.plan


def save_plan() -> None:
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Live mission numbers. Gene `set` writes these.\n"]
    for key, val in desk.plan.items():
        lines.append(f"{key}: {val:g}\n")
    PLAN_PATH.write_text("".join(lines), encoding="utf-8")


def note(who: str, text: str) -> None:
    LOOP_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = f"{who}: {text.rstrip()}\n"
    with LOOP_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line)


def _parse(text: str) -> Command | None:
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        verb = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""
        if verb not in _VERBS:
            log.warning("uplink ignored unknown verb %r", verb)
            continue
        return Command(verb=verb, arg=arg, raw=line)
    return None


def peek() -> Command | None:
    if not UPLINK_PATH.is_file():
        return None
    try:
        return _parse(UPLINK_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def _ack_file(raw: str | None) -> None:
    try:
        UPLINK_PATH.parent.mkdir(parents=True, exist_ok=True)
        if raw:
            LAST_PATH.write_text(raw + "\n", encoding="utf-8")
        UPLINK_PATH.write_text(_CLEARED, encoding="utf-8")
    except Exception:
        log.debug("uplink ack failed", exc_info=True)


def take() -> Command | None:
    """Consume uplink.md. Only the mun/recover writer may call this."""
    cmd = peek()
    if cmd is None:
        return None
    _ack_file(cmd.raw)
    _apply(cmd)
    note("script", f"acked {cmd.raw}")
    log.info("uplink %s", cmd.raw)
    try:
        from flightlog import event

        event("uplink", cmd.raw)
    except Exception:
        pass
    return cmd


def clear(*, reason: str = "new flight") -> Command | None:
    """Drop leftover radio. mun/recover start here so last flight's abort cannot fire."""
    cmd = peek()
    desk.hold = False
    desk.skip_warp = False
    desk.no_warp_pe = False
    desk.capture = False
    _ack_file(f"cleared {cmd.raw}" if cmd is not None else None)
    if cmd is None:
        return None
    note("script", f"cleared leftover {cmd.raw} ({reason})")
    log.info("uplink cleared leftover %s (%s)", cmd.raw, reason)
    try:
        from flightlog import event

        event("uplink", f"cleared leftover {cmd.raw}")
    except Exception:
        pass
    return cmd


def _apply(cmd: Command) -> None:
    if cmd.verb == "hold":
        desk.hold = True
    elif cmd.verb == "resume":
        desk.hold = False
        desk.skip_warp = False
    elif cmd.verb == "freeze":
        desk.hold = True
    elif cmd.verb == "skip-warp":
        desk.skip_warp = True
    elif cmd.verb == "no-warp-pe":
        desk.no_warp_pe = True
    elif cmd.verb == "warp-pe":
        desk.no_warp_pe = False
    elif cmd.verb == "capture":
        desk.capture = True
        desk.no_warp_pe = True
    elif cmd.verb == "set":
        m = re.match(r"([a-z_]+)\s+([0-9.+-eE]+)$", cmd.arg.strip(), re.I)
        if not m:
            log.warning("uplink set needs `set key number`, got %r", cmd.arg)
            return
        key = m.group(1).lower().replace("-", "_")
        if key not in _PLAN_CLAMP:
            log.warning("uplink set unknown key %s", key)
            return
        lo, hi = _PLAN_CLAMP[key]
        desk.plan[key] = min(hi, max(lo, float(m.group(2))))
        save_plan()


def radio_text() -> str:
    """Gene inbox. No kRPC. Ship line + pending uplink + last talk."""
    bits: list[str] = []
    if SHIP_PATH.is_file():
        bits.append("SHIP " + SHIP_PATH.read_text(encoding="utf-8").strip())
    else:
        bits.append("SHIP (none — mun not publishing yet)")
    cmd = peek()
    bits.append("UPLINK " + (cmd.raw if cmd else "(clear)"))
    bits.append("PLAN " + " ".join(f"{k}={v:g}" for k, v in desk.plan.items()))
    if LOOP_PATH.is_file():
        lines = [
            ln
            for ln in LOOP_PATH.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        bits.append("LOOP")
        bits.extend(f"  {ln}" for ln in lines[-8:])
    else:
        bits.append("LOOP (empty)")
    return "\n".join(bits) + "\n"


def write(verb: str, arg: str = "", *, who: str = "Gene") -> None:
    """Gene / parent. Last write wins. Does not touch kRPC."""
    verb = verb.lower().strip()
    if verb not in _VERBS:
        raise ValueError(f"unknown uplink verb {verb}")
    UPLINK_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = verb if not arg else f"{verb} {arg}"
    UPLINK_PATH.write_text(line + "\n", encoding="utf-8")
    note(who, line)


def holding() -> bool:
    return desk.hold


def skip_warp() -> bool:
    return desk.skip_warp or desk.hold


def no_warp_pe() -> bool:
    return desk.no_warp_pe or desk.hold


def want_capture() -> bool:
    return desk.capture


def clear_capture() -> None:
    desk.capture = False


load_plan()
