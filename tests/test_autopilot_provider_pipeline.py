import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from src.autopilot.provider_pipeline import TrustedCallRecord, process_authenticated_provider_event
from src.autopilot.consent import ConsentStore
from src.autopilot.missed_call import Policy
from src.autopilot.queue import MessageQueue

NOW = datetime(2026, 10, 13, 15, tzinfo=timezone.utc)
URL = "https://example.test/twilio/status"
SID = "CA" + "a" * 32
PHONE = "+15557654321"
POLICY = Policy("shop-a", "America/New_York", "+15551234567")
PARAMS = {"CallSid": SID, "From": PHONE, "To": POLICY.approved_number, "CallStatus": "no-answer"}

class Validator:
    def __init__(self, valid=True):
        self.valid = valid
    def validate(self, url, params, signature):
        return self.valid

class TestProviderPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        db = str(Path(self.tmp.name) / "data.sqlite")
        self.queue = MessageQueue(db)
        self.consent = ConsentStore(db)
        self.record = TrustedCallRecord(SID, True, False, True, NOW)

    def run_event(self, *, params=PARAMS, record=None, validator=None):
        return process_authenticated_provider_event(
            URL, params, "sig", "token", policy=POLICY, queue=self.queue,
            consent=self.consent, record=self.record if record is None else record,
            now=NOW, validator=validator if validator is not None else Validator(),
        )

    def test_requires_consent(self):
        self.assertEqual(self.run_event().reason, "consent_missing")

    def test_simulated_once_with_consent(self):
        self.consent.grant_verified(POLICY.tenant_id, PHONE, "optin-123", "web_form", NOW)
        self.assertEqual(self.run_event().status, "simulated")
        self.assertEqual(self.run_event().status, "rejected")

    def test_untrusted_record_rejected(self):
        record = TrustedCallRecord(SID, True, False, False, NOW)
        self.assertEqual(self.run_event(record=record).reason, "trusted_call_record_required")

    def test_sid_mismatch_rejected(self):
        record = TrustedCallRecord("CA" + "b"*32, True, False, True, NOW)
        self.assertEqual(self.run_event(record=record).reason, "call_record_mismatch")

    def test_signature_failure_rejected(self):
        self.assertEqual(self.run_event(validator=Validator(False)).reason, "invalid_provider_callback")

    def test_completed_not_missed(self):
        self.assertEqual(self.run_event(params=dict(PARAMS, CallStatus="completed")).reason, "answered_or_unresolved")

    def test_opt_out_rejected(self):
        self.consent.grant_verified(POLICY.tenant_id, PHONE, "optin-123", "web_form", NOW)
        self.consent.revoke(POLICY.tenant_id, PHONE)
        self.assertEqual(self.run_event().reason, "suppressed")

    def test_answered_elsewhere_rejected(self):
        record = TrustedCallRecord(SID, True, True, True, NOW)
        self.assertEqual(self.run_event(record=record).reason, "answered_elsewhere")

if __name__ == "__main__":
    unittest.main()
