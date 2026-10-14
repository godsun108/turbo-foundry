"""Synthetic test: read-only SQLite role cannot mutate stop or audit state."""
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone

from src.autopilot.operator_readonly import ReadOnlyOperatorView
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 20, tzinfo=timezone.utc)


class ReadOnlyBoundaryTests(unittest.TestCase):
    def test_readonly_view_blocks_control_and_audit_mutations(self):
        with tempfile.TemporaryDirectory() as temp:
            db_path = os.path.join(temp, "control.db")
            control = WorkerControl(db_path)
            control.set_enabled(False, actor="synthetic-admin",
                                reason="offline stop", now=NOW)
            view = ReadOnlyOperatorView(db_path)
            state = view.snapshot()
            self.assertFalse(state.enabled)
            self.assertEqual(state.audit_events, 1)
            # This connection intentionally has no write privileges even
            # when the underlying file is owned by the same test process.
            with view.connect() as readonly:
                with self.assertRaises(sqlite3.OperationalError):
                    readonly.execute("""UPDATE worker_control SET enabled=1
                        WHERE name='read_only_recheck'""")
                with self.assertRaises(sqlite3.OperationalError):
                    readonly.execute("""DELETE FROM worker_control_audit""")
            self.assertEqual(view.snapshot(), state)
            self.assertFalse(control.is_enabled())

    def test_missing_database_never_created(self):
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "missing.db")
            with self.assertRaises(sqlite3.OperationalError):
                ReadOnlyOperatorView(path).snapshot()
            self.assertFalse(os.path.exists(path))

    def test_authorized_writer_changes_readonly_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "control.db")
            control = WorkerControl(path)
            view = ReadOnlyOperatorView(path)
            self.assertFalse(view.snapshot().enabled)
            control.set_enabled(True, actor="synthetic-admin",
                                reason="trusted offline change", now=NOW)
            self.assertTrue(view.snapshot().enabled)
            self.assertEqual(view.snapshot().audit_events, 1)


if __name__ == "__main__":
    unittest.main()
