"""Offline operator stop/restart rehearsal with synthetic data only.

Runs under unittest and never imports Twilio, opens a network connection,
sends SMS, charges customers, or schedules background work.
"""
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from src.autopilot.observation_store import ObservationStore
from src.autopilot.recheck_metrics import snapshot_recheck_metrics
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_worker import run_recheck
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 14, tzinfo=timezone.utc)
ENDED = NOW - timedelta(minutes=20)
CHILD = "CA" + "a" * 32


class CountingOfflinePager:
    def __init__(self):
        self.calls = 0

    def enumerate_all(self, parent_sid):
        self.calls += 1
        return SimpleNamespace(
            complete=True,
            reason="sdk_page_exhaustion",
            child_sids=(CHILD,),
        )


class OperatorRehearsalTests(unittest.TestCase):
    def test_enable_observe_stop_block_reopen_and_monitor(self):
        with tempfile.TemporaryDirectory() as temp:
            db = os.path.join(temp, "synthetic-operator.db")
            queue = RecheckQueue(db)
            observations = ObservationStore(db)
            control = WorkerControl(db)
            pager = CountingOfflinePager()
            self.assertTrue(queue.schedule("synthetic-a", "parent-a", now=NOW))
            self.assertFalse(control.is_enabled())

            initial = snapshot_recheck_metrics(db, "synthetic-a", now=NOW)
            self.assertEqual((initial.pending, initial.due), (1, 1))
            self.assertEqual(snapshot_recheck_metrics(db, "synthetic-b", now=NOW).pending, 0)

            control.set_enabled(True)
            first = run_recheck(
                db, "synthetic-a", "parent-a", now=NOW, call_ended_at=ENDED,
                pager=pager, clock=lambda: NOW, enabled=True, control=control,
            )
            self.assertTrue(first.recorded)
            self.assertFalse(first.settled_for_review)
            self.assertEqual(first.reason, "insufficient_observations")
            self.assertEqual(pager.calls, 1)
            self.assertEqual(len(observations.load("synthetic-a", "parent-a")), 1)

            # Revoke authorization and recreate the operator control object
            # to verify that disabled state survives reopening the database.
            control.set_enabled(False)
            restarted_control = WorkerControl(db)
            self.assertFalse(restarted_control.is_enabled())
            later = NOW + timedelta(minutes=3)
            blocked = run_recheck(
                db, "synthetic-a", "parent-a", now=later, call_ended_at=ENDED,
                pager=pager, clock=lambda: later, enabled=True,
                control=restarted_control,
            )
            self.assertEqual(blocked.reason, "worker_disabled")
            self.assertFalse(blocked.recorded)
            self.assertEqual(pager.calls, 1)
            self.assertEqual(len(observations.load("synthetic-a", "parent-a")), 1)

            metrics = snapshot_recheck_metrics(db, "synthetic-a", now=later)
            self.assertEqual((metrics.pending, metrics.due), (1, 1))
            self.assertEqual((metrics.exhausted, metrics.complete), (0, 0))
            self.assertEqual((metrics.active_leases, metrics.expired_leases), (0, 0))
            self.assertEqual(snapshot_recheck_metrics(db, "synthetic-b", now=later).due, 0)
            self.assertEqual(queue.due(now=later), [("synthetic-a", "parent-a", 1, 4)])
            # No consent, provider authorization, or messaging action occurs here.


if __name__ == "__main__":
    unittest.main()
