"""Paid-order-only, expiring onboarding invites for offline integration tests.

No HTTP routes, encryption at rest, credentials, real client data, or provider
connections. A trusted backend must create invitations after verifying payment.
Tokens are returned once; only SHA-256 digests are persisted.
"""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import hashlib
import secrets
import sqlite3


class OnboardingDenied(ValueError):
    pass


@dataclass(frozen=True)
class OnboardingStatus:
    order_id: str
    completed: bool
    business_name: str | None
    industry: str | None
    workflow_goal: str | None


def _clock(now):
    if now is None:
        now = datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise OnboardingDenied("trusted timezone-aware clock required")
    return int(now.timestamp())


def _limited(value: str, label: str, maximum: int):
    if (not isinstance(value, str) or not value.strip()
            or len(value.strip()) > maximum or any(ord(c) < 32 for c in value)):
        raise OnboardingDenied(f"invalid {label}")
    return value.strip()


class OnboardingInvites:
    """Requires checkout_orders from TestCheckoutLedger in the SAME SQLite DB."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS onboarding_invites (
                token_hash TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                used_at INTEGER
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS onboarding_submissions (
                order_id TEXT PRIMARY KEY,
                business_name TEXT NOT NULL,
                industry TEXT NOT NULL,
                workflow_goal TEXT NOT NULL,
                submitted_at INTEGER NOT NULL
            )""")

    def issue_for_paid_order(self, order_id: str, *, now=None, ttl_seconds=3600) -> str:
        """Trusted-server-only issuance. Untrusted web clients MUST NOT call this."""
        order_id = _limited(order_id, "order ID", 100)
        when = _clock(now)
        if type(ttl_seconds) is not int or not 60 <= ttl_seconds <= 86400:
            raise OnboardingDenied("invalid expiry")
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode("ascii")).hexdigest()
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT status FROM checkout_orders WHERE order_id=?",
                             (order_id,)).fetchone()
            if row is None or row[0] != "paid":
                raise OnboardingDenied("verified paid order required")
            if db.execute("SELECT 1 FROM onboarding_submissions WHERE order_id=?",
                          (order_id,)).fetchone():
                raise OnboardingDenied("onboarding already submitted")
            db.execute("INSERT INTO onboarding_invites VALUES (?,?,?,NULL)",
                       (digest, order_id, when + ttl_seconds))
        return token

    def submit(self, token: str, *, business_name: str, industry: str,
               workflow_goal: str, now=None) -> str:
        """One-time scoped form intake; no provider secrets or activation."""
        if not isinstance(token, str) or len(token) > 256 or not token:
            raise OnboardingDenied("invalid invitation")
        when = _clock(now)
        business_name = _limited(business_name, "business name", 120)
        industry = _limited(industry, "industry", 100)
        workflow_goal = _limited(workflow_goal, "workflow goal", 500)
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT order_id,expires_at,used_at
                FROM onboarding_invites WHERE token_hash=?""",(digest,)).fetchone()
            if row is None or row[2] is not None or row[1] <= when:
                raise OnboardingDenied("invitation invalid, used or expired")
            order_id = row[0]
            status = db.execute("SELECT status FROM checkout_orders WHERE order_id=?",
                                (order_id,)).fetchone()
            if status is None or status[0] != "paid":
                raise OnboardingDenied("order not paid")
            db.execute("""INSERT INTO onboarding_submissions
                (order_id,business_name,industry,workflow_goal,submitted_at)
                VALUES (?,?,?,?,?)""",
                (order_id,business_name,industry,workflow_goal,when))
            db.execute("UPDATE onboarding_invites SET used_at=? WHERE token_hash=?",
                       (when,digest))
            return order_id

    def status_for_trusted_operator(self, order_id: str) -> OnboardingStatus:
        """Caller must authenticate/authorize the operator outside this helper."""
        order_id = _limited(order_id, "order ID", 100)
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("""SELECT business_name,industry,workflow_goal
                FROM onboarding_submissions WHERE order_id=?""",(order_id,)).fetchone()
        return OnboardingStatus(order_id, row is not None,
                                None if row is None else row[0],
                                None if row is None else row[1],
                                None if row is None else row[2])
