import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from src.autopilot.call_journal import CallJournal
from src.autopilot.call_replay import assess_call_history

PARENT="CA"+"a"*32
CHILD="CA"+"b"*32
NUMBER="+15551234567"
NOW=datetime(2026,10,13,15,tzinfo=timezone.utc)
class Validator:
    def validate(self,url,params,signature): return True

class TestReplay(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.journal=CallJournal(str(Path(tmp.name)/"journal.sqlite"))

    def record(self,sid,status,key,parent=""):
        params=dict(CallSid=sid,From="+15557654321",To=NUMBER,CallStatus=status)
        if parent: params["ParentCallSid"]=parent
        result=self.journal.record_signed_callback(
            tenant_id="shop-a",provisioned_destination=NUMBER,
            url="https://example.test/status",params=params,signature="sig",
            auth_token="token",event_key=key,received_at=NOW,validator=Validator())
        self.assertTrue(result.recorded)

    def test_missing_parent(self):
        self.assertEqual(assess_call_history(self.journal,"shop-a",PARENT).reason,"parent_missing")

    def test_parent_only(self):
        self.record(PARENT,"no-answer","p")
        self.assertEqual(assess_call_history(self.journal,"shop-a",PARENT).reason,"child_evidence_missing")

    def test_candidate_only_for_review(self):
        self.record(PARENT,"no-answer","p")
        self.record(CHILD,"no-answer","c",PARENT)
        r=assess_call_history(self.journal,"shop-a",PARENT)
        self.assertTrue(r.ready_for_review)
        self.assertEqual(r.reason,"candidate_for_manual_review_only")

    def test_answered_child_blocks(self):
        self.record(PARENT,"no-answer","p")
        self.record(CHILD,"completed","c",PARENT)
        self.assertEqual(assess_call_history(self.journal,"shop-a",PARENT).reason,"child_may_have_answered")

    def test_parent_completed_blocks(self):
        self.record(PARENT,"completed","p")
        self.record(CHILD,"no-answer","c",PARENT)
        self.assertEqual(assess_call_history(self.journal,"shop-a",PARENT).reason,"parent_completed")

    def test_tenant_isolation(self):
        self.record(PARENT,"no-answer","p")
        self.record(CHILD,"no-answer","c",PARENT)
        self.assertEqual(assess_call_history(self.journal,"shop-b",PARENT).reason,"parent_missing")

    def test_child_ringing_blocks(self):
        self.record(PARENT,"no-answer","p")
        self.record(CHILD,"ringing","c",PARENT)
        self.assertEqual(assess_call_history(self.journal,"shop-a",PARENT).reason,"child_nonterminal")

if __name__=="__main__": unittest.main()
