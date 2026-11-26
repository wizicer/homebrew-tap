from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_formula.py"
spec = importlib.util.spec_from_file_location("update_formula", SCRIPT)
update_formula = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_formula)

MACOS15_DIGEST = "a" * 64
MACOS26_DIGEST = "b" * 64
MACOS15_URL = "https://example.test/mlx-stt-macos15.tar.gz"
MACOS26_URL = "https://example.test/mlx-stt-macos26.tar.gz"


def render(source, **overrides):
    values = {
        "version": "0.2.0",
        "sha256_macos15": MACOS15_DIGEST,
        "url_macos15": MACOS15_URL,
        "sha256_macos26": MACOS26_DIGEST,
        "url_macos26": MACOS26_URL,
        "owner": "ExampleOwner",
    }
    values.update(overrides)
    return update_formula.update_formula_text(source, **values)


class UpdateFormulaTest(unittest.TestCase):
    def test_release_url(self):
        self.assertEqual(
            update_formula.release_url("wizicer", "0.1.1", "26"),
            "https://github.com/wizicer/mlx-stt/releases/download/v0.1.1/mlx-stt-0.1.1-macos26-arm64.tar.gz",
        )

    def test_update_formula_text_replaces_release_fields(self):
        source = (Path(__file__).resolve().parents[1] / "Formula" / "mlx-stt.rb").read_text(encoding="utf-8")

        rendered = render(source)

        self.assertIn('homepage "https://github.com/ExampleOwner/mlx-stt"', rendered)
        self.assertIn('version "0.2.0"', rendered)
        self.assertIn('url "' + MACOS15_URL + '"', rendered)
        self.assertIn('sha256 "' + MACOS15_DIGEST + '"', rendered)
        self.assertIn('url "' + MACOS26_URL + '"', rendered)
        self.assertIn('sha256 "' + MACOS26_DIGEST + '"', rendered)

    def test_rejects_invalid_sha256(self):
        source = (Path(__file__).resolve().parents[1] / "Formula" / "mlx-stt.rb").read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            render(source, sha256_macos26="not-a-digest")


if __name__ == "__main__":
    unittest.main()
