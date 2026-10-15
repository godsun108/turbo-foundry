"""Read-only provider pilot metadata cannot authorize a real connection."""
import unittest
from src.autopilot.provider_pilot_preflight import (
    ProviderPilotRequest, ProviderPreflightDenied, inspect_provider_pilot,
)

SID = "AC" + "a" * 32


class ProviderPreflightTests(unittest.TestCase):
    def test_valid_metadata_remains_no_go_and_redacted(self):
        r = inspect_provider_pilot(ProviderPilotRequest(
            "fictional-a", "twilio", SID, "client-consent-ref",
            "operator-review-ref"))
        self.assertEqual(r["max_pages"], 2)
        self.assertEqual(r["max_legs"], 20)
        self.assertFalse(r["connected_staging_approved"])
        self.assertFalse(r["authorization_independently_verified"])
        self.assertFalse(r["provider_account_ownership_verified"])
        self.assertFalse(r["provider_called"])
        self.assertFalse(r["cost_approved"])
        self.assertEqual(r["network_calls"], 0)
        self.assertNotIn(SID, str(r))
        self.assertNotIn("token", str(r).lower())

    def test_incorrect_provider_billing_or_scope_denied(self):
        examples = [
            ProviderPilotRequest("tenant", "fictional", SID, "consent-ref", "review-ref"),
            ProviderPilotRequest("bad tenant", "twilio", SID, "consent-ref", "review-ref"),
            ProviderPilotRequest("tenant", "twilio", "not-an-account", "consent-ref", "review-ref"),
            ProviderPilotRequest("tenant", "twilio", SID, "", "review-ref"),
            ProviderPilotRequest("tenant", "twilio", SID, "consent-ref", "consent-ref"),
            ProviderPilotRequest("tenant", "twilio", SID, "consent-ref", "review-ref", max_pages=3),
            ProviderPilotRequest("tenant", "twilio", SID, "consent-ref", "review-ref", max_legs=21),
            ProviderPilotRequest("tenant", "twilio", SID, "consent-ref", "review-ref", max_legs=True),
        ]
        for item in examples:
            with self.subTest(item=item), self.assertRaises(ProviderPreflightDenied):
                inspect_provider_pilot(item)

    def test_no_live_operation_is_offered(self):
        p = ProviderPilotRequest("tenant", "twilio", SID, "consent-ref", "review-ref")
        r = inspect_provider_pilot(p)
        for forbidden in ("send_sms", "create_call", "activate",
                          "authentication_verified", "send_message"):
            self.assertNotIn(forbidden, r)
        self.assertEqual(r["allowed_operation"], "bounded_read_only_call_history")


if __name__ == "__main__":
    unittest.main()
