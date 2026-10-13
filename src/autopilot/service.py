"""Offline end-to-end orchestration. This module does not accept public webhooks."""
from dataclasses import dataclass
from datetime import datetime
from .missed_call import MissedCall, Policy, evaluate
from .queue import MessageQueue, QueuedMessage

@dataclass(frozen=True)
class Result:
    status: str
    reason: str
    key: str = ""

def process_missed_call(event: MissedCall, policy: Policy, queue: MessageQueue, now: datetime) -> Result:
    """Evaluate, persist once, and simulate a deterministic response.

    This does not send SMS or assert that webhook authenticity has been verified.
    Production adapters must cryptographically verify provider signatures before
    setting signature_valid=True and must enforce authorization at the boundary.
    """
    decision = evaluate(event, policy, now)
    if not decision.eligible:
        return Result("rejected", decision.reason)
    message = QueuedMessage(
        decision.idempotency_key,
        event.tenant_id,
        event.caller,
        "Sorry we missed your call. Please reply if you'd like us to follow up.",
    )
    if not queue.enqueue(message):
        return Result("rejected", "duplicate_or_suppressed", decision.idempotency_key)
    if queue.simulate_delivery(message.key, event.tenant_id):
        return Result("simulated", "mock_delivery_only", message.key)
    return Result("rejected", "suppressed_or_unavailable", message.key)
