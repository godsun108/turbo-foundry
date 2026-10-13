import unittest
from datetime import datetime, timezone
from dataclasses import replace
from src.autopilot.call_records import CallRecordResolver, ProviderCallSnapshot

SID = "CA" + "a"*32
NOW = datetime(2026, 10, 13, 15, tzinfo=timezone.utc)
SNAP = ProviderCallSnapshot(SID, None, "inbound", "no-answer", NOW, False, True, False)

class Client:
    def __init__(self, snapshot=SNAP, error=False):
        self.snapshot, self.error = snapshot, error
    def fetch_call_snapshot(self, sid):
        if self.error:
            raise RuntimeError("provider unavailable")
        return self.snapshot

class TestCallRecordResolver(unittest.TestCase):
    def test_verified_record(self):
        r = CallRecordResolver(Client()).resolve(SID)
        self.assertTrue(r.authoritative)
        self.assertEqual(r.call_sid, SID)

    def test_missing_record(self):
        self.assertIsNone(CallRecordResolver(Client(None)).resolve(SID))

    def test_api_error(self):
        self.assertIsNone(CallRecordResolver(Client(error=True)).resolve(SID))

    def test_wrong_sid(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, sid="CA"+"b"*32))).resolve(SID))

    def test_child_leg_rejected(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, parent_sid="CA"+"b"*32))).resolve(SID))

    def test_answered_child_rejected(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, any_child_answered=True))).resolve(SID))

    def test_incomplete_child_history_rejected(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, child_legs_complete=False))).resolve(SID))

    def test_unknown_answer_evidence_rejected(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, answered=None))).resolve(SID))

    def test_completed_call_rejected(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, status="completed"))).resolve(SID))

    def test_outbound_call_rejected(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, direction="outbound-api"))).resolve(SID))

    def test_naive_time_rejected(self):
        self.assertIsNone(CallRecordResolver(Client(replace(SNAP, started_at=datetime(2026,10,13)))).resolve(SID))

if __name__ == "__main__":
    unittest.main()
