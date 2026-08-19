"""On-disk 1 Hz flight recorder. Not for the TUI.

Mun/recover start a jsonl under docs/flights/. Status does not.
Flag changes are written immediately. After exit, review.py rolls it up.
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("kspstuff")

FLIGHTS = Path("docs/flights")

_path: Path | None = None
_command: str = ""
_stamp: str = ""
_t0: float = 0.0
_last_flags: tuple[str, ...] | None = None
_last_write: float = 0.0
_count: int = 0


def stamp() -> str:
    return _stamp


def path() -> Path | None:
    return _path


def start(command: str, *, crew: str = "") -> Path:
    global _path, _command, _stamp, _t0, _last_flags, _last_write, _count
    FLIGHTS.mkdir(parents=True, exist_ok=True)
    _stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")
    _command = command
    _path = FLIGHTS / f"{_stamp}-{command}.jsonl"
    _t0 = time.monotonic()
    _last_flags = None
    _last_write = 0.0
    _count = 0
    event("start", f"command={command} crew={crew}")
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


def close() -> Path | None:
    global _path
    if _path is None:
        return None
    event("end", f"samples={_count}")
    done = _path
    _path = None
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
