import unittest
from src.autopilot.recovery import Outcome, decide_recovery

class TestRecovery(unittest.TestCase):
    def test_unknown_without_idempotency_is_held(self):
        self.assertEqual(decide_recovery(Outcome.UNKNOWN, provider_supports_idempotency=False).action, "hold")

    def test_unknown_with_idempotency_requires_reconciliation(self):
        self.assertEqual(decide_recovery(Outcome.UNKNOWN, provider_supports_idempotency=True).action, "reconcile")

    def test_known_absence_can_retry(self):
        self.assertEqual(decide_recovery(Outcome.UNKNOWN, provider_supports_idempotency=False, lookup_confirms_absence=True).action, "retry")

    def test_not_submitted_can_retry(self):
        self.assertEqual(decide_recovery(Outcome.NOT_SUBMITTED, provider_supports_idempotency=False).action, "retry")

    def test_delivered_closes(self):
        self.assertEqual(decide_recovery(Outcome.CONFIRMED_DELIVERED, provider_supports_idempotency=False).action, "close")

    def test_rejected_stops(self):
        self.assertEqual(decide_recovery(Outcome.CONFIRMED_REJECTED, provider_supports_idempotency=False).action, "stop")

if __name__ == "__main__":
    unittest.main()
