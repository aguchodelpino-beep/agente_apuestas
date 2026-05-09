from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from core.health import get_health_status


class HealthTests(unittest.TestCase):
    @patch("core.health._is_stale")
    def test_health_status_shape(self, mock_stale) -> None:
        mock_stale.return_value = False
        status = get_health_status()
        self.assertIn("ok", status)
        self.assertIn("timezone", status)
        self.assertIn("stale_files", status)
        self.assertIsInstance(status["stale_files"], list)
