"""Synthetic business signup state-machine tests: nothing can charge or activate."""
import unittest
from dataclasses import replace

from src.autopilot.customer_fulfillment import (
    Order, PaymentEvidence, State, TransitionError,
    accept_scope, authorize_test_checkout, record_verified_payment,
    complete_onboarding, approve_fulfillment, activate,
)


class CustomerFulfillmentTests(unittest.TestCase):
    def setUp(self):
        self.order = Order("test-order-001", "missed-call-recovery",
                           expected_amount_cents=25000)
        self.receipt = PaymentEvidence(
            "evt_fixture", "cs_test_fixture", "pi_fixture", 25000, "usd", True
        )

    def test_default_does_not_create_checkout_or_activation(self):
        with self.assertRaises(TransitionError):
            authorize_test_checkout(self.order, checkout_feature_enabled=True)
        with self.assertRaises(TransitionError):
            activate(self.order, deployment_verified=True)

    def test_complete_synthetic_happy_path_requires_every_gate(self):
        scoped = accept_scope(self.order, agreement_accepted=True)
        with self.assertRaises(TransitionError):
            authorize_test_checkout(scoped, checkout_feature_enabled=False)
        checkout = authorize_test_checkout(scoped, checkout_feature_enabled=True)
        with self.assertRaises(TransitionError):
            record_verified_payment(checkout, self.receipt, trusted_webhook=False)
        paid = record_verified_payment(checkout, self.receipt, trusted_webhook=True)
        self.assertEqual(paid.state, State.PAID_AWAITING_ONBOARDING)
        with self.assertRaises(TransitionError):
            activate(paid, deployment_verified=True)
        with self.assertRaises(TransitionError):
            complete_onboarding(paid, fields_validated=True,
                                authorized_customer=False)
        onboarding = complete_onboarding(paid, fields_validated=True,
                                         authorized_customer=True)
        with self.assertRaises(TransitionError):
            approve_fulfillment(onboarding, release_gate_verified=False,
                                operator_approved=True)
        ready = approve_fulfillment(onboarding, release_gate_verified=True,
                                    operator_approved=True)
        with self.assertRaises(TransitionError):
            activate(ready, deployment_verified=False)
        self.assertEqual(activate(ready, deployment_verified=True).state, State.ACTIVE)

    def test_replay_and_payment_mismatch_denied(self):
        scoped = accept_scope(self.order, agreement_accepted=True)
        checkout = authorize_test_checkout(scoped, checkout_feature_enabled=True)
        for mismatch in (
            replace(self.receipt, paid=False),
            replace(self.receipt, amount_cents=24999),
            replace(self.receipt, currency="eur"),
            replace(self.receipt, checkout_session_id=""),
            replace(self.receipt, payment_intent_id=""),
            replace(self.receipt, amount_cents=True),
        ):
            with self.subTest(mismatch=mismatch), self.assertRaises(TransitionError):
                record_verified_payment(checkout, mismatch, trusted_webhook=True)
        paid = record_verified_payment(checkout, self.receipt, trusted_webhook=True)
        with self.assertRaises(TransitionError):
            record_verified_payment(paid, self.receipt, trusted_webhook=True)

    def test_no_self_approval_via_skipped_states(self):
        fake = replace(self.order, state=State.ONBOARDING_REVIEW,
                       onboarding_complete=True)
        with self.assertRaises(TransitionError):
            approve_fulfillment(fake, release_gate_verified=True,
                                operator_approved=True)


if __name__ == "__main__":
    unittest.main()
