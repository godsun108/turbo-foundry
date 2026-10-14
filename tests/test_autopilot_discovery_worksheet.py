"""A prospect can download a short worksheet without transmission."""
import unittest
from src.autopilot.signup_preview import render_signup_preview


class DiscoveryWorksheetTests(unittest.TestCase):
    def test_local_export_without_collection_or_checkout(self):
        html = render_signup_preview()
        self.assertIn('id="export" disabled', html)
        self.assertIn("FOUNDRY — DISCOVERY WORKSHEET (NOT AN ORDER)", html)
        self.assertIn("new Blob([worksheet", html)
        self.assertIn("URL.createObjectURL(blob)", html)
        self.assertIn("URL.revokeObjectURL(url)", html)
        self.assertIn("No purchase or service activation has occurred", html)
        self.assertIn('disabled aria-disabled="true"', html)
        for forbidden in ("fetch(", "XMLHttpRequest", "navigator.sendBeacon",
                          "localStorage", "sessionStorage", "<form",
                          'type="submit"'):
            self.assertNotIn(forbidden, html)

    def test_only_synthetic_preview_fields_exported(self):
        html = render_signup_preview()
        for field in ("Business:", "Automation:", "Problem:", "Industry:",
                      "Current systems:", "Goal:"):
            self.assertIn(field, html)
        self.assertIn("Do not enter client records", html)
        self.assertIn("worksheet stays on your device", html)


if __name__ == "__main__":
    unittest.main()
