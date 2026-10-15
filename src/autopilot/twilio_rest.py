"""Read-only Twilio REST adapter. Never asserts complete answer history.

The Twilio Call resource does not expose a definitive 'was a human reached'
boolean. This adapter intentionally leaves answer evidence unresolved.
"""
from datetime import datetime
from .call_records import ProviderCallSnapshot

class TwilioRestCallClient:
    def __init__(self, client):
        """Inject an authenticated twilio.rest.Client from secure configuration."""
        self.client = client

    def fetch_call_snapshot(self, call_sid: str) -> ProviderCallSnapshot:
        call = self.client.calls(call_sid).fetch()
        if call.sid != call_sid:
            raise ValueError("Twilio returned mismatched CallSid")
        started = getattr(call, "start_time", None)
        if not isinstance(started, datetime) or started.tzinfo is None:
            started = None
        return ProviderCallSnapshot(
            sid=call.sid,
            parent_sid=getattr(call, "parent_call_sid", None),
            direction=getattr(call, "direction", ""),
            status=getattr(call, "status", ""),
            started_at=started,
            answered=None,  # answered_by is AMD, NOT a general answer boolean
            child_legs_complete=False,  # cannot prove completeness from one fetch
            any_child_answered=None,
        )
