import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from src.autopilot.call_journal import CallJournal
from src.autopilot.parent_routing import ParentCallRouting
from src.autopilot.routed_journal import record_routed_callback
from src.autopilot.call_replay import assess_call_history

PARENT="CA"+"a"*32
CHILD="CA"+"b"*32
NUMBER="+15551234567"
AGENT="+15559998888"
NOW=datetime(2026,10,13,15,tzinfo=timezone.utc)
class Validator:
    def __init__(self,valid=True): self.valid=valid
    def validate(self,url,params,signature): return self.valid

class TestRoutedJournal(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        db=str(Path(tmp.name)/"db.sqlite")
        self.routing=ParentCallRouting(db)
        self.journal=CallJournal(db)

    def record(self,sid,to,status,key,parent="",**overrides):
        params=dict(CallSid=sid,From="+15557654321",To=to,CallStatus=status)
        if parent: params["ParentCallSid"]=parent
        args=dict(routing=self.routing,journal=self.journal,
                  tenant_id="shop-a",provisioned_number=NUMBER,
                  url="https://example.test/status",params=params,signature="sig",
                  auth_token="token",event_key=key,received_at=NOW,validator=Validator())
        args.update(overrides)
        return record_routed_callback(**args)

    def test_forwarded_child_stored_with_parent(self):
        self.assertTrue(self.record(PARENT,NUMBER,"no-answer","p").recorded)
        self.assertTrue(self.record(CHILD,AGENT,"no-answer","c",PARENT).recorded)
        self.assertEqual(self.journal.list_events("shop-a",CHILD)[0][2],PARENT)
        self.assertTrue(assess_call_history(self.journal,"shop-a",PARENT).ready_for_review)

    def test_unknown_parent_rejected(self):
        self.assertEqual(self.record(CHILD,AGENT,"no-answer","c",PARENT).reason,"unknown_parent")

    def test_invalid_signature_rejected(self):
        self.record(PARENT,NUMBER,"no-answer","p")
        self.assertEqual(self.record(CHILD,AGENT,"no-answer","c",PARENT,validator=Validator(False)).reason,"invalid_signature")
        self.assertEqual(self.journal.list_events("shop-a",CHILD),[])

    def test_child_claimed_tenant_ignored(self):
        self.record(PARENT,NUMBER,"no-answer","p")
        self.record(CHILD,AGENT,"no-answer","c",PARENT,tenant_id="shop-b")
        self.assertEqual(len(self.journal.list_events("shop-a",CHILD)),1)
        self.assertEqual(self.journal.list_events("shop-b",CHILD),[])

    def test_replay_duplicate_rejected(self):
        self.record(PARENT,NUMBER,"no-answer","p")
        self.assertTrue(self.record(CHILD,AGENT,"no-answer","c",PARENT).recorded)
        self.assertEqual(self.record(CHILD,AGENT,"no-answer","c",PARENT).reason,"duplicate")

if __name__=="__main__":
    unittest.main()
