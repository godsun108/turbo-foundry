"""Offline account-order tenancy controls; no login or Stripe network."""
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from src.autopilot.account_ownership import AccountOwnership, OwnershipDenied
from src.autopilot.stripe_test_checkout import TestCheckoutLedger

NOW = datetime(2026, 10, 14, tzinfo=timezone.utc)


class AccountOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "orders.db")
        self.checkout = TestCheckoutLedger(self.path)
        self.checkout.register_test_order(
            order_id="order-alpha", session_id="cs_test_alpha",
            amount_cents=20000)
        self.checkout.register_test_order(
            order_id="order-beta", session_id="cs_test_beta",
            amount_cents=30000)
        self.owners = AccountOwnership(self.path)
        self.owners.register_account("account-alpha")
        self.owners.register_account("account-beta")
        self.owners.bind_order("account-alpha", "order-alpha")
        self.owners.bind_order("account-beta", "order-beta")

    def tearDown(self):
        self.tmp.cleanup()

    def test_cross_tenant_read_and_invite_denied(self):
        with self.assertRaises(OwnershipDenied):
            self.owners.read_onboarding(
                authenticated_account_id="account-alpha",
                order_id="order-beta")
        with self.assertRaises(OwnershipDenied):
            self.owners.issue_paid_invite(
                authenticated_account_id="account-alpha",
                order_id="order-beta", now=NOW)

    def test_correct_account_must_still_have_verified_payment(self):
        self.owners.assert_owner(authenticated_account_id="account-alpha",
                                 order_id="order-alpha")
        with self.assertRaises(ValueError):
            self.owners.issue_paid_invite(
                authenticated_account_id="account-alpha",
                order_id="order-alpha", now=NOW)
        state = self.owners.read_onboarding(
            authenticated_account_id="account-beta",
            order_id="order-beta")
        self.assertFalse(state.completed)

    def test_order_binding_cannot_be_stolen(self):
        with self.assertRaises(OwnershipDenied):
            self.owners.bind_order("account-beta", "order-alpha")
        with self.assertRaises(OwnershipDenied):
            self.owners.bind_order("unknown", "order-alpha")
        with self.assertRaises(OwnershipDenied):
            self.owners.bind_order("account-alpha", "unknown")

    def test_reopened_registry_keeps_tenant_ownership(self):
        reopened = AccountOwnership(self.path)
        reopened.assert_owner(authenticated_account_id="account-alpha",
                              order_id="order-alpha")
        with self.assertRaises(OwnershipDenied):
            reopened.assert_owner(authenticated_account_id="account-beta",
                                  order_id="order-alpha")

    def test_invalid_identifiers_rejected(self):
        for unsafe in ("", "../evil", "a@b.com", "hello world", "x" * 101):
            with self.subTest(unsafe=unsafe), self.assertRaises(OwnershipDenied):
                self.owners.assert_owner(
                    authenticated_account_id=unsafe,order_id="order-alpha")


if __name__ == "__main__":
    unittest.main()
