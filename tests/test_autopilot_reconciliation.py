import tempfile
import unittest
from pathlib import Path
from src.autopilot.queue import MessageQueue, QueuedMessage
from src.autopilot.reconciliation import ReconciliationStore
from src.autopilot.recovery import Outcome

class TestReconciliation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.queue = MessageQueue(str(Path(self.tmp.name) / "reconcile.sqlite"))
        self.queue.enqueue(QueuedMessage("a:evt", "a", "+15557654321", "test"))

    def test_unknown_held_and_persists(self):
        store = ReconciliationStore(self.queue)
        self.assertEqual(store.record("a:evt", "a", Outcome.UNKNOWN, provider_supports_idempotency=False), "hold")
        self.assertEqual(ReconciliationStore(self.queue).action("a:evt", "a"), "hold")

    def test_reconcile_if_provider_supports_lookup(self):
        store = ReconciliationStore(self.queue)
        self.assertEqual(store.record("a:evt", "a", Outcome.UNKNOWN, provider_supports_idempotency=True), "reconcile")

    def test_terminal_close_cannot_be_downgraded(self):
        store = ReconciliationStore(self.queue)
        self.assertEqual(store.record("a:evt", "a", Outcome.CONFIRMED_DELIVERED, provider_supports_idempotency=False), "close")
        self.assertEqual(store.record("a:evt", "a", Outcome.UNKNOWN, provider_supports_idempotency=False), "close")

    def test_tenant_isolation(self):
        store = ReconciliationStore(self.queue)
        self.assertEqual(store.record("a:evt", "b", Outcome.UNKNOWN, provider_supports_idempotency=False), "unknown_message")
        self.assertIsNone(store.action("a:evt", "b"))

if __name__ == "__main__":
    unittest.main()
