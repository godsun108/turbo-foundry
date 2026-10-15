"""Offline, fail-closed Foundry-to-Genesis orchestration boundary.

No network, model execution, persistence, credentials, or customer communications.
The caller supplies an authenticated tenant/session and a separately obtained
untrusted model response. This is NOT a deployed inference integration.
"""
from dataclasses import dataclass
import re

from .genesis_reply_contract import GenesisContractDenied, validate_genesis_reply
from .offline_customer_experience import OfflineCustomerExperience

_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
_INDUSTRIES = frozenset({"automotive", "hvac", "plumbing", "landscaping", "cleaning", "general"})
_STOP = re.compile(r"\b(stop|unsubscribe|opt out)\b", re.I)
_URGENT = re.compile(r"\b(gas leak|smell gas|carbon monoxide|sparks|electrical fire|fire|flooding|burst pipe|smoke)\b", re.I)
_HUMAN = re.compile(r"\b(human|person|manager|representative|agent|complaint)\b", re.I)


@dataclass(frozen=True)
class TurnResult:
    reply: str
    source: str
    intent: str
    disposition: str


class GenesisOfflineBoundary:
    def __init__(self):
        self._sessions = {}
        self._fallback = OfflineCustomerExperience()

    def respond(self, *, tenant, session, industry, message, candidate=None, verified_facts=None):
        if not isinstance(tenant, str) or not _ID.fullmatch(tenant) or not isinstance(session, str) or not _ID.fullmatch(session):
            raise ValueError("invalid authenticated scope")
        if industry not in _INDUSTRIES or not isinstance(message, str) or not 1 <= len(message) <= 1000:
            raise ValueError("invalid turn")
        if verified_facts is not None and (not isinstance(verified_facts, dict) or set(verified_facts) - {"business_name", "service_area", "services"} or any(not isinstance(v, str) or len(v) > 160 for v in verified_facts.values())):
            raise ValueError("invalid verified facts")
        key = (tenant, session)
        record = self._sessions.get(key, {"industry": industry, "closed": False, "history": []})
        if record["industry"] != industry:
            raise ValueError("session industry mismatch")
        if record["closed"]:
            return TurnResult("This simulated conversation is closed.", "deterministic", "stop", "closed")
        # Safety decisions are independent of any model-proposed disposition.
        force = "stop" if _STOP.search(message) else "urgent" if _URGENT.search(message) else "human" if _HUMAN.search(message) else None
        fallback = self._fallback.respond(tenant=tenant, session=session, industry=industry, message=message, verified_facts=verified_facts)
        if force:
            reply = TurnResult(fallback.message, "deterministic", fallback.intent, fallback.disposition)
        else:
            try:
                if candidate is None:
                    raise GenesisContractDenied("no candidate")
                validated = validate_genesis_reply(candidate)
                if validated.intent in {"urgent", "human", "stop"}:
                    raise GenesisContractDenied("model cannot originate safety disposition")
                reply = TurnResult(validated.reply, "validated_candidate", validated.intent, validated.disposition)
            except (GenesisContractDenied, TypeError, ValueError):
                reply = TurnResult(fallback.message, "deterministic", fallback.intent, fallback.disposition)
        history = (record["history"] + [{"role": "user", "content": message}, {"role": "assistant", "content": reply.reply}])[-20:]
        self._sessions[key] = {"industry": industry, "closed": reply.disposition == "closed", "history": history}
        return reply

    def context(self, *, tenant, session):
        if not isinstance(tenant, str) or not _ID.fullmatch(tenant) or not isinstance(session, str) or not _ID.fullmatch(session):
            raise ValueError("invalid scope")
        record = self._sessions.get((tenant, session))
        return [] if record is None else [dict(item) for item in record["history"]]
