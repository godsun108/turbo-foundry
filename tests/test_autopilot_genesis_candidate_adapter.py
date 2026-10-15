import unittest
from src.autopilot.genesis_candidate_adapter import GenesisCandidateAdapter


class CandidateAdapterTests(unittest.TestCase):
    def test_no_provider_fallback(self):
        result = GenesisCandidateAdapter().respond(tenant="t", session="s", industry="general", message="Hello")
        self.assertEqual(result.source, "deterministic")

    def test_provider_failure_fallback(self):
        def failing(_):
            raise RuntimeError("offline")
        result = GenesisCandidateAdapter(failing).respond(tenant="t", session="s", industry="general", message="Hello")
        self.assertEqual(result.source, "deterministic")

    def test_provider_context_is_scoped(self):
        inputs = []
        def infer(turn):
            inputs.append(turn)
            return dict(schema="foundry.genesis.reply.v0", reply="What service?", intent="intake",
                        disposition="collect_details", proposed_actions=[], evidence=[],
                        verified_booking=False, real_message_sent=False)
        adapter = GenesisCandidateAdapter(infer)
        adapter.respond(tenant="a", session="s", industry="general", message="Hello")
        adapter.respond(tenant="b", session="s", industry="general", message="Hi")
        adapter.respond(tenant="a", session="s", industry="general", message="Again")
        self.assertEqual(inputs[0]["context"], [])
        self.assertEqual(inputs[1]["context"], [])
        self.assertEqual(len(inputs[2]["context"]), 2)
        self.assertEqual(inputs[2]["permitted_actions"], [])

    def test_invalid_candidate_fallback(self):
        result = GenesisCandidateAdapter(lambda _: {"reply": "Booked!"}).respond(
            tenant="t", session="s", industry="general", message="appointment")
        self.assertEqual(result.source, "deterministic")


if __name__ == "__main__":
    unittest.main()
