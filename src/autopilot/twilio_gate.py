"""Fail-closed authenticated Twilio outcome gate.

Pure classification only: never sends SMS or creates a MissedCall. Inbound
direction and answered-elsewhere evidence must come from trusted call records;
a callback's own fields are insufficient to establish those facts.
"""
from dataclasses import dataclass
from typing import Mapping

from .call_outcome import classify_call_status
from .twilio_adapter import authenticate_twilio_voice_form

@dataclass(frozen=True)
class ProviderGate:
    accepted: bool
    reason: str
    call_sid: str = ""

def screen_twilio_callback(
    url: str, params: Mapping[str, str], signature: str, auth_token: str,
    *, provisioned_destination: str, trusted_inbound: bool,
    trusted_answered_elsewhere: bool = False, validator=None,
) -> ProviderGate:
    """Return classification; never treat this as authorization to send SMS."""
    call = authenticate_twilio_voice_form(
        url, params, signature, auth_token, validator=validator
    )
    if call is None:
        return ProviderGate(False, "invalid_provider_callback")
    if not provisioned_destination or call.destination != provisioned_destination:
        return ProviderGate(False, "destination_not_provisioned", call.call_sid)
    outcome = classify_call_status(
        call.call_status, inbound=trusted_inbound,
        answered_elsewhere=trusted_answered_elsewhere,
    )
    return ProviderGate(outcome.eligible_missed, outcome.reason, call.call_sid)
