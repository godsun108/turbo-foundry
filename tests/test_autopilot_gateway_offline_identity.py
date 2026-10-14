"""Local identity -> session -> tenant binding -> audit rehearsal.

Fictional call records only. No network, SMS, billing or real authentication.
"""
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.autopilot.fictional_history_adapter import FictionalHistoryAdapter
from src.autopilot.gateway_audited_reads import AuditedGatewayReads
from src.autopilot.gateway_local_sessions import LocalGatewaySessions
from src.autopilot.gateway_offline_identity import OfflineIdentityGateway
from src.autopilot.universal_gateway import ReadOnlyGateway

NOW = datetime(2026, 10, 14, 20, tzinfo=timezone.utc)
ALICE_SECRET = "synthetic-alice-only-" + "a" * 32
BOB_SECRET = "synthetic-bob-only-" + "b" * 32


class IdentityDispatchRehearsal(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = str(Path(tmp.name) / "test.db")
        gateway = ReadOnlyGateway()
        gateway.register(FictionalHistoryAdapter("shop-a", {"call-a": ("leg-a",)}))
        self.audit = AuditedGatewayReads(self.db, gateway, {
            "alice": frozenset({"shop-a"}),
            "bob": frozenset({"shop-b"}),
        })
        self.audit.bind_parent(tenant_id="shop-a", provider="fictional", parent_id="call-a")
        self.sessions = LocalGatewaySessions(self.db, self.audit)
        self.identity = OfflineIdentityGateway(self.sessions, {
            "alice": ALICE_SECRET, "bob": BOB_SECRET,
        })

    def read(self, token, tenant="shop-a", parent="call-a", now=NOW):
        return self.identity.observe(token=token, tenant_id=tenant,
                                     provider="fictional", parent_id=parent, now=now)

    def test_login_read_audit_cross_tenant_logout(self):
        self.assertIsNone(self.identity.login(operator_id="alice", credential="wrong", now=NOW))
        token = self.identity.login(operator_id="alice", credential=ALICE_SECRET, now=NOW)
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 64)
        good = self.read(token)
        self.assertTrue(good.accepted)
        self.assertEqual(good.history.child_ids, ("leg-a",))
        self.assertEqual(self.audit.audit_records()[-1][-1], "read_requested")
        self.assertFalse(self.read(token, tenant="shop-b").accepted)
        self.assertFalse(self.read(token, parent="another-call").accepted)
        bob_token = self.identity.login(operator_id="bob", credential=BOB_SECRET, now=NOW)
        self.assertIsNotNone(bob_token)
        self.assertFalse(self.read(bob_token).accepted)
        self.assertTrue(self.identity.logout(token))
        self.assertFalse(self.read(token).accepted)

    def test_expiry_and_unknown_identity(self):
        token = self.identity.login(operator_id="alice", credential=ALICE_SECRET,
                                    now=NOW, ttl_seconds=10)
        self.assertIsNotNone(token)
        self.assertTrue(self.read(token, now=NOW + timedelta(seconds=9)).accepted)
        self.assertFalse(self.read(token, now=NOW + timedelta(seconds=10)).accepted)
        self.assertIsNone(self.identity.login(operator_id="nobody", credential=ALICE_SECRET, now=NOW))

    def test_password_attempt_quota_survives_new_facade(self):
        for i in range(5):
            self.assertIsNone(self.identity.login(operator_id="alice", credential="wrong", now=NOW))
        self.assertIsNone(self.identity.login(operator_id="alice", credential=ALICE_SECRET, now=NOW))
        new_facade = OfflineIdentityGateway(self.sessions, {"alice": ALICE_SECRET})
        self.assertIsNone(new_facade.login(operator_id="alice", credential=ALICE_SECRET, now=NOW))
        next_window = NOW + timedelta(minutes=6)
        self.assertIsNotNone(new_facade.login(operator_id="alice",
                                               credential=ALICE_SECRET, now=next_window))

    def test_attempt_database_failure_denies_login(self):
        with sqlite3.connect(self.db) as db:
            db.execute("DROP TABLE operator_attempt_windows")
        self.assertIsNone(self.identity.login(operator_id="alice",
                                               credential=ALICE_SECRET, now=NOW))

    def test_provisioning_rejects_weak_secrets(self):
        with self.assertRaises(ValueError):
            OfflineIdentityGateway(self.sessions, {"alice": "short"})

    def test_no_customer_side_effects(self):
        for operation in ("send_sms", "dial", "charge", "create_payment"):
            self.assertFalse(hasattr(self.identity, operation))


if __name__ == "__main__":
    unittest.main()
