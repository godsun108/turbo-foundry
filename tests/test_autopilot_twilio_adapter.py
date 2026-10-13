import unittest
from src.autopilot.twilio_adapter import authenticate_twilio_voice_form

URL = "https://example.test/voice/status"
PARAMS = {"CallSid": "CA" + "a" * 32, "From": "+15557654321", "To": "+15551234567", "CallStatus": "no-answer"}

class StubValidator:
    def __init__(self, valid):
        self.valid = valid
        self.calls = 0
    def validate(self, url, params, signature):
        self.calls += 1
        return self.valid

class TestTwilioAdapter(unittest.TestCase):
    def test_authenticated_event(self):
        validator = StubValidator(True)
        event = authenticate_twilio_voice_form(URL, PARAMS, "signature", "token", validator=validator)
        self.assertEqual(event.call_status, "no-answer")
        self.assertEqual(validator.calls, 1)

    def test_invalid_signature(self):
        self.assertIsNone(authenticate_twilio_voice_form(URL, PARAMS, "signature", "token", validator=StubValidator(False)))

    def test_missing_auth_token(self):
        self.assertIsNone(authenticate_twilio_voice_form(URL, PARAMS, "signature", "", validator=StubValidator(True)))

    def test_requires_https(self):
        self.assertIsNone(authenticate_twilio_voice_form("http://example.test", PARAMS, "signature", "token", validator=StubValidator(True)))

    def test_invalid_call_sid(self):
        self.assertIsNone(authenticate_twilio_voice_form(URL, dict(PARAMS, CallSid="bad"), "signature", "token", validator=StubValidator(True)))

    def test_missing_status(self):
        self.assertIsNone(authenticate_twilio_voice_form(URL, dict(PARAMS, CallStatus=""), "signature", "token", validator=StubValidator(True)))

if __name__ == "__main__":
    unittest.main()
