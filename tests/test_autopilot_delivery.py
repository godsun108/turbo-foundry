import tempfile
import unittest
from pathlib import Path
from src.autopilot.queue import MessageQueue, QueuedMessage
from src.autopilot.delivery import MockDelivery

class TestMockDelivery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.queue = MessageQueue(str(Path(self.tmp.name) / "delivery.sqlite"))
        self.worker = MockDelivery(self.queue)
        self.item = QueuedMessage("a:evt", "a", "+15557654321", "Example")
        self.queue.enqueue(self.item)

    def test_once(self):
        self.assertEqual(self.worker.attempt("a:evt", "a"), "simulated")
        self.assertEqual(self.worker.attempt("a:evt", "a"), "not_queued")

    def test_retry_then_success(self):
        self.assertEqual(self.worker.attempt("a:evt", "a", simulate_failure=True), "failed")
        self.assertEqual(self.worker.attempt("a:evt", "a"), "simulated")

    def test_exhausted(self):
        for expected in ("failed", "failed", "exhausted"):
            self.assertEqual(self.worker.attempt("a:evt", "a", simulate_failure=True), expected)
        self.assertEqual(self.queue.status("a:evt", "a"), "failed")
        self.assertEqual(self.worker.attempt("a:evt", "a"), "not_queued")

    def test_suppressed(self):
        self.queue.suppress("a", self.item.recipient)
        self.assertEqual(self.worker.attempt("a:evt", "a"), "not_queued")

    def test_tenant_boundary(self):
        self.assertEqual(self.worker.attempt("a:evt", "b"), "not_queued")

if __name__ == "__main__":
    unittest.main()
