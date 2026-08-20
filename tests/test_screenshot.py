"""Window capture: grim -T even when KSP is not visible. No compositor."""

from __future__ import annotations

import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
from unittest import TestCase

from screenshot import (
    PRESERVE,
    ScreenshotError,
    capture,
    choose_window,
    parse_hypr_clients,
    png_size,
    resolve_dest,
)


def _png(w: int, h: int, rgb: tuple[int, int, int] = (20, 40, 60)) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def _client(**kw) -> dict:
    base = {
        "class": "KSP.x86_64",
        "title": "Kerbal Space Program",
        "stableId": "18000063",
        "address": "0xabc",
        "pid": 7523,
        "at": [2045, 850],
        "size": [945, 1030],
        "visible": False,
        "mapped": True,
        "xwayland": True,
        "workspace": {"id": 1, "name": "1"},
    }
    base.update(kw)
    return base


def _cp(stdout="", returncode=0, stderr="") -> CompletedProcess:
    return CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class TestParse(TestCase):
    def test_ignores_other_windows(self):
        raw = json.dumps(
            [
                {"class": "Grok", "title": "Grok", "at": [0, 0], "size": [100, 100]},
                _client(),
            ]
        )
        wins = parse_hypr_clients(raw)
        self.assertEqual(len(wins), 1)
        self.assertEqual(wins[0].stable_id, "18000063")
        self.assertFalse(wins[0].visible)

    def test_png_size(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "a.png"
            p.write_bytes(_png(80, 64))
            self.assertEqual(png_size(p), (80, 64))


class TestResolve(TestCase):
    def test_default_is_not_goo(self):
        dest = resolve_dest(now=datetime(2026, 8, 20, 15, 36, tzinfo=timezone.utc))
        self.assertEqual(dest.name, "ksp-20260820T153600Z.png")
        self.assertNotIn(dest.name, PRESERVE)

    def test_preserves_first_mystery_goo(self):
        goo = Path(__file__).resolve().parents[1] / "screenshots" / "first-mystery-goo.png"
        self.assertTrue(goo.is_file())
        with self.assertRaises(ScreenshotError) as ctx:
            resolve_dest(name="first-mystery-goo")
        self.assertIn("preserved", str(ctx.exception))


class TestCapture(TestCase):
    def test_grim_toplevel_when_not_visible(self):
        written: list[str] = []

        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                return _cp(json.dumps([_client(visible=False)]))
            if argv[0] == "grim" and "-T" in argv:
                self.assertEqual(argv[2], "18000063")
                Path(argv[-1]).write_bytes(_png(945, 1030))
                written.append("toplevel")
                return _cp()
            if argv[0] == "grim" and "-g" in argv:
                self.fail("grim -g must not run while grim -T works")
            if argv[0] == "magick":
                self.fail("x11 import must not run while grim -T works")
            if argv[0] == "hyprctl" and argv[1] == "repl":
                self.fail("must not focus the window")
            return _cp(returncode=1, stderr="unexpected " + " ".join(argv))

        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "shot.png"
            path, method, win = capture(out=dest, run=run, rss=None, force=True)
            self.assertEqual(method, "grim-toplevel")
            self.assertEqual(written, ["toplevel"])
            self.assertEqual(path, dest.resolve())
            self.assertFalse(win.visible)
            self.assertEqual(png_size(path), (945, 1030))

    def test_x11_fallback_when_grim_t_fails(self):
        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                return _cp(json.dumps([_client(visible=False, stableId="nope")]))
            if argv[0] == "grim" and "-T" in argv:
                return _cp(returncode=1, stderr="cannot find toplevel")
            if argv[:2] == ["xprop", "-root"]:
                return _cp("_NET_CLIENT_LIST(WINDOW): window id # 0x100001a\n")
            if argv[:2] == ["xprop", "-id"]:
                return _cp(
                    'WM_CLASS(STRING) = "KSP.x86_64", "KSP.x86_64"\n'
                    'WM_NAME(STRING) = "Kerbal Space Program"\n'
                    "_NET_WM_PID(CARDINAL) = 7523\n"
                )
            if argv[0] == "magick":
                Path(argv[-1]).write_bytes(_png(945, 1030))
                return _cp()
            if argv[0] == "grim" and "-g" in argv:
                self.fail("grim -g skipped when x11 import works")
            return _cp(returncode=1, stderr="unexpected " + " ".join(argv))

        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "shot.png"
            path, method, _win = capture(out=dest, run=run, rss=None, force=True)
            self.assertEqual(method, "x11-import")
            self.assertEqual(png_size(path), (945, 1030))

    def test_no_window(self):
        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                return _cp("[]")
            if argv[:2] == ["xprop", "-root"]:
                return _cp("_NET_CLIENT_LIST(WINDOW): window id # 0x1\n")
            if argv[:2] == ["xprop", "-id"]:
                return _cp('WM_CLASS(STRING) = "Grok", "Grok"\n')
            return _cp(returncode=1)

        with TemporaryDirectory() as tmp:
            with self.assertRaises(ScreenshotError):
                capture(out=Path(tmp) / "x.png", run=run, rss=None, force=True)

    def test_full_then_restore_tile(self):
        fs_on = []
        fs_off = []

        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                if fs_on and not fs_off:
                    return _cp(json.dumps([_client(visible=True, size=[1920, 1080], at=[1080, 840])]))
                return _cp(json.dumps([_client(visible=True, size=[945, 1030], at=[2045, 850])]))
            if argv[:2] == ["hyprctl", "repl"]:
                lua = argv[2]
                self.assertIn("fullscreen_state", lua)
                self.assertNotIn("firefox", lua.lower())
                if "internal=2" in lua:
                    fs_on.append(lua)
                    self.assertIn("client=0", lua)
                elif "internal=0" in lua:
                    fs_off.append(lua)
                else:
                    self.fail(lua)
                return _cp("ok")
            if argv[0] == "grim" and "-T" in argv:
                Path(argv[-1]).write_bytes(_png(1920, 1080))
                return _cp()
            if argv[0] == "grim" and "-g" in argv:
                self.fail("grim -g not used for --full")
            return _cp(returncode=1, stderr="unexpected " + " ".join(argv))

        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "shot.png"
            path, method, win = capture(
                out=dest,
                run=run,
                rss=None,
                force=True,
                full=True,
                settle=0,
                grow_timeout=0,
                restore_timeout=0,
            )
            self.assertEqual(method, "grim-toplevel-full")
            self.assertEqual(png_size(path), (1920, 1080))
            self.assertEqual(win.size, (1920, 1080))
            self.assertEqual(len(fs_on), 1)
            self.assertEqual(len(fs_off), 1)

    def test_full_relative_resize_if_unfullscreen_keeps_large(self):
        resizes = []
        # tile -> compositor FS -> un-FS still large -> relative resize back
        stage = ["tile"]

        def size_for_stage():
            if stage[0] == "fs":
                return [1920, 1080], [1080, 840]
            if stage[0] == "stuck":
                return [1910, 1070], [1085, 845]
            return [945, 1030], [2045, 850]

        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                size, at = size_for_stage()
                return _cp(json.dumps([_client(visible=True, size=size, at=at)]))
            if argv[:2] == ["hyprctl", "repl"]:
                lua = argv[2]
                if "fullscreen_state" in lua and "internal=2" in lua:
                    stage[0] = "fs"
                    return _cp("ok")
                if "fullscreen_state" in lua and "internal=0" in lua:
                    stage[0] = "stuck"
                    return _cp("ok")
                if "relative=true" in lua:
                    resizes.append(lua)
                    stage[0] = "tile"
                    return _cp("ok")
                self.fail(lua)
            if argv[0] == "grim" and "-T" in argv:
                Path(argv[-1]).write_bytes(_png(1920, 1080))
                return _cp()
            return _cp(returncode=1, stderr="unexpected " + " ".join(argv))

        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "shot.png"
            capture(
                out=dest,
                run=run,
                rss=None,
                force=True,
                full=True,
                settle=0,
                grow_timeout=0,
                restore_timeout=0,
            )
            self.assertEqual(len(resizes), 1)
            self.assertIn("x=-965", resizes[0])
            self.assertIn("y=-40", resizes[0])

    def test_choose_prefers_mapped_then_larger(self):
        wins = parse_hypr_clients(
            json.dumps(
                [
                    _client(pid=1, size=[100, 100], stableId="steam"),
                    _client(pid=2, size=[50, 50], stableId="rss"),
                ]
            )
        )
        self.assertEqual(choose_window(wins, None).stable_id, "steam")
