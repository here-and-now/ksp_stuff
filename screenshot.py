"""Capture the KSP window. No kRPC. Does not steal focus on the happy path.

``grim -g`` of the Hyprland layout box is not a window shot. When KSP is on
another workspace, covered, or resized, ``at``/``size`` still exist and
``visible`` is false — grim copies whatever is on the output (TUI, Firefox).
Use ``grim -T <stableId>`` (foreign toplevel buffer) first.
"""

from __future__ import annotations

import json
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

ROOT = Path(__file__).resolve().parent
SHOT_DIR = ROOT / "screenshots"
PRESERVE = frozenset({"first-mystery-goo.png"})
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
            )
        )
    return out


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


def _capture_full(
    run: Run,
    window: KspWindow,
    dest: Path,
    *,
    rss: Path | None,
    settle: float,
    grow_timeout: float = 3.0,
    restore_timeout: float = 2.0,
) -> tuple[str, KspWindow]:
    """Fill the monitor for the shot, then restore the exact tile.

    ``internal=2, client=0``: compositor fullscreen. XWayland gets the
    monitor size (Unity re-renders) without exclusive client FS. Tile
    geometry is restored by clearing fullscreen — no ``window.resize``.
    Does not dispatch FS on Firefox (pip_tile media band).
    """
    orig_w, orig_h = window.size
    orig_at = window.at
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
        if _grim_toplevel(run, shot, dest):
            return "grim-toplevel-full", shot
        if _x11_import(run, shot, dest):
            return "x11-import-full", shot
        raise ScreenshotError("fullscreen capture failed after compositor FS")
    finally:
        _set_fullscreen(run, window, internal=0, client=0)
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
        method, window = _capture_full(
            run,
            window,
            dest,
            rss=rss_root,
            settle=settle,
            grow_timeout=grow_timeout,
            restore_timeout=restore_timeout,
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
