import unittest
from src.autopilot.account_auth import TrustedAccountVerifier

ACCOUNT="AC"+"a"*32
OTHER="AC"+"b"*32
SID="CA"+"c"*32
NUMBER="+15551234567"
PARAMS=dict(AccountSid=ACCOUNT,CallSid=SID,From="+15557654321",
            To=NUMBER,CallStatus="no-answer")
class Validator:
    def __init__(self,valid): self.valid=valid
    def validate(self,url,params,signature): return self.valid

class TestAccountAuth(unittest.TestCase):
    def setUp(self):
        self.verifier=TrustedAccountVerifier({ACCOUNT:"trusted-token"})

    def verify(self,**overrides):
        args=dict(url="https://example.test/twilio",params=PARAMS,
                  signature="sig",validator_factory=lambda token:Validator(token=="trusted-token"))
        args.update(overrides)
        return self.verifier.verify(**args)

    def test_valid_configured_account(self):
        self.assertTrue(self.verify().verified)

    def test_unknown_account(self):
        self.assertEqual(self.verify(params=dict(PARAMS,AccountSid=OTHER)).reason,"unknown_account")

    def test_invalid_signature(self):
        self.assertEqual(self.verify(validator_factory=lambda token:Validator(False)).reason,
                         "invalid_signature_or_event")

    def test_missing_account(self):
        p=dict(PARAMS)
        del p["AccountSid"]
        self.assertEqual(self.verify(params=p).reason,"invalid_account_sid")

    def test_token_cannot_be_injected_from_callback(self):
        p=dict(PARAMS,AuthToken="attacker-controlled")
        self.assertTrue(self.verify(params=p).verified)

    def test_invalid_call_fields(self):
        self.assertEqual(self.verify(params=dict(PARAMS,CallSid="invalid")).reason,
                         "invalid_signature_or_event")

if __name__=="__main__":
    unittest.main()
