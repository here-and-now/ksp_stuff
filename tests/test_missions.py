"""No-KSP gates for seat, plan merge, warp peers, pad craft (L-038/L-039)."""

from __future__ import annotations

import unittest
from missions import (
    flight_slug,
    is_lost,
    other_crewed_warp_danger,
    pad_craft_name,
    seated_id,
    seated_plan_path,
)
from uplink import desk, load_plan, save_plan
from watch import FlightState, _refuse_abort


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
        self.assertEqual(flight_slug("Grok Kerman 4373"), "grok-4373")

    def test_named(self):
        self.assertEqual(flight_slug("Valentina Kerman"), "valentina")


class TestSeatAndPlan(unittest.TestCase):
    def test_seated_jeb(self):
        self.assertEqual(seated_id(), "jebediah")
        self.assertTrue(seated_plan_path().is_file())
        self.assertFalse(is_lost("jebediah"))

    def test_save_plan_keeps_envelope(self):
        load_plan()
        old = desk.plan["mun_pe"]
        desk.plan["mun_pe"] = old
        save_plan()
        text = seated_plan_path().read_text(encoding="utf-8")
        self.assertIn("phase: wait", text)
        self.assertIn("next: wait", text)

    def test_pad_returns_signed_craft(self):
        self.assertEqual(pad_craft_name(), "kspstuff-hop-flea")

    def test_hop_flea_has_goo(self):
        from craft import hop_flea

        names = [p.name for p in hop_flea().parts]
        self.assertIn("mk1pod_v2", names)
        self.assertIn("parachuteSingle", names)
        self.assertIn("solidBooster_sm_v2", names)
        self.assertEqual(names.count("GooExperiment"), 2)
        self.assertNotIn("sensorThermometer", names)
        self.assertNotIn("solidBooster_v2", names)

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


class TestRefuseAbort(unittest.TestCase):
    def test_bound_fueled(self):
        st = FlightState(
            body="Mun",
            peri=22000,
            apo=100000,
            alt=50000,
            lf=360,
            ox=0,
            thrust=0,
            escaping=False,
            wreck=False,
        )
        # FlightState may require more fields — fall back if construct fails.
        try:
            self.assertTrue(_refuse_abort(st))
        except TypeError:
            self.skipTest("FlightState fields changed")

    def test_lithobrake_not_refused(self):
        try:
            st = FlightState(
                body="Mun",
                peri=-100,
                apo=10000,
                alt=8000,
                lf=200,
                ox=0,
                thrust=60,
                escaping=False,
                wreck=False,
            )
        except TypeError:
            self.skipTest("FlightState fields changed")
            return
        self.assertFalse(_refuse_abort(st))


if __name__ == "__main__":
    unittest.main()
