"""Disk desk snapshot — no kRPC."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from desk import (
    card_experiments,
    format_desk,
    helm_card,
    leftover_decision,
    parse_last_flight,
)
from world import SaveVessel


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

    def test_format_desk_uses_world_sci(self):
        from world import load_world

        world = load_world()
        with patch("desk.lock_state", return_value="free"):
            text = format_desk(world)
        self.assertIn("lock: free", text)
        self.assertIn("sci:", text)
        self.assertIn("unlocked:", text)
        self.assertIn("capable:", text)
        self.assertIn("sci_delta:", text)
        self.assertIn("leftover science", text)
        self.assertIn("leftover vessels", text)
        self.assertIn("f013:", text)
        self.assertIn("instrument:", text)
        self.assertIn("leftover:", text)
        self.assertIn("scene: unknown", text)
        self.assertIn("active_vessel:", text)
        self.assertIn("experiment budgets", text)
        from desk import DESK_MD

        self.assertTrue(DESK_MD.is_file())
        disk = DESK_MD.read_text(encoding="utf-8")
        self.assertIn("lock:", disk)
        self.assertIn("leftover:", disk)

    def test_leftover_none_when_ksc_empty(self):
        leftover, active = leftover_decision(vessels=(), lock="free")
        self.assertEqual(leftover, "none")
        self.assertEqual(active, "none")

    def test_leftover_recover_names_save_vessel(self):
        ships = (
            SaveVessel(name="kspstuff-hop-flea-pbc", sit="FLYING", type="Ship", landed=False),
        )
        leftover, active = leftover_decision(vessels=ships, lock="free")
        self.assertEqual(leftover, "recover kspstuff-hop-flea-pbc")
        self.assertEqual(active, "kspstuff-hop-flea-pbc")

    def test_leftover_hangar_blocked_when_lock_live(self):
        ships = (
            SaveVessel(name="pad", sit="PRELAUNCH", type="Ship", landed=True),
        )
        leftover, active = leftover_decision(vessels=ships, lock="live")
        self.assertEqual(leftover, "hangar-blocked")
        self.assertEqual(active, "pad")

    def test_helm_card_writes(self):
        card = helm_card()
        self.assertIn("craft", card)
        self.assertIn("slots", card)
        self.assertIn("do_not_toggle", card)
        self.assertIn("wait", card)


if __name__ == "__main__":
    unittest.main()
