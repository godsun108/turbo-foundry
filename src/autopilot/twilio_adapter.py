"""Twilio form-webhook authentication boundary. No HTTP server or outbound SMS.

Requires the official twilio Python package at runtime. The public webhook URL
must be configured and supplied exactly as Twilio requested it.
"""
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class AuthenticatedTwilioCall:
    call_sid: str
    caller: str
    destination: str
    call_status: str

def authenticate_twilio_voice_form(
    url: str, params: Mapping[str, str], signature: str, auth_token: str,
    *, validator=None,
) -> AuthenticatedTwilioCall | None:
    """Authenticate before reading event data; never infer a missed call here."""
    if not (url.startswith("https://") and signature and auth_token):
        return None
    if validator is None:
        from twilio.request_validator import RequestValidator
        validator = RequestValidator(auth_token)
    if not validator.validate(url, params, signature):
        return None
    sid = params.get("CallSid", "")
    caller = params.get("From", "")
    destination = params.get("To", "")
    status = params.get("CallStatus", "")
    if not (isinstance(sid, str) and sid.startswith("CA") and len(sid) == 34):
        return None
    if not (isinstance(caller, str) and isinstance(destination, str)
            and caller.startswith("+") and destination.startswith("+")):
        return None
    if not isinstance(status, str) or status not in {
        "queued", "ringing", "in-progress", "completed", "busy", "failed", "no-answer", "canceled"
    }:
        return None
    return AuthenticatedTwilioCall(sid, caller, destination, status)
