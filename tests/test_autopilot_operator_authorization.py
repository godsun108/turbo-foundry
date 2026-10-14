"""Offline allowlisted operator control tests; no external identity provider."""
import os
import tempfile
import unittest
from datetime import datetime, timezone

from src.autopilot.operator_authorization import OperatorAuthorization, OperatorPrincipal
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 19, tzinfo=timezone.utc)


class OperatorAuthorizationTests(unittest.TestCase):
    def test_denied_unknown_and_claimed_roles_have_no_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = WorkerControl(os.path.join(tmp, "operator.db"))
            auth = OperatorAuthorization({"alice": frozenset({"autopilot.worker.admin"})})
            for principal in (
                OperatorPrincipal("unknown", frozenset({"autopilot.worker.admin"})),
                OperatorPrincipal("bob", frozenset({"autopilot.worker.admin"})),
                None,
            ):
                self.assertFalse(auth.set_worker_enabled(
                    principal=principal, control=control, enabled=True,
                    reason="attempt", now=NOW))
            self.assertFalse(control.is_enabled())
            self.assertEqual(control.audit_events(), [])

    def test_allowlisted_admin_can_enable_and_disable_with_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = WorkerControl(os.path.join(tmp, "operator.db"))
            auth = OperatorAuthorization({"alice": frozenset({"autopilot.worker.admin"})})
            principal = OperatorPrincipal("alice", frozenset())
            self.assertTrue(auth.set_worker_enabled(
                principal=principal, control=control, enabled=True,
                reason="offline rehearsal", now=NOW))
            self.assertTrue(control.is_enabled())
            self.assertTrue(auth.set_worker_enabled(
                principal=principal, control=control, enabled=False,
                reason="stop", now=NOW))
            self.assertFalse(control.is_enabled())
            events = control.audit_events()
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0][2:6], ("alice", "stop", 1, 0))

    def test_allowlisted_nonadmin_cannot_enable(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = WorkerControl(os.path.join(tmp, "operator.db"))
            auth = OperatorAuthorization({"bob": frozenset({"autopilot.worker.viewer"})})
            self.assertFalse(auth.set_worker_enabled(
                principal=OperatorPrincipal("bob", frozenset({"autopilot.worker.admin"})),
                control=control, enabled=True, reason="attempt", now=NOW))
            self.assertFalse(control.is_enabled())
            self.assertEqual(control.audit_events(), [])

    def test_default_empty_allowlist_denies(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = WorkerControl(os.path.join(tmp, "operator.db"))
            auth = OperatorAuthorization({})
            self.assertFalse(auth.set_worker_enabled(
                principal=OperatorPrincipal("alice", frozenset({"autopilot.worker.admin"})),
                control=control, enabled=True, reason="attempt", now=NOW))
            self.assertFalse(control.is_enabled())


if __name__ == "__main__":
    unittest.main()
