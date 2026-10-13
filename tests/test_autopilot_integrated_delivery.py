import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from src.autopilot.delivery import MockDelivery
from src.autopilot.missed_call import MissedCall, Policy
from src.autopilot.queue import MessageQueue, QueuedMessage
from src.autopilot.service import process_missed_call

NOW = datetime(2026, 10, 13, 15, tzinfo=timezone.utc)
POLICY = Policy("tenant-a", "America/New_York", "+15551234567")
EVENT = MissedCall("evt-1", "tenant-a", "+15557654321", "+15551234567", NOW, True, True)

class TestIntegratedDelivery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.queue = MessageQueue(str(Path(self.tmp.name) / "integrated.sqlite"))

    def test_service_uses_delivery_attempt_record(self):
        result = process_missed_call(EVENT, POLICY, self.queue, NOW)
        self.assertEqual(result.status, "simulated")
        with self.queue._connect() as db:
            record = db.execute("SELECT attempts,state FROM delivery_attempts WHERE key=?", ("tenant-a:evt-1",)).fetchone()
        self.assertEqual(record, (1, "simulated"))

    def test_retry_persists_across_worker_recreation(self):
        item = QueuedMessage("tenant-a:retry", "tenant-a", EVENT.caller, "Hello")
        self.assertTrue(self.queue.enqueue(item))
        self.assertEqual(MockDelivery(self.queue).attempt(item.key, item.tenant_id, simulate_failure=True), "failed")
        self.assertEqual(MockDelivery(self.queue).attempt(item.key, item.tenant_id), "simulated")

    def test_suppression_between_attempts(self):
        item = QueuedMessage("tenant-a:stop", "tenant-a", EVENT.caller, "Hello")
        self.assertTrue(self.queue.enqueue(item))
        self.assertEqual(MockDelivery(self.queue).attempt(item.key, item.tenant_id, simulate_failure=True), "failed")
        self.queue.suppress(item.tenant_id, item.recipient)
        self.assertEqual(MockDelivery(self.queue).attempt(item.key, item.tenant_id), "not_queued")

if __name__ == "__main__":
    unittest.main()
