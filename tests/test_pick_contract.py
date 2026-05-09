from __future__ import annotations
import unittest

REQUIRED_KEYS = {
    "event_id",
    "match",
    "live",
    "best_side",
    "bookmaker",
    "book_odds",
    "fair_odds",
    "edge_percent",
    "book_prob",
    "fair_prob",
}

class TestPickContract(unittest.TestCase):
    def test_pick_keys_contract(self):
        sample_pick = {
            "event_id": "abc123",
            "match": "A vs B",
            "live": False,
            "best_side": "away",
            "bookmaker": "betmgm",
            "book_odds": "+145",
            "fair_odds": "+142",
            "edge_percent": 0.51,
            "book_prob": 40.8,
            "fair_prob": 41.3,
        }
        self.assertTrue(REQUIRED_KEYS.issubset(sample_pick.keys()))
