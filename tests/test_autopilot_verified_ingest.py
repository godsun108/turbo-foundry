import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from src.autopilot.verified_ingest import VerifiedAtomicIngest
from src.autopilot.provisioning import NumberProvisioning
from src.autopilot.call_journal import CallJournal

ACCOUNT="AC"+"a"*32
UNKNOWN="AC"+"b"*32
CALL="CA"+"c"*32
NUMBER="+15551234567"
NOW=datetime(2026,10,13,15,tzinfo=timezone.utc)
class Validator:
    def __init__(self,valid): self.valid=valid
    def validate(self,url,params,signature): return self.valid

class TestVerifiedIngest(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db=str(Path(tmp.name)/"verified.sqlite")
        self.ingest=VerifiedAtomicIngest(self.db,{ACCOUNT:"trusted-token"})
        NumberProvisioning(self.db).provision(phone_number=NUMBER,tenant_id="shop-a",
                                              provider_account_sid=ACCOUNT)

    def record(self,**overrides):
        args=dict(tenant_id="shop-a",provisioned_number=NUMBER,
                  url="https://example.test/twilio",
                  params=dict(AccountSid=ACCOUNT,CallSid=CALL,From="+15557654321",
                              To=NUMBER,CallStatus="no-answer"),
                  signature="sig",event_key="event-1",received_at=NOW,
                  validator_factory=lambda token:Validator(token=="trusted-token"))
        args.update(overrides)
        return self.ingest.record(**args)

    def test_authenticated_parent_persisted(self):
        self.assertTrue(self.record().recorded)

    def test_unknown_account_fails_closed(self):
        params=dict(AccountSid=UNKNOWN,CallSid=CALL,From="+15557654321",
                    To=NUMBER,CallStatus="no-answer")
        self.assertEqual(self.record(params=params).reason,"unknown_account")
        self.assertEqual(CallJournal(self.db).list_events("shop-a",CALL),[])

    def test_invalid_signature_fails_closed(self):
        self.assertEqual(self.record(validator_factory=lambda token:Validator(False)).reason,
                         "invalid_signature_or_event")
        self.assertEqual(CallJournal(self.db).list_events("shop-a",CALL),[])

    def test_duplicate(self):
        self.assertTrue(self.record().recorded)
        self.assertEqual(self.record().reason,"duplicate")

    def test_disabled_provisioning(self):
        NumberProvisioning(self.db).disable(NUMBER)
        self.assertEqual(self.record().reason,"unverified_provisioning")

if __name__=="__main__":
    unittest.main()
