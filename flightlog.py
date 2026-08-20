"""On-disk 1 Hz flight recorder. Not for the TUI.

Mun/recover start a jsonl under docs/flights/. Status does not.
Flag changes are written immediately. After exit, review.py rolls it up.
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("kspstuff")

FLIGHTS = Path("docs/flights")
LOCK = Path("docs/program/flight.lock")

_path: Path | None = None
_command: str = ""
_stamp: str = ""
_flight: str = ""
_t0: float = 0.0
_last_flags: tuple[str, ...] | None = None
_last_write: float = 0.0
_count: int = 0


def live_records() -> bool:
    """False under unittest so fixtures do not clobber last-flight / sorties."""
    flag = os.environ.get("KSPSTUFF_HANDOFF", "").lower()
    if flag in {"0", "off", "no"}:
        return False
    if "unittest" in sys.modules:
        return False
    return True


def stamp() -> str:
    return _stamp


def path() -> Path | None:
    return _path


def locked_flight() -> str:
    return _flight


class WriterLockError(RuntimeError):
    """A second phase/mun/recover tried to take the helm."""


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_lock(command: str) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if LOCK.is_file():
        raw = LOCK.read_text(encoding="utf-8")
        old_pid = 0
        old_cmd = "?"
        for line in raw.splitlines():
            if line.startswith("pid="):
                try:
                    old_pid = int(line.split("=", 1)[1].strip())
                except ValueError:
                    old_pid = 0
            if line.startswith("command="):
                old_cmd = line.split("=", 1)[1].strip()
        if _pid_alive(old_pid):
            raise WriterLockError(
                f"writer already running pid={old_pid} command={old_cmd}"
            )
        log.info("stale flight.lock pid=%s — taking helm", old_pid)
    LOCK.write_text(
        f"pid={os.getpid()}\ncommand={command}\nflight={_flight}\n",
        encoding="utf-8",
    )


def release_lock() -> None:
    try:
        if not LOCK.is_file():
            return
        raw = LOCK.read_text(encoding="utf-8")
        mine = f"pid={os.getpid()}"
        if mine in raw:
            LOCK.unlink()
    except Exception:
        log.debug("flight.lock release failed", exc_info=True)


def start(command: str, *, crew: str = "") -> Path:
    global _path, _command, _stamp, _flight, _t0, _last_flags, _last_write, _count
    if not live_records():
        acquire_lock(command)
        _path = None
        _stamp = ""
        _command = command
        _flight = ""
        _t0 = time.monotonic()
        _last_flags = None
        _last_write = 0.0
        _count = 0
        return Path()
    try:
        from missions import seated_id, seated_sorties_dir

        _flight = seated_id()
        dest = seated_sorties_dir(_flight)
        dest.mkdir(parents=True, exist_ok=True)
    except Exception:
        _flight = ""
        dest = FLIGHTS
        dest.mkdir(parents=True, exist_ok=True)
    acquire_lock(command)
    _stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    _command = command
    _path = dest / f"{_stamp}-{command}.jsonl"
    _t0 = time.monotonic()
    _last_flags = None
    _last_write = 0.0
    _count = 0
    event("start", f"command={command} crew={crew}")
    try:
        from uplink import clear

        clear(reason=f"{command} start")
    except Exception:
        log.debug("uplink clear at start failed", exc_info=True)
    return _path


def event(kind: str, msg: str, **extra: Any) -> None:
    if _path is None:
        return
    row = {
        "t": round(time.monotonic() - _t0, 3),
        "kind": kind,
        "msg": msg,
        **{k: _jsonable(v) for k, v in extra.items()},
    }
    _write(row)


def record(state: Any, tag: str = "", *, ut: float | None = None, force: bool = False) -> None:
    """1 Hz snapshots, or immediately on flag change."""
    global _last_flags, _last_write
    if _path is None:
        return
    flags = tuple(getattr(state, "flags", ()) or ())
    now = time.monotonic()
    changed = flags != _last_flags
    if not force and not changed and now - _last_write < 1.0:
        return
    _last_flags = flags
    _last_write = now
    row: dict[str, Any] = {
        "t": round(now - _t0, 3),
        "kind": "state",
        "tag": tag.strip(),
        "ut": None if ut is None else round(float(ut), 3),
        "danger": None,
    }
    try:
        row["danger"] = state.danger()
    except Exception:
        pass
    try:
        data = asdict(state)
        data["flags"] = list(flags)
        for key, val in data.items():
            row[key] = _jsonable(val)
    except Exception:
        row["line"] = getattr(state, "line", lambda: "")() 
    _write(row)
    _publish_ship(state, tag)


def _publish_ship(state: Any, tag: str) -> None:
    """Heartbeat + as_of so a crash is visibly stale (L-032 / L-037)."""
    try:
        line = state.line(tag) if hasattr(state, "line") else str(state)
        utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        bits = []
        if _flight:
            bits.append(f"flight: {_flight}")
        bits.append(line.strip())
        bits.append(f"as_of: {utc}")
        Path("docs/program/ship.md").write_text("\n".join(bits) + "\n", encoding="utf-8")
    except Exception:
        pass


def close() -> Path | None:
    global _path
    done = None
    if _path is not None:
        event("end", f"samples={_count}")
        done = _path
        _path = None
    release_lock()
    return done


def _jsonable(val: Any) -> Any:
    if isinstance(val, tuple):
        return list(val)
    if isinstance(val, float) and not math.isfinite(val):
        return None
    return val


def _write(row: dict[str, Any]) -> None:
    global _count
    if _path is None:
        return
    try:
        with _path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, default=str) + "\n")
        _count += 1
    except Exception:
        log.debug("flightlog write failed", exc_info=True)
