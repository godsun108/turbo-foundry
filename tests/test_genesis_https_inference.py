import io
import unittest
from src.autopilot.genesis_https_inference import GenesisHTTPSInference
from src.autopilot.genesis_candidate_adapter import GenesisCandidateAdapter


class FakeResponse:
    status = 200
    def __init__(self, data):
        self.data = io.BytesIO(data)
    def read(self, size):
        return self.data.read(size)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class GenesisHTTPTests(unittest.TestCase):
    def test_valid_candidate_flows_through_foundry(self):
        calls = []
        candidate = {
            "schema": "foundry.genesis.reply.v0",
            "reply": "What type of plumbing repair do you need?",
            "intent": "intake", "disposition": "collect_details",
            "proposed_actions": [], "evidence": [],
            "verified_booking": False, "real_message_sent": False
        }
        def opener(request, timeout):
            calls.append((request, timeout))
            return FakeResponse(__import__("json").dumps(candidate).encode())
        infer = GenesisHTTPSInference(endpoint="https://example.org/infer",
                                      bearer_token="x" * 32, opener=opener)
        turn = GenesisCandidateAdapter(infer=infer).respond(
            tenant="business1", session="session1", industry="plumbing",
            message="My faucet is leaking")
        self.assertEqual(turn.source, "validated_candidate")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0].get_method(), "POST")

    def test_invalid_candidate_falls_back(self):
        infer = GenesisHTTPSInference(endpoint="https://example.org/infer",
            bearer_token="x" * 32, opener=lambda req, timeout: FakeResponse(b'{"bad":true}'))
        turn = GenesisCandidateAdapter(infer=infer).respond(
            tenant="business1", session="session1", industry="plumbing", message="My faucet is leaking")
        self.assertEqual(turn.source, "deterministic")

    def test_invalid_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            GenesisHTTPSInference(endpoint="http://example.org/infer", bearer_token="x" * 32)

    def test_safety_turn_does_not_call_transport(self):
        def fail(req, timeout):
            raise AssertionError("unsafe request reached model")
        infer = GenesisHTTPSInference(endpoint="https://example.org/infer",
            bearer_token="x" * 32, opener=fail)
        turn = GenesisCandidateAdapter(infer=infer).respond(
            tenant="business1", session="session1", industry="plumbing", message="I smell gas")
        self.assertEqual(turn.intent, "urgent")


if __name__ == "__main__":
    unittest.main()
