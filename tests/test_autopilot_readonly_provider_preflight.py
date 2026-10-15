"""Synthetic checks of read-only preflight; no provider credentials/network."""
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.autopilot.readonly_provider_preflight import (
    ReadonlyProbePermit, preflight_readonly_probe,
)
from src.autopilot.worker_control import WorkerControl

NOW = datetime(2026, 10, 14, 18, tzinfo=timezone.utc)
ACCOUNT = "AC" + "a" * 32
OTHER_ACCOUNT = "AC" + "b" * 32
PARENT = "CA" + "c" * 32
OTHER_PARENT = "CA" + "d" * 32


class ReadonlyProviderPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.control = WorkerControl(str(Path(self.tmp.name) / "gates.db"))
        self.permit = ReadonlyProbePermit(
            tenant_id="synthetic-tenant",
            provider_account_sid=ACCOUNT, parent_call_sid=PARENT,
            authorized_by="synthetic-authorizer",
            approval_reference="fictional-approval-only",
            expires_at=NOW + timedelta(minutes=30),
            read_only=True,
        )
        self.trusted = dict(expected_tenant_id="synthetic-tenant",
                            trusted_provider_account_sid=ACCOUNT,
                            trusted_parent_sid=PARENT, now=NOW,
                            control=self.control,
                            operator_authorization_verified=True,
                            provider_ownership_verified=True,
                            zero_charge_verified=True)

    def check(self, permit=None, **overrides):
        args = dict(self.trusted)
        args.update(overrides)
        return preflight_readonly_probe(self.permit if permit is None else permit, **args)

    def test_default_disabled_even_with_claimed_approvals(self):
        result = self.check()
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "operator_stop_active")

    def test_missing_independent_approvals_fail_closed(self):
        self.control.set_enabled(True)
        for name in ("operator_authorization_verified",
                     "provider_ownership_verified", "zero_charge_verified"):
            with self.subTest(name=name):
                self.assertFalse(self.check(**{name: False}).allowed)
                self.assertEqual(self.check(**{name: 1}).reason, "independent_approval_missing")

    def test_bounded_synthetic_policy_pass_then_stop(self):
        self.control.set_enabled(True)
        result = self.check()
        self.assertTrue(result.allowed)
        self.assertIn("not_live_authorization", result.reason)
        self.control.set_enabled(False)
        self.assertEqual(self.check().reason, "operator_stop_active")

    def test_cross_tenant_account_and_parent_denied(self):
        self.control.set_enabled(True)
        for altered in (
            replace(self.permit, tenant_id="other-tenant"),
            replace(self.permit, provider_account_sid=OTHER_ACCOUNT),
            replace(self.permit, parent_call_sid=OTHER_PARENT),
        ):
            with self.subTest(permit=altered):
                self.assertEqual(self.check(altered).reason, "unbound_tenant_or_provider_record")

    def test_expiry_and_clock_rejected(self):
        self.control.set_enabled(True)
        for altered in (
            replace(self.permit, expires_at=NOW),
            replace(self.permit, expires_at=NOW + timedelta(hours=2)),
            replace(self.permit, expires_at=datetime(2026, 10, 14)),
        ):
            self.assertEqual(self.check(altered).reason, "expired_or_oversized_permit")
        self.assertEqual(self.check(now=datetime(2026, 10, 14)).reason, "invalid_clock")

    def test_unsafe_scope_and_blank_evidence_rejected(self):
        self.control.set_enabled(True)
        for altered in (
            replace(self.permit, read_only=False),
            replace(self.permit, max_pages=3),
            replace(self.permit, max_legs=21),
            replace(self.permit, page_size=11),
            replace(self.permit, page_size=True),
        ):
            self.assertEqual(self.check(altered).reason, "unsafe_probe_scope")
        for altered in (
            replace(self.permit, authorized_by=" "),
            replace(self.permit, approval_reference=" "),
        ):
            self.assertEqual(self.check(altered).reason, "missing_approval_evidence")

    def test_missing_control_and_forged_bound_fields(self):
        self.control.set_enabled(True)
        self.assertEqual(self.check(control=None).reason, "operator_stop_unavailable")
        self.assertEqual(self.check(trusted_provider_account_sid=OTHER_ACCOUNT).reason,
                         "unbound_tenant_or_provider_record")
        self.assertEqual(self.check(trusted_parent_sid=OTHER_PARENT).reason,
                         "unbound_tenant_or_provider_record")


if __name__ == "__main__":
    unittest.main()
