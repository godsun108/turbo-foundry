"""Conservative voice-call outcome classification for authenticated events.

Only authoritative terminal status 'no-answer' is classified as missed here.
This is not a complete call lifecycle or call-leg correlation implementation.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class CallOutcome:
    eligible_missed: bool
    reason: str

def classify_call_status(status: str, *, inbound: bool, answered_elsewhere: bool = False) -> CallOutcome:
    if not inbound:
        return CallOutcome(False, "not_inbound")
    if answered_elsewhere:
        return CallOutcome(False, "answered_elsewhere")
    if status == "no-answer":
        return CallOutcome(True, "verified_no_answer")
    if status in ("completed", "in-progress"):
        return CallOutcome(False, "answered_or_unresolved")
    if status in ("busy", "failed", "canceled"):
        return CallOutcome(False, "not_confirmed_missed")
    if status in ("queued", "ringing"):
        return CallOutcome(False, "nonterminal")
    return CallOutcome(False, "unknown_status")
