"""Offline capability session / trusted-tenant dispatch tests."""
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.autopilot.universal_gateway import ReadOnlyGateway
from src.autopilot.fictional_history_adapter import FictionalHistoryAdapter
from src.autopilot.gateway_audited_reads import AuditedGatewayReads
from src.autopilot.gateway_local_sessions import LocalGatewaySessions

NOW = datetime(2026, 10, 14, 20, tzinfo=timezone.utc)


class LocalSessionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = str(Path(tmp.name) / "gateway.sqlite")
        gateway = ReadOnlyGateway()
        gateway.register(FictionalHistoryAdapter("shop-a", {"call-a": ("leg-a",)}))
        self.audit = AuditedGatewayReads(self.db, gateway, {
            "alice": frozenset({"shop-a"}),
            "bob": frozenset({"shop-b"}),
        })
        self.audit.bind_parent(tenant_id="shop-a", provider="fictional",
                               parent_id="call-a")
        self.sessions = LocalGatewaySessions(self.db, self.audit)

    def observe(self, token, *, tenant="shop-a", parent="call-a", now=NOW):
        return self.sessions.observe(token=token, tenant_id=tenant,
                                     provider="fictional", parent_id=parent,
                                     now=now)

    def test_valid_session_resolves_server_side_identity(self):
        token = self.sessions.issue("alice", now=NOW, ttl_seconds=60)
        self.assertEqual(len(token), 64)
        self.assertTrue(self.observe(token).accepted)
        self.assertEqual(self.audit.audit_records()[-1][0], "alice")
        with sqlite3.connect(self.db) as db:
            saved = db.execute("SELECT token_digest FROM gateway_sessions").fetchone()[0]
        self.assertNotEqual(saved, token)
        self.assertEqual(len(saved), 64)

    def test_wrong_tenant_or_parent_denied(self):
        token = self.sessions.issue("alice", now=NOW)
        self.assertFalse(self.observe(token, tenant="shop-b").accepted)
        self.assertFalse(self.observe(token, parent="call-b").accepted)
        bob = self.sessions.issue("bob", now=NOW)
        self.assertFalse(self.observe(bob).accepted)
        self.assertEqual(self.audit.audit_records()[-1][-1], "permission_or_binding_denied")

    def test_expiry_and_revocation(self):
        token = self.sessions.issue("alice", now=NOW, ttl_seconds=10)
        self.assertTrue(self.observe(token, now=NOW + timedelta(seconds=9)).accepted)
        self.assertEqual(self.observe(token, now=NOW + timedelta(seconds=10)).reason,
                         "invalid_or_expired_session")
        fresh = self.sessions.issue("alice", now=NOW)
        self.assertTrue(self.sessions.revoke(fresh))
        self.assertFalse(self.sessions.revoke(fresh))
        self.assertEqual(self.observe(fresh).reason, "invalid_or_expired_session")

    def test_unknown_and_fake_credentials_denied(self):
        for value in ("", "not-a-token", "g" * 64, "0" * 64, None):
            with self.subTest(token=value):
                self.assertFalse(self.observe(value).accepted)
        with self.assertRaises(ValueError):
            self.sessions.issue("unknown", now=NOW)
        with self.assertRaises(ValueError):
            self.sessions.issue("alice", now=NOW, ttl_seconds=3600)
        with self.assertRaises(ValueError):
            self.sessions.issue("alice", now=NOW, ttl_seconds=True)

    def test_restart_and_storage_failure(self):
        token = self.sessions.issue("alice", now=NOW)
        restarted = LocalGatewaySessions(self.db, self.audit)
        self.assertTrue(restarted.observe(token=token, tenant_id="shop-a",
                        provider="fictional", parent_id="call-a", now=NOW).accepted)
        with sqlite3.connect(self.db) as db:
            db.execute("DROP TABLE gateway_sessions")
        self.assertEqual(self.observe(token).reason, "session_store_unavailable")

    def test_revoking_access_mapping_on_restart_blocks_old_session(self):
        token = self.sessions.issue("alice", now=NOW)
        gateway = ReadOnlyGateway()
        gateway.register(FictionalHistoryAdapter("shop-a", {"call-a": ("leg-a",)}))
        no_access = AuditedGatewayReads(self.db, gateway, {})
        restarted = LocalGatewaySessions(self.db, no_access)
        result = restarted.observe(token=token, tenant_id="shop-a",
                                   provider="fictional", parent_id="call-a", now=NOW)
        self.assertEqual(result.reason, "permission_or_binding_denied")


if __name__ == "__main__":
    unittest.main()
