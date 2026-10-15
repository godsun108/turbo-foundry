"""Static signup preview cannot collect payment or submit customer data."""
import tempfile
import unittest
from pathlib import Path

from src.autopilot.commercial_catalog import OFFERS
from src.autopilot.signup_preview import render_signup_preview, write_signup_preview


class SignupPreviewTests(unittest.TestCase):
    def test_all_offers_and_fields_are_present(self):
        result = render_signup_preview()
        for offer in OFFERS:
            self.assertIn(offer.slug, result)
        for input_id in ("product", "business", "industry", "system", "goal", "problem"):
            self.assertIn('id="' + input_id + '"', result)
        self.assertIn('name="viewport"', result)
        self.assertIn('aria-live="polite"', result)

    def test_no_payment_or_data_submission_in_preview(self):
        html = render_signup_preview()
        self.assertIn("Checkout — not yet available", html)
        self.assertIn('disabled aria-disabled="true"', html)
        self.assertIn("No payment requested or service activated", html)
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage",
                          "navigator.sendBeacon", 'type="submit"', "<form", "https://"):
            self.assertNotIn(forbidden, html)

    def test_local_generation(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "preview.html"
            write_signup_preview(output)
            self.assertEqual(output.read_text(encoding="utf-8"),
                             render_signup_preview())


if __name__ == "__main__":
    unittest.main()
