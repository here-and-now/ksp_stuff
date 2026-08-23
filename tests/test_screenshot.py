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
    MISSION_INTERVAL_S,
    PRESERVE,
    ScreenshotError,
    ShotCadence,
    already_monitor_size,
    apply_pose,
    capture,
    choose_window,
    mission_dest,
    parse_hypr_clients,
    parse_hypr_monitors,
    png_size,
    resolve_dest,
    trim_tick_shots,
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
    def test_already_full_skips_grow(self):
        tiled = parse_hypr_clients(json.dumps([_client(size=[945, 1030])]))[0]
        huge = parse_hypr_clients(json.dumps([_client(size=[1916, 1046])]))[0]
        fs = parse_hypr_clients(
            json.dumps([_client(size=[945, 1030], fullscreen=2)])
        )[0]
        self.assertFalse(already_monitor_size(tiled, None))
        self.assertTrue(already_monitor_size(huge, None))
        self.assertTrue(already_monitor_size(fs, None))

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

    def test_full_noop_when_already_monitor_sized(self):
        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                return _cp(
                    json.dumps(
                        [
                            _client(
                                visible=False,
                                size=[1916, 1046],
                                at=[1082, 842],
                                fullscreen=0,
                            )
                        ]
                    )
                )
            if argv[:3] == ["hyprctl", "-j", "monitors"]:
                return _cp(
                    json.dumps(
                        [
                            {
                                "id": 1,
                                "name": "DP-1",
                                "width": 1920,
                                "height": 1080,
                                "focused": True,
                                "activeWorkspace": {"id": 1, "name": "1"},
                            }
                        ]
                    )
                )
            if argv[:2] == ["hyprctl", "repl"]:
                self.fail("must not compositor-FS a window that is already full")
            if argv[0] == "grim" and "-T" in argv:
                Path(argv[-1]).write_bytes(_png(1916, 1046))
                return _cp()
            return _cp(returncode=1, stderr="unexpected " + " ".join(argv))

        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "shot.png"
            path, method, win = capture(
                out=dest, run=run, rss=None, force=True, full=True, settle=0
            )
            self.assertEqual(method, "grim-toplevel")
            self.assertFalse(win.visible)
            self.assertEqual(png_size(path), (1916, 1046))

    def test_full_noop_when_already_fullscreen(self):
        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                return _cp(
                    json.dumps(
                        [_client(visible=True, size=[1920, 1080], fullscreen=2)]
                    )
                )
            if argv[:2] == ["hyprctl", "repl"]:
                self.fail("must not clear existing fullscreen")
            if argv[0] == "grim" and "-T" in argv:
                Path(argv[-1]).write_bytes(_png(1920, 1080))
                return _cp()
            return _cp(returncode=1, stderr="unexpected " + " ".join(argv))

        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "shot.png"
            _path, method, _win = capture(
                out=dest, run=run, rss=None, force=True, full=True, settle=0
            )
            self.assertEqual(method, "grim-toplevel")

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


class _Snap:
    def __init__(self, sit="pre_launch", stage=1, thrust=0.0, wreck=False, ec=10.0, met=0.0):
        self.situation = sit
        self.stage = stage
        self.thrust = thrust
        self.wreck = wreck
        self.ec = ec
        self.met = met


class TestShotCadence(TestCase):
    def test_interval_and_events(self):
        written: list[str] = []
        t = {"now": 0.0}

        def clock():
            return t["now"]

        def grab(dest: Path) -> None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"png")
            written.append(dest.name)

        cad = ShotCadence(interval_s=60.0, grab=grab, clock=clock, min_gap_s=0.0)
        first = cad.observe(_Snap(sit="pre_launch", met=0))
        self.assertIsNotNone(first)
        self.assertIn("-start", written[0])
        self.assertIsNone(cad.observe(_Snap(sit="pre_launch", met=1)))
        air = cad.observe(_Snap(sit="flying", met=2, thrust=50.0))
        self.assertIsNotNone(air)
        self.assertIn("sit-flying", written[-1])
        t["now"] = 60.0
        tick = cad.observe(_Snap(sit="flying", met=60, thrust=50.0))
        self.assertIsNotNone(tick)
        self.assertTrue(written[-1].endswith("-tick.png"))
        stage = cad.observe(_Snap(sit="flying", met=61, thrust=50.0, stage=0))
        self.assertIsNotNone(stage)
        self.assertTrue(written[-1].endswith("-stage.png"))
        sci = cad.event("science", _Snap(sit="flying", met=62))
        self.assertIsNotNone(sci)
        self.assertTrue(written[-1].endswith("-science.png"))

    def test_mission_dest_uses_run_folder(self):
        dest = mission_dest("airborne", met=7.4, stamp="2026-08-20T15-58-12Z", command="hop")
        self.assertEqual(dest.name, "T+000007-airborne.png")
        self.assertEqual(dest.parent.name, "2026-08-20T15-58-12Z-hop")
        self.assertEqual(dest.parent.parent.name, "runs")

    def test_default_interval_is_ten(self):
        self.assertEqual(MISSION_INTERVAL_S, 10.0)
        self.assertEqual(ShotCadence().interval_s, 10.0)

    def test_trims_old_ticks_keeps_events(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for i in range(5):
                (folder / f"T+{i:06d}-tick.png").write_bytes(b"x")
            (folder / "T+000002-light.png").write_bytes(b"keep")
            trim_tick_shots(folder, keep=3)
            ticks = sorted(p.name for p in folder.glob("*-tick.png"))
            self.assertEqual(
                ticks,
                ["T+000002-tick.png", "T+000003-tick.png", "T+000004-tick.png"],
            )
            self.assertEqual((folder / "T+000002-light.png").read_bytes(), b"keep")

    def test_cadence_trims_ticks_live(self):
        folders: list[Path] = []
        t = {"now": 0.0}

        def clock():
            return t["now"]

        def grab(dest: Path) -> None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"png")
            folders.append(dest.parent)

        cad = ShotCadence(interval_s=10.0, grab=grab, clock=clock, min_gap_s=0.0)
        cad.observe(_Snap(sit="pre_launch", met=0))
        for i in range(1, 6):
            t["now"] = float(i * 10)
            cad.observe(_Snap(sit="pre_launch", met=i * 10))
        folder = folders[-1]
        on_disk = sorted(p.name for p in folder.glob("*-tick.png"))
        self.assertEqual(len(on_disk), 3)

    def test_slow_grab_skips_later_ticks(self):
        written: list[str] = []
        t = {"now": 0.0}

        def clock():
            return t["now"]

        def grab(dest: Path) -> None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"png")
            written.append(dest.name)
            t["now"] += 2.0

        cad = ShotCadence(interval_s=10.0, grab=grab, clock=clock, min_gap_s=0.0)
        self.assertIsNotNone(cad.observe(_Snap(sit="flying", met=0)))
        t["now"] = 12.0
        self.assertIsNone(cad.observe(_Snap(sit="flying", met=12)))
        self.assertTrue(any("-start" in n for n in written))
        self.assertFalse(any(n.endswith("-tick.png") for n in written))
        wreck = cad.observe(_Snap(sit="flying", met=13, wreck=True))
        self.assertIsNotNone(wreck)
        self.assertTrue(written[-1].endswith("-wreck.png"))


class _Cam:
    mode = "automatic"
    pitch = 11.0
    heading = 17.0
    distance = 30.0
    fo_v = 60.0


class _CM:
    free = "free"
    automatic = "automatic"


class _SC:
    CameraMode = _CM

    def __init__(self) -> None:
        self.camera = _Cam()


class TestPoseAndBeauty(TestCase):
    def test_apply_pose_holds_and_restores(self):
        sc = _SC()
        naps: list[float] = []
        restore = apply_pose(sc, "pad-plume", hold_s=0.08, nap=naps.append)
        self.assertEqual(sc.camera.mode, "free")
        self.assertAlmostEqual(sc.camera.pitch, 12.0)
        self.assertAlmostEqual(sc.camera.heading, 52.0)
        self.assertAlmostEqual(sc.camera.distance, 28.0)
        restore()
        self.assertEqual(sc.camera.mode, "automatic")
        self.assertAlmostEqual(sc.camera.pitch, 11.0)
        self.assertAlmostEqual(sc.camera.heading, 17.0)
        self.assertAlmostEqual(sc.camera.distance, 30.0)

    def test_apply_pose_unknown_is_noop(self):
        sc = _SC()
        restore = apply_pose(sc, "nope", nap=lambda _s: None)
        restore()
        self.assertEqual(sc.camera.pitch, 11.0)

    def test_beauty_toggles_f2_around_grim(self):
        evals: list[str] = []
        grim_at: list[int] = []

        def run(argv, **_kw):
            if argv[:3] == ["hyprctl", "-j", "clients"]:
                return _cp(
                    json.dumps(
                        [_client(visible=True, size=[1920, 1080], stableId="18000063")]
                    )
                )
            if len(argv) >= 2 and argv[0] == "hyprctl" and argv[1] == "eval":
                evals.append(argv[2])
                self.assertIn("F2", argv[2])
                self.assertNotIn("focus", argv[2])
                return _cp("ok\n")
            if argv[0] == "grim" and "-T" in argv:
                grim_at.append(len(evals))
                Path(argv[-1]).write_bytes(_png(1920, 1080))
                return _cp()
            return _cp(returncode=1, stderr="unexpected " + " ".join(argv))

        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "shot.png"
            _path, method, _win = capture(
                out=dest, run=run, rss=None, force=True, beauty=True
            )
            self.assertEqual(method, "grim-toplevel")
            self.assertEqual(len(evals), 2)
            self.assertEqual(evals[0], evals[1])
            self.assertEqual(grim_at, [1])
