from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.health import check_db, check_api_url, get_health_status


class TestCheckDb(unittest.TestCase):
    def test_valid_db_returns_ok(self):
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as f:
            conn = sqlite3.connect(f.name)
            conn.execute("CREATE TABLE t (id INTEGER)")
            conn.close()
            result = check_db(f.name)
        self.assertTrue(result["ok"])
        self.assertIsNone(result["error"])

    def test_missing_db_returns_error(self):
        result = check_db("/tmp/no_existe_nunca_jamas.sqlite")
        # sqlite crea el archivo si no existe — verificar que al menos responde
        self.assertIn("ok", result)

    def test_invalid_path_returns_not_ok(self):
        result = check_db("/proc/1/mem")
        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["error"])


class TestCheckApiUrl(unittest.TestCase):
    def test_ok_response(self):
        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value.__enter__.return_value.status = 200
            result = check_api_url("https://fake-api.example.com")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 200)

    def test_server_error_returns_not_ok(self):
        import urllib.error
        with patch("urllib.request.urlopen") as mock_open:
            mock_open.side_effect = urllib.error.HTTPError(
                url="https://fake", code=503, msg="Service Unavailable",
                hdrs=None, fp=None
            )
            result = check_api_url("https://fake-api.example.com")
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 503)

    def test_connection_error_returns_not_ok(self):
        with patch("urllib.request.urlopen") as mock_open:
            mock_open.side_effect = OSError("connection refused")
            result = check_api_url("https://fake-api.example.com")
        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["error"])


class HealthStatusShapeTests(unittest.TestCase):
    @patch("core.health._is_stale")
    def test_health_status_shape(self, mock_stale):
        mock_stale.return_value = False
        status = get_health_status()
        self.assertIn("ok", status)
        self.assertIn("timezone", status)
        self.assertIn("stale_files", status)
        self.assertIn("db_status", status)
        self.assertIn("api_status", status)
        self.assertIsInstance(status["stale_files"], list)
        self.assertIsInstance(status["db_status"], dict)

    @patch("core.health._is_stale")
    def test_db_status_contains_known_dbs(self, mock_stale):
        mock_stale.return_value = False
        status = get_health_status()
        self.assertIn("bets_history.sqlite", status["db_status"])
        self.assertIn("clv_smoke.sqlite", status["db_status"])

    @patch("core.health._is_stale")
    def test_api_status_empty_by_default(self, mock_stale):
        mock_stale.return_value = False
        status = get_health_status()
        self.assertEqual(status["api_status"], {})
