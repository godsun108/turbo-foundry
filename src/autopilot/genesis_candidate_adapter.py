"""Dependency-injected Genesis candidate adapter, offline by default.

A caller may provide a *trusted server-side* inference function. This module
does not discover endpoints, read secrets, perform HTTP, or enable production.
Timeout is enforced for cooperative providers only; do not use an untrusted
blocking provider in this in-process rehearsal.
"""
from dataclasses import dataclass
from .genesis_offline_boundary import GenesisOfflineBoundary


@dataclass(frozen=True)
class AdapterTurn:
    reply: str
    source: str
    intent: str
    disposition: str


class GenesisCandidateAdapter:
    def __init__(self, infer=None):
        self._infer = infer
        self._boundary = GenesisOfflineBoundary()

    def respond(self, *, tenant, session, industry, message, verified_facts=None):
        # Authentication/authorization must be performed by the calling gateway.
        # Never accept tenant/session identifiers from the customer utterance.
        # Never send urgent, opt-out, or human-escalation utterances to an
        # optional model. The deterministic boundary owns these decisions.
        import re
        if re.search(r"\\b(stop|unsubscribe|opt out|gas leak|smell gas|carbon monoxide|sparks|electrical fire|fire|flooding|burst pipe|smoke|human|person|manager|representative|agent|complaint)\\b", message, re.I):
            result = self._boundary.respond(
                tenant=tenant, session=session, industry=industry,
                message=message, candidate=None, verified_facts=verified_facts)
            return AdapterTurn(result.reply, result.source, result.intent, result.disposition)
        candidate = None
        if self._infer is not None:
            try:
                context = self._boundary.context(tenant=tenant, session=session)
                candidate = self._infer({
                    "schema": "foundry.genesis.turn.v0",
                    "tenant": tenant,
                    "session": session,
                    "industry": industry,
                    "utterance": message,
                    "context": context,
                    "verified_business_facts": verified_facts or {},
                    "permitted_actions": [],
                })
            except Exception:
                candidate = None
        result = self._boundary.respond(
            tenant=tenant, session=session, industry=industry,
            message=message, candidate=candidate, verified_facts=verified_facts)
        return AdapterTurn(result.reply, result.source, result.intent, result.disposition)
