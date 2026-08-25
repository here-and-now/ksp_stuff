"""Protobuf get_services shape (L-040). Reader Session (T-454)."""

from __future__ import annotations

import time
import unittest

from session import (
    READ_CLIENT,
    WRITE_CLIENT,
    ReadOnlyError,
    Session,
    _krpc_service_names,
)


class _Svc:
    def __init__(self, name: str):
        self.name = name


class _Msg:
    def __init__(self, services):
        self.services = services


class _Conn:
    def __init__(self, raw):
        self.krpc = type("K", (), {"get_services": lambda self: raw})()


class TestServiceNames(unittest.TestCase):
    def test_protobuf_services_field(self):
        raw = _Msg([_Svc("SpaceCenter"), _Svc("KRPC")])
        names = _krpc_service_names(_Conn(raw))
        self.assertEqual(names, ("SpaceCenter", "KRPC"))

    def test_empty_on_raise(self):
        class Boom:
            @property
            def krpc(self):
                raise RuntimeError("no")

        self.assertEqual(_krpc_service_names(Boom()), ())


class TestNoStockMunRequires(unittest.TestCase):
    def test_session_does_not_require_mechjeb_or_remotetech(self):
        self.assertFalse(hasattr(Session, "require_mechjeb"))
        self.assertFalse(hasattr(Session, "require_remotetech"))


class TestCloseTimeout(unittest.TestCase):
    def test_close_does_not_block_on_hung_conn(self):
        session = Session()

        class _Hung:
            def close(self):
                time.sleep(30)

        session.conn = _Hung()
        session.space_center = object()
        t0 = time.monotonic()
        session.close()
        self.assertLess(time.monotonic() - t0, 8.0)
        self.assertIsNone(session.conn)


class TestReadOnlySession(unittest.TestCase):
    def test_readonly_uses_read_client_name(self):
        writer = Session()
        reader = Session(readonly=True)
        self.assertEqual(writer.settings.name, WRITE_CLIENT)
        self.assertEqual(reader.settings.name, READ_CLIENT)
        self.assertTrue(reader.readonly)
        self.assertFalse(writer.readonly)

    def test_switch_to_refuses(self):
        session = Session(readonly=True)
        session.conn = object()
        session.space_center = object()
        with self.assertRaises(ReadOnlyError):
            session.switch_to(object(), settle=0.0)

    def test_control_and_scene_writes_refuse(self):
        class _Ctrl:
            throttle = 0.0

            def activate_next_stage(self):
                raise AssertionError("writer")

        class _Sc:
            def __init__(self):
                self.active_vessel = type(
                    "V", (), {"control": _Ctrl(), "auto_pilot": object()}
                )()
                self.rails_warp_factor = 0

            def launch_vessel(self, *a, **k):
                raise AssertionError("launch")

        class _Krpc:
            game_scene = "flight"

        class _Conn:
            def __init__(self):
                self.krpc = _Krpc()
                self.space_center = _Sc()

            def close(self):
                pass

            def add_stream(self, *a, **k):
                class _S:
                    def remove(self):
                        self.removed = True

                s = _S()
                s.removed = False
                return s

        session = Session(readonly=True)
        session.conn = _Conn()
        session.space_center = session.conn.space_center
        session._wrap_readonly()
        with self.assertRaises(ReadOnlyError):
            session.space_center.active_vessel = object()
        with self.assertRaises(ReadOnlyError):
            session.space_center.launch_vessel("VAB", "x", "LaunchPad")
        with self.assertRaises(ReadOnlyError):
            session.conn.krpc.game_scene = "space_center"
        vessel = session.space_center.active_vessel
        with self.assertRaises(ReadOnlyError):
            vessel.control.throttle = 1.0
        with self.assertRaises(ReadOnlyError):
            vessel.control.activate_next_stage()
        with self.assertRaises(ReadOnlyError):
            vessel.recover()

    def test_close_removes_streams(self):
        removed: list[bool] = []

        class _S:
            def remove(self):
                removed.append(True)

        class _Conn:
            def add_stream(self, *a, **k):
                return _S()

            def close(self):
                pass

        session = Session(readonly=True)
        session.conn = _Conn()
        session.space_center = object()
        session.add_stream(getattr, object(), "x")
        session.add_stream(getattr, object(), "y")
        session.close()
        self.assertEqual(removed, [True, True])
        self.assertEqual(session._streams, [])
