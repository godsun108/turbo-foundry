"""Bounded, fail-closed enumeration of Twilio child calls (read-only)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Enumeration:
    complete: bool
    reason: str
    child_sids: tuple[str,...]

def enumerate_child_calls(provider_client, parent_sid: str, *, max_legs: int = 100) -> Enumeration:
    if not isinstance(parent_sid,str) or not parent_sid.startswith("CA") or len(parent_sid)!=34:
        return Enumeration(False,"invalid_parent_sid",())
    if not isinstance(max_legs,int) or isinstance(max_legs,bool) or max_legs<1 or max_legs>1000:
        return Enumeration(False,"invalid_limit",())
    try:
        # Request one extra record: if returned, the bounded result is incomplete.
        calls=provider_client.calls.list(parent_call_sid=parent_sid,limit=max_legs+1)
        if not isinstance(calls,(list,tuple)):
            return Enumeration(False,"unverified_pagination",())
        if len(calls)>max_legs:
            return Enumeration(False,"limit_exceeded",())
        # A returned sequence with no explicit provider page-completion signal
        # cannot establish exhaustive enumeration. Keep result advisory.
        sids=[]
        for call in calls:
            sid=getattr(call,"sid",None)
            linked=getattr(call,"parent_call_sid",None)
            if not isinstance(sid,str) or not sid.startswith("CA") or len(sid)!=34 or sid==parent_sid:
                return Enumeration(False,"invalid_child_sid",())
            if linked!=parent_sid:
                return Enumeration(False,"child_parent_mismatch",())
            if sid in sids:
                return Enumeration(False,"duplicate_child",())
            sids.append(sid)
        # The SDK's list(limit=...) contract must be verified for the
        # deployed version; a short result alone does not prove full history.
        return Enumeration(False,"pagination_completeness_unverified",tuple(sorted(sids)))
    except Exception:
        return Enumeration(False,"provider_list_failed",())
