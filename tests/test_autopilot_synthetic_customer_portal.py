"""Offline customer portal order isolation, revocation and expiry tests."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import sqlite3
import unittest

from src.autopilot.synthetic_customer_portal import (
    SyntheticCustomerPortal, PortalDenied,
)

NOW = datetime(2026, 10, 14, 20, tzinfo=timezone.utc)


class CustomerPortalTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = str(Path(tmp.name) / "portal.sqlite")
        self.portal = SyntheticCustomerPortal(self.db)
        self.portal.fulfillment.checkout.register_test_order(
            order_id="order-a", session_id="cs_test_a", amount_cents=100)
        self.portal.fulfillment.checkout.register_test_order(
            order_id="order-b", session_id="cs_test_b", amount_cents=100)
        self.portal.ownership.register_account("shop-a")
        self.portal.ownership.register_account("shop-b")
        self.portal.ownership.bind_order("shop-a", "order-a")
        self.portal.ownership.bind_order("shop-b", "order-b")

    def test_only_owned_orders_are_readable(self):
        token = self.portal.issue_trusted_fixture(account_id="shop-a", now=NOW)
        result = self.portal.order_status(token=token, order_id="order-a", now=NOW)
        self.assertEqual(result["order_id"], "order-a")
        self.assertIsNone(result["synthetic_state"])
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["service_delivered_to_customer"])
        with self.assertRaises(PortalDenied):
            self.portal.order_status(token=token, order_id="order-b", now=NOW)
        with self.assertRaises(PortalDenied):
            self.portal.order_status(token=token, order_id="unknown", now=NOW)
        with sqlite3.connect(self.db) as db:
            digest = db.execute(
                "SELECT token_digest FROM synthetic_customer_sessions").fetchone()[0]
        self.assertNotEqual(digest, token)

    def test_revocation_expiry_and_no_replay(self):
        token = self.portal.issue_trusted_fixture(
            account_id="shop-a", now=NOW, ttl_seconds=5)
        self.assertEqual(self.portal.order_status(
            token=token, order_id="order-a", now=NOW + timedelta(seconds=4)
        )["order_id"], "order-a")
        with self.assertRaises(PortalDenied):
            self.portal.order_status(
                token=token, order_id="order-a", now=NOW + timedelta(seconds=5))
        fresh = self.portal.issue_trusted_fixture(account_id="shop-a", now=NOW)
        self.assertTrue(self.portal.revoke(fresh))
        self.assertFalse(self.portal.revoke(fresh))
        with self.assertRaises(PortalDenied):
            self.portal.order_status(token=fresh, order_id="order-a", now=NOW)

    def test_invalid_accounts_tokens_and_store_failure(self):
        with self.assertRaises(PortalDenied):
            self.portal.issue_trusted_fixture(account_id="nobody", now=NOW)
        with self.assertRaises(PortalDenied):
            self.portal.issue_trusted_fixture(account_id="shop-a", now=NOW,
                                              ttl_seconds=True)
        for token in ("", "0" * 64, "x" * 64, None):
            with self.subTest(token=token), self.assertRaises(PortalDenied):
                self.portal.order_status(token=token, order_id="order-a", now=NOW)
        token = self.portal.issue_trusted_fixture(account_id="shop-a", now=NOW)
        with sqlite3.connect(self.db) as db:
            db.execute("DROP TABLE synthetic_customer_sessions")
        with self.assertRaises(PortalDenied):
            self.portal.order_status(token=token, order_id="order-a", now=NOW)

    def test_no_customer_mutation_interface(self):
        for name in ("create_checkout", "activate", "send_sms", "charge", "update_order"):
            self.assertFalse(hasattr(self.portal, name))


if __name__ == "__main__":
    unittest.main()
