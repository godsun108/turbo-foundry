import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from src.autopilot.call_journal import CallJournal
from src.autopilot.provider_audit import audit_parent_call
from src.autopilot.call_records import ProviderCallSnapshot

PARENT="CA"+"a"*32
CHILD="CA"+"b"*32
NUMBER="+15551234567"
NOW=datetime(2026,10,13,15,tzinfo=timezone.utc)
class Validator:
    def validate(self,url,params,signature): return True

class Provider:
    def __init__(self,**changes): self.changes=changes
    def fetch_call_snapshot(self,sid):
        values=dict(sid=sid,parent_sid=None if sid==PARENT else PARENT,
                    direction="inbound" if sid==PARENT else "outbound-dial",
                    status="no-answer",started_at=NOW,answered=None,
                    child_legs_complete=False,any_child_answered=None)
        values.update(self.changes.get(sid,{}))
        return ProviderCallSnapshot(**values)

class TestProviderAudit(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.journal=CallJournal(str(Path(tmp.name)/"journal.sqlite"))

    def add(self,sid,key,parent=""):
        params=dict(CallSid=sid,From="+15557654321",To=NUMBER,CallStatus="no-answer")
        if parent: params["ParentCallSid"]=parent
        self.journal.record_signed_callback(tenant_id="shop-a",provisioned_destination=NUMBER,
            url="https://example.test",params=params,signature="sig",
            auth_token="token",event_key=key,received_at=NOW,validator=Validator())

    def audit(self,provider=None):
        return audit_parent_call(journal=self.journal,provider_client=provider or Provider(),
                                 tenant_id="shop-a",parent_sid=PARENT)

    def test_no_local_history(self):
        self.assertEqual(self.audit().reason,"parent_missing")

    def test_valid_matching_snapshots_still_not_authoritative(self):
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        result=self.audit()
        self.assertFalse(result.consistent)
        self.assertEqual(result.reason,"provider_leg_completeness_unverified")
        self.assertEqual(result.checked_legs,2)

    def test_provider_parent_mismatch(self):
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        self.assertEqual(self.audit(Provider(**{PARENT:{"status":"completed"}})).reason,
                         "provider_parent_status_mismatch")

    def test_child_link_mismatch(self):
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        self.assertEqual(self.audit(Provider(**{CHILD:{"parent_sid":"CA"+"c"*32}})).reason,
                         "provider_child_link_mismatch")

    def test_child_answered_blocks(self):
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        self.assertEqual(self.audit(Provider(**{CHILD:{"status":"completed"}})).reason,
                         "provider_child_may_have_answered")

if __name__=="__main__":
    unittest.main()
