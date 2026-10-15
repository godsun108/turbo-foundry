"""Offline Twilio-to-consent pipeline. No live provider calls or SMS.

A trusted call-record resolver must supply direction, parent/child call
correlation and answered-elsewhere evidence. Without it, fail closed.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from .consent import ConsentStore
from .missed_call import MissedCall, Policy
from .queue import MessageQueue
from .service import Result, process_missed_call
from .twilio_gate import screen_twilio_callback

@dataclass(frozen=True)
class TrustedCallRecord:
    call_sid: str
    inbound: bool
    answered_elsewhere: bool
    authoritative: bool
    occurred_at: datetime

def process_authenticated_provider_event(
    url: str, params: Mapping[str, str], signature: str, auth_token: str,
    *, policy: Policy, queue: MessageQueue, consent: ConsentStore,
    record: TrustedCallRecord | None, now: datetime, validator=None,
) -> Result:
    """Record must originate from trusted server-side provider reconciliation."""
    if record is None or not record.authoritative or record.occurred_at.tzinfo is None:
        return Result("rejected", "trusted_call_record_required")
    gate = screen_twilio_callback(
        url, params, signature, auth_token,
        provisioned_destination=policy.approved_number,
        trusted_inbound=record.inbound,
        trusted_answered_elsewhere=record.answered_elsewhere,
        validator=validator,
    )
    if not gate.accepted:
        return Result("rejected", gate.reason)
    if gate.call_sid != record.call_sid:
        return Result("rejected", "call_record_mismatch")
    caller = params["From"]
    state = consent.lookup(policy.tenant_id, caller)
    event = MissedCall(
        event_id=gate.call_sid,
        tenant_id=policy.tenant_id,
        caller=caller,
        destination=policy.approved_number,
        occurred_at=record.occurred_at,
        signature_valid=True,
        consent_evidence=state.permitted,
        opted_out=state.opted_out,
    )
    return process_missed_call(event, policy, queue, now)
