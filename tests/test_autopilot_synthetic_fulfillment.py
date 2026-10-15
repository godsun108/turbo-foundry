"""End-to-end synthetic purchase, onboarding and fulfillment tests."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import hmac
import json
import tempfile
import unittest

from src.autopilot.synthetic_fulfillment import SyntheticFulfillment, FulfillmentDenied

T = 1792000000
NOW = datetime.fromtimestamp(T, timezone.utc)
SECRET = "whsec_local_fixture_not_real"


class FulfillmentTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.system = SyntheticFulfillment(str(Path(tmp.name) / "fixture.sqlite"))
        self.system.checkout.register_test_order(
            order_id="order-1", session_id="cs_test_fixture-1", amount_cents=25000)
        self.system.ownership.register_account("shop-1")
        self.system.ownership.register_account("shop-2")
        self.system.ownership.bind_order("shop-1", "order-1")

    def pay(self):
        event = {"id": "evt_fixture-1", "livemode": False,
                 "type": "checkout.session.completed",
                 "data": {"object": {"id": "cs_test_fixture-1",
                     "payment_intent": "pi_fixture-1",
                     "amount_total": 25000, "currency": "usd",
                     "payment_status": "paid", "mode": "payment"}}}
        data = json.dumps(event).encode()
        signature = hmac.new(SECRET.encode(),
                             str(T).encode() + b"." + data, hashlib.sha256).hexdigest()
        return self.system.checkout.consume_signed_event(
            payload=data, signature_header="t=%s,v1=%s" % (T, signature),
            webhook_secret=SECRET, now=T)

    def onboard(self, industry="hvac"):
        token = self.system.ownership.issue_paid_invite(
            authenticated_account_id="shop-1", order_id="order-1", now=NOW)
        self.system.onboarding.submit(token, business_name="Fictional Heating",
            industry=industry, workflow_goal="Synthetic missed calls", now=NOW)

    def test_full_rehearsal_and_stop(self):
        self.assertTrue(self.pay())
        self.assertFalse(self.pay())
        self.onboard()
        self.system.prepare(order_id="order-1", authenticated_account_id="shop-1",
                            industry="hvac", workflow="missed-call-recovery")
        self.system.transition(order_id="order-1", authenticated_account_id="shop-1",
            expected_state="prepared", next_state="reviewed", reason="fictional approval")
        self.system.transition(order_id="order-1", authenticated_account_id="shop-1",
            expected_state="reviewed", next_state="simulated_delivered",
            reason="offline read-only fixture accepted")
        report = self.system.status_report("order-1")
        self.assertEqual(report["synthetic_state"], "simulated_delivered")
        self.assertFalse(report["service_delivered_to_customer"])
        self.assertFalse(report["real_payment_processed"])
        self.system.transition(order_id="order-1", authenticated_account_id="shop-1",
            expected_state="simulated_delivered", next_state="stopped",
            reason="operator stopped fictional service")
        self.assertEqual(self.system.state("order-1"), "stopped")

    def test_unpaid_or_no_onboarding_denied(self):
        with self.assertRaises(FulfillmentDenied):
            self.system.prepare(order_id="order-1", authenticated_account_id="shop-1",
                                industry="hvac", workflow="missed-call-recovery")
        self.pay()
        with self.assertRaises(FulfillmentDenied):
            self.system.prepare(order_id="order-1", authenticated_account_id="shop-1",
                                industry="hvac", workflow="missed-call-recovery")

    def test_wrong_owner_and_workflow_denied(self):
        self.pay()
        self.onboard()
        for account, industry, workflow in (
            ("shop-2", "hvac", "missed-call-recovery"),
            ("shop-1", "landscaping", "missed-call-recovery"),
            ("shop-1", "hvac", "unapproved-sms"),
        ):
            with self.subTest(account=account, industry=industry, workflow=workflow):
                with self.assertRaises(FulfillmentDenied):
                    self.system.prepare(order_id="order-1",
                        authenticated_account_id=account, industry=industry,
                        workflow=workflow)

    def test_invalid_and_duplicate_transitions_denied(self):
        self.pay()
        self.onboard()
        self.system.prepare(order_id="order-1", authenticated_account_id="shop-1",
                            industry="hvac", workflow="missed-call-recovery")
        with self.assertRaises(Exception):
            self.system.prepare(order_id="order-1", authenticated_account_id="shop-1",
                                industry="hvac", workflow="missed-call-recovery")
        for account, old, new in (
            ("shop-2", "prepared", "reviewed"),
            ("shop-1", "reviewed", "simulated_delivered"),
            ("shop-1", "prepared", "live"),
        ):
            with self.assertRaises(FulfillmentDenied):
                self.system.transition(order_id="order-1",
                    authenticated_account_id=account, expected_state=old,
                    next_state=new, reason="fixture only")
        self.assertEqual(self.system.state("order-1"), "prepared")


if __name__ == "__main__":
    unittest.main()
