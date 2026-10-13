"""Fail-closed reconciliation for ambiguous provider outcomes.

No network calls. A timeout after a provider request is NOT evidence of failure.
An unknown outcome must not be automatically retried.
"""
from dataclasses import dataclass
from enum import Enum

class Outcome(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    CONFIRMED_DELIVERED = "confirmed_delivered"
    CONFIRMED_REJECTED = "confirmed_rejected"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class RecoveryDecision:
    action: str
    reason: str

def decide_recovery(outcome: Outcome, *, provider_supports_idempotency: bool, lookup_confirms_absence: bool = False) -> RecoveryDecision:
    if outcome == Outcome.CONFIRMED_DELIVERED:
        return RecoveryDecision("close", "provider_confirmed_delivery")
    if outcome == Outcome.CONFIRMED_REJECTED:
        return RecoveryDecision("stop", "provider_rejected")
    if outcome == Outcome.NOT_SUBMITTED:
        return RecoveryDecision("retry", "provider_never_contacted")
    if outcome == Outcome.UNKNOWN:
        if provider_supports_idempotency:
            return RecoveryDecision("reconcile", "query_provider_by_idempotency_key")
        if lookup_confirms_absence:
            return RecoveryDecision("retry", "provider_confirmed_absence")
        return RecoveryDecision("hold", "manual_reconciliation_required")
    return RecoveryDecision("hold", "unrecognized_outcome")
