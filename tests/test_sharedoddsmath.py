from __future__ import annotations

import unittest

from sharedoddsmath import american_to_prob, edge_percent


class TestSharedOddsMath(unittest.TestCase):
    def test_american_to_prob_positive(self) -> None:
        prob = american_to_prob(150)
        self.assertGreater(prob, 0.0)
        self.assertLess(prob, 1.0)

    def test_american_to_prob_negative(self) -> None:
        prob = american_to_prob(-120)
        self.assertGreater(prob, 0.0)
        self.assertLess(prob, 1.0)

    def test_edge_percent(self) -> None:
        self.assertAlmostEqual(edge_percent(0.60, 0.50), 0.10, places=6)
