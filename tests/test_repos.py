from __future__ import annotations

import unittest
from unittest.mock import patch

from departments.deportes.futbol.repo import get_fixture_by_id, list_fixtures, list_live_fixtures


class RepoTests(unittest.TestCase):
    @patch("departments.deportes.futbol.repo.load_sport_day")
    def test_list_fixtures(self, mock_load) -> None:
        mock_load.return_value = [{"fixture_id": "1"}, {"fixture_id": "2"}]
        rows = list_fixtures()
        self.assertEqual(len(rows), 2)

    @patch("departments.deportes.futbol.repo.load_sport_day")
    def test_list_live_fixtures(self, mock_load) -> None:
        mock_load.return_value = [
            {"fixture_id": "1", "live": True},
            {"fixture_id": "2", "live": False},
        ]
        rows = list_live_fixtures()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["fixture_id"], "1")

    @patch("departments.deportes.futbol.repo.load_sport_day")
    def test_get_fixture_by_id(self, mock_load) -> None:
        mock_load.return_value = [{"fixture_id": "x1"}, {"fixture_id": "x2"}]
        row = get_fixture_by_id("x2")
        self.assertIsNotNone(row)
        self.assertEqual(row["fixture_id"], "x2")
