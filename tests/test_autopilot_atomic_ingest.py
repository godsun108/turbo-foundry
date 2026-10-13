import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from src.autopilot.atomic_ingest import AtomicCallIngest
from src.autopilot.call_journal import CallJournal
from src.autopilot.event_integrity import EventIntegrity

PARENT="CA"+"a"*32
CHILD="CA"+"b"*32
NUMBER="+15551234567"
AGENT="+15559998888"
NOW=datetime(2026,10,13,15,tzinfo=timezone.utc)
class Validator:
    def __init__(self,valid=True): self.valid=valid
    def validate(self,url,params,signature): return self.valid

class TestAtomicIngest(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db=str(Path(tmp.name)/"atomic.sqlite")
        self.ingest=AtomicCallIngest(self.db)
        self.journal=CallJournal(self.db)

    def record(self,sid,to,status,key,parent="",**overrides):
        params=dict(CallSid=sid,From="+15557654321",To=to,CallStatus=status)
        if parent: params["ParentCallSid"]=parent
        args=dict(tenant_id="shop-a",provisioned_number=NUMBER,
                  url="https://example.test/twilio",params=params,signature="sig",
                  auth_token="token",event_key=key,received_at=NOW,validator=Validator())
        args.update(overrides)
        return self.ingest.record(**args)

    def test_parent_and_child_commit(self):
        self.assertTrue(self.record(PARENT,NUMBER,"no-answer","p").recorded)
        self.assertTrue(self.record(CHILD,AGENT,"no-answer","c",PARENT).recorded)
        self.assertEqual(self.journal.list_events("shop-a",CHILD)[0][2],PARENT)

    def test_duplicate(self):
        self.record(PARENT,NUMBER,"no-answer","p")
        self.assertEqual(self.record(PARENT,NUMBER,"no-answer","p").reason,"duplicate")

    def test_conflict_audited(self):
        self.record(PARENT,NUMBER,"ringing","p")
        self.assertEqual(self.record(PARENT,NUMBER,"no-answer","p").reason,"payload_conflict")
        self.assertTrue(EventIntegrity(self.db).has_conflict("shop-a","p"))
        self.assertEqual(self.journal.list_events("shop-a",PARENT)[0][1],"ringing")

    def test_invalid_signature_no_route(self):
        self.assertEqual(self.record(PARENT,NUMBER,"no-answer","p",validator=Validator(False)).reason,
                         "invalid_signature_or_event")
        self.assertEqual(self.record(CHILD,AGENT,"no-answer","c",PARENT).reason,"unknown_parent")

    def test_unknown_child_parent_no_journal(self):
        self.assertEqual(self.record(CHILD,AGENT,"no-answer","c",PARENT).reason,"unknown_parent")
        self.assertEqual(self.journal.list_events("shop-a",CHILD),[])

    def test_tenant_claim_on_child_ignored(self):
        self.record(PARENT,NUMBER,"no-answer","p")
        self.record(CHILD,AGENT,"no-answer","c",PARENT,tenant_id="shop-b")
        self.assertEqual(len(self.journal.list_events("shop-a",CHILD)),1)
        self.assertEqual(self.journal.list_events("shop-b",CHILD),[])

if __name__=="__main__":
    unittest.main()
