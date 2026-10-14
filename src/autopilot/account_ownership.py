"""Offline server-side account/order ownership registry.

This is NOT an identity provider or public API. The account_id argument must
come from a verified hosted authentication session, never request JSON.
No emails, passwords, API credentials, payment methods or customer PII.
"""
import sqlite3


class OwnershipDenied(ValueError):
    pass


def _identifier(value, label):
    if (not isinstance(value, str) or not 1 <= len(value) <= 100
            or not all(ch.isascii() and (ch.isalnum() or ch in "-_") for ch in value)):
        raise OwnershipDenied(f"invalid {label}")
    return value


class AccountOwnership:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS customer_accounts (
                account_id TEXT PRIMARY KEY
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS owned_orders (
                order_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL REFERENCES customer_accounts(account_id)
            )""")

    def register_account(self, account_id: str):
        """Privileged provisioning; do not expose to untrusted customers."""
        account_id = _identifier(account_id, "account ID")
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO customer_accounts VALUES (?)", (account_id,))

    def bind_order(self, account_id: str, order_id: str):
        """Privileged binding after validated checkout identity/order ownership."""
        account_id = _identifier(account_id, "account ID")
        order_id = _identifier(order_id, "order ID")
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM customer_accounts WHERE account_id=?",
                          (account_id,)).fetchone() is None:
                raise OwnershipDenied("unknown account")
            if db.execute("SELECT 1 FROM checkout_orders WHERE order_id=?",
                          (order_id,)).fetchone() is None:
                raise OwnershipDenied("unknown checkout order")
            try:
                db.execute("INSERT INTO owned_orders VALUES (?,?)",
                           (order_id, account_id))
            except sqlite3.IntegrityError:
                raise OwnershipDenied("order already bound") from None

    def assert_owner(self, *, authenticated_account_id: str, order_id: str):
        """Call ONLY with an independently authenticated server session."""
        account_id = _identifier(authenticated_account_id, "account ID")
        order_id = _identifier(order_id, "order ID")
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT account_id FROM owned_orders WHERE order_id=?",
                             (order_id,)).fetchone()
        if row is None or row[0] != account_id:
            raise OwnershipDenied("order unavailable to this account")

    def issue_paid_invite(self, *, authenticated_account_id: str,
                          order_id: str, now=None, ttl_seconds=3600):
        """Account-scoped wrapper; not a public endpoint or full authentication."""
        self.assert_owner(authenticated_account_id=authenticated_account_id,
                          order_id=order_id)
        from .onboarding_invites import OnboardingInvites
        return OnboardingInvites(self.db_path).issue_for_paid_order(
            order_id, now=now, ttl_seconds=ttl_seconds,
        )

    def read_onboarding(self, *, authenticated_account_id: str, order_id: str):
        self.assert_owner(authenticated_account_id=authenticated_account_id,
                          order_id=order_id)
        from .onboarding_invites import OnboardingInvites
        return OnboardingInvites(self.db_path).status_for_trusted_operator(order_id)
