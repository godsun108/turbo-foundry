"""Truthful customer-facing portfolio rendering, without network or PII."""
import tempfile
import unittest
from pathlib import Path

from src.autopilot.commercial_catalog import OFFERS
from src.autopilot.portfolio_page import render_portfolio, write_portfolio


class PortfolioPageTests(unittest.TestCase):
    def test_all_offers_labeled_and_no_live_claims(self):
        page = render_portfolio()
        for offer in OFFERS:
            self.assertIn(offer.title, page)
        self.assertEqual(page.count("Offline demonstration available"), 1)
        self.assertEqual(page.count("Concept — discovery only"), 4)
        self.assertIn("No live integrations", page)
        self.assertNotIn("<form", page)
        self.assertNotIn("<script", page)
        self.assertNotIn("https://", page)
        self.assertIn('name="viewport"', page)

    def test_static_file_export(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "portfolio.html"
            write_portfolio(path)
            self.assertEqual(path.read_text(encoding="utf-8"), render_portfolio())


if __name__ == "__main__":
    unittest.main()
