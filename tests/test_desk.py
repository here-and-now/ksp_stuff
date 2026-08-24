"""Disk sit snapshot — no kRPC."""

from __future__ import annotations

import unittest
from pathlib import Path

from desk import (
    DeskSit,
    F013,
    _clip_note,
    card_experiments,
    format_sit,
    hangar_call,
    hangar_from_live,
    latest_review,
    parse_last_flight,
    pick_banked_science,
    prior_sci,
    review_field,
    sci_delta,
)
from ops import leftover_cli, leftover_sit
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
        self.assertIn("sci_src: sfs", text)
        self.assertNotIn("sci_disk:", text)
        self.assertIn("leftover: 0", text)
        self.assertIn("scene: unknown (disk)", text)
        self.assertIn("mods: none", text)
        self.assertIn("f013:", text)
        self.assertIn("instrument: none", text)
        self.assertNotIn("geigerCounter", text)
        self.assertNotIn("open science at this tree", text)
        self.assertNotIn("mysteryGoo", text)
        self.assertNotIn("Cape", text)

    def test_format_sit_review_not_parked_or_missing(self):
        path = latest_review()
        if path is not None:
            posix = path.as_posix().replace("\\", "/")
            self.assertNotIn("/archive/", posix)
            self.assertFalse(posix.startswith("docs/archive/"))
            self.assertTrue(path.is_file())
        field = review_field()
        text = format_sit(_sit(review=field))
        line = next(row for row in text.splitlines() if row.startswith("review:"))
        val = line.split(":", 1)[1].strip()
        self.assertNotIn("/archive/", val.replace("\\", "/"))
        self.assertFalse(val.startswith("docs/archive/"))
        if val.endswith("-review.md"):
            dest = Path(val)
            self.assertTrue(dest.is_file(), val)
            self.assertNotIn("/archive/", dest.as_posix().replace("\\", "/"))
        elif val not in {"none", ""}:
            self.assertTrue(Path(val).is_file(), val)

    def test_prior_sci_from_desk_md(self):
        self.assertAlmostEqual(prior_sci("lock: free\nsci: 2.4272\nsci_delta: x\n"), 2.4272)
        self.assertIsNone(prior_sci("hangar: none\n"))

    def test_sci_delta(self):
        self.assertIn("+1.0000", sci_delta(2.0, 1.0))
        self.assertIn("no prior", sci_delta(2.0, None))

    def test_parse_last_flight_sci(self):
        text = "command: hop\nexit: 0\nabort:\nsci: 5.6718\nlast:\n  x\n"
        out = parse_last_flight(text)
        self.assertEqual(out["sci"], "5.6718")

    def test_pick_banked_science_live_beats_stale_sfs(self):
        now, src, lag = pick_banked_science(1.4718, live=5.6718)
        self.assertAlmostEqual(now, 5.6718)
        self.assertEqual(src, "krpc")
        self.assertAlmostEqual(lag, 1.4718)

    def test_pick_banked_science_last_flight_when_sfs_lags(self):
        now, src, lag = pick_banked_science(1.4718, last_flight=5.6718)
        self.assertAlmostEqual(now, 5.6718)
        self.assertEqual(src, "last-flight")
        self.assertAlmostEqual(lag, 1.4718)

    def test_pick_banked_science_disk_when_last_not_ahead(self):
        now, src, lag = pick_banked_science(5.6718, last_flight=5.6718)
        self.assertAlmostEqual(now, 5.6718)
        self.assertEqual(src, "sfs")
        self.assertIsNone(lag)

    def test_format_sit_notes_disk_lag(self):
        text = format_sit(_sit(sci=5.6718, sci_src="last-flight", sci_disk=1.4718))
        self.assertIn("sci: 5.6718", text)
        self.assertIn("sci_src: last-flight", text)
        self.assertIn("sci_disk: 1.4718 (lag)", text)

    def test_hangar_none_when_ksc_empty(self):
        hangar, active = hangar_call(vessels=(), lock="free")
        self.assertEqual(hangar, "none")
        self.assertEqual(active, "none")

    def test_hangar_live_empty_is_not_disk_suborbital_ghost(self):
        hangar, active = hangar_from_live((), lock="free")
        self.assertEqual(hangar, "none")
        self.assertEqual(active, "none")

    def test_hangar_live_recover_sub_orbital(self):
        hangar, active = hangar_from_live(
            (("kspstuff-hop-valiant-t7-pbc", "SUB_ORBITAL"),),
            lock="free",
        )
        self.assertEqual(
            hangar, "recover kspstuff-hop-valiant-t7-pbc sit=SUB_ORBITAL"
        )
        self.assertEqual(active, "kspstuff-hop-valiant-t7-pbc")

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

    def test_hangar_ignores_flying_debris(self):
        """Disk FLYING Debris is not leftover. Empty Tracking Hangars (I-017)."""
        ships = (
            SaveVessel(
                name="kspstuff-hop-flea-pbc Debris",
                sit="FLYING",
                type="Debris",
                landed=False,
            ),
        )
        hangar, active = hangar_call(vessels=ships, lock="free")
        self.assertEqual(hangar, "none")
        self.assertEqual(active, "none")

    def test_hangar_ship_not_debris_when_both_in_save(self):
        ships = (
            SaveVessel(
                name="kspstuff-hop-flea-pbc Debris",
                sit="FLYING",
                type="Debris",
                landed=False,
            ),
            SaveVessel(
                name="kspstuff-hop-flea-pbc",
                sit="PRELAUNCH",
                type="Ship",
                landed=True,
            ),
        )
        hangar, active = hangar_call(vessels=ships, lock="free")
        self.assertEqual(hangar, "phase kspstuff-hop-flea-pbc sit=PRELAUNCH")
        self.assertEqual(active, "kspstuff-hop-flea-pbc")

    def test_leftover_overlay_cli_space_center(self):
        d = {"hangar": "none", "leftover": "0", "can_revert": "true"}
        self.assertTrue(leftover_sit(d))
        self.assertIn("--space-center", leftover_cli(d))

    def test_leftover_ksc_ready_ignores_stale_can_revert(self):
        d = {
            "hangar": "none",
            "leftover": "0",
            "can_revert": "true",
            "ksc_ready": "true",
        }
        self.assertFalse(leftover_sit(d))

    def test_leftover_phase_prelaunch_cli_recover(self):
        d = {"hangar": "phase flea sit=PRELAUNCH", "leftover": "1"}
        self.assertTrue(leftover_sit(d))
        self.assertIn("--recover", leftover_cli(d))
        self.assertNotIn("--space-center", leftover_cli(d))

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

    def test_format_sit_clips_note_tech(self):
        text = format_sit(_sit(note_tech="word " * 80))
        line = next(ln for ln in text.splitlines() if ln.startswith("note-tech:"))
        self.assertLessEqual(len(line), 180)
        self.assertTrue(line.endswith("…"))

    def test_format_sit_bind_hop_apo(self):
        text = format_sit(
            _sit(bind="T-020 TELEMETRY 30/0.052 seq0", hop_apo="18 km")
        )
        self.assertIn("bind: T-020 TELEMETRY 30/0.052 seq0", text)
        self.assertIn("hop_apo: 18 km", text)
        self.assertNotIn("bind:", format_sit(_sit()))
        self.assertNotIn("pay:", format_sit(_sit()))
        self.assertIn("pay: no", format_sit(_sit(pay="no")))

    def test_clip_note_one_line(self):
        self.assertEqual(_clip_note("  a \n b  "), "a b")
        self.assertLessEqual(len(_clip_note("x" * 400)), 160)


if __name__ == "__main__":
    unittest.main()
