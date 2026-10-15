"""Cryptographic interoperability test using the real Twilio SDK."""
import unittest
from src.autopilot.twilio_gate import screen_twilio_callback

try:
    from twilio.request_validator import RequestValidator
except ImportError:
    RequestValidator = None

@unittest.skipUnless(RequestValidator is not None, "Twilio SDK not installed")
class TestRealTwilioSignature(unittest.TestCase):
    def test_real_sdk_signature_and_tampering(self):
        token = "offline-fixture-auth-token"
        url = "https://example.test/twilio/status"
        params = {
            "CallSid": "CA" + "b" * 32,
            "From": "+15557654321",
            "To": "+15551234567",
            "CallStatus": "no-answer",
        }
        validator = RequestValidator(token)
        signature = validator.compute_signature(url, params)
        kwargs = dict(
            provisioned_destination="+15551234567", trusted_inbound=True
        )
        valid = screen_twilio_callback(url, params, signature, token, **kwargs)
        self.assertTrue(valid.accepted, valid.reason)
        changed = screen_twilio_callback(
            url, dict(params, CallStatus="completed"), signature, token, **kwargs
        )
        self.assertEqual(changed.reason, "invalid_provider_callback")
        incorrect_url = screen_twilio_callback(
            url + "?spoofed=1", params, signature, token, **kwargs
        )
        self.assertEqual(incorrect_url.reason, "invalid_provider_callback")

if __name__ == "__main__":
    unittest.main()
