"""Offline credential and role checks; synthetic secrets and no network."""
import os
import tempfile
import unittest
from datetime import datetime, timezone

from src.autopilot.operator_authorization import OperatorAuthorization
from src.autopilot.operator_entrypoint import OfflineOperatorEntrypoint, OperatorCommand
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 20, tzinfo=timezone.utc)
SECRET = "offline-demo-credential-not-for-production-123456"


class EntrypointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.control = WorkerControl(os.path.join(self.tmp.name, "operator.db"))
        self.auth = OperatorAuthorization({
            "admin": frozenset({"autopilot.worker.admin"}),
            "viewer": frozenset({"autopilot.worker.viewer"}),
        })
        self.entry = OfflineOperatorEntrypoint({
            "admin": SECRET, "viewer": "another-offline-test-credential-123456789",
        }, self.auth)

    def tearDown(self):
        self.tmp.cleanup()

    def test_authorized_credential_and_role_record_audit(self):
        approved = OperatorCommand("admin", SECRET, True, "offline enable")
        self.assertTrue(self.entry.apply(approved, self.control, now=NOW))
        self.assertTrue(self.control.is_enabled())
        self.assertEqual(self.control.audit_events()[0][2], "admin")
        self.assertTrue(self.entry.apply(
            OperatorCommand("admin", SECRET, False, "offline stop"),
            self.control, now=NOW))
        self.assertFalse(self.control.is_enabled())

    def test_claimed_identity_without_secret_denied_without_audit(self):
        for command in (
            OperatorCommand("admin", "wrong-secret", True, "impersonate"),
            OperatorCommand("unknown", SECRET, True, "impersonate"),
            OperatorCommand("viewer", SECRET, True, "escalate"),
            OperatorCommand("admin", SECRET, 1, "invalid flag"),
        ):
            self.assertFalse(self.entry.apply(command, self.control, now=NOW))
        self.assertFalse(self.control.is_enabled())
        self.assertEqual(self.control.audit_events(), [])

    def test_valid_credential_with_no_admin_permission_denied(self):
        command = OperatorCommand(
            "viewer", "another-offline-test-credential-123456789",
            True, "attempt",
        )
        self.assertFalse(self.entry.apply(command, self.control, now=NOW))
        self.assertEqual(self.control.audit_events(), [])
        self.assertFalse(self.control.is_enabled())

    def test_empty_configuration_denies_all(self):
        empty = OfflineOperatorEntrypoint({}, OperatorAuthorization({}))
        self.assertFalse(empty.apply(
            OperatorCommand("admin", SECRET, True, "attempt"),
            self.control, now=NOW))
        self.assertFalse(self.control.is_enabled())

    def test_repeated_bad_credentials_lock_out_and_survive_recreation(self):
        from datetime import timedelta
        for _ in range(5):
            self.assertFalse(self.entry.apply(
                OperatorCommand("admin", "incorrect", True, "guess"),
                self.control, now=NOW))
        reopened = OfflineOperatorEntrypoint({"admin": SECRET}, self.auth)
        self.assertFalse(reopened.apply(
            OperatorCommand("admin", SECRET, True, "locked"),
            self.control, now=NOW))
        self.assertFalse(self.control.is_enabled())
        self.assertEqual(self.control.audit_events(), [])
        later = NOW + timedelta(minutes=6)
        self.assertTrue(reopened.apply(
            OperatorCommand("admin", SECRET, True, "new window"),
            self.control, now=later))
        self.assertTrue(self.control.is_enabled())

    def test_rate_limit_storage_failure_fails_closed(self):
        from unittest.mock import patch
        with patch("src.autopilot.operator_entrypoint.OperatorAttemptLimiter",
                   side_effect=OSError("storage unavailable")):
            self.assertFalse(self.entry.apply(
                OperatorCommand("admin", SECRET, True, "attempt"),
                self.control, now=NOW))
        self.assertFalse(self.control.is_enabled())

    def test_invalid_control_object_fails_closed(self):
        for value in (None, object(), "malformed"):
            self.assertFalse(self.entry.apply(
                OperatorCommand("admin", SECRET, True, "attempt"),
                value, now=NOW))
        self.assertFalse(self.control.is_enabled())
        self.assertEqual(self.control.audit_events(), [])

    def test_direct_control_mutation_is_known_auth_bypass(self):
        # Explicit regression evidence: this legacy local method does not
        # enforce operator authentication and MUST NOT be exposed to clients.
        self.control.set_enabled(True, actor="unattributed_local_caller",
                                 reason="legacy_local_call", now=NOW)
        self.assertTrue(self.control.is_enabled())
        self.assertEqual(self.control.audit_events()[0][2],
                         "unattributed_local_caller")
        self.control.set_enabled(False, now=NOW)

    def test_short_secret_configuration_rejected(self):
        with self.assertRaises(ValueError):
            OfflineOperatorEntrypoint({"admin": "guessable"},
                                      self.auth)


if __name__ == "__main__":
    unittest.main()
