"""Offline authenticated mock-event ingestion. Not a public HTTP endpoint."""
from datetime import datetime
from .missed_call import MissedCall, Policy
from .queue import MessageQueue
from .service import Result, process_missed_call
from .webhook import verify_mock_webhook

def ingest_signed_mock_event(raw_body: bytes, signature: str, secret: bytes,
                             policy: Policy, queue: MessageQueue, now: datetime,
                             *, consent_evidence: bool = False,
                             opted_out: bool = False,
                             recent_message_sent: bool = False) -> Result:
    """Only the local test harness supplies consent state; production must query trusted records."""
    verified = verify_mock_webhook(raw_body, signature, secret, now)
    if verified is None:
        return Result("rejected", "unverified_webhook")
    event = MissedCall(
        event_id=verified.event_id,
        tenant_id=verified.tenant_id,
        caller=verified.caller,
        destination=verified.destination,
        occurred_at=verified.occurred_at,
        signature_valid=True,
        consent_evidence=consent_evidence,
        opted_out=opted_out,
        recent_message_sent=recent_message_sent,
    )
    return process_missed_call(event, policy, queue, now)
