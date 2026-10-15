import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from src.autopilot.call_journal import CallJournal

SID="CA"+"a"*32
NUMBER="+15551234567"
PARAMS={"CallSid":SID,"From":"+15557654321","To":NUMBER,"CallStatus":"no-answer"}
NOW=datetime(2026,10,13,15,tzinfo=timezone.utc)
class Validator:
    def __init__(self, valid=True): self.valid=valid
    def validate(self,url,params,signature): return self.valid

class TestJournal(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.journal=CallJournal(str(Path(tmp.name)/"journal.sqlite"))

    def record(self, **overrides):
        args=dict(tenant_id="shop-a",provisioned_destination=NUMBER,
                  url="https://example.test/twilio",params=PARAMS,
                  signature="sig",auth_token="token",event_key="event-1",
                  received_at=NOW,validator=Validator())
        args.update(overrides)
        return self.journal.record_signed_callback(**args)

    def test_record_and_replay_idempotent(self):
        self.assertEqual(self.record().reason,"recorded")
        self.assertEqual(self.record().reason,"duplicate")
        self.assertEqual(len(self.journal.list_events("shop-a",SID)),1)

    def test_invalid_signature(self):
        self.assertEqual(self.record(validator=Validator(False)).reason,"invalid_signature_or_event")

    def test_wrong_destination(self):
        self.assertEqual(self.record(provisioned_destination="+15550000000").reason,"unprovisioned_destination")

    def test_tenant_isolation(self):
        self.record()
        self.assertEqual(self.journal.list_events("shop-b",SID),[])

    def test_parent_sid_recorded(self):
        p=dict(PARAMS,ParentCallSid="CA"+"b"*32)
        self.assertTrue(self.record(params=p).recorded)
        self.assertEqual(self.journal.list_events("shop-a",SID)[0][2],p["ParentCallSid"])

    def test_invalid_parent_rejected(self):
        self.assertEqual(self.record(params=dict(PARAMS,ParentCallSid="bad")).reason,"invalid_parent_sid")

    def test_missing_metadata_rejected(self):
        self.assertEqual(self.record(event_key="").reason,"invalid_journal_metadata")

if __name__=="__main__": unittest.main()
