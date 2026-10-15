"""Synthetic offline operator metrics tests: no provider, SMS, or billing."""
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.recheck_metrics import snapshot_recheck_metrics
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)


class MetricsTests(unittest.TestCase):
    def test_tenant_isolation_and_lease_expiry(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "metrics.db")
            queue = RecheckQueue(db_path)
            leases = RecheckLeases(db_path)
            control = WorkerControl(db_path)
            control.set_enabled(True)
            queue.schedule("a", "a1", now=NOW)
            queue.schedule("a", "a2", now=NOW)
            queue.schedule("b", "b1", now=NOW)
            token = leases.claim("a", "a1", now=NOW, lease_seconds=10, control=control)
            self.assertTrue(token)
            self.assertTrue(leases.finish(
                "a", "a2", "invalid", now=NOW, reason="none", control=control
            ) is False)
            queue.record_attempt("b", "b1", now=NOW, reason="simulated_timeout")
            at_start = snapshot_recheck_metrics(db_path, "a", now=NOW)
            self.assertEqual(at_start.pending, 2)
            self.assertEqual(at_start.due, 2)
            self.assertEqual(at_start.active_leases, 1)
            self.assertEqual(at_start.expired_leases, 0)
            self.assertEqual(at_start.exhausted, 0)
            self.assertEqual(snapshot_recheck_metrics(db_path, "b", now=NOW).due, 0)
            after = snapshot_recheck_metrics(db_path, "a", now=NOW + timedelta(seconds=11))
            self.assertEqual(after.active_leases, 0)
            self.assertEqual(after.expired_leases, 1)

    def test_missing_db_fails_without_creating_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "missing.db")
            with self.assertRaises(sqlite3.OperationalError):
                snapshot_recheck_metrics(path, "tenant", now=NOW)
            self.assertFalse(os.path.exists(path))

    def test_invalid_time_rejected(self):
        with self.assertRaises(ValueError):
            snapshot_recheck_metrics("missing.db", "tenant", now=NOW.replace(tzinfo=None))


if __name__ == "__main__":
    unittest.main()
