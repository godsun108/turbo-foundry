import hashlib
import hmac
import json
import unittest
from datetime import datetime, timezone, timedelta
from src.autopilot.webhook import verify_mock_webhook

NOW = datetime(2026, 10, 13, 15, tzinfo=timezone.utc)
SECRET = b"local-test-only-secret"
PAYLOAD = {"tenant_id":"a","event_id":"evt-1","caller":"+15557654321","destination":"+15551234567","occurred_at":NOW.isoformat(),"type":"missed_call"}

def signed(payload):
    raw = json.dumps(payload, sort_keys=True).encode()
    return raw, hmac.new(SECRET, raw, hashlib.sha256).hexdigest()

class TestWebhook(unittest.TestCase):
    def test_valid_signature(self):
        raw, signature = signed(PAYLOAD)
        self.assertEqual(verify_mock_webhook(raw, signature, SECRET, NOW).event_id, "evt-1")

    def test_tampered_body(self):
        raw, signature = signed(PAYLOAD)
        self.assertIsNone(verify_mock_webhook(raw + b" ", signature, SECRET, NOW))

    def test_invalid_signature(self):
        raw, _ = signed(PAYLOAD)
        self.assertIsNone(verify_mock_webhook(raw, "0"*64, SECRET, NOW))

    def test_stale_event(self):
        payload = dict(PAYLOAD, occurred_at=(NOW-timedelta(minutes=10)).isoformat())
        raw, signature = signed(payload)
        self.assertIsNone(verify_mock_webhook(raw, signature, SECRET, NOW))

    def test_wrong_event_type(self):
        raw, signature = signed(dict(PAYLOAD, type="answered_call"))
        self.assertIsNone(verify_mock_webhook(raw, signature, SECRET, NOW))

    def test_unexpected_field(self):
        raw, signature = signed(dict(PAYLOAD, injected="data"))
        self.assertIsNone(verify_mock_webhook(raw, signature, SECRET, NOW))

    def test_empty_secret(self):
        raw, signature = signed(PAYLOAD)
        self.assertIsNone(verify_mock_webhook(raw, signature, b"", NOW))

if __name__ == "__main__":
    unittest.main()
