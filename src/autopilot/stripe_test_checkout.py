"""Offline Stripe TEST-MODE Checkout webhook ledger.

No HTTP endpoint, API credential, card processing or Checkout Session creator
is included. This is a trusted server-side component, NOT a deployable
authentication service. Only Stripe-signed, test-mode, fully paid Sessions
previously registered by a trusted backend may mark an order paid.
"""
import hashlib
import hmac
import json
import sqlite3
import time


class WebhookRejected(ValueError):
    pass


def verify_stripe_signature(payload: bytes, signature_header: str,
                            secret: str, *, now: int | None = None,
                            tolerance: int = 300) -> dict:
    if (not isinstance(payload, bytes) or len(payload) > 256_000
            or not isinstance(signature_header, str)
            or not isinstance(secret, str) or not secret.startswith("whsec_")
            or not isinstance(tolerance, int) or tolerance < 0):
        raise WebhookRejected("invalid webhook input")
    pairs = [piece.split("=", 1) for piece in signature_header.split(",")
             if "=" in piece]
    timestamps = [v for k, v in pairs if k == "t"]
    signatures = [v for k, v in pairs if k == "v1"]
    if len(timestamps) != 1 or not signatures:
        raise WebhookRejected("missing Stripe signature")
    try:
        stamp = int(timestamps[0])
    except ValueError:
        raise WebhookRejected("invalid signature timestamp") from None
    current = int(time.time()) if now is None else int(now)
    if stamp <= 0 or abs(current - stamp) > tolerance:
        raise WebhookRejected("signature timestamp outside tolerance")
    signed = str(stamp).encode("ascii") + b"." + payload
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, sig) for sig in signatures):
        raise WebhookRejected("signature mismatch")
    try:
        event = json.loads(payload)
    except (ValueError, UnicodeDecodeError):
        raise WebhookRejected("invalid JSON payload") from None
    if not isinstance(event, dict):
        raise WebhookRejected("invalid event")
    return event


class TestCheckoutLedger:
    """Orders and Checkout Session IDs must be provisioned server-side.

    This helper cannot create a real Stripe session or verify session ownership
    when a caller registers untrusted IDs. Use only inside a trusted service.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS checkout_orders (
                order_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL UNIQUE,
                expected_amount INTEGER NOT NULL CHECK (expected_amount > 0),
                currency TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending','paid')),
                payment_intent TEXT
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS checkout_webhook_events (
                event_id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL
            )""")

    def register_test_order(self, *, order_id: str, session_id: str,
                            amount_cents: int, currency: str = "usd"):
        if (not isinstance(order_id, str) or not order_id.strip()
                or len(order_id) > 100
                or not isinstance(session_id, str) or not session_id.startswith("cs_test_")
                or type(amount_cents) is not int or amount_cents <= 0
                or not isinstance(currency, str) or currency.lower() != "usd"):
            raise ValueError("valid local test-order details required")
        with sqlite3.connect(self.db_path) as db:
            db.execute("INSERT INTO checkout_orders VALUES (?,?,?,?,?,?)",
                       (order_id, session_id, amount_cents, "usd", "pending", None))

    def consume_signed_event(self, *, payload: bytes, signature_header: str,
                             webhook_secret: str, now: int | None = None) -> bool:
        """True only when a matching signed test-mode paid event changes state.

        Replays return False. All other event types are non-fulfilling.
        """
        event = verify_stripe_signature(payload, signature_header,
                                        webhook_secret, now=now)
        if event.get("livemode") is not False:
            raise WebhookRejected("live-mode event forbidden")
        if event.get("type") != "checkout.session.completed":
            return False
        data = event.get("data")
        session = data.get("object") if isinstance(data, dict) else None
        if not isinstance(session, dict):
            raise WebhookRejected("missing session")
        event_id = event.get("id")
        session_id = session.get("id")
        intent = session.get("payment_intent")
        amount = session.get("amount_total")
        currency = session.get("currency")
        if (not isinstance(event_id, str) or not event_id.startswith("evt_")
                or not isinstance(session_id, str) or not session_id.startswith("cs_test_")
                or not isinstance(intent, str) or not intent.startswith("pi_")
                or type(amount) is not int
                or currency != "usd"
                or session.get("payment_status") != "paid"
                or session.get("mode") != "payment"):
            raise WebhookRejected("incomplete or unpaid session")
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT order_id,expected_amount,status
                FROM checkout_orders WHERE session_id=?""",(session_id,)).fetchone()
            if row is None or row[1] != amount:
                raise WebhookRejected("unknown session or amount mismatch")
            if row[2] == "paid":
                return False
            db.execute("INSERT INTO checkout_webhook_events VALUES (?,?)",
                       (event_id, row[0]))
            db.execute("""UPDATE checkout_orders SET status='paid',
                payment_intent=? WHERE order_id=? AND status='pending'""",
                (intent,row[0]))
            return True

    def get_status(self, order_id: str) -> str | None:
        with sqlite3.connect(self.db_path) as db:
            row = db.execute("SELECT status FROM checkout_orders WHERE order_id=?",
                             (order_id,)).fetchone()
            return None if row is None else row[0]
