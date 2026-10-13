"""Pure, fail-closed missed-call eligibility engine. No network or SMS sends."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

PHONE = re.compile(r"^\+[1-9][0-9]{7,14}$")

@dataclass(frozen=True)
class Policy:
    tenant_id: str
    timezone: str
    approved_number: str
    consent_required: bool = True
    quiet_start: int = 21
    quiet_end: int = 8
    max_event_age_minutes: int = 15

@dataclass(frozen=True)
class MissedCall:
    event_id: str
    tenant_id: str
    caller: str
    destination: str
    occurred_at: datetime
    signature_valid: bool
    consent_evidence: bool
    opted_out: bool = False
    previously_processed: bool = False
    recent_message_sent: bool = False

@dataclass(frozen=True)
class Decision:
    eligible: bool
    reason: str
    idempotency_key: str = ""

def evaluate(event: MissedCall, policy: Policy, now: datetime) -> Decision:
    """Determine whether to queue a response; caller must persist idempotency atomically."""
    if not event.signature_valid:
        return Decision(False, "invalid_signature")
    if not policy.tenant_id or event.tenant_id != policy.tenant_id:
        return Decision(False, "unknown_tenant")
    if not event.event_id or not PHONE.fullmatch(event.caller) or not PHONE.fullmatch(event.destination):
        return Decision(False, "invalid_event")
    if event.destination != policy.approved_number:
        return Decision(False, "unapproved_destination")
    if now.tzinfo is None or event.occurred_at.tzinfo is None:
        return Decision(False, "timezone_missing")
    age = now - event.occurred_at
    if age < timedelta(0) or age > timedelta(minutes=policy.max_event_age_minutes):
        return Decision(False, "stale_or_future_event")
    if event.previously_processed:
        return Decision(False, "duplicate")
    if event.opted_out:
        return Decision(False, "suppressed")
    if policy.consent_required and not event.consent_evidence:
        return Decision(False, "consent_missing")
    if event.recent_message_sent:
        return Decision(False, "frequency_capped")
    try:
        hour = now.astimezone(ZoneInfo(policy.timezone)).hour
    except (KeyError, ValueError):
        return Decision(False, "invalid_timezone")
    if not 0 <= policy.quiet_start <= 23 or not 0 <= policy.quiet_end <= 23:
        return Decision(False, "invalid_quiet_hours")
    start, end = policy.quiet_start, policy.quiet_end
    quiet = (start <= hour or hour < end) if start > end else (start <= hour < end)
    if start == end:
        quiet = True
    if quiet:
        return Decision(False, "quiet_hours")
    return Decision(True, "eligible", f"{event.tenant_id}:{event.event_id}")
