"""Fail-closed call record retrieval boundary.

A provider client is injected for offline testing. Real client credentials and
provider API response validation belong in a separate authenticated adapter.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from .provider_pipeline import TrustedCallRecord

@dataclass(frozen=True)
class ProviderCallSnapshot:
    sid: str
    parent_sid: str | None
    direction: str
    status: str
    started_at: datetime | None
    answered: bool | None
    child_legs_complete: bool
    any_child_answered: bool | None

class CallRecordResolver:
    def __init__(self, provider_client):
        self.provider_client = provider_client

    def resolve(self, call_sid: str) -> TrustedCallRecord | None:
        """Require provider-attested parent leg and complete answer evidence."""
        if not isinstance(call_sid, str) or not call_sid.startswith("CA") or len(call_sid) != 34:
            return None
        try:
            record = self.provider_client.fetch_call_snapshot(call_sid)
        except Exception:
            return None
        if not isinstance(record, ProviderCallSnapshot) or record.sid != call_sid:
            return None
        if record.parent_sid is not None or record.direction not in ("inbound", "inbound-api"):
            return None
        if record.status != "no-answer" or record.answered is not False:
            return None
        if not record.child_legs_complete or record.any_child_answered is not False:
            return None
        if not isinstance(record.started_at, datetime) or record.started_at.tzinfo is None:
            return None
        return TrustedCallRecord(record.sid, True, False, True, record.started_at)
