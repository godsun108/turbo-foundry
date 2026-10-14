"""Audited offline gateway facade tests. No real communications."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.autopilot.gateway_audited_reads import AuditedGatewayReads, TrustedReader
from src.autopilot.universal_gateway import ReadOnlyGateway
from src.autopilot.fictional_history_adapter import FictionalHistoryAdapter


class AuditedGatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = str(Path(self.tmp.name) / "gateway.sqlite")
        self.adapter = FictionalHistoryAdapter("shop-a", {"call-a": ("leg-1",)})
        self.gateway = ReadOnlyGateway()
        self.gateway.register(self.adapter)
        self.facade = AuditedGatewayReads(self.path, self.gateway, {
            "alice": frozenset({"shop-a"}),
            "bob": frozenset({"shop-b"}),
        })
        self.facade.bind_parent(tenant_id="shop-a", provider="fictional", parent_id="call-a")

    def test_authorized_read_records_intent(self):
        result = self.facade.observe(principal=TrustedReader("alice"),
                                     tenant_id="shop-a", provider="fictional",
                                     parent_id="call-a")
        self.assertTrue(result.accepted)
        self.assertEqual(result.history.child_ids, ("leg-1",))
        self.assertEqual(self.facade.audit_records()[0][-2:], (1, "read_requested"))

    def test_wrong_operator_and_missing_binding_are_denied_and_audited(self):
        for who, parent in (("bob", "call-a"), ("alice", "call-b"),
                            ("unknown", "call-a")):
            with self.subTest(who=who, parent=parent):
                result = self.facade.observe(principal=TrustedReader(who),
                    tenant_id="shop-a", provider="fictional", parent_id=parent)
                self.assertFalse(result.accepted)
                self.assertEqual(result.reason, "permission_or_binding_denied")
        self.assertEqual(len(self.facade.audit_records()), 3)
        self.assertTrue(all(row[-2] == 0 for row in self.facade.audit_records()))

    def test_audit_failure_prevents_adapter_read(self):
        class Counting:
            provider = "fictional"
            tenant_id = "shop-a"
            calls = 0
            def enumerate_children(self, *args, **kwargs):
                self.calls += 1
                raise AssertionError("must not call adapter")
        count = Counting()
        gateway = ReadOnlyGateway()
        gateway.register(count)
        facade = AuditedGatewayReads(self.path, gateway, {
            "alice": frozenset({"shop-a"})
        })
        with sqlite3.connect(self.path) as db:
            db.execute("DROP TABLE gateway_read_audit")
        result = facade.observe(principal=TrustedReader("alice"), tenant_id="shop-a",
                                provider="fictional", parent_id="call-a")
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "audit_store_unavailable")
        self.assertEqual(count.calls, 0)

    def test_invalid_principal_and_scope_do_not_dispatch(self):
        result = self.facade.observe(principal="alice", tenant_id="shop-a",
                                     provider="fictional", parent_id="call-a")
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "invalid_principal_or_request")
        with self.assertRaises(ValueError):
            self.facade.bind_parent(tenant_id="shop-a", provider="fictional",
                                    parent_id="../../etc/passwd")

    def test_registry_persists_but_actor_mapping_is_runtime_only(self):
        facade = AuditedGatewayReads(self.path, self.gateway, {})
        result = facade.observe(principal=TrustedReader("alice"), tenant_id="shop-a",
                                provider="fictional", parent_id="call-a")
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "permission_or_binding_denied")


if __name__ == "__main__":
    unittest.main()
