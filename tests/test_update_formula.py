from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_formula.py"
spec = importlib.util.spec_from_file_location("update_formula", SCRIPT)
update_formula = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_formula)


class UpdateFormulaTest(unittest.TestCase):
    def test_release_url(self):
        self.assertEqual(
            update_formula.release_url("wizicer", "0.1.0"),
            "https://github.com/wizicer/mlx-stt/releases/download/v0.1.0/mlx-stt-0.1.0-macos-arm64.tar.gz",
        )

    def test_update_formula_text_replaces_release_fields(self):
        source = (Path(__file__).resolve().parents[1] / "Formula" / "mlx-stt.rb").read_text(encoding="utf-8")
        digest = "a" * 64

        rendered = update_formula.update_formula_text(
            source,
            version="0.2.0",
            sha256=digest,
            url="https://example.test/mlx-stt.tar.gz",
            owner="ExampleOwner",
        )

        self.assertIn('homepage "https://github.com/ExampleOwner/mlx-stt"', rendered)
        self.assertIn('version "0.2.0"', rendered)
        self.assertIn('url "https://example.test/mlx-stt.tar.gz"', rendered)
        self.assertIn('sha256 "' + digest + '"', rendered)

    def test_rejects_invalid_sha256(self):
        with self.assertRaises(ValueError):
            update_formula.update_formula_text(
                '  homepage "x"\n  version "0.1.0"\n  url "https://x"\n  sha256 "x"\n',
                version="0.1.0",
                sha256="not-a-digest",
                url="https://example.test/a.tar.gz",
                owner="wizicer",
            )


if __name__ == "__main__":
    unittest.main()
