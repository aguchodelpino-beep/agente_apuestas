from __future__ import annotations

import unittest

from sharedoddsnormalizer import parse_odd_id, normalize_sgo_odds


class TestSharedOddsNormalizer(unittest.TestCase):
    def test_parse_odd_id(self) -> None:
        self.assertEqual(parse_odd_id(" abc "), "abc")

    def test_normalize_sgo_odds(self) -> None:
        row = {
            "id": "o1",
            "fixture_id": "fx1",
            "market": "Moneyline",
            "selection": "Home",
            "odds": 1.91,
            "bookmaker": "Pinnacle",
        }
        out = normalize_sgo_odds(row)
        self.assertEqual(out["odd_id"], "o1")
        self.assertEqual(out["fixture_id"], "fx1")
        self.assertEqual(out["market"], "moneyline")
        self.assertEqual(out["selection"], "home")
        self.assertEqual(out["odds"], 1.91)
        self.assertEqual(out["bookmaker"], "pinnacle")
