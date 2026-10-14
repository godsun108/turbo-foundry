"""Synthetic control audit tests, without network/provider/SMS operations."""
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 16, tzinfo=timezone.utc)


class WorkerAuditTests(unittest.TestCase):
    def test_enable_disable_and_audit_survive_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, "audit.db")
            control = WorkerControl(path)
            self.assertFalse(control.is_enabled())
            control.set_enabled(True, actor="synthetic-operator",
                                reason="offline rehearsal", now=NOW)
            control.set_enabled(False, actor="synthetic-operator",
                                reason="offline stop", now=NOW)
            restored = WorkerControl(path)
            self.assertFalse(restored.is_enabled())
            events = restored.audit_events()
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0][2:6],
                             ("synthetic-operator","offline stop",1,0))
            self.assertEqual(events[1][2:6],
                             ("synthetic-operator","offline rehearsal",None,1))

    def test_legacy_caller_is_attributed_as_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            control = WorkerControl(os.path.join(temp,"audit.db"))
            control.set_enabled(False, now=NOW)
            self.assertEqual(control.audit_events()[0][2],
                             "unattributed_local_caller")

    def test_invalid_actor_reason_timestamp_fail_before_state_change(self):
        with tempfile.TemporaryDirectory() as temp:
            control = WorkerControl(os.path.join(temp,"audit.db"))
            for kwargs in ({"actor":""},{"reason":""},
                           {"now":NOW.replace(tzinfo=None)}):
                with self.assertRaises(ValueError):
                    control.set_enabled(True, **kwargs)
            self.assertFalse(control.is_enabled())
            self.assertEqual(control.audit_events(), [])

    def test_audit_failure_rolls_back_control_change(self):
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp,"audit.db")
            control = WorkerControl(path)
            control.set_enabled(False, now=NOW)
            with sqlite3.connect(path) as db:
                db.execute("DROP TABLE worker_control_audit")
            with self.assertRaises(sqlite3.OperationalError):
                control.set_enabled(True, actor="test", reason="must rollback", now=NOW)
            self.assertFalse(control.is_enabled())

    def test_audit_limit_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            control = WorkerControl(os.path.join(temp, "audit.db"))
            for limit in (0, 101, True, "5"):
                with self.assertRaises(ValueError):
                    control.audit_events(limit=limit)


if __name__ == "__main__":
    unittest.main()
