import hashlib
import hmac
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from src.autopilot.consent import ConsentStore
from src.autopilot.trusted_ingest import ingest_with_stored_consent
from src.autopilot.queue import MessageQueue
from src.autopilot.missed_call import Policy

NOW = datetime(2026,10,13,15,tzinfo=timezone.utc)
SECRET = b"offline-test-key"
POLICY = Policy("shop-a","America/New_York","+15551234567")
PHONE = "+15557654321"

def signed(**extras):
    payload = dict(tenant_id="shop-a",event_id="evt-1",caller=PHONE,destination=POLICY.approved_number,occurred_at=NOW.isoformat(),type="missed_call")
    payload.update(extras)
    raw = json.dumps(payload,sort_keys=True).encode()
    return raw,hmac.new(SECRET,raw,hashlib.sha256).hexdigest()

class TestStoredConsent(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        file=str(Path(self.tmp.name)/"data.sqlite")
        self.consent=ConsentStore(file)
        self.queue=MessageQueue(file)

    def ingest(self, **extras):
        raw,sig=signed(**extras)
        return ingest_with_stored_consent(raw,sig,SECRET,POLICY,self.queue,self.consent,NOW)

    def test_missing_consent_fails_closed(self):
        self.assertEqual(self.ingest().reason,"consent_missing")

    def test_verified_consent_allows_simulation(self):
        self.assertTrue(self.consent.grant_verified("shop-a",PHONE,"form-123","web_form",NOW))
        self.assertEqual(self.ingest().status,"simulated")
        self.assertEqual(self.ingest().status,"rejected")

    def test_revoked_consent_stays_revoked(self):
        self.consent.grant_verified("shop-a",PHONE,"form-123","web_form",NOW)
        self.consent.revoke("shop-a",PHONE)
        self.assertEqual(self.ingest().reason,"suppressed")
        self.assertFalse(self.consent.grant_verified("shop-a",PHONE,"form-456","web_form",NOW))

    def test_tenant_separation(self):
        self.consent.grant_verified("shop-b",PHONE,"other-form","web_form",NOW)
        self.assertEqual(self.ingest().reason,"consent_missing")

    def test_tenant_claim_not_authorized(self):
        self.consent.grant_verified("shop-a",PHONE,"form-123","web_form",NOW)
        self.assertEqual(self.ingest(tenant_id="shop-b").reason,"unapproved_tenant_or_destination")

    def test_persistence(self):
        self.consent.grant_verified("shop-a",PHONE,"form-123","web_form",NOW)
        reopened=ConsentStore(self.consent.db_path)
        self.assertEqual(reopened.lookup("shop-a",PHONE).evidence_reference,"form-123")

    def test_no_anonymous_or_naive_grants(self):
        self.assertFalse(self.consent.grant_verified("shop-a",PHONE,"","web_form",NOW))
        self.assertFalse(self.consent.grant_verified("shop-a",PHONE,"id","web_form",datetime(2026,10,13)))

if __name__ == "__main__":
    unittest.main()
