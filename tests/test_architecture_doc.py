from __future__ import annotations

import unittest
from pathlib import Path


class TestArchitectureDocument(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path("ARCHITECTURE.md")

    def test_exists(self) -> None:
        self.assertTrue(self.path.exists(), "ARCHITECTURE.md no existe")

    def test_has_key_sections(self) -> None:
        text = self.path.read_text(encoding="utf-8")
        required = [
            "# ARCHITECTURE",
            "## Propósito",
            "## Regla principal",
            "## Flujo de datos",
            "### 1) Providers",
            "### 2) Scheduler",
            "### 3) Cache local",
            "### 4) Repositorios",
            "### 5) Servicios",
            "### 6) Handlers",
            "### 7) Telegram UI",
            "### 8) Analítica",
            "### 9) ML",
            "### 10) Bankroll",
            "## Orden de implementación",
            "## Qué debe hacer cada archivo",
            "## Qué no debe pasar",
            "## Regla final",
        ]
        for item in required:
            self.assertIn(item, text, f"Falta sección: {item}")

    def test_has_no_placeholder_text(self) -> None:
        text = self.path.read_text(encoding="utf-8")
        forbidden = ["TODO", "TBD", "lorem ipsum"]
        for item in forbidden:
            self.assertNotIn(item.lower(), text.lower(), f"Encontrado placeholder: {item}")


if __name__ == "__main__":
    unittest.main()
