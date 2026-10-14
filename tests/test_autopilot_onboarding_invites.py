"""Test paid-order onboarding invite scope, expiry, token secrecy and replay."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.autopilot.onboarding_invites import OnboardingInvites, OnboardingDenied
from src.autopilot.stripe_test_checkout import TestCheckoutLedger
from tests.test_autopilot_stripe_test_checkout import signed, paid_event, SECRET, T

NOW = datetime.fromtimestamp(T, tz=timezone.utc)


class OnboardingInviteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp.name) / "onboarding.sqlite")
        self.checkout = TestCheckoutLedger(self.db_path)
        self.checkout.register_test_order(
            order_id="test-order", session_id="cs_test_fixture_001",
            amount_cents=25000,
        )
        self.invites = OnboardingInvites(self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def mark_paid(self):
        payload, signature = signed(paid_event())
        self.assertTrue(self.checkout.consume_signed_event(
            payload=payload, signature_header=signature,
            webhook_secret=SECRET, now=T,
        ))

    def test_unpaid_order_cannot_receive_invite(self):
        with self.assertRaises(OnboardingDenied):
            self.invites.issue_for_paid_order("test-order", now=NOW)
        self.assertFalse(self.invites.status_for_trusted_operator("test-order").completed)

    def test_paid_order_one_time_token_and_no_plaintext_secret(self):
        self.mark_paid()
        token = self.invites.issue_for_paid_order("test-order", now=NOW)
        self.assertGreaterEqual(len(token), 32)
        with sqlite3.connect(self.db_path) as db:
            hashes = [row[0] for row in db.execute("SELECT token_hash FROM onboarding_invites")]
        self.assertNotIn(token, hashes)
        self.assertEqual(self.invites.submit(
            token, business_name="Synthetic Shop", industry="HVAC",
            workflow_goal="Respond to eligible missed inquiries", now=NOW,
        ), "test-order")
        state = OnboardingInvites(self.db_path).status_for_trusted_operator("test-order")
        self.assertTrue(state.completed)
        self.assertEqual(state.business_name, "Synthetic Shop")
        with self.assertRaises(OnboardingDenied):
            self.invites.submit(token,business_name="Again", industry="HVAC",
                                workflow_goal="Replay", now=NOW)
        with self.assertRaises(OnboardingDenied):
            self.invites.issue_for_paid_order("test-order", now=NOW)

    def test_expired_token_and_wrong_token_denied(self):
        self.mark_paid()
        token = self.invites.issue_for_paid_order("test-order", now=NOW, ttl_seconds=60)
        for attempt, when in ((token, NOW+timedelta(seconds=61)),
                              ("arbitrary-token", NOW)):
            with self.subTest(attempt=attempt), self.assertRaises(OnboardingDenied):
                self.invites.submit(attempt,business_name="Synthetic Shop",
                                    industry="HVAC",workflow_goal="Follow up",now=when)
        self.assertFalse(self.invites.status_for_trusted_operator("test-order").completed)

    def test_invalid_input_does_not_consume_invite(self):
        self.mark_paid()
        token = self.invites.issue_for_paid_order("test-order", now=NOW)
        with self.assertRaises(OnboardingDenied):
            self.invites.submit(token,business_name="",industry="HVAC",
                                workflow_goal="Follow up",now=NOW)
        self.assertEqual(self.invites.submit(
            token,business_name="Synthetic",industry="HVAC",
            workflow_goal="Follow up",now=NOW), "test-order")

    def test_invalid_ttl_rejected(self):
        self.mark_paid()
        with self.assertRaises(OnboardingDenied):
            self.invites.issue_for_paid_order("test-order", now=NOW,ttl_seconds=True)


if __name__ == "__main__":
    unittest.main()
