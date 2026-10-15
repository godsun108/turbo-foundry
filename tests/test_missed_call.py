import unittest
from dataclasses import replace
from datetime import datetime, timezone
from src.autopilot.missed_call import Policy, MissedCall, evaluate

NOW = datetime(2026, 10, 13, 15, 0, tzinfo=timezone.utc)
POLICY = Policy("tenant-a", "America/New_York", "+15551234567")
EVENT = MissedCall("evt-1", "tenant-a", "+15557654321", "+15551234567", NOW, True, True)

class TestMissedCall(unittest.TestCase):
    def test_eligible(self):
        result = evaluate(EVENT, POLICY, NOW)
        self.assertTrue(result.eligible)
        self.assertEqual(result.idempotency_key, "tenant-a:evt-1")

    def test_invalid_signature(self):
        self.assertEqual(evaluate(replace(EVENT, signature_valid=False), POLICY, NOW).reason, "invalid_signature")

    def test_cross_tenant(self):
        self.assertEqual(evaluate(replace(EVENT, tenant_id="tenant-b"), POLICY, NOW).reason, "unknown_tenant")

    def test_no_consent(self):
        self.assertEqual(evaluate(replace(EVENT, consent_evidence=False), POLICY, NOW).reason, "consent_missing")

    def test_opt_out(self):
        self.assertEqual(evaluate(replace(EVENT, opted_out=True), POLICY, NOW).reason, "suppressed")

    def test_duplicate(self):
        self.assertEqual(evaluate(replace(EVENT, previously_processed=True), POLICY, NOW).reason, "duplicate")

    def test_frequency_cap(self):
        self.assertEqual(evaluate(replace(EVENT, recent_message_sent=True), POLICY, NOW).reason, "frequency_capped")

    def test_quiet_hours(self):
        self.assertEqual(evaluate(replace(EVENT, occurred_at=NOW.replace(hour=3)), POLICY, NOW.replace(hour=3)).reason, "quiet_hours")

    def test_wrong_destination(self):
        self.assertEqual(evaluate(replace(EVENT, destination="+15550000000"), POLICY, NOW).reason, "unapproved_destination")

    def test_missing_timezone(self):
        self.assertEqual(evaluate(EVENT, POLICY, NOW.replace(tzinfo=None)).reason, "timezone_missing")

if __name__ == "__main__":
    unittest.main()
