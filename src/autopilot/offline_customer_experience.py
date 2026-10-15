"""Deterministic, offline customer-experience rehearsal for Foundry.

No LLM, network, calendar, real customer records, or outbound communication.
Never invent prices, appointment slots, or confirmed bookings.
"""
from dataclasses import dataclass
import re

from .universal_business_templates import get_template

_ALLOWED = {"automotive", "hvac", "plumbing", "landscaping", "cleaning", "general"}
_URGENT = re.compile(r"\b(gas leak|smell gas|carbon monoxide|sparks|electrical fire|fire|flooding|burst pipe|smoke)\b",re.I)
_PRICE = re.compile(r"\b(price|cost|quote|estimate|how much)\b",re.I)
_BOOK = re.compile(r"\b(book|appointment|schedule|available|availability|tomorrow|today)\b",re.I)
_HUMAN = re.compile(r"\b(human|person|manager|representative|agent|complaint)\b",re.I)
_STOP = re.compile(r"\b(stop|unsubscribe|opt out)\b",re.I)


@dataclass(frozen=True)
class ExperienceResponse:
    message: str
    intent: str
    disposition: str
    verified_booking: bool = False
    real_message_sent: bool = False


class OfflineCustomerExperience:
    """Tenant-scoped fictional session with explicit verified business facts."""

    def __init__(self):
        self._sessions = {}

    def respond(self, *, tenant, industry, session, message, verified_facts=None):
        if (not isinstance(tenant,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}",tenant)
                or not isinstance(session,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}",session)
                or industry not in _ALLOWED or not isinstance(message,str)
                or not 1 <= len(message) <= 1000):
            raise ValueError("invalid fictional conversation")
        get_template(industry)
        if verified_facts is not None and (not isinstance(verified_facts,dict)
                or set(verified_facts) - {"business_name","service_area","services"}
                or any(not isinstance(v,str) or len(v)>160 for v in verified_facts.values())):
            raise ValueError("unsupported business facts")
        key=(tenant,session)
        previous=self._sessions.get(key)
        if previous and previous["industry"]!=industry:
            raise ValueError("session industry mismatch")
        if previous and previous["stopped"]:
            return ExperienceResponse("This simulated conversation is closed.","stop","closed")
        facts=verified_facts or {}
        name=facts.get("business_name","the business")
        if _STOP.search(message):
            self._sessions[key]={"industry":industry,"stopped":True,"turns":(previous or {}).get("turns",0)+1}
            return ExperienceResponse("Understood. This simulated conversation is closed.","stop","closed")
        if _URGENT.search(message):
            answer=("This may be urgent. Move away from immediate danger and contact "
                    "local emergency services or an appropriately qualified professional. "
                    "I cannot dispatch emergency assistance.")
            intent,disposition="urgent","human_escalation"
        elif _HUMAN.search(message):
            answer="I can flag a request for a human, but no staff member has been contacted in this demo."
            intent,disposition="human","human_escalation"
        elif _PRICE.search(message):
            answer=f"I can help prepare a quote request for {name}, but I cannot verify a price. What service do you need?"
            intent,disposition="quote","collect_details"
        elif _BOOK.search(message):
            answer=("I can help prepare an appointment request. I cannot see live availability "
                    "or confirm a booking. What service and preferred day work for you?")
            intent,disposition="appointment","collect_details"
        else:
            service=facts.get("services")
            answer=(f"Thanks for contacting {name}. "
                    +(f"Verified service information: {service}. " if service else "")
                    +"What service do you need help with?")
            intent,disposition="intake","collect_details"
        self._sessions[key]={"industry":industry,"stopped":False,
                             "turns":(previous or {}).get("turns",0)+1}
        return ExperienceResponse(answer,intent,disposition)

    def session_status(self, *, tenant, session):
        record=self._sessions.get((tenant,session))
        return None if record is None else dict(record)
