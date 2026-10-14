"""Disposable, synthetic, offline staging rehearsal. No Twilio SDK or SMS."""
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.observation_store import ObservationStore
from src.autopilot.recheck_worker import run_recheck

START = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
ENDED = START - timedelta(minutes=20)
CHILD = "CA" + "a" * 32


class OfflinePager:
    def __init__(self):
        self.calls = 0

    def enumerate_all(self, parent_sid):
        self.calls += 1
        return SimpleNamespace(
            complete=True, reason="sdk_page_exhaustion",
            child_sids=(CHILD,),
        )


class OfflineStagingRehearsal(unittest.TestCase):
    def test_disabled_default_then_review_only_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "synthetic.db")
            queue = RecheckQueue(db_path)
            store = ObservationStore(db_path)
            self.assertTrue(queue.schedule("synthetic-tenant", "synthetic-parent", now=START))
            pager = OfflinePager()

            disabled = run_recheck(
                db_path, "synthetic-tenant", "synthetic-parent",
                now=START, call_ended_at=ENDED, pager=pager,
                clock=lambda: START,
            )
            self.assertEqual(disabled.reason, "worker_disabled")
            self.assertEqual(pager.calls, 0)
            self.assertEqual(store.load("synthetic-tenant", "synthetic-parent"), ())

            first = run_recheck(
                db_path, "synthetic-tenant", "synthetic-parent",
                now=START, call_ended_at=ENDED, pager=pager,
                clock=lambda: START, enabled=True,
            )
            self.assertTrue(first.recorded)
            self.assertFalse(first.settled_for_review)
            self.assertEqual(first.reason, "insufficient_observations")

            later = START + timedelta(minutes=3)
            second = run_recheck(
                db_path, "synthetic-tenant", "synthetic-parent",
                now=later, call_ended_at=ENDED, pager=pager,
                clock=lambda: later, enabled=True,
            )
            self.assertTrue(second.recorded)
            self.assertTrue(second.settled_for_review)
            self.assertEqual(second.reason, "stable_history_for_review_only")
            self.assertEqual(pager.calls, 2)
            self.assertEqual(len(store.load("synthetic-tenant", "synthetic-parent")), 2)
            self.assertEqual(queue.due(now=later), [])
            # This test only exercises injected offline pagination and SQLite.
            # Review readiness is not consent or permission to send a message.


if __name__ == "__main__":
    unittest.main()
