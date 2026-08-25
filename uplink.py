"""Gene → flying script. Last write wins. The Commander takes it.

Files (git-friendly, next to the slate):

- ``docs/program/uplink.md`` — one command. Gene/parent writes; the
  flying process *takes* it. ``status`` must not.
- ``docs/program/loop.md`` — one-line notes. Not the stick (L-032).
- ``docs/program/note-tech.md`` — Commander → Lars/Gus/Wernher. What
  the stack needed. Gene still owns the CLI.
- ``docs/program/plan.md`` — live numbers ``set`` can change; ``phase`` /
  ``expect_*`` survive ``save_plan`` (L-037).

Gene is not on console every tick. Mid-phase the parent may
``abort|hold`` on wreck-class only. Telem wreck gates still abort even
if he said nothing. Bound+fueled ``abort`` is refused (L-033). pad/hop
start with ``clear()`` so a leftover abort cannot kill the next pad
(L-026).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from emergencies import ALIASES, CALLABLES, NAMES as EMERGENCY_NAMES

log = logging.getLogger("kspstuff")

UPLINK_PATH = Path("docs/program/uplink.md")
LAST_PATH = Path("docs/program/uplink.last")
LOOP_PATH = Path("docs/program/loop.md")  # shim; Commander notes go to the dossier
NOTE_TECH_PATH = Path("docs/program/note-tech.md")
_LEGACY_NOTE_TECH = Path("docs/program/helm-tech.md")
PLAN_PATH = Path("docs/program/plan.md")  # shim; canonical is missions/<id>/plan.md
SHIP_PATH = Path("docs/program/ship.md")


def plan_file() -> Path:
    """Seated mission plan. Do not fall through to a stale shim (L-038)."""
    from missions import seated_plan_path

    path = seated_plan_path()
    if not path.is_file():
        raise FileNotFoundError(f"no seated mission plan: {path}")
    return path


def loop_file() -> Path:
    from missions import seated_loop_path

    path = seated_loop_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text("# Gene ↔ this mission. Not the stick.\n", encoding="utf-8")
    return path

_VERBS = tuple(
    dict.fromkeys(
        (
            "abort",
            "freeze",
            "hold",
            "cut",
            "no_warp",
            "no-warp",
            "stage",
            "recover",
            "science",
            "transmit",
            "abort_pad",
            "resume",
            "capture",
            "skip-warp",
            "no-warp-pe",
            "warp-pe",
            "phys-warp",
            "phys_warp",
            "warp",
            "set",
        )
        + EMERGENCY_NAMES
        + tuple(ALIASES)
    )
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

# Envelope keys Gene owns. ``save_plan`` must not drop these (L-037).
_PLAN_META = (
    "phase",
    "next",
    "expect_body",
    "expect_peri_min",
    "expect_apo_max",
    "craft",
    "hop_apo",
    "go",
    "recommended",
)


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
    phys_warp: int | None = None
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
    try:
        path = plan_file()
    except Exception:
        log.warning("no seated mission plan — not using a stale shim")
        desk.plan = dict(_PLAN_DEFAULTS)
        return desk.plan
    desk.plan = _parse_plan(path.read_text(encoding="utf-8"))
    return desk.plan


def plan_meta() -> dict[str, str]:
    """``phase`` / ``next`` / ``expect_*`` currently on disk."""
    out: dict[str, str] = {}
    try:
        path = plan_file()
    except Exception:
        path = PLAN_PATH if PLAN_PATH.is_file() else None
    if path is None or not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower().replace("-", "_")
        if key in _PLAN_META:
            out[key] = val.strip()
    return out


def write_plan_file(*, extra: dict[str, str] | None = None) -> None:
    """Numbers from ``desk.plan`` plus preserved Gene envelope (L-037)."""
    meta = plan_meta()
    if extra:
        for key, val in extra.items():
            if key in _PLAN_META and str(val).strip():
                meta[key] = str(val).strip()
    path = plan_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Gene's plan. `python main.py phase` runs `phase:`.\n"]
    for key, val in desk.plan.items():
        lines.append(f"{key}: {val:g}\n")
    for key in _PLAN_META:
        if key in meta:
            lines.append(f"{key}: {meta[key]}\n")
    path.write_text("".join(lines), encoding="utf-8")
    try:
        from missions import sync_shim

        sync_shim()
    except Exception:
        log.debug("shim sync failed", exc_info=True)


def save_plan() -> None:
    write_plan_file()


def note(who: str, text: str) -> None:
    path = loop_file()
    line = f"{who}: {text.rstrip()}\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def note_tech(desk: str, text: str, *, who: str = "") -> Path:
    """Commander → tech desks. Does not rewrite Gene's plan."""
    from datetime import datetime, timezone

    path = NOTE_TECH_PATH
    if _LEGACY_NOTE_TECH.is_file() and not path.is_file():
        path = _LEGACY_NOTE_TECH
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text(
            "# Commander → tech\n\n"
            "The seated Commander writes what the stack needed.\n"
            "Lars / Gus / Wernher / Gene read between exits. Not the stick.\n\n",
            encoding="utf-8",
        )
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    speaker = (who or "Commander").strip() or "Commander"
    dest = (desk or "tech").strip() or "tech"
    line = f"- {stamp} **{speaker} → {dest}:** {text.rstrip()}\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return path


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
    """Consume uplink.md. Only the Commander process may call this."""
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
    desk.phys_warp = None
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
    elif cmd.verb in ("no_warp", "no-warp"):
        desk.skip_warp = True
        desk.phys_warp = 1
    elif cmd.verb in ("phys-warp", "phys_warp", "warp"):
        rate = _parse_phys_warp(cmd.arg)
        if rate is None:
            log.warning("uplink phys-warp needs 1-4, got %r", cmd.arg)
            return
        desk.phys_warp = rate
        desk.skip_warp = False
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
        bits.append("SHIP (none — flight not publishing yet)")
    cmd = peek()
    bits.append("UPLINK " + (cmd.raw if cmd else "(clear)"))
    bits.append("PLAN " + " ".join(f"{k}={v:g}" for k, v in desk.plan.items()))
    loop = loop_file()
    if loop.is_file():
        lines = [
            ln
            for ln in loop.read_text(encoding="utf-8").splitlines()
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


def _parse_phys_warp(arg: str) -> int | None:
    token = (arg or "").strip().split(None, 1)
    if not token:
        return None
    try:
        n = int(float(token[0]))
    except ValueError:
        return None
    if n < 1 or n > 4:
        return None
    return n


def phys_warp_rate() -> int | None:
    """Uplink override. None = factory. 1–4 = ×. hold/skip_warp → 1."""
    if desk.hold or desk.skip_warp:
        return 1
    return desk.phys_warp


def want_capture() -> bool:
    return desk.capture


def clear_capture() -> None:
    desk.capture = False


load_plan()
