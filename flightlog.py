"""On-disk flight recorder. Not for the TUI.

One **run** is one Commander command (`python main.py pad`). Files live
under the seated mission ``logs/``. Stamp is Earth UTC with seconds
plus Kerbal UT/MET in the jsonl start event. Cadence is Telem
``pulse_s`` (cruise ~5 Hz, ~20 Hz while throttled or near the surface). A ``kind=landing``
row is the flying→splashed/landed transition. ``docs/flights/index.jsonl``
indexes runs for the ticket bus.
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("kspstuff")

FLIGHTS = Path("docs/flights")
INDEX = FLIGHTS / "index.jsonl"
LOCK = Path("docs/program/flight.lock")
SHIP = Path("docs/program/ship.md")
_SHIP_PRINT = ("heading", "wreck", "ec", "alt", "as_of")
_SHIP_EXTRA = (
    "sit",
    "vessel",
    "flight",
    "horiz",
    "pitch",
    "fuel",
    "met",
    "lat",
    "lon",
    "downrange",
    "biome",
    "flags",
    "stale",
    "mass",
    "parts_n",
    "root",
)
_AS_OF_FMT = ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ")
_REPR_FIELD = re.compile(
    r"\b(heading|wreck|ec|alt|situation|vessel|horiz|pitch|fuel|met|lat|lon|downrange|biome|apo|hz|throttle|body|mass|parts_n|root)="
    r"([^,)]+)"
)
_STATUS_FIELD = re.compile(
    r"\b(body|sit|alt|peri|apo|ec|fuel|wreck|horiz|vz|hdg|pitch|aoa|biome|lat|lon|downrange|vessel)=(\S+)"
)
_KV_LINE = re.compile(r"^([A-Za-z_]+)\s*:\s*(.*)$")
_FLAGS_REPR = re.compile(r"\bflags=\(([^)]*)\)")

_path: Path | None = None
_command: str = ""
_stamp: str = ""
_flight: str = ""
_session: Any = None
_t0: float = 0.0
_last_flags: tuple[str, ...] | None = None
_last_write: float = 0.0
_count: int = 0
_last_state: dict[str, Any] | None = None
_wrote_landing: bool = False


def live_records() -> bool:
    """False under unittest so fixtures do not clobber last-flight / logs."""
    flag = os.environ.get("KSPSTUFF_HANDOFF", "").lower()
    if flag in {"0", "off", "no"}:
        return False
    if "unittest" in sys.modules:
        return False
    return True


def earth_stamp(now: datetime | None = None) -> str:
    """Filesystem-safe Earth UTC: 2026-08-20T12-35-42Z (not 1235Z)."""
    t = now or datetime.now(timezone.utc)
    return t.strftime("%Y-%m-%dT%H-%M-%SZ")


def earth_display(now: datetime | None = None) -> str:
    t = now or datetime.now(timezone.utc)
    return t.strftime("%Y-%m-%d %H:%M:%S UTC")


def format_kerbal_clock(seconds: float, *, label: str = "UT") -> str:
    """KSP universal/MET as days + hh:mm:ss. Raw seconds stay in jsonl."""
    try:
        s = float(seconds)
    except (TypeError, ValueError):
        return "?"
    if not math.isfinite(s) or s < 0:
        return "?"
    whole = int(s)
    days, rem = divmod(whole, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    if label == "MET":
        return f"MET {days}d {hours:02d}:{mins:02d}:{secs:02d}"
    return f"{days}d {hours:02d}:{mins:02d}:{secs:02d} UT"


def kerbal_clocks(session: Any = None) -> dict[str, Any]:
    ut = met = None
    if session is not None:
        try:
            ut = float(session.space_center.ut)
        except Exception:
            ut = None
        try:
            vessel = session.active_vessel
            if vessel is not None:
                met = float(vessel.met)
        except Exception:
            met = None
    out: dict[str, Any] = {
        "kerbal_ut_s": None if ut is None else round(ut, 3),
        "kerbal_met_s": None if met is None else round(met, 3),
        "kerbal_ut": format_kerbal_clock(ut) if ut is not None else "?",
        "kerbal_met": format_kerbal_clock(met, label="MET") if met is not None else "?",
    }
    return out


def stamp() -> str:
    return _stamp


def command() -> str:
    return _command


def path() -> Path | None:
    return _path


def locked_flight() -> str:
    return _flight


def writer_session() -> Any:
    """Session for this run, if ``start()`` still holds it."""
    return _session


class WriterLockError(RuntimeError):
    """A second pad/phase tried to take the stick."""


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def writer_lock_live() -> bool:
    """True only if flight.lock names a still-running pid."""
    if not LOCK.is_file():
        return False
    raw = LOCK.read_text(encoding="utf-8")
    pid = 0
    for line in raw.splitlines():
        if line.startswith("pid="):
            try:
                pid = int(line.split("=", 1)[1].strip())
            except ValueError:
                pid = 0
            break
    return _pid_alive(pid)


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
        log.info("stale flight.lock pid=%s — taking the stick", old_pid)
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


def start(command: str, *, crew: str = "", session: Any = None) -> Path:
    global _path, _command, _stamp, _flight, _t0, _last_flags, _last_write, _count
    global _last_state, _wrote_landing, _session
    _session = session
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
        _last_state = None
        _wrote_landing = False
        return Path()
    try:
        from missions import seated_id, seated_logs_dir

        _flight = seated_id()
        dest = seated_logs_dir(_flight)
        dest.mkdir(parents=True, exist_ok=True)
    except Exception:
        _flight = ""
        dest = FLIGHTS
        dest.mkdir(parents=True, exist_ok=True)
    acquire_lock(command)
    now = datetime.now(timezone.utc)
    _stamp = earth_stamp(now)
    _command = command
    _path = dest / f"{_stamp}-{command}.jsonl"
    _t0 = time.monotonic()
    _last_flags = None
    _last_write = 0.0
    _count = 0
    _last_state = None
    _wrote_landing = False
    clocks = kerbal_clocks(session)
    event(
        "start",
        f"command={command} crew={crew}",
        earth_utc=earth_display(now),
        earth_stamp=_stamp,
        **clocks,
    )
    try:
        from uplink import clear

        clear(reason=f"{command} start")
    except Exception:
        log.debug("uplink clear at start failed", exc_info=True)
    try:
        from screenshot import reset_mission_shots

        reset_mission_shots()
    except Exception:
        log.debug("mission shots reset failed", exc_info=True)
    return _path


def event(kind: str, msg: str, **extra: Any) -> None:
    global _wrote_landing
    if _path is None:
        return
    if kind == "landing":
        _wrote_landing = True
    row = {
        "t": round(time.monotonic() - _t0, 3),
        "kind": kind,
        "msg": msg,
        **{k: _jsonable(v) for k, v in extra.items()},
    }
    _write(row)


def record(state: Any, tag: str = "", *, ut: float | None = None, force: bool = False) -> None:
    """Snapshots. ``force=True`` (Telem.read) writes every pulse."""
    global _last_flags, _last_write, _last_state, _wrote_landing
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
    _last_state = row
    if row.get("landing"):
        _wrote_landing = True
    _publish_ship(state, tag)


def _ship_num(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        if isinstance(val, float) and not math.isfinite(val):
            return None
        return val
    text = str(val).strip()
    if text in {"", "?", "None", "nan", "NaN"}:
        return None
    if text in {"True", "true", "yes"}:
        return True
    if text in {"False", "false", "no"}:
        return False
    try:
        if text.startswith("'") or text.startswith('"'):
            return text.strip("'\"")
        if "." in text or "e" in text.lower() or text in {"inf", "-inf"}:
            num = float(text)
            return None if not math.isfinite(num) else num
        return int(text)
    except ValueError:
        return text.strip("'\"")


def _fmt_ship(key: str, val: Any) -> str:
    if key == "wreck":
        if val in (True, 1, "1", "True", "true", "yes"):
            return "yes"
        if val in (False, 0, "0", "False", "false", "no"):
            return "no"
        return "?"
    if val is None:
        return "?"
    if isinstance(val, float):
        if not math.isfinite(val):
            return "?"
        if key in {"heading", "pitch", "alt", "mass"}:
            return format(val, ".0f")
        if key in {"lat", "lon"}:
            return format(val, ".4f")
        if key in {"horiz", "downrange"}:
            return format(val, ".2f")
        return format(val, "g")
    if isinstance(val, (list, tuple)):
        return ",".join(str(x) for x in val) or "?"
    text = str(val).strip()
    return text if text else "?"


def envelope_from_snapshot(
    state: Any, *, as_of: str = "", flight: str = ""
) -> dict[str, Any]:
    flags = getattr(state, "flags", ()) or ()
    if isinstance(flags, (list, tuple)):
        flag_s = ",".join(str(x) for x in flags)
    else:
        flag_s = str(flags)
    sit = getattr(state, "situation", None)
    return {
        "heading": getattr(state, "heading", None),
        "wreck": getattr(state, "wreck", None),
        "ec": getattr(state, "ec", None),
        "alt": getattr(state, "alt", None),
        "as_of": as_of or None,
        "sit": sit,
        "vessel": getattr(state, "vessel", None),
        "flight": flight or None,
        "horiz": getattr(state, "horiz", None),
        "pitch": getattr(state, "pitch", None),
        "fuel": getattr(state, "fuel", None),
        "met": getattr(state, "met", None),
        "lat": getattr(state, "lat", None),
        "lon": getattr(state, "lon", None),
        "downrange": getattr(state, "downrange", None),
        "biome": getattr(state, "biome", None) or None,
        "flags": flag_s or None,
        "mass": getattr(state, "mass", None),
        "parts_n": getattr(state, "parts_n", None),
        "root": getattr(state, "root", None) or None,
    }


def parse_ship(text: str) -> dict[str, Any]:
    """Disk radio. Understands envelope kv, Snapshot() repr, status line."""
    env: dict[str, Any] = {}
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("Snapshot(") or "Snapshot(" in line:
            for key, val in _REPR_FIELD.findall(line):
                env["sit" if key == "situation" else key] = _ship_num(val)
            flags_m = _FLAGS_REPR.search(line)
            if flags_m:
                inner = flags_m.group(1).replace("'", "").replace('"', "")
                env["flags"] = ",".join(
                    p.strip() for p in inner.split(",") if p.strip()
                ) or None
            continue
        if line.startswith("status "):
            for key, val in _STATUS_FIELD.findall(line):
                dest = {"hdg": "heading", "sit": "sit"}.get(key, key)
                env[dest] = _ship_num(val)
            continue
        m = _KV_LINE.match(line)
        if not m:
            continue
        key = m.group(1).strip().lower()
        if key == "situation":
            key = "sit"
        env[key] = _ship_num(m.group(2).strip())
    return env


def format_ship(env: dict[str, Any]) -> str:
    """Token-cheap live eyes. Never a Snapshot() blob, never jsonl."""
    lines = [f"{key}: {_fmt_ship(key, env.get(key))}" for key in _SHIP_PRINT]
    for key in _SHIP_EXTRA:
        val = env.get(key)
        if val in (None, "", [], ()):
            continue
        if isinstance(val, float) and not math.isfinite(val):
            continue
        lines.append(f"{key}: {_fmt_ship(key, val)}")
    return "\n".join(lines) + "\n"


def read_ship(path: str | Path | None = None) -> dict[str, Any]:
    src = Path(path) if path is not None else SHIP
    if not src.is_file():
        return {}
    return parse_ship(src.read_text(encoding="utf-8"))


def parse_as_of(text: str) -> datetime | None:
    raw = (text or "").strip()
    if not raw:
        return None
    for fmt in _AS_OF_FMT:
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def ship_stale(
    env: dict[str, Any],
    *,
    lock_path: Path | None = None,
) -> bool:
    """Lock-live radio from a previous hop: as_of older than flight.lock."""
    src = LOCK if lock_path is None else lock_path
    if not src.is_file():
        return False
    as_dt = parse_as_of(str(env.get("as_of") or ""))
    if as_dt is None:
        return False
    lock_dt = datetime.fromtimestamp(src.stat().st_mtime, timezone.utc)
    return as_dt.timestamp() + 60.0 < lock_dt.timestamp()


def cmd_ship(path: str | Path | None = None) -> int:
    src = Path(path) if path is not None else SHIP
    if not src.is_file():
        print("ship: none")
        return 0
    env = parse_ship(src.read_text(encoding="utf-8"))
    if src.resolve() == SHIP.resolve() and ship_stale(env):
        env["stale"] = "yes"
    print(format_ship(env), end="")
    return 0


def publish_hangar_radio(*, vessel: str = "", why: str = "preflight") -> None:
    """KSC/preflight sit so Hank does not read the previous hop as live."""
    if not live_records():
        return
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    env: dict[str, Any] = {
        "heading": None,
        "wreck": False,
        "ec": None,
        "alt": None,
        "as_of": utc,
        "sit": "ksc",
        "vessel": vessel or None,
        "flight": _flight or None,
        "flags": why,
    }
    try:
        SHIP.parent.mkdir(parents=True, exist_ok=True)
        SHIP.write_text(format_ship(env), encoding="utf-8")
    except Exception:
        log.debug("hangar ship.md publish failed", exc_info=True)


def _publish_ship(state: Any, tag: str) -> None:
    """Heartbeat envelope + as_of so a crash is visibly stale (L-032 / L-037)."""
    if not live_records():
        return
    try:
        utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        env = envelope_from_snapshot(state, as_of=utc, flight=_flight)
        SHIP.parent.mkdir(parents=True, exist_ok=True)
        SHIP.write_text(format_ship(env), encoding="utf-8")
    except Exception:
        log.debug("ship.md publish failed", exc_info=True)


def _emit_landing_if_missing() -> None:
    """T-110: hops that stay flying still get a landing kind at close."""
    if _wrote_landing or not _last_state:
        return
    try:
        from telem import classify_impact, format_landing, impact_speed
    except Exception:
        return
    vz = _last_state.get("v_vert")
    impact = impact_speed(
        v_vert=float(vz) if isinstance(vz, (int, float)) else float("nan"),
        speed=_last_state.get("speed") if isinstance(_last_state.get("speed"), (int, float)) else float("nan"),
        horiz=_last_state.get("horiz") if isinstance(_last_state.get("horiz"), (int, float)) else float("nan"),
    )
    landing = classify_impact(impact)
    if not landing:
        return
    sit = str(_last_state.get("situation") or "")
    event(
        "landing",
        format_landing(
            {
                "landing": landing,
                "impact_ms": impact,
                "heading": _last_state.get("heading"),
                "horiz": _last_state.get("horiz"),
                "pitch": _last_state.get("pitch"),
                "sit": sit,
            }
        ),
        landing=landing,
        v_vert=_last_state.get("v_vert"),
        speed=_last_state.get("speed"),
        horiz=_last_state.get("horiz"),
        heading=_last_state.get("heading"),
        pitch=_last_state.get("pitch"),
        sit=sit,
        met=_last_state.get("met"),
        biome=_last_state.get("biome"),
        lat=_last_state.get("lat"),
        lon=_last_state.get("lon"),
        downrange=_last_state.get("downrange"),
        wreck=_last_state.get("wreck"),
        synthesized=True,
    )


def close() -> Path | None:
    global _path, _session
    done = None
    if _path is not None:
        _emit_landing_if_missing()
        event("end", f"samples={_count}")
        done = _path
        _index_run(done)
        _path = None
    _session = None
    release_lock()
    return done


def _index_run(path: Path) -> None:
    """Append one index row. No-op under unittest / missing tape."""
    if not live_records() or path is None or not path.is_file():
        return
    try:
        from telem import landing_from_jsonl

        landing = landing_from_jsonl(path)
    except Exception:
        landing = {"path": str(path), "run": path.name}
    row = {
        "stamp": _stamp,
        "command": _command,
        "flight": _flight,
        "path": str(path),
        "samples": _count,
        "landing": landing.get("landing"),
        "impact_ms": landing.get("impact_ms"),
        "heading": landing.get("heading"),
        "sit": landing.get("sit"),
    }
    try:
        INDEX.parent.mkdir(parents=True, exist_ok=True)
        with INDEX.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, default=str) + "\n")
    except Exception:
        log.debug("flights index write failed", exc_info=True)


def latest_run() -> Path | None:
    """Newest jsonl on the flights index, else newest seated logs jsonl."""
    if INDEX.is_file():
        last = None
        for line in INDEX.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            p = Path(str(row.get("path") or ""))
            if p.is_file():
                last = p
        if last is not None:
            return last
    if _path is not None and _path.is_file():
        return _path
    try:
        from missions import seated_id, seated_logs_dir

        dest = seated_logs_dir(seated_id())
    except Exception:
        dest = FLIGHTS
    if not dest.is_dir():
        return None
    files = sorted(dest.glob("*.jsonl"))
    return files[-1] if files else None


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
