import tempfile
import unittest
from pathlib import Path
from src.autopilot.parent_routing import ParentCallRouting

PARENT="CA"+"a"*32
CHILD="CA"+"b"*32
NUMBER="+15551234567"
URL="https://example.test/twilio"
class Validator:
    def __init__(self,valid=True): self.valid=valid
    def validate(self,url,params,signature): return self.valid

def event(sid,to,parent=""):
    d=dict(CallSid=sid,From="+15557654321",To=to,CallStatus="no-answer")
    if parent:d["ParentCallSid"]=parent
    return d

class TestParentRouting(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.routing=ParentCallRouting(str(Path(tmp.name)/"routing.sqlite"))

    def parent(self, **overrides):
        kwargs=dict(tenant_id="shop-a",provisioned_number=NUMBER,url=URL,
                    params=event(PARENT,NUMBER),signature="sig",
                    auth_token="token",validator=Validator())
        kwargs.update(overrides)
        return self.routing.register_parent(**kwargs)

    def child(self, **overrides):
        kwargs=dict(url=URL,params=event(CHILD,"+15559998888",PARENT),
                    signature="sig",auth_token="token",validator=Validator())
        kwargs.update(overrides)
        return self.routing.route_child(**kwargs)

    def test_child_routes_to_parent_tenant(self):
        self.assertTrue(self.parent().accepted)
        result=self.child()
        self.assertTrue(result.accepted)
        self.assertEqual(result.tenant_id,"shop-a")

    def test_unknown_parent_fails_closed(self):
        self.assertEqual(self.child().reason,"unknown_parent")

    def test_wrong_parent_destination(self):
        self.assertEqual(self.parent(provisioned_number="+15550000000").reason,"invalid_parent_route")

    def test_invalid_parent_signature(self):
        self.assertEqual(self.parent(validator=Validator(False)).reason,"invalid_signature")

    def test_invalid_child_signature(self):
        self.parent()
        self.assertEqual(self.child(validator=Validator(False)).reason,"invalid_signature")

    def test_idempotent_child(self):
        self.parent()
        self.assertEqual(self.child().reason,"child_routed")
        self.assertEqual(self.child().reason,"existing_child")

    def test_parent_conflict(self):
        self.parent()
        self.assertEqual(self.parent(tenant_id="shop-b").reason,"parent_conflict")

    def test_child_conflict(self):
        self.parent()
        self.child()
        self.assertEqual(self.child(params=event(CHILD,"+15559998888","CA"+"c"*32)).reason,"unknown_parent")

if __name__=="__main__": unittest.main()
