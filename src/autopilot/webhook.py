"""Provider-neutral signed webhook boundary for offline pilot tests.

Uses HMAC-SHA256 over raw request bytes. This is a *custom test protocol*,
NOT a Twilio or other vendor signature verification implementation.
"""
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

@dataclass(frozen=True)
class VerifiedEvent:
    tenant_id: str
    event_id: str
    caller: str
    destination: str
    occurred_at: datetime

def verify_mock_webhook(raw_body: bytes, signature: str, secret: bytes, now: datetime, max_age_seconds: int = 300) -> VerifiedEvent | None:
    """Reject unsigned, tampered, stale, malformed, or ambiguous test payloads."""
    if not secret or not isinstance(raw_body, bytes) or len(raw_body) > 16_384:
        return None
    if not isinstance(signature, str) or len(signature) != 64:
        return None
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    if now.tzinfo is None:
        return None
    try:
        payload = json.loads(raw_body)
        if not isinstance(payload, dict) or set(payload) != {"tenant_id", "event_id", "caller", "destination", "occurred_at", "type"}:
            return None
        if payload["type"] != "missed_call":
            return None
        if any(not isinstance(payload[k], str) or not payload[k] or len(payload[k]) > 200 for k in ("tenant_id", "event_id", "caller", "destination")):
            return None
        occurred_at = datetime.fromisoformat(payload["occurred_at"].replace("Z", "+00:00"))
        if occurred_at.tzinfo is None:
            return None
        age = now - occurred_at
        if age < timedelta(0) or age > timedelta(seconds=max_age_seconds):
            return None
        return VerifiedEvent(payload["tenant_id"], payload["event_id"], payload["caller"], payload["destination"], occurred_at)
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
        return None
