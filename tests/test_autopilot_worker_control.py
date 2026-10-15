"""Offline-only tests for persistent read-only worker control."""
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.observation_store import ObservationStore
from src.autopilot.recheck_worker import run_recheck
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
END = NOW - timedelta(minutes=20)


class CountingPager:
    def __init__(self):
        self.calls = 0

    def enumerate_all(self, parent_sid):
        self.calls += 1
        raise AssertionError("provider should not be contacted")


class WorkerControlTests(unittest.TestCase):
    def test_persistent_default_off_and_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "control.db")
            queue = RecheckQueue(path)
            queue.schedule("tenant", "parent", now=NOW)
            control = WorkerControl(path)
            pager = CountingPager()
            self.assertFalse(control.is_enabled())
            for expected in ("worker_disabled", "worker_disabled"):
                result = run_recheck(
                    path, "tenant", "parent", now=NOW,
                    call_ended_at=END, pager=pager, clock=lambda: NOW,
                    enabled=True, control=control,
                )
                self.assertEqual(result.reason, expected)
                control.set_enabled(False)
            control.set_enabled(True)
            self.assertTrue(WorkerControl(path).is_enabled())
            control.set_enabled(False)
            self.assertFalse(WorkerControl(path).is_enabled())
            result = run_recheck(
                path, "tenant", "parent", now=NOW,
                call_ended_at=END, pager=pager, clock=lambda: NOW,
                enabled=True, control=WorkerControl(path),
            )
            self.assertEqual(result.reason, "worker_disabled")
            self.assertEqual(pager.calls, 0)
            self.assertEqual(queue.due(now=NOW), [("tenant", "parent", 0, 4)])
            self.assertEqual(ObservationStore(path).load("tenant", "parent"), ())

    def test_enabled_flag_cannot_bypass_missing_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "control.db")
            queue = RecheckQueue(path)
            queue.schedule("tenant", "parent", now=NOW)
            pager = CountingPager()
            result = run_recheck(
                path, "tenant", "parent", now=NOW, call_ended_at=END,
                pager=pager, clock=lambda: NOW, enabled=True,
            )
            self.assertEqual(result.reason, "worker_disabled")
            self.assertEqual(pager.calls, 0)
            self.assertEqual(queue.due(now=NOW), [("tenant", "parent", 0, 4)])

    def test_stop_during_pagination_blocks_observation_and_preserves_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "control.db")
            queue = RecheckQueue(path)
            queue.schedule("tenant", "parent", now=NOW)
            control = WorkerControl(path)
            control.set_enabled(True)

            class RevokingPager:
                calls = 0
                def enumerate_all(self, parent_sid):
                    self.calls += 1
                    control.set_enabled(False)
                    from types import SimpleNamespace
                    return SimpleNamespace(
                        complete=True, reason="sdk_page_exhaustion",
                        child_sids=("CA" + "a" * 32,),
                    )

            pager = RevokingPager()
            result = run_recheck(
                path, "tenant", "parent", now=NOW, call_ended_at=END,
                pager=pager, clock=lambda: NOW, enabled=True, control=control,
            )
            self.assertEqual(result.reason, "worker_disabled")
            self.assertFalse(result.recorded)
            self.assertEqual(pager.calls, 1)
            self.assertEqual(ObservationStore(path).load("tenant", "parent"), ())
            self.assertEqual(queue.due(now=NOW), [("tenant", "parent", 0, 4)])

    def test_stop_during_failed_pagination_does_not_consume_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "control.db")
            queue = RecheckQueue(path)
            queue.schedule("tenant", "parent", now=NOW)
            control = WorkerControl(path)
            control.set_enabled(True)

            class RevokingPager:
                def enumerate_all(self, parent_sid):
                    control.set_enabled(False)
                    from types import SimpleNamespace
                    return SimpleNamespace(
                        complete=False, reason="provider_timeout", child_sids=(),
                    )

            result = run_recheck(
                path, "tenant", "parent", now=NOW, call_ended_at=END,
                pager=RevokingPager(), clock=lambda: NOW,
                enabled=True, control=control,
            )
            self.assertEqual(result.reason, "worker_disabled")
            self.assertEqual(queue.due(now=NOW), [("tenant", "parent", 0, 4)])

    def test_invalid_values_and_missing_table_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "control.db")
            control = WorkerControl(path)
            for invalid in (1, 0, None, "true"):
                with self.assertRaises(ValueError):
                    control.set_enabled(invalid)
            with sqlite3.connect(path) as db:
                db.execute("DROP TABLE worker_control")
            self.assertFalse(control.is_enabled())


if __name__ == "__main__":
    unittest.main()
