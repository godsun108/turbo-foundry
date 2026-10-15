"""The static export makes no requests, charges, or service promises."""
import json
from pathlib import Path
import tempfile
import unittest

from src.autopilot.static_preview_build import build_static_preview


class StaticPreviewBuildTests(unittest.TestCase):
    def test_exports_whole_public_bundle_without_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = build_static_preview(Path(tmp) / "site")
            names = {p.name for p in files}
            self.assertEqual(names, {
                "index.html", "offers.json", "readiness.json", "robots.txt", ".nojekyll"
            })
            page = (Path(tmp) / "site" / "index.html").read_text()
            self.assertIn("Checkout — not yet available", page)
            self.assertIn('disabled aria-disabled="true"', page)
            self.assertNotIn("fetch(", page)
            self.assertNotIn("XMLHttpRequest", page)
            self.assertNotIn("<form", page)
            self.assertNotIn('type="submit"', page)
            readiness = json.loads((Path(tmp) / "site" / "readiness.json").read_text())
            self.assertFalse(readiness["payment_collection"])
            self.assertFalse(readiness["signup_submission"])
            self.assertFalse(readiness["live_messaging"])
            self.assertEqual(len(json.loads((Path(tmp) / "site" / "offers.json").read_text())), 5)

    def test_deterministic_without_any_external_services(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = build_static_preview(Path(tmp) / "site")
            original = {p.name: p.read_bytes() for p in first}
            second = build_static_preview(Path(tmp) / "site")
            self.assertEqual(original, {p.name: p.read_bytes() for p in second})


if __name__ == "__main__":
    unittest.main()
