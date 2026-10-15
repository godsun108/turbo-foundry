"""Read-only test customer portal boundary for Foundry fulfillment rehearsals.

No HTTP routes or public authentication. Trusted offline provisioning issues an
opaque expiring capability; account identity is resolved from the stored digest,
never from caller JSON. Do not expose provisioning to untrusted code.
"""
import hashlib
import secrets
import sqlite3
from datetime import datetime, timezone, timedelta

from .account_ownership import AccountOwnership, OwnershipDenied, _identifier
from .synthetic_fulfillment import SyntheticFulfillment


class PortalDenied(ValueError):
    pass


def _clock(now):
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise PortalDenied("timezone-aware trusted clock required")
    return int(now.timestamp())


def _digest(token):
    if not isinstance(token, str) or len(token) != 64:
        return None
    try:
        raw = bytes.fromhex(token)
    except ValueError:
        return None
    return hashlib.sha256(raw).hexdigest()


class SyntheticCustomerPortal:
    """Offline trusted boundary; never a real user identity provider."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.ownership = AccountOwnership(db_path)
        self.fulfillment = SyntheticFulfillment(db_path)
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS synthetic_customer_sessions (
                token_digest TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0 CHECK(revoked IN (0,1))
            )""")

    def issue_trusted_fixture(self, *, account_id, now, ttl_seconds=600):
        """Privileged test operator only; issuance is NOT login/authentication."""
        try:
            account_id = _identifier(account_id, "account ID")
            when = _clock(now)
        except (OwnershipDenied, PortalDenied) as exc:
            raise PortalDenied("invalid trusted account") from exc
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 900:
            raise PortalDenied("invalid lifetime")
        with sqlite3.connect(self.db_path) as db:
            exists = db.execute(
                "SELECT 1 FROM customer_accounts WHERE account_id=?",
                (account_id,)).fetchone()
        if exists is None:
            raise PortalDenied("unknown test account")
        token = secrets.token_hex(32)
        with sqlite3.connect(self.db_path) as db:
            db.execute("""INSERT INTO synthetic_customer_sessions
                (token_digest, account_id, expires_at, revoked)
                VALUES (?,?,?,0)""",
                (_digest(token), account_id, when + ttl_seconds))
        return token

    def revoke(self, token):
        digest = _digest(token)
        if digest is None:
            return False
        try:
            with sqlite3.connect(self.db_path) as db:
                result = db.execute("""UPDATE synthetic_customer_sessions
                    SET revoked=1 WHERE token_digest=? AND revoked=0""",
                    (digest,))
                return result.rowcount == 1
        except sqlite3.Error:
            return False

    def order_status(self, *, token, order_id, now):
        """Return strictly scoped synthetic order status or deny generically."""
        digest = _digest(token)
        if digest is None:
            raise PortalDenied("unavailable")
        try:
            when = _clock(now)
            _identifier(order_id, "order ID")
            with sqlite3.connect(self.db_path) as db:
                row = db.execute("""SELECT account_id FROM synthetic_customer_sessions
                    WHERE token_digest=? AND revoked=0 AND expires_at>?""",
                    (digest, when)).fetchone()
            if row is None:
                raise PortalDenied("unavailable")
            self.ownership.assert_owner(
                authenticated_account_id=row[0], order_id=order_id)
            report = self.fulfillment.status_report(order_id)
            return {
                "order_id": report["order_id"],
                "synthetic_state": report["synthetic_state"],
                "production_ready": False,
                "service_delivered_to_customer": False,
                "live_customer_activated": False,
                "real_payment_processed": False,
            }
        except (sqlite3.Error, OSError, ValueError, OwnershipDenied) as exc:
            raise PortalDenied("unavailable") from exc
