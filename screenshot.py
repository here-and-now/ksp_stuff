"""Capture the KSP window. No kRPC. Does not steal focus on the happy path.

``grim -g`` of the Hyprland layout box is not a window shot. When KSP is on
another workspace, covered, or resized, ``at``/``size`` still exist and
``visible`` is false — grim copies whatever is on the output (TUI, Firefox).
Use ``grim -T <stableId>`` (foreign toplevel buffer) first.
"""

from __future__ import annotations

import json
import logging
import os
import re
import struct
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from hangar import discover_ksp

log = logging.getLogger("kspstuff")

ROOT = Path(__file__).resolve().parent
SHOT_DIR = ROOT / "screenshots"
PRESERVE = frozenset(
    {"first-mystery-goo.png", "first-hop.png", "rocket-flea.png"}
)
RUNS_DIR = SHOT_DIR / "runs"
MISSION_INTERVAL_S = 60.0
_SLUG = re.compile(r"[^a-z0-9-]+")
KSP_CLASSES = frozenset({"KSP.x86_64", "KSP.x86", "KSP"})
MIN_PX = 64

Run = Callable[..., subprocess.CompletedProcess]


class ScreenshotError(RuntimeError):
    """KSP window missing, compositor capture failed, or dest is preserved."""


@dataclass(frozen=True, slots=True)
class KspWindow:
    class_name: str
    title: str
    stable_id: str
    address: str
    pid: int
    at: tuple[int, int]
    size: tuple[int, int]
    visible: bool
    mapped: bool
    xwayland: bool
    workspace: str
    monitor: int = -1
    fullscreen: int = 0
    fullscreen_client: int = 0


@dataclass(frozen=True, slots=True)
class HyprMonitor:
    id: int
    name: str
    width: int
    height: int
    active_workspace: str
    focused: bool


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ScreenshotError(f"not a PNG: {path}")
    w, h = struct.unpack(">II", data[16:24])
    return int(w), int(h)


def _run(
    argv: list[str],
    *,
    env: dict[str, str] | None = None,
    timeout: float = 20.0,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        env=env,
        timeout=timeout,
        capture_output=True,
        text=True,
        check=False,
    )


def _ok_png(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 128:
        return False
    try:
        w, h = png_size(path)
    except ScreenshotError:
        return False
    return w >= MIN_PX and h >= MIN_PX


def _pid_in_root(pid: int, root: Path) -> bool:
    root_s = str(root.resolve())
    for name in ("cwd", "exe"):
        try:
            p = Path(f"/proc/{pid}/{name}").resolve()
        except OSError:
            continue
        if str(p) == root_s or str(p).startswith(root_s + os.sep):
            return True
    return False


def parse_hypr_clients(raw: str) -> list[KspWindow]:
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ScreenshotError("hyprctl clients: not a list")
    out: list[KspWindow] = []
    for c in data:
        if not isinstance(c, dict):
            continue
        cls = str(c.get("class") or "")
        title = str(c.get("title") or "")
        if cls not in KSP_CLASSES and "Kerbal Space Program" not in title:
            continue
        at = c.get("at") or [0, 0]
        size = c.get("size") or [0, 0]
        ws = c.get("workspace") or {}
        ws_name = str(ws.get("name") or ws.get("id") or "")
        out.append(
            KspWindow(
                class_name=cls,
                title=title,
                stable_id=str(c.get("stableId") or ""),
                address=str(c.get("address") or ""),
                pid=int(c.get("pid") or 0),
                at=(int(at[0]), int(at[1])),
                size=(int(size[0]), int(size[1])),
                visible=bool(c.get("visible")),
                mapped=bool(c.get("mapped", True)),
                xwayland=bool(c.get("xwayland")),
                workspace=ws_name,
                monitor=int(c["monitor"]) if c.get("monitor") is not None else -1,
                fullscreen=int(c.get("fullscreen") or 0),
                fullscreen_client=int(c.get("fullscreenClient") or 0),
            )
        )
    return out


def parse_hypr_monitors(raw: str) -> list[HyprMonitor]:
    data = json.loads(raw)
    if not isinstance(data, list):
        return []
    out: list[HyprMonitor] = []
    for m in data:
        if not isinstance(m, dict):
            continue
        ws = m.get("activeWorkspace") or {}
        out.append(
            HyprMonitor(
                id=int(m.get("id") or 0),
                name=str(m.get("name") or ""),
                width=int(m.get("width") or 0),
                height=int(m.get("height") or 0),
                active_workspace=str(ws.get("name") or ws.get("id") or ""),
                focused=bool(m.get("focused")),
            )
        )
    return out


def already_monitor_size(window: KspWindow, mon: HyprMonitor | None) -> bool:
    """True if grim -T already has monitor pixels (no compositor FS needed)."""
    if window.fullscreen or window.fullscreen_client:
        return True
    if mon is None:
        return window.size[0] >= 1600 and window.size[1] >= 900
    return window.size[0] >= mon.width - 40 and window.size[1] >= mon.height - 80


def choose_window(windows: list[KspWindow], rss: Path | None = None) -> KspWindow:
    if not windows:
        raise ScreenshotError("no KSP window (hyprctl class KSP.x86_64 / xprop WM_CLASS)")
    pool = windows
    if rss is not None and len(windows) > 1:
        hits = [w for w in windows if w.pid and _pid_in_root(w.pid, rss)]
        if hits:
            pool = hits
    pool = sorted(
        pool,
        key=lambda w: (not w.mapped, not w.visible, -(w.size[0] * w.size[1])),
    )
    return pool[0]


def _try_run(run: Run, argv: list[str], **kw) -> subprocess.CompletedProcess[str] | None:
    try:
        return run(argv, **kw)
    except FileNotFoundError:
        return None


def _hypr_windows(run: Run) -> list[KspWindow]:
    r = _try_run(run, ["hyprctl", "-j", "clients"])
    if r is None or r.returncode != 0:
        return []
    try:
        return parse_hypr_clients(r.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise ScreenshotError(f"hyprctl clients: bad JSON ({exc})") from exc


def _hypr_monitors(run: Run) -> list[HyprMonitor]:
    r = _try_run(run, ["hyprctl", "-j", "monitors"])
    if r is None or r.returncode != 0:
        return []
    try:
        return parse_hypr_monitors(r.stdout or "[]")
    except json.JSONDecodeError:
        return []


def _active_address(run: Run) -> str:
    r = _try_run(run, ["hyprctl", "-j", "activewindow"])
    if r is None or r.returncode != 0 or not r.stdout:
        return ""
    try:
        return str(json.loads(r.stdout).get("address") or "")
    except json.JSONDecodeError:
        return ""


def _focus_workspace(run: Run, ws: str) -> bool:
    if not ws:
        return False
    arg = ws if str(ws).isdigit() else json.dumps(str(ws))
    lua = f'hl.dispatch(hl.dsp.focus({{ workspace = {arg} }})); return "ok"'
    r = _try_run(run, ["hyprctl", "repl", lua])
    return r is not None and r.returncode == 0 and "ok" in (r.stdout or "")


def _focus_addr(run: Run, addr: str) -> bool:
    if not addr:
        return False
    lua = (
        f'local w=hl.get_window("address:{addr}"); '
        "if w==nil then return \"missing\" end; "
        "hl.dispatch(hl.dsp.focus({ window = w })); return \"ok\""
    )
    r = _try_run(run, ["hyprctl", "repl", lua])
    return r is not None and r.returncode == 0 and "ok" in (r.stdout or "")


def _x11_scan(run: Run) -> list[KspWindow]:
    found: list[KspWindow] = []
    for display in _displays():
        env = {**os.environ, "DISPLAY": display}
        root = _try_run(run, ["xprop", "-root", "_NET_CLIENT_LIST"], env=env)
        if root is None or root.returncode != 0:
            continue
        for wid in re.findall(r"0x[0-9a-fA-F]+", root.stdout or ""):
            info = _try_run(
                run,
                ["xprop", "-id", wid, "WM_CLASS", "WM_NAME", "_NET_WM_PID"],
                env=env,
            )
            text = (info.stdout if info is not None else "") or ""
            if "KSP.x86_64" not in text and "Kerbal Space Program" not in text:
                continue
            pid_m = re.search(r"_NET_WM_PID\(CARDINAL\)\s*=\s*(\d+)", text)
            found.append(
                KspWindow(
                    class_name="KSP.x86_64",
                    title="Kerbal Space Program",
                    stable_id="",
                    address=wid,
                    pid=int(pid_m.group(1)) if pid_m else 0,
                    at=(0, 0),
                    size=(0, 0),
                    visible=False,
                    mapped=True,
                    xwayland=True,
                    workspace="",
                )
            )
    return found


def _grim_toplevel(run: Run, window: KspWindow, dest: Path) -> bool:
    if not window.stable_id:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = _try_run(run, ["grim", "-T", window.stable_id, str(dest)])
    if r is None or r.returncode != 0 or not _ok_png(dest):
        if dest.exists() and not dest.name in PRESERVE:
            dest.unlink()
        return False
    return True


def _displays() -> list[str]:
    seen: list[str] = []
    for d in (os.environ.get("DISPLAY"), ":1", ":0"):
        if d and d not in seen:
            seen.append(d)
    return seen


def _x11_window_id(run: Run, display: str, pid: int | None) -> str | None:
    env = {**os.environ, "DISPLAY": display}
    root = _try_run(run, ["xprop", "-root", "_NET_CLIENT_LIST"], env=env)
    if root is None or root.returncode != 0:
        return None
    ids = re.findall(r"0x[0-9a-fA-F]+", root.stdout or "")
    class_hit: str | None = None
    for wid in ids:
        info = _try_run(
            run,
            ["xprop", "-id", wid, "WM_CLASS", "WM_NAME", "_NET_WM_PID"],
            env=env,
        )
        text = (info.stdout if info is not None else "") or ""
        if "KSP.x86_64" not in text and "Kerbal Space Program" not in text:
            continue
        if pid and re.search(rf"_NET_WM_PID\(CARDINAL\)\s*=\s*{pid}\b", text):
            return wid
        if class_hit is None:
            class_hit = wid
    return class_hit


def _x11_import(run: Run, window: KspWindow, dest: Path) -> bool:
    if not window.xwayland:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    for display in _displays():
        wid = window.address if window.address.startswith("0x") and not window.stable_id else None
        wid = wid or _x11_window_id(run, display, window.pid or None)
        if not wid:
            continue
        env = {**os.environ, "DISPLAY": display}
        r = _try_run(run, ["magick", "import", "-window", wid, str(dest)], env=env)
        if r is not None and r.returncode == 0 and _ok_png(dest):
            return True
        if dest.exists() and dest.name not in PRESERVE:
            dest.unlink()
    return False


def _hypr_focus(run: Run, selector: str) -> bool:
    lua = (
        f'local w=hl.get_window("{selector}"); '
        "if w==nil then return \"missing\" end; "
        "hl.dsp.focus(w); return \"ok\""
    )
    r = _try_run(run, ["hyprctl", "repl", lua])
    return r is not None and r.returncode == 0 and "ok" in (r.stdout or "")


def _grim_geometry(run: Run, window: KspWindow, dest: Path) -> bool:
    x, y = window.at
    w, h = window.size
    if w < MIN_PX or h < MIN_PX:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = _try_run(run, ["grim", "-g", f"{x},{y} {w}x{h}", str(dest)])
    if r is None or r.returncode != 0 or not _ok_png(dest):
        if dest.exists() and dest.name not in PRESERVE:
            dest.unlink()
        return False
    return True


def _focus_then_grim(run: Run, window: KspWindow, dest: Path) -> bool:
    """Last resort. Only copies output pixels if the window is actually shown."""
    prev = ""
    active = _try_run(run, ["hyprctl", "-j", "activewindow"])
    if active is not None and active.returncode == 0 and active.stdout:
        try:
            prev = str(json.loads(active.stdout).get("address") or "")
        except json.JSONDecodeError:
            prev = ""
    selector = (
        f"class:{window.class_name}" if window.class_name else f"address:{window.address}"
    )
    _hypr_focus(run, selector)
    shown: KspWindow | None = None
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        try:
            cur = choose_window(_hypr_windows(run), None)
        except ScreenshotError:
            time.sleep(0.05)
            continue
        if cur.visible and cur.mapped:
            shown = cur
            break
        time.sleep(0.05)
    ok = False
    if shown is not None:
        ok = _grim_geometry(run, shown, dest)
    if prev and prev != window.address:
        _hypr_focus(run, f"address:{prev}")
    return ok


def _resize_relative(run: Run, window: KspWindow, dx: int, dy: int) -> bool:
    """Dwindle split restore. Not used on Firefox."""
    if dx == 0 and dy == 0:
        return True
    cls = window.class_name or "KSP.x86_64"
    lua = (
        f'local w=hl.get_window("class:{cls}"); '
        'if w==nil then return "missing" end; '
        "hl.dispatch(hl.dsp.window.resize({"
        f"x={int(dx)}, y={int(dy)}, relative=true, window=w"
        "})); return \"ok\""
    )
    r = _try_run(run, ["hyprctl", "repl", lua])
    return r is not None and r.returncode == 0 and "ok" in (r.stdout or "")


def _set_fullscreen(
    run: Run,
    window: KspWindow,
    *,
    internal: int,
    client: int,
) -> bool:
    """Hyprland 0.56: compositor FS without Unity exclusive (client=0)."""
    cls = window.class_name or "KSP.x86_64"
    lua = (
        f'local w=hl.get_window("class:{cls}"); '
        'if w==nil then return "missing" end; '
        "hl.dispatch(hl.dsp.window.fullscreen_state({"
        f"internal={int(internal)}, client={int(client)}, window=w"
        "})); return \"ok\""
    )
    r = _try_run(run, ["hyprctl", "repl", lua])
    return r is not None and r.returncode == 0 and "ok" in (r.stdout or "")


def _wait_window(
    run: Run,
    pred,
    *,
    timeout: float,
    rss: Path | None,
) -> KspWindow | None:
    deadline = time.monotonic() + timeout
    last: KspWindow | None = None
    while True:
        try:
            last = choose_window(_hypr_windows(run), rss)
            if pred(last):
                return last
        except ScreenshotError:
            pass
        if time.monotonic() >= deadline:
            return last
        time.sleep(0.05)


def _take_buffer(run: Run, window: KspWindow, dest: Path) -> str | None:
    if _grim_toplevel(run, window, dest):
        return "grim-toplevel"
    if _x11_import(run, window, dest):
        return "x11-import"
    return None


def _capture_full(
    run: Run,
    window: KspWindow,
    dest: Path,
    *,
    rss: Path | None,
    settle: float,
    grow_timeout: float = 3.0,
    restore_timeout: float = 2.0,
    mon: HyprMonitor | None = None,
) -> tuple[str, KspWindow]:
    """Grow a small tile to the monitor, shoot, restore orig FS/size/focus.

    Skip this path when ``already_monitor_size`` — grim -T does not need
    the window focused, visible, or on the active workspace.
    """
    orig_w, orig_h = window.size
    orig_at = window.at
    orig_fs = window.fullscreen
    orig_fsc = window.fullscreen_client
    orig_ws = mon.active_workspace if mon is not None else ""
    prev_addr = _active_address(run)
    shot = window
    try:
        if not _set_fullscreen(run, window, internal=2, client=0):
            raise ScreenshotError("hypr fullscreen_state on failed")
        grown = _wait_window(
            run,
            lambda w: w.size[0] >= orig_w + 200 or w.size[0] >= 1600,
            timeout=grow_timeout,
            rss=rss,
        )
        if grown is None:
            raise ScreenshotError("KSP did not grow after compositor fullscreen")
        if settle > 0:
            time.sleep(settle)
        try:
            shot = choose_window(_hypr_windows(run), rss)
        except ScreenshotError:
            shot = grown
        how = _take_buffer(run, shot, dest)
        if how:
            return f"{how}-full", shot
        raise ScreenshotError("fullscreen capture failed after compositor FS")
    finally:
        _set_fullscreen(run, window, internal=orig_fs, client=orig_fsc)
        restored = _wait_window(
            run,
            lambda w: abs(w.size[0] - orig_w) <= 40 and abs(w.size[1] - orig_h) <= 40,
            timeout=restore_timeout,
            rss=rss,
        )
        if restored is not None and (
            abs(restored.size[0] - orig_w) > 40 or abs(restored.size[1] - orig_h) > 40
        ):
            _resize_relative(
                run,
                window,
                orig_w - restored.size[0],
                orig_h - restored.size[1],
            )
            restored = _wait_window(
                run,
                lambda w: abs(w.size[0] - orig_w) <= 40
                and abs(w.size[1] - orig_h) <= 40,
                timeout=restore_timeout,
                rss=rss,
            )
        if restored is None or abs(restored.size[0] - orig_w) > 40:
            print(
                f"screenshot restore warn: wanted {orig_w}x{orig_h} "
                f"at {orig_at}, got "
                f"{getattr(restored, 'size', None)} at "
                f"{getattr(restored, 'at', None)}",
                file=sys.stderr,
            )
        if orig_ws:
            now = None
            for m in _hypr_monitors(run):
                if mon is not None and m.id == mon.id:
                    now = m
                    break
            if now is not None and now.active_workspace != orig_ws:
                _focus_workspace(run, orig_ws)
        if prev_addr:
            _focus_addr(run, prev_addr)


def resolve_dest(
    out: Path | None = None,
    *,
    name: str | None = None,
    force: bool = False,
    now: datetime | None = None,
) -> Path:
    auto = out is None and not name
    if out is not None:
        dest = out if out.is_absolute() else ROOT / out
    elif name:
        dest = SHOT_DIR / f"{name.removesuffix('.png')}.png"
    else:
        stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
        dest = SHOT_DIR / f"ksp-{stamp}.png"
    dest = dest.resolve()
    if dest.name in PRESERVE and dest.exists() and not force:
        raise ScreenshotError(
            f"refusing to overwrite {dest.as_posix()} "
            "(preserved pad shot; pass --force)"
        )
    if dest.exists() and not force:
        if auto:
            dest = dest.with_name(f"{dest.stem}-{os.getpid()}.png")
        else:
            raise ScreenshotError(
                f"refusing to overwrite {dest.as_posix()} (pass --force)"
            )
    return dest


def capture(
    out: Path | None = None,
    *,
    name: str | None = None,
    force: bool = False,
    run: Run | None = None,
    now: datetime | None = None,
    rss: Path | None | bool = True,
    full: bool = False,
    settle: float = 0.8,
    grow_timeout: float = 3.0,
    restore_timeout: float = 2.0,
) -> tuple[Path, str, KspWindow]:
    run = run or _run
    dest = resolve_dest(out, name=name, force=force, now=now)
    windows = _hypr_windows(run)
    if not windows:
        windows = _x11_scan(run)
    root = discover_ksp() if rss is True else rss or None
    rss_root = root if isinstance(root, Path) else None
    window = choose_window(windows, rss_root)
    if full:
        mons = _hypr_monitors(run)
        mon = next((m for m in mons if m.id == window.monitor), None)
        if already_monitor_size(window, mon):
            how = _take_buffer(run, window, dest)
            if how:
                return dest, how, window
            raise ScreenshotError(
                "KSP already monitor-sized but grim -T / x11 import failed"
            )
        method, window = _capture_full(
            run,
            window,
            dest,
            rss=rss_root,
            settle=settle,
            grow_timeout=grow_timeout,
            restore_timeout=restore_timeout,
            mon=mon,
        )
        return dest, method, window
    if _grim_toplevel(run, window, dest):
        return dest, "grim-toplevel", window
    if _x11_import(run, window, dest):
        return dest, "x11-import", window
    if window.visible and _grim_geometry(run, window, dest):
        return dest, "grim-geometry", window
    if _focus_then_grim(run, window, dest):
        return dest, "grim-focus", window
    raise ScreenshotError(
        "KSP window found but capture failed "
        f"(visible={window.visible} xwayland={window.xwayland} "
        f"stableId={window.stable_id or '-'}). "
        "Need grim -T (Hyprland stableId) or magick import on the X11 id."
    )


def _slug(event: str) -> str:
    text = _SLUG.sub("-", str(event).lower()).strip("-")
    return (text or "tick")[:40]


def run_shot_dir(*, stamp: str | None = None, command: str | None = None) -> Path:
    """``screenshots/runs/<earth-stamp>-<command>/``. Not press heroes."""
    st = stamp
    cmd = command
    if not st or not cmd:
        try:
            from flightlog import command as fl_command
            from flightlog import stamp as fl_stamp

            st = st or fl_stamp()
            cmd = cmd or fl_command()
        except Exception:
            pass
    st = st or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    cmd = _slug(cmd or "run")
    return RUNS_DIR / f"{st}-{cmd}"


def mission_dest(
    event: str,
    *,
    met: float | None = None,
    stamp: str | None = None,
    command: str | None = None,
) -> Path:
    folder = run_shot_dir(stamp=stamp, command=command)
    met_s = 0
    if met is not None:
        try:
            m = float(met)
        except (TypeError, ValueError):
            m = float("nan")
        if m == m and m >= 0:
            met_s = int(m)
    return folder / f"T+{met_s:06d}-{_slug(event)}.png"


class ShotCadence:
    """Quiet stills: ~1 min, plus sit/stage/light/wreck. Never reads the PNG."""

    def __init__(
        self,
        *,
        interval_s: float = MISSION_INTERVAL_S,
        grab: Callable[[Path], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
        min_gap_s: float = 1.5,
    ) -> None:
        self.interval_s = float(interval_s)
        self.grab = grab
        self.clock = clock
        self.min_gap_s = float(min_gap_s)
        self.t0 = clock()
        self._last = 0.0
        self._sit: str | None = None
        self._stage: int | None = None
        self._thrust_on: bool | None = None
        self._ec0 = False
        self._started = False

    def observe(self, snap: object, *, event: str | None = None) -> Path | None:
        reasons: list[str] = []
        if event:
            reasons.append(_slug(event))
        sit = str(getattr(snap, "situation", "") or "")
        if self._sit is not None and sit and sit != self._sit:
            reasons.append(f"sit-{_slug(sit)}")
        if sit:
            self._sit = sit
        stage = getattr(snap, "stage", None)
        try:
            stage_i = int(stage) if stage is not None else None
        except (TypeError, ValueError):
            stage_i = None
        if (
            stage_i is not None
            and self._stage is not None
            and stage_i != self._stage
        ):
            reasons.append("stage")
        if stage_i is not None:
            self._stage = stage_i
        thrust = getattr(snap, "thrust", 0.0)
        try:
            thrust_f = float(thrust)
        except (TypeError, ValueError):
            thrust_f = 0.0
        on = thrust_f == thrust_f and thrust_f > 10.0
        if self._thrust_on is False and on:
            reasons.append("light")
        if thrust_f == thrust_f:
            self._thrust_on = on
        if bool(getattr(snap, "wreck", False)):
            reasons.append("wreck")
        ec = getattr(snap, "ec", None)
        try:
            ec_f = float(ec) if ec is not None else None
        except (TypeError, ValueError):
            ec_f = None
        if ec_f is not None and ec_f <= 0 and not self._ec0:
            self._ec0 = True
            reasons.append("ec0")
        now = self.clock()
        if not self._started:
            self._started = True
            reasons.append("start")
        elif now - self._last >= self.interval_s:
            reasons.append("tick")
        if not reasons:
            return None
        if (
            self._last
            and now - self._last < self.min_gap_s
            and event is None
            and "tick" in reasons
            and len(reasons) == 1
        ):
            return None
        return self._grab(reasons[0], snap)

    def event(self, name: str, snap: object | None = None) -> Path | None:
        return self.observe(snap or object(), event=name)

    def _grab(self, slug: str, snap: object) -> Path | None:
        from flightlog import live_records

        if self.grab is None and not live_records():
            return None
        met = getattr(snap, "met", None)
        dest = mission_dest(slug, met=met if isinstance(met, (int, float)) else None)
        if dest.name in PRESERVE:
            return None
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest = dest.with_name(f"{dest.stem}-{os.getpid()}.png")
        try:
            if self.grab is not None:
                self.grab(dest)
            else:
                capture(out=dest, force=False, full=False)
        except Exception:
            log.debug("mission shot failed slug=%s", slug, exc_info=True)
            return None
        self._last = self.clock()
        log.info("shot %s", dest)
        return dest


_cadence: ShotCadence | None = None


def reset_mission_shots() -> ShotCadence:
    global _cadence
    _cadence = ShotCadence()
    return _cadence


def mission_shots() -> ShotCadence:
    global _cadence
    if _cadence is None:
        _cadence = ShotCadence()
    return _cadence


def mission_observe(snap: object, *, event: str | None = None) -> Path | None:
    """Helm cadence. Capture only — do not read the PNG."""
    try:
        return mission_shots().observe(snap, event=event)
    except Exception:
        log.debug("mission_observe failed", exc_info=True)
        return None


def mission_event(name: str, snap: object | None = None) -> Path | None:
    try:
        return mission_shots().event(name, snap)
    except Exception:
        log.debug("mission_event failed", exc_info=True)
        return None


def cmd_screenshot(
    out: Path | None = None,
    *,
    force: bool = False,
    name: str | None = None,
    full: bool = False,
) -> int:
    try:
        path, method, window = capture(out=out, force=force, name=name, full=full)
    except ScreenshotError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    w, h = png_size(path)
    print(
        f"screenshot method={method} path={path.as_posix()} "
        f"png={w}x{h} window={window.size[0]}x{window.size[1]} "
        f"visible={str(window.visible).lower()} ws={window.workspace}",
        flush=True,
    )
    return 0
