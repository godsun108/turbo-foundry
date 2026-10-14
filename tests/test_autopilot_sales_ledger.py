"""Sales records are local and require evidence, never assumed revenue."""
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.autopilot.sales_ledger import SalesLedger, STAGES


class SalesLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "prospects.sqlite")
        self.ledger = SalesLedger(self.path)
        self.ledger.add_prospect("business-001", "HVAC", "Publicly identified business")

    def tearDown(self):
        self.temp.cleanup()

    def _advance_to(self, stage):
        for next_stage in STAGES[1:]:
            self.ledger.advance("business-001", next_stage, "Human-confirmed event")
            if next_stage == stage:
                return

    def test_new_prospect_has_no_sales_or_revenue(self):
        summary = self.ledger.summary()
        self.assertEqual(summary.collected_revenue_usd, Decimal("0"))
        self.assertEqual(dict(summary.stages)["researched"], 1)
        self.assertEqual(dict(summary.stages)["paying"], 0)

    def test_cannot_jump_stages_or_mark_paying_without_collected_payment(self):
        with self.assertRaises(ValueError):
            self.ledger.advance("business-001", "paying", "unsupported")
        self._advance_to("pilot_authorized")
        with self.assertRaises(ValueError):
            self.ledger.advance("business-001", "paying", "invoice only")
        self.assertEqual(self.ledger.summary().collected_revenue_usd, Decimal("0"))

    def test_payment_reference_required_after_authorization_and_unique(self):
        with self.assertRaises(ValueError):
            self.ledger.record_collected_payment(
                "business-001", "settled-001", "200.00", "verified statement")
        self._advance_to("pilot_authorized")
        self.ledger.record_collected_payment(
            "business-001", "settled-001", "200.15", "Operator reviewed actual settlement")
        with self.assertRaises(Exception):
            self.ledger.record_collected_payment(
                "business-001", "settled-001", "200.15", "Duplicate")
        self.assertEqual(self.ledger.summary().collected_revenue_usd,
                         Decimal("200.15"))
        self.ledger.advance("business-001", "paying", "Payment reconciled")
        self.assertEqual(dict(self.ledger.summary().stages)["paying"], 1)

    def test_invalid_amounts_and_notes_rejected_without_state_change(self):
        self._advance_to("pilot_authorized")
        for amount in ("-1", "0", "1.001", "NaN", "Infinity", "invalid", True):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.ledger.record_collected_payment(
                    "business-001", "settlement", amount, "verified")
        with self.assertRaises(ValueError):
            self.ledger.advance("business-001", "paying", "")
        self.assertEqual(self.ledger.summary().collected_revenue_usd, Decimal("0"))

    def test_reopen_retains_stages_but_never_infers_payment(self):
        self._advance_to("qualified")
        reopened = SalesLedger(self.path)
        self.assertEqual(dict(reopened.summary().stages)["qualified"], 1)
        self.assertEqual(reopened.summary().collected_revenue_usd, Decimal("0"))


if __name__ == "__main__":
    unittest.main()
