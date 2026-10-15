"""Fail-closed, offline validation for a future Sovereign Genesis adapter.

This module NEVER calls a network endpoint or runs a model. Responses from
Genesis are untrusted suggestions, not authorization for business actions.
"""
from dataclasses import dataclass


class GenesisContractDenied(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedGenesisReply:
    reply: str
    intent: str
    disposition: str
    verified_booking: bool = False
    real_message_sent: bool = False


_ALLOWED_INTENTS = frozenset({"intake","quote_request","appointment_request","support","urgent","human","stop"})
_ALLOWED_DISPOSITIONS = frozenset({"collect_details","human_escalation","closed","informational"})


def validate_genesis_reply(payload):
    """Validate the v0 schema; explicitly prohibit external side effects."""
    if not isinstance(payload, dict) or set(payload) != {
        "schema","reply","intent","disposition","proposed_actions","evidence",
        "verified_booking","real_message_sent"
    }:
        raise GenesisContractDenied("invalid Genesis reply schema")
    if payload["schema"] != "foundry.genesis.reply.v0":
        raise GenesisContractDenied("unsupported Genesis reply schema")
    reply = payload["reply"]
    if not isinstance(reply,str) or not reply.strip() or len(reply)>1200:
        raise GenesisContractDenied("invalid response text")
    if payload["intent"] not in _ALLOWED_INTENTS:
        raise GenesisContractDenied("unapproved intent")
    if payload["disposition"] not in _ALLOWED_DISPOSITIONS:
        raise GenesisContractDenied("unapproved disposition")
    if payload["proposed_actions"] != [] or payload["evidence"] != []:
        raise GenesisContractDenied("actions and evidence unavailable in offline v0")
    if payload["verified_booking"] is not False or payload["real_message_sent"] is not False:
        raise GenesisContractDenied("unsupported completion claim")
    if payload["intent"] in ("urgent","human") and payload["disposition"] != "human_escalation":
        raise GenesisContractDenied("unsafe escalation disposition")
    if payload["intent"] == "stop" and payload["disposition"] != "closed":
        raise GenesisContractDenied("unsafe opt-out disposition")
    return ValidatedGenesisReply(reply.strip(),payload["intent"],payload["disposition"])
