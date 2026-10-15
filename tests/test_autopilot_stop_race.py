"""Offline concurrency checks for SQLite stop/commit serialization."""
import os
import sqlite3
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone

from src.autopilot.atomic_observation import commit_observation
from src.autopilot.observation_store import ObservationStore
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.settlement import Observation
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
CHILD = "CA" + "a" * 32


class StopRaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, "test.db")
        self.queue = RecheckQueue(self.path)
        self.leases = RecheckLeases(self.path)
        self.store = ObservationStore(self.path)
        self.control = WorkerControl(self.path)
        self.control.set_enabled(True)
        self.queue.schedule("t", "p", now=NOW)
        self.token = self.leases.claim("t", "p", now=NOW)

    def tearDown(self):
        self.temp.cleanup()

    def test_stop_committed_first_blocks_observation(self):
        self.control.set_enabled(False)
        result = commit_observation(
            self.path, "t", "p", self.token, now=NOW,
            observation=Observation(NOW, (CHILD,), True),
            control=self.control,
        )
        self.assertFalse(result)
        self.assertEqual(self.store.load("t", "p"), ())
        self.assertEqual(self.queue.due(now=NOW), [("t", "p", 0, 4)])

    def test_stop_committed_first_blocks_retry_finish(self):
        self.control.set_enabled(False)
        self.assertFalse(self.leases.finish(
            "t", "p", self.token, now=NOW, reason="provider_timeout",
            control=self.control,
        ))
        self.assertEqual(self.queue.due(now=NOW), [("t", "p", 0, 4)])

    def test_stop_waits_for_active_writer_and_blocks_subsequent_commit(self):
        # Hold an SQLite write lock to verify stop updates serialize with
        # observation writes. No Twilio or external network is involved.
        acquired = threading.Event()
        failures = []

        def stopper():
            try:
                acquired.set()
                self.control.set_enabled(False)
            except Exception as exc:
                failures.append(exc)

        with sqlite3.connect(self.path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            worker = threading.Thread(target=stopper)
            worker.start()
            self.assertTrue(acquired.wait(timeout=2))
        worker.join(timeout=5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(failures, [])
        self.assertFalse(self.control.is_enabled())
        self.assertFalse(commit_observation(
            self.path, "t", "p", self.token, now=NOW,
            observation=Observation(NOW, (CHILD,), True),
            control=self.control,
        ))
        self.assertEqual(self.store.load("t", "p"), ())


if __name__ == "__main__":
    unittest.main()
