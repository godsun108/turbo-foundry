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
    class Calls:
        def __init__(self,owner): self.owner=owner
        def list(self,*,parent_call_sid,limit):
            from types import SimpleNamespace
            return [SimpleNamespace(sid=sid,parent_call_sid=parent_call_sid)
                    for sid in self.owner.child_sids][:limit]
    def __init__(self,child_sids=(CHILD,),**changes):
        self.changes=changes
        self.child_sids=child_sids
        self.calls=self.Calls(self)
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

    def test_provider_extra_child_blocks(self):
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        result=self.audit(Provider(child_sids=(CHILD,"CA"+"d"*32)))
        self.assertEqual(result.reason,"provider_children_missing_from_journal")

    def test_local_extra_child_blocks(self):
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        result=self.audit(Provider(child_sids=()))
        self.assertEqual(result.reason,"journal_children_missing_from_provider")

    def test_explicit_pagination_reconciliation(self):
        from types import SimpleNamespace
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        def fetch(parent,cursor,size):
            return ([SimpleNamespace(sid=CHILD,parent_call_sid=PARENT)],None)
        result=audit_parent_call(journal=self.journal,provider_client=Provider(),
                                 tenant_id="shop-a",parent_sid=PARENT,fetch_page=fetch)
        self.assertFalse(result.consistent)
        self.assertEqual(result.reason,"provider_leg_completeness_unverified")
        self.assertEqual(result.checked_legs,2)

    def test_explicit_pagination_timeout(self):
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        def fetch(parent,cursor,size): raise TimeoutError()
        result=audit_parent_call(journal=self.journal,provider_client=Provider(),
                                 tenant_id="shop-a",parent_sid=PARENT,fetch_page=fetch)
        self.assertEqual(result.reason,"enumeration_provider_timeout")

    def test_sdk_pager_reconciles(self):
        from src.autopilot.twilio_paging import TwilioCallPager
        from types import SimpleNamespace
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        class Page:
            next_page_url=None
            def __iter__(self):
                return iter([SimpleNamespace(sid=CHILD,parent_call_sid=PARENT,
                                             account_sid="AC"+"a"*32)])
        class Calls:
            def page(self,**kwargs): return Page()
        class Client:
            calls=Calls()
        pager=TwilioCallPager(Client(),"AC"+"a"*32)
        result=audit_parent_call(journal=self.journal,provider_client=Provider(),
                                 tenant_id="shop-a",parent_sid=PARENT,sdk_pager=pager)
        self.assertEqual(result.reason,"provider_leg_completeness_unverified")
        self.assertFalse(result.consistent)

    def test_sdk_pager_account_mismatch_blocks(self):
        from src.autopilot.twilio_paging import TwilioCallPager
        from types import SimpleNamespace
        self.add(PARENT,"p")
        self.add(CHILD,"c",PARENT)
        class Page:
            next_page_url=None
            def __iter__(self):
                return iter([SimpleNamespace(sid=CHILD,parent_call_sid=PARENT,
                                             account_sid="AC"+"d"*32)])
        class Calls:
            def page(self,**kwargs): return Page()
        class Client:
            calls=Calls()
        pager=TwilioCallPager(Client(),"AC"+"a"*32)
        result=audit_parent_call(journal=self.journal,provider_client=Provider(),
                                 tenant_id="shop-a",parent_sid=PARENT,sdk_pager=pager)
        self.assertEqual(result.reason,"enumeration_account_mismatch")

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
