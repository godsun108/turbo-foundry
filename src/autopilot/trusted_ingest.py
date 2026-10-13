"""Offline signed-mock ingestion consulting trusted tenant-scoped consent storage."""
from datetime import datetime
from .webhook import verify_mock_webhook
from .missed_call import MissedCall, Policy
from .queue import MessageQueue
from .consent import ConsentStore
from .service import Result, process_missed_call

def ingest_with_stored_consent(raw_body: bytes, signature: str, secret: bytes,
                               policy: Policy, queue: MessageQueue,
                               consent: ConsentStore, now: datetime) -> Result:
    event = verify_mock_webhook(raw_body, signature, secret, now)
    if event is None:
        return Result("rejected", "unverified_webhook")
    if event.tenant_id != policy.tenant_id or event.destination != policy.approved_number:
        return Result("rejected", "unapproved_tenant_or_destination")
    state = consent.lookup(event.tenant_id, event.caller)
    verified = MissedCall(event.event_id, event.tenant_id, event.caller,
                          event.destination, event.occurred_at, True,
                          state.permitted, opted_out=state.opted_out)
    return process_missed_call(verified, policy, queue, now)
