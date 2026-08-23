"""Protobuf get_services shape (L-040)."""

from __future__ import annotations

import time
import unittest

from session import Session, _krpc_service_names


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
