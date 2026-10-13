import tempfile
import unittest
from pathlib import Path
from src.autopilot.queue import MessageQueue, QueuedMessage

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.q = MessageQueue(str(Path(self.tmp.name) / "queue.sqlite"))
        self.item = QueuedMessage("a:event-1", "a", "+15557654321", "Thanks for calling. Please reply if you need assistance.")

    def test_single_delivery(self):
        self.assertTrue(self.q.enqueue(self.item))
        self.assertFalse(self.q.enqueue(self.item))
        self.assertTrue(self.q.simulate_delivery(self.item.key, "a"))
        self.assertFalse(self.q.simulate_delivery(self.item.key, "a"))
        self.assertEqual(self.q.status(self.item.key, "a"), "simulated")

    def test_suppression(self):
        self.assertTrue(self.q.enqueue(self.item))
        self.q.suppress("a", self.item.recipient)
        self.assertFalse(self.q.simulate_delivery(self.item.key, "a"))
        self.assertEqual(self.q.status(self.item.key, "a"), "suppressed")
        self.assertFalse(self.q.enqueue(QueuedMessage("a:event-2", "a", self.item.recipient, "Hello")))

    def test_tenant_isolation(self):
        self.assertIsNone(self.q.status(self.item.key, "b"))
        self.assertFalse(self.q.enqueue(QueuedMessage("a:event-1", "b", self.item.recipient, "Hello")))

    def test_persists_across_restart(self):
        self.assertTrue(self.q.enqueue(self.item))
        reopened = MessageQueue(self.q.db_path)
        self.assertFalse(reopened.enqueue(self.item))
        self.assertEqual(reopened.status(self.item.key, "a"), "queued")

if __name__ == "__main__":
    unittest.main()
