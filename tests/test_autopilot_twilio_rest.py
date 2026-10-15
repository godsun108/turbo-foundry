import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from src.autopilot.twilio_rest import TwilioRestCallClient
from src.autopilot.call_records import CallRecordResolver

SID = "CA" + "a"*32
CALL = SimpleNamespace(sid=SID, parent_call_sid=None, direction="inbound",
                       status="no-answer", start_time=datetime(2026,10,13,15,tzinfo=timezone.utc),
                       answered_by=None)

class Calls:
    def __init__(self, call):
        self.call=call
    def __call__(self, sid):
        self.requested=sid
        return self
    def fetch(self):
        return self.call

class Client:
    def __init__(self, call):
        self.calls=Calls(call)

class TestTwilioRest(unittest.TestCase):
    def test_read_only_snapshot_never_invents_answer_history(self):
        adapter=TwilioRestCallClient(Client(CALL))
        snapshot=adapter.fetch_call_snapshot(SID)
        self.assertIsNone(snapshot.answered)
        self.assertFalse(snapshot.child_legs_complete)
        self.assertIsNone(snapshot.any_child_answered)
        self.assertIsNone(CallRecordResolver(adapter).resolve(SID))

    def test_mismatched_sid_rejected(self):
        adapter=TwilioRestCallClient(Client(SimpleNamespace(sid="CA"+"b"*32)))
        with self.assertRaises(ValueError):
            adapter.fetch_call_snapshot(SID)

    def test_missing_timestamp_unresolved(self):
        call=SimpleNamespace(**{**vars(CALL), "start_time":None})
        snapshot=TwilioRestCallClient(Client(call)).fetch_call_snapshot(SID)
        self.assertIsNone(snapshot.started_at)

    def test_completed_call_still_unresolved(self):
        call=SimpleNamespace(**{**vars(CALL), "status":"completed"})
        snapshot=TwilioRestCallClient(Client(call)).fetch_call_snapshot(SID)
        self.assertIsNone(snapshot.answered)

if __name__ == "__main__":
    unittest.main()
