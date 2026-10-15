import unittest
from src.autopilot.twilio_gate import screen_twilio_callback

URL = "https://example.test/twilio/status"
NUMBER = "+15551234567"
BASE = {"CallSid": "CA" + "a" * 32, "From": "+15557654321", "To": NUMBER, "CallStatus": "no-answer"}

class StubValidator:
    def __init__(self, valid=True):
        self.valid = valid
    def validate(self, url, params, signature):
        return self.valid

def screen(params=BASE, **overrides):
    options = dict(provisioned_destination=NUMBER, trusted_inbound=True, validator=StubValidator())
    options.update(overrides)
    return screen_twilio_callback(URL, params, "test-signature", "test-auth-token", **options)

class TestTwilioGate(unittest.TestCase):
    def test_verified_inbound_no_answer(self):
        self.assertTrue(screen().accepted)

    def test_invalid_signature_rejected(self):
        self.assertEqual(screen(validator=StubValidator(False)).reason, "invalid_provider_callback")

    def test_wrong_destination_rejected(self):
        self.assertEqual(screen(provisioned_destination="+15550000000").reason, "destination_not_provisioned")

    def test_completed_is_not_missed(self):
        self.assertFalse(screen(dict(BASE, CallStatus="completed")).accepted)

    def test_outbound_not_missed(self):
        self.assertEqual(screen(trusted_inbound=False).reason, "not_inbound")

    def test_answered_elsewhere(self):
        self.assertEqual(screen(trusted_answered_elsewhere=True).reason, "answered_elsewhere")

    def test_ringing_not_missed(self):
        self.assertFalse(screen(dict(BASE, CallStatus="ringing")).accepted)

    def test_replay_screening_does_not_send(self):
        a, b = screen(), screen()
        self.assertEqual(a, b)
        self.assertFalse(hasattr(a, "send"))

if __name__ == "__main__":
    unittest.main()
