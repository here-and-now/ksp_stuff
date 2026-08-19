"""Protobuf get_services shape (L-040)."""

from __future__ import annotations

import unittest

from session import _krpc_service_names


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
