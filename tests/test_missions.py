"""No-KSP gates for seat, plan merge, warp peers, pad craft (L-038/L-039)."""

from __future__ import annotations

import unittest
from pathlib import Path

from missions import (
    flight_slug,
    is_lost,
    other_crewed_warp_danger,
    pad_craft_name,
    seated_id,
    seated_plan_path,
)
from uplink import desk, load_plan, save_plan


class _O:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Crew:
    def __init__(self, name: str):
        self.name = name


class _Vessel:
    def __init__(self, vid, crew, peri, atm=True, atm_depth=70000, alt=100000):
        self.id = vid
        self.crew = [_Crew(c) for c in crew]
        body = _O(has_atmosphere=atm, atmosphere_depth=atm_depth, name="Kerbin")
        self.orbit = _O(body=body, periapsis_altitude=peri)
        self._alt = alt

    def flight(self):
        return _O(mean_altitude=self._alt)


class _S:
    def __init__(self, vessels):
        self.space_center = _O(vessels=vessels)
        self.active_vessel = vessels[0]


class TestSlugs(unittest.TestCase):
    def test_grok_number(self):
        self.assertEqual(flight_slug("Grok Grokman 4373"), "grok-4373")
        self.assertEqual(flight_slug("Grok Kerman 4373"), "grok-4373")

    def test_named(self):
        self.assertEqual(flight_slug("Valentina Grokman"), "valentina")


class TestSeatAndPlan(unittest.TestCase):
    def test_seated_jeb(self):
        self.assertEqual(seated_id(), "jebediah")
        self.assertTrue(seated_plan_path().is_file())
        self.assertFalse(is_lost("jebediah"))

    def test_save_plan_keeps_envelope(self):
        load_plan()
        old = desk.plan["mun_pe"]
        phase = desk.plan.get("phase", "")
        desk.plan["mun_pe"] = old
        save_plan()
        text = seated_plan_path().read_text(encoding="utf-8")
        if phase:
            self.assertIn(f"phase: {phase}", text)
        self.assertIn("next: wait", text)
        self.assertIn("go: wait", text)

    def test_pad_unsigned_raises(self):
        from session import SessionError

        with self.assertRaises(SessionError) as ctx:
            pad_craft_name()
        self.assertIn("capable", str(ctx.exception))

    def test_seat_missing_refused(self):
        from missions import seat

        with self.assertRaises(FileNotFoundError):
            seat("grok-4761")


class TestWarpPeers(unittest.TestCase):
    def test_safe_peers(self):
        s = _S(
            [
                _Vessel(1, ["Grok Kerman 4373"], 89000),
                _Vessel(2, ["Grok Kerman 6189"], 349000),
            ]
        )
        self.assertIsNone(other_crewed_warp_danger(s))

    def test_peri_in_air(self):
        s = _S(
            [
                _Vessel(1, ["Grok Kerman 4373"], 89000),
                _Vessel(3, ["Bob Kerman"], 50000),
            ]
        )
        msg = other_crewed_warp_danger(s)
        self.assertIsNotNone(msg)
        self.assertIn("Bob", msg)


if __name__ == "__main__":
    unittest.main()
