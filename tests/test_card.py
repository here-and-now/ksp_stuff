"""Linus card parser. Empty is not a sit."""

from __future__ import annotations

import unittest
from pathlib import Path

from card import (
    HOP_EXPERIMENTS,
    PAD_EXPERIMENTS,
    card_experiment_ids,
    card_experiments,
    card_flying_ids,
    card_pad_ids,
    card_splash_ids,
)

FIX = Path("tests/fixtures/cards")


class TestCardParse(unittest.TestCase):
    def test_fixtures(self):
        self.assertEqual(PAD_EXPERIMENTS, ("mysteryGoo", "temperatureScan"))
        self.assertEqual(HOP_EXPERIMENTS, ("kerbalism_TELEMETRY", "temperatureScan"))
        self.assertEqual(
            card_pad_ids((FIX / "pad-geiger.md").read_text(encoding="utf-8")),
            ("geigerCounter",),
        )
        self.assertEqual(
            card_flying_ids((FIX / "hop-flying.md").read_text(encoding="utf-8")),
            ("kerbalism_TELEMETRY", "temperatureScan"),
        )
        self.assertEqual(
            card_splash_ids((FIX / "splash-goo.md").read_text(encoding="utf-8")),
            ("mysteryGoo",),
        )
        empty = (FIX / "empty.md").read_text(encoding="utf-8")
        self.assertEqual(card_pad_ids(empty), ())
        self.assertEqual(card_flying_ids(empty), ())
        self.assertEqual(card_experiment_ids(empty), ())
        self.assertEqual(card_experiments(empty), [])

    def test_empty_text_is_empty(self):
        self.assertEqual(card_experiment_ids(""), ())
        self.assertEqual(card_pad_ids(""), ())
        self.assertEqual(card_flying_ids(""), ())
        self.assertEqual(card_splash_ids(""), ())

    def test_experiment_id_and_dash(self):
        text = (
            "science: card\n"
            "- experiment: temperatureScan\n"
            "  part: sensorThermometer\n"
            "experiment_id: geigerCounter\n"
        )
        self.assertEqual(
            card_experiments(text),
            ["temperatureScan", "geigerCounter"],
        )
