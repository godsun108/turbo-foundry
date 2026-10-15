"""Universal Gateway contract tests: strictly offline, read-only."""
import unittest

from src.autopilot.universal_gateway import (
    CallHistory, GatewayResult, ReadOnlyGateway,
)
from src.autopilot.fictional_history_adapter import FictionalHistoryAdapter
from src.autopilot.twilio_history_adapter import TwilioHistoryAdapter
from src.autopilot.synthetic_provider_sdk import SyntheticTwilioClient
from src.autopilot.twilio_paging import TwilioCallPager

ACCOUNT = "AC" + "a" * 32
PARENT = "CA" + "b" * 32
CHILD = "CA" + "c" * 32
CHILD2 = "CA" + "d" * 32


class GatewayContractTests(unittest.TestCase):
    def test_two_independent_providers_same_tenant(self):
        gateway = ReadOnlyGateway()
        twilio = SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD, CHILD2)})
        gateway.register(TwilioHistoryAdapter(
            tenant_id="tenant-a", pager=TwilioCallPager(twilio, ACCOUNT)))
        gateway.register(FictionalHistoryAdapter("tenant-a", {
            "call-123": ("leg-2", "leg-1")}))
        twilio_result = gateway.observe(
            trusted_tenant="tenant-a", provider="twilio", parent_id=PARENT,
            page_size=1)
        fictional_result = gateway.observe(
            trusted_tenant="tenant-a", provider="fictional",
            parent_id="call-123", page_size=1)
        self.assertTrue(twilio_result.accepted)
        self.assertEqual(twilio_result.history.child_ids, (CHILD, CHILD2))
        self.assertEqual(twilio.page_requests, 2)
        self.assertTrue(fictional_result.accepted)
        self.assertEqual(fictional_result.history.child_ids, ("leg-1", "leg-2"))
        self.assertEqual(fictional_result.history.pages_checked, 2)

    def test_tenant_isolation_and_unregistered_provider(self):
        gateway = ReadOnlyGateway()
        gateway.register(FictionalHistoryAdapter("tenant-a", {"p": ("c",)}))
        for tenant, provider in (
            ("tenant-b", "fictional"), ("tenant-a", "unknown")):
            result = gateway.observe(
                trusted_tenant=tenant, provider=provider, parent_id="p")
            self.assertFalse(result.accepted)
            self.assertEqual(result.reason, "unbound_provider")

    def test_unknown_parent_and_page_limit_fail_closed(self):
        gateway = ReadOnlyGateway()
        gateway.register(FictionalHistoryAdapter("tenant-a", {
            "p": ("c1", "c2", "c3")}))
        missing = gateway.observe(
            trusted_tenant="tenant-a", provider="fictional",
            parent_id="missing")
        self.assertFalse(missing.accepted)
        self.assertEqual(missing.reason, "unknown_parent")
        over_limit = gateway.observe(
            trusted_tenant="tenant-a", provider="fictional",
            parent_id="p", page_size=1)
        self.assertFalse(over_limit.accepted)
        self.assertEqual(over_limit.reason, "read_limit_exceeded")
        for scope in ({"page_size": 11}, {"max_pages": 3},
                      {"max_legs": True}):
            denial = gateway.observe(
                trusted_tenant="tenant-a", provider="fictional",
                parent_id="p", **scope)
            self.assertFalse(denial.accepted)
            self.assertEqual(denial.reason, "unapproved_read_bounds")

    def test_twilio_account_mismatch_is_not_accepted(self):
        sdk = SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD,)})
        gateway = ReadOnlyGateway()
        gateway.register(TwilioHistoryAdapter(
            tenant_id="tenant-a",
            pager=TwilioCallPager(sdk, "AC" + "f" * 32)))
        result = gateway.observe(
            trusted_tenant="tenant-a", provider="twilio", parent_id=PARENT)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "account_mismatch")

    def test_result_injection_and_exceptions_fail_closed(self):
        class CorruptAdapter:
            provider = "fictional"
            tenant_id = "tenant-a"
            def enumerate_children(self, parent_id, **kwargs):
                return CallHistory("fictional", "tenant-b", parent_id,
                                   ("unsafe",), True, "complete", 1)
        class ExplodingAdapter:
            provider = "explode"
            tenant_id = "tenant-a"
            def enumerate_children(self, parent_id, **kwargs):
                raise RuntimeError("private upstream details")
        gateway = ReadOnlyGateway()
        gateway.register(CorruptAdapter())
        gateway.register(ExplodingAdapter())
        self.assertEqual(gateway.observe(
            trusted_tenant="tenant-a", provider="fictional",
            parent_id="p").reason, "invalid_provider_result")
        self.assertEqual(gateway.observe(
            trusted_tenant="tenant-a", provider="explode",
            parent_id="p").reason, "provider_adapter_error")

    def test_duplicate_registration_blocked(self):
        gateway = ReadOnlyGateway()
        adapter = FictionalHistoryAdapter("tenant-a", {})
        gateway.register(adapter)
        with self.assertRaises(ValueError):
            gateway.register(adapter)

    def test_gateway_has_no_send_or_dial_api(self):
        gateway = ReadOnlyGateway()
        self.assertFalse(hasattr(gateway, "send_sms"))
        self.assertFalse(hasattr(gateway, "dial"))
        self.assertFalse(hasattr(gateway, "charge"))


if __name__ == "__main__":
    unittest.main()
