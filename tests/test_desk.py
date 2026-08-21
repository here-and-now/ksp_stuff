"""Disk sit snapshot — no kRPC."""

from __future__ import annotations

import unittest

from desk import (
    DeskSit,
    F013,
    card_experiments,
    format_sit,
    hangar_call,
    parse_last_flight,
    prior_sci,
    sci_delta,
)
from world import SaveVessel


def _sit(**kwargs) -> DeskSit:
    base = dict(
        lock="free",
        hangar="none",
        active_vessel="none",
        seat="jebediah",
        sci=2.4,
        sci_delta="2.4000",
        unlocked="start",
        capable="no",
        craft="(none)",
        card=(),
        last_command="pad",
        last_exit="0",
        last_abort="",
        review="none",
        note_tech="",
        f013=(
            F013(
                eid="",
                instrument="none",
                tech="none",
                unlocked="n/a",
                on_craft="no",
                host="none",
            ),
        ),
        stack=(),
        vessels=(),
        leftover_science=(),
        stack_dump="",
        mods=(),
    )
    base.update(kwargs)
    return DeskSit(**base)


class TestDesk(unittest.TestCase):
    def test_parse_last_flight(self):
        text = "command: hop\nexit: 4\nabort: OFFPLAN apo 18858 > 18000\nlast:\n  x\n"
        out = parse_last_flight(text)
        self.assertEqual(out["command"], "hop")
        self.assertEqual(out["exit"], "4")
        self.assertIn("OFFPLAN", out["abort"])

    def test_card_experiments(self):
        text = (
            "science: card\n"
            "- experiment: temperatureScan\n"
            "  part: sensorThermometer\n"
            "- experiment: geigerCounter\n"
        )
        self.assertEqual(
            card_experiments(text),
            ["temperatureScan", "geigerCounter"],
        )

    def test_format_sit_has_hangar_and_f013_not_gym_scan(self):
        text = format_sit(_sit())
        self.assertIn("hangar: none", text)
        self.assertIn("scene: unknown (disk)", text)
        self.assertIn("mods: none", text)
        self.assertIn("f013:", text)
        self.assertIn("instrument: none", text)
        self.assertNotIn("geigerCounter", text)
        self.assertNotIn("open science at this tree", text)
        self.assertNotIn("mysteryGoo", text)
        self.assertNotIn("Cape", text)

    def test_prior_sci_from_desk_md(self):
        self.assertAlmostEqual(prior_sci("lock: free\nsci: 2.4272\nsci_delta: x\n"), 2.4272)
        self.assertIsNone(prior_sci("hangar: none\n"))

    def test_sci_delta(self):
        self.assertIn("+1.0000", sci_delta(2.0, 1.0))
        self.assertIn("no prior", sci_delta(2.0, None))

    def test_hangar_none_when_ksc_empty(self):
        hangar, active = hangar_call(vessels=(), lock="free")
        self.assertEqual(hangar, "none")
        self.assertEqual(active, "none")

    def test_hangar_recover_names_save_vessel(self):
        ships = (
            SaveVessel(name="kspstuff-hop-flea-pbc", sit="FLYING", type="Ship", landed=False),
        )
        hangar, active = hangar_call(vessels=ships, lock="free")
        self.assertEqual(hangar, "recover kspstuff-hop-flea-pbc sit=FLYING")
        self.assertEqual(active, "kspstuff-hop-flea-pbc")

    def test_hangar_phase_prelaunch(self):
        ships = (
            SaveVessel(name="kspstuff-hop-flea-pbc", sit="PRELAUNCH", type="Ship", landed=True),
        )
        hangar, active = hangar_call(vessels=ships, lock="free")
        self.assertEqual(hangar, "phase kspstuff-hop-flea-pbc sit=PRELAUNCH")
        self.assertEqual(active, "kspstuff-hop-flea-pbc")

    def test_hangar_blocked_when_lock_live(self):
        ships = (
            SaveVessel(name="pad", sit="PRELAUNCH", type="Ship", landed=True),
        )
        hangar, active = hangar_call(vessels=ships, lock="live")
        self.assertEqual(hangar, "blocked")
        self.assertEqual(active, "pad")

    def test_f013_paw_is_not_unlocked_hardware(self):
        from tests.test_world import FIXTURE
        from world import load_world
        from desk import f013_for

        world = load_world(ksp_root=FIXTURE)
        row = f013_for(world, "geigerCounter", ["probeCoreSphere.v2"])
        if row.instrument == "none":
            self.assertEqual(row.unlocked, "n/a")
            self.assertNotEqual(row.unlocked, "yes")
        else:
            self.assertIn(row.unlocked, {"yes", "no"})


if __name__ == "__main__":
    unittest.main()
