import hashlib
import hmac
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from src.autopilot.ingest import ingest_signed_mock_event
from src.autopilot.missed_call import Policy
from src.autopilot.queue import MessageQueue

NOW = datetime(2026, 10, 13, 15, tzinfo=timezone.utc)
SECRET = b"test-key"
POLICY = Policy("a", "America/New_York", "+15551234567")
PAYLOAD = {"tenant_id": "a", "event_id": "evt-1", "caller": "+15557654321", "destination": "+15551234567", "occurred_at": NOW.isoformat(), "type": "missed_call"}

def signed(payload):
    raw = json.dumps(payload, sort_keys=True).encode()
    return raw, hmac.new(SECRET, raw, hashlib.sha256).hexdigest()

class TestIngest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.queue = MessageQueue(str(Path(self.tmp.name) / "test.sqlite"))

    def test_authenticated_once(self):
        raw, sig = signed(PAYLOAD)
        first = ingest_signed_mock_event(raw, sig, SECRET, POLICY, self.queue, NOW, consent_evidence=True)
        second = ingest_signed_mock_event(raw, sig, SECRET, POLICY, self.queue, NOW, consent_evidence=True)
        self.assertEqual(first.status, "simulated")
        self.assertEqual(second.status, "rejected")
        self.assertEqual(self.queue.status("a:evt-1", "a"), "simulated")

    def test_rejects_tampering(self):
        raw, sig = signed(PAYLOAD)
        result = ingest_signed_mock_event(raw + b" ", sig, SECRET, POLICY, self.queue, NOW, consent_evidence=True)
        self.assertEqual(result.reason, "unverified_webhook")

    def test_consent_fail_closed(self):
        raw, sig = signed(PAYLOAD)
        result = ingest_signed_mock_event(raw, sig, SECRET, POLICY, self.queue, NOW)
        self.assertEqual(result.reason, "consent_missing")

    def test_cross_tenant(self):
        raw, sig = signed(dict(PAYLOAD, tenant_id="b"))
        result = ingest_signed_mock_event(raw, sig, SECRET, POLICY, self.queue, NOW, consent_evidence=True)
        self.assertEqual(result.reason, "unknown_tenant")

    def test_suppression(self):
        self.queue.suppress("a", PAYLOAD["caller"])
        raw, sig = signed(PAYLOAD)
        result = ingest_signed_mock_event(raw, sig, SECRET, POLICY, self.queue, NOW, consent_evidence=True)
        self.assertEqual(result.status, "rejected")

if __name__ == "__main__":
    unittest.main()
