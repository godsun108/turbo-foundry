"""Synthetic database backup/restore rehearsal; no live credentials or network."""
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from src.autopilot.observation_store import ObservationStore
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.recheck_metrics import snapshot_recheck_metrics
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_worker import run_recheck
from src.autopilot.sqlite_backup import backup_readonly_state
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 18, tzinfo=timezone.utc)
END = NOW - timedelta(minutes=20)


class OfflinePager:
    def enumerate_all(self, parent_sid):
        return SimpleNamespace(complete=True, reason="sdk_page_exhaustion",
                               child_sids=("CA" + "a"*32,))


class BackupRehearsalTests(unittest.TestCase):
    def test_restore_preserves_stop_observation_and_pending_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "state.db")
            backup = os.path.join(tmp, "safe-copy.db")
            queue = RecheckQueue(source)
            RecheckLeases(source)
            store = ObservationStore(source)
            control = WorkerControl(source)
            queue.schedule("tenant", "parent", now=NOW)
            control.set_enabled(True)
            result = run_recheck(source, "tenant", "parent", now=NOW,
                                 call_ended_at=END, pager=OfflinePager(),
                                 clock=lambda: NOW, enabled=True, control=control)
            self.assertTrue(result.recorded)
            control.set_enabled(False)
            snapshot = snapshot_recheck_metrics(source, "tenant",
                                                now=NOW + timedelta(minutes=3))
            before = store.load("tenant", "parent")
            backup_readonly_state(source, backup)
            self.assertEqual(snapshot_recheck_metrics(
                backup, "tenant", now=NOW + timedelta(minutes=3)), snapshot)
            self.assertEqual(ObservationStore(backup).load("tenant", "parent"), before)
            restored_control = WorkerControl(backup)
            self.assertFalse(restored_control.is_enabled())
            blocked = run_recheck(backup, "tenant", "parent",
                                  now=NOW + timedelta(minutes=3),
                                  call_ended_at=END, pager=OfflinePager(),
                                  clock=lambda: NOW + timedelta(minutes=3),
                                  enabled=True, control=restored_control)
            self.assertEqual(blocked.reason, "worker_disabled")
            self.assertEqual(RecheckQueue(backup).due(
                now=NOW + timedelta(minutes=3)), [("tenant", "parent", 1, 4)])

    def test_missing_source_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "missing.db")
            dst = os.path.join(tmp, "backup.db")
            with self.assertRaises(FileNotFoundError):
                backup_readonly_state(src, dst)
            self.assertFalse(os.path.exists(dst))
            with sqlite3.connect(src) as db:
                db.execute("CREATE TABLE sample (value TEXT)")
            with open(dst, "wb") as existing:
                existing.write(b"retain")
            with self.assertRaises(FileExistsError):
                backup_readonly_state(src, dst)
            with open(dst, "rb") as existing:
                self.assertEqual(existing.read(), b"retain")
            with self.assertRaises(ValueError):
                backup_readonly_state(src, src)


if __name__ == "__main__":
    unittest.main()
