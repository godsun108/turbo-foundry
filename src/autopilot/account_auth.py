"""Trusted Twilio credential selection for offline callback verification."""
from dataclasses import dataclass
from typing import Mapping
from .twilio_adapter import authenticate_twilio_voice_form

@dataclass(frozen=True)
class AccountAuthResult:
    verified: bool
    reason: str
    account_sid: str = ""

class TrustedAccountVerifier:
    def __init__(self, tokens_by_account: Mapping[str,str]):
        """Tokens are injected from trusted server config, never callback fields."""
        self._tokens=dict(tokens_by_account)

    def verify(self, *, url: str, params: Mapping[str,str], signature: str,
               validator_factory=None) -> AccountAuthResult:
        sid=params.get("AccountSid","")
        if not sid.startswith("AC") or len(sid)!=34:
            return AccountAuthResult(False,"invalid_account_sid")
        token=self._tokens.get(sid)
        if not token:
            return AccountAuthResult(False,"unknown_account")
        validator=validator_factory(token) if validator_factory else None
        call=authenticate_twilio_voice_form(url,params,signature,token,validator=validator)
        if call is None:
            return AccountAuthResult(False,"invalid_signature_or_event")
        return AccountAuthResult(True,"verified",sid)
