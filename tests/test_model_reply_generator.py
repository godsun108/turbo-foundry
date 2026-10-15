import io
import json
import unittest
from src.autopilot.model_reply_generator import ModelReplyGenerator
from src.autopilot.genesis_candidate_adapter import GenesisCandidateAdapter


class FakeResponse:
    status = 200
    def __init__(self, body):
        self.body = io.BytesIO(body)
    def read(self, n):
        return self.body.read(n)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class ModelGeneratorTests(unittest.TestCase):
    def test_model_backed_turn(self):
        calls = []
        candidate = {
            "schema": "foundry.genesis.reply.v0",
            "reply": "I can help prepare a request. What service do you need?",
            "intent": "intake", "disposition": "collect_details",
            "proposed_actions": [], "evidence": [],
            "verified_booking": False, "real_message_sent": False,
        }
        def opener(req, timeout):
            calls.append(json.loads(req.data))
            return FakeResponse(json.dumps({"choices": [{"message": {
                "content": json.dumps(candidate)}}]}).encode())
        model = ModelReplyGenerator(endpoint="https://example.org/v1/chat/completions",
                                    model="test-model", api_key="k" * 24, opener=opener)
        result = GenesisCandidateAdapter(infer=model).respond(
            tenant="business1", session="session1", industry="hvac",
            message="My air conditioner stopped working",
            verified_facts={"business_name": "Example HVAC"})
        self.assertEqual(result.source, "validated_candidate")
        self.assertEqual(len(calls), 1)
        self.assertIn("Example HVAC", calls[0]["messages"][0]["content"])

    def test_invalid_model_claim_falls_back(self):
        candidate = {
            "schema": "foundry.genesis.reply.v0", "reply": "Booked!",
            "intent": "appointment_request", "disposition": "informational",
            "proposed_actions": [], "evidence": [],
            "verified_booking": True, "real_message_sent": False,
        }
        def opener(req, timeout):
            return FakeResponse(json.dumps({"choices": [{"message": {
                "content": json.dumps(candidate)}}]}).encode())
        model = ModelReplyGenerator(endpoint="https://example.org/v1/chat/completions",
                                    model="test-model", api_key="k" * 24, opener=opener)
        result = GenesisCandidateAdapter(infer=model).respond(
            tenant="business1", session="session1", industry="hvac",
            message="I need an appointment")
        self.assertEqual(result.source, "deterministic")

    def test_no_http_or_weak_key(self):
        for endpoint, key in [
            ("http://example.org/v1/chat/completions", "k" * 24),
            ("https://example.org/v1/chat/completions", "weak"),
        ]:
            with self.assertRaises(ValueError):
                ModelReplyGenerator(endpoint=endpoint, model="test", api_key=key)


if __name__ == "__main__":
    unittest.main()
