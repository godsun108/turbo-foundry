"""Offline order-to-delivery rehearsal: NEVER a customer activation system.

Requires an existing test-paid order, owned account and completed onboarding.
All transitions are local operator simulations; no provider or billing access.
"""
import sqlite3
from .account_ownership import AccountOwnership, OwnershipDenied
from .onboarding_invites import OnboardingInvites
from .stripe_test_checkout import TestCheckoutLedger
from .universal_business_templates import configure_business


class FulfillmentDenied(ValueError):
    pass


class SyntheticFulfillment:
    STATES = ("prepared", "reviewed", "simulated_delivered", "stopped")

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.checkout = TestCheckoutLedger(db_path)
        self.ownership = AccountOwnership(db_path)
        self.onboarding = OnboardingInvites(db_path)
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS synthetic_fulfillment (
                order_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                template_slug TEXT NOT NULL,
                workflow_slug TEXT NOT NULL,
                state TEXT NOT NULL,
                CHECK(state IN ('prepared','reviewed','simulated_delivered','stopped'))
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS synthetic_fulfillment_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL, from_state TEXT, to_state TEXT NOT NULL,
                reason TEXT NOT NULL
            )""")

    def state(self, order_id):
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT state FROM synthetic_fulfillment WHERE order_id=?",
                             (order_id,)).fetchone()
        return row[0] if row else None

    def prepare(self, *, order_id, authenticated_account_id, industry, workflow):
        # The account_id MUST be from a trusted caller; not browser input.
        try:
            self.ownership.assert_owner(
                authenticated_account_id=authenticated_account_id, order_id=order_id)
        except OwnershipDenied as exc:
            raise FulfillmentDenied("unverified account ownership") from exc
        if self.checkout.get_status(order_id) != "paid":
            raise FulfillmentDenied("test order not paid")
        onboarding = self.onboarding.status_for_trusted_operator(order_id)
        if not onboarding.completed or onboarding.industry != industry:
            raise FulfillmentDenied("onboarding missing or industry mismatch")
        try:
            configure_business("fictional-" + authenticated_account_id,
                               industry, (workflow,))
        except ValueError as exc:
            raise FulfillmentDenied("unapproved industry or workflow") from exc
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("""INSERT INTO synthetic_fulfillment
                (order_id,account_id,template_slug,workflow_slug,state)
                VALUES (?,?,?,?,'prepared')""",
                (order_id, authenticated_account_id, industry, workflow))
            db.execute("""INSERT INTO synthetic_fulfillment_events
                (order_id,from_state,to_state,reason)
                VALUES (?,NULL,'prepared','fixture_order_and_onboarding_checked')""",
                (order_id,))

    def transition(self, *, order_id, authenticated_account_id, expected_state,
                   next_state, reason):
        transitions = {
            ("prepared", "reviewed"),
            ("reviewed", "simulated_delivered"),
            ("prepared", "stopped"),
            ("reviewed", "stopped"),
            ("simulated_delivered", "stopped"),
        }
        if ((expected_state, next_state) not in transitions
                or not isinstance(reason, str) or not 1 <= len(reason) <= 200
                or any(ord(ch) < 32 for ch in reason)):
            raise FulfillmentDenied("invalid synthetic transition")
        try:
            self.ownership.assert_owner(
                authenticated_account_id=authenticated_account_id, order_id=order_id)
        except OwnershipDenied as exc:
            raise FulfillmentDenied("unverified account ownership") from exc
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT state,account_id FROM synthetic_fulfillment
                WHERE order_id=?""", (order_id,)).fetchone()
            if row is None or row != (expected_state, authenticated_account_id):
                raise FulfillmentDenied("state or owner mismatch")
            if self.checkout.get_status(order_id) != "paid":
                raise FulfillmentDenied("test payment no longer verified")
            if not self.onboarding.status_for_trusted_operator(order_id).completed:
                raise FulfillmentDenied("onboarding incomplete")
            db.execute("""UPDATE synthetic_fulfillment SET state=?
                WHERE order_id=? AND state=?""", (next_state, order_id, expected_state))
            db.execute("""INSERT INTO synthetic_fulfillment_events
                (order_id,from_state,to_state,reason) VALUES (?,?,?,?)""",
                (order_id, expected_state, next_state, reason))

    def status_report(self, order_id):
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("""SELECT template_slug,workflow_slug,state
                FROM synthetic_fulfillment WHERE order_id=?""",
                             (order_id,)).fetchone()
        return {
            "order_id": order_id,
            "industry": row[0] if row else None,
            "workflow": row[1] if row else None,
            "synthetic_state": row[2] if row else None,
            "live_customer_activated": False,
            "service_delivered_to_customer": False,
            "real_payment_processed": False,
            "production_ready": False,
        }
