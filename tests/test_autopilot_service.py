import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from src.autopilot.missed_call import Policy, MissedCall
from src.autopilot.queue import MessageQueue
from src.autopilot.service import process_missed_call

NOW = datetime(2026, 10, 13, 15, tzinfo=timezone.utc)
POLICY = Policy("a", "America/New_York", "+15551234567")
EVENT = MissedCall("call-1", "a", "+15557654321", "+15551234567", NOW, True, True)

class TestService(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.queue = MessageQueue(str(Path(self.tmp.name) / "service.sqlite"))

    def test_end_to_end_once(self):
        first = process_missed_call(EVENT, POLICY, self.queue, NOW)
        second = process_missed_call(EVENT, POLICY, self.queue, NOW)
        self.assertEqual(first.status, "simulated")
        self.assertEqual(second.status, "rejected")
        self.assertEqual(self.queue.status("a:call-1", "a"), "simulated")

    def test_unverified_webhook_rejected(self):
        result = process_missed_call(replace(EVENT, signature_valid=False), POLICY, self.queue, NOW)
        self.assertEqual(result.reason, "invalid_signature")
        self.assertIsNone(self.queue.status("a:call-1", "a"))

    def test_opt_out_before_queue(self):
        self.queue.suppress("a", EVENT.caller)
        result = process_missed_call(EVENT, POLICY, self.queue, NOW)
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.reason, "duplicate_or_suppressed")

    def test_no_consent(self):
        result = process_missed_call(replace(EVENT, consent_evidence=False), POLICY, self.queue, NOW)
        self.assertEqual(result.reason, "consent_missing")

if __name__ == "__main__":
    unittest.main()
