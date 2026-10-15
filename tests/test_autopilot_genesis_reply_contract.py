import unittest
from src.autopilot.genesis_reply_contract import validate_genesis_reply, GenesisContractDenied


def valid():
    return dict(schema="foundry.genesis.reply.v0",reply="What service do you need?",
                intent="intake",disposition="collect_details",proposed_actions=[],
                evidence=[],verified_booking=False,real_message_sent=False)


class GenesisReplyContractTests(unittest.TestCase):
    def test_accepts_fictional_safe_reply(self):
        self.assertEqual(validate_genesis_reply(valid()).intent,"intake")

    def test_rejects_claims_of_real_actions(self):
        for key,value in (("verified_booking",True),("real_message_sent",True),
                          ("proposed_actions",[{"type":"book"}]),("evidence",["fictional"])):
            payload=valid()
            payload[key]=value
            with self.subTest(key=key),self.assertRaises(GenesisContractDenied):
                validate_genesis_reply(payload)

    def test_rejects_unapproved_schema_and_intent(self):
        for key,value in (("schema","portal.chat.v1"),("intent","send_payment"),
                          ("reply",""),("disposition","booked")):
            payload=valid()
            payload[key]=value
            with self.subTest(key=key),self.assertRaises(GenesisContractDenied):
                validate_genesis_reply(payload)

    def test_escalation_and_opt_out_are_fail_closed(self):
        for intent in ("urgent","human","stop"):
            payload=valid()
            payload["intent"]=intent
            with self.subTest(intent=intent),self.assertRaises(GenesisContractDenied):
                validate_genesis_reply(payload)

    def test_rejects_extra_fields(self):
        payload=valid()
        payload["tenant"]="another"
        with self.assertRaises(GenesisContractDenied):
            validate_genesis_reply(payload)


if __name__=="__main__":
    unittest.main()
