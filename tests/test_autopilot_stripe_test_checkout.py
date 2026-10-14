"""No-network Stripe-style test event signatures and durable order checks."""
import hashlib
import hmac
import json
from pathlib import Path
import tempfile
import unittest

from src.autopilot.stripe_test_checkout import (
    TestCheckoutLedger, WebhookRejected, verify_stripe_signature,
)

SECRET = "whsec_synthetic_testing_only"
T = 1792000000


def signed(event, timestamp=T, secret=SECRET):
    raw = json.dumps(event).encode()
    signature = hmac.new(secret.encode(), str(timestamp).encode()+b"."+raw,
                         hashlib.sha256).hexdigest()
    return raw, f"t={timestamp},v1={signature}"


def paid_event(**changes):
    session = {
        "id": "cs_test_fixture_001", "payment_intent": "pi_fixture_001",
        "amount_total": 25000, "currency": "usd", "payment_status": "paid",
        "mode": "payment",
    }
    session.update(changes)
    return {"id": "evt_fixture_001", "livemode": False,
            "type": "checkout.session.completed",
            "data": {"object": session}}


class StripeTestCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "orders.db")
        self.ledger = TestCheckoutLedger(self.path)
        self.ledger.register_test_order(order_id="order-001",
                                        session_id="cs_test_fixture_001",
                                        amount_cents=25000)

    def tearDown(self):
        self.tmp.cleanup()

    def consume(self, event, *, stamp=T, secret=SECRET):
        payload, header = signed(event, stamp, secret)
        return self.ledger.consume_signed_event(
            payload=payload, signature_header=header,
            webhook_secret=SECRET, now=T,
        )

    def test_verified_paid_event_transitions_once_and_survives_restart(self):
        self.assertEqual(self.ledger.get_status("order-001"), "pending")
        self.assertTrue(self.consume(paid_event()))
        reopened = TestCheckoutLedger(self.path)
        self.assertEqual(reopened.get_status("order-001"), "paid")
        self.assertFalse(self.consume(paid_event()))

    def test_unsigned_or_stale_payload_cannot_mark_paid(self):
        event = paid_event()
        with self.assertRaises(WebhookRejected):
            self.consume(event, secret="whsec_wrong")
        with self.assertRaises(WebhookRejected):
            self.consume(event, stamp=T-301)
        self.assertEqual(self.ledger.get_status("order-001"), "pending")

    def test_bad_amount_payment_status_and_mode_rejected(self):
        for changes in (
            {"amount_total": 24999}, {"payment_status": "unpaid"},
            {"mode": "subscription"}, {"id": "cs_test_wrong"},
            {"payment_intent": None},
        ):
            with self.subTest(changes=changes), self.assertRaises(WebhookRejected):
                self.consume(paid_event(**changes))
        self.assertEqual(self.ledger.get_status("order-001"), "pending")

    def test_live_events_rejected_and_irrelevant_events_ignored(self):
        event = paid_event()
        event["livemode"] = True
        with self.assertRaises(WebhookRejected):
            self.consume(event)
        event["livemode"] = False
        event["type"] = "customer.created"
        self.assertFalse(self.consume(event))
        self.assertEqual(self.ledger.get_status("order-001"), "pending")

    def test_local_registered_session_required(self):
        another = TestCheckoutLedger(str(Path(self.tmp.name) / "empty.db"))
        payload, header = signed(paid_event())
        with self.assertRaises(WebhookRejected):
            another.consume_signed_event(payload=payload,signature_header=header,
                                         webhook_secret=SECRET,now=T)

    def test_no_fake_self_signed_browser_status(self):
        with self.assertRaises(WebhookRejected):
            verify_stripe_signature(b'{"payment_status":"paid"}',
                                    "t=1792000000,v1=fake", SECRET, now=T)
        self.assertEqual(self.ledger.get_status("order-001"), "pending")


if __name__ == "__main__":
    unittest.main()
