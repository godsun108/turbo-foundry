import unittest
from src.autopilot.genesis_candidate_adapter import GenesisCandidateAdapter


class SafetyBypassTests(unittest.TestCase):
    def test_safety_turns_do_not_invoke_model(self):
        calls = []
        def infer(payload):
            calls.append(payload)
            raise AssertionError("model must not receive safety-critical utterance")
        adapter = GenesisCandidateAdapter(infer=infer)
        for index, (utterance, expected) in enumerate([
            ("STOP", "stop"),
            ("I smell gas", "urgent"),
            ("I want a human", "human"),
        ]):
            result = adapter.respond(tenant="tenant1", session=f"session{index}", industry="plumbing", message=utterance)
            self.assertEqual(result.intent, expected)
            self.assertEqual(result.source, "deterministic")
        self.assertEqual(calls, [])

    def test_regular_turn_can_reach_model(self):
        calls = []
        def infer(payload):
            calls.append(payload)
            return None
        adapter = GenesisCandidateAdapter(infer=infer)
        result = adapter.respond(tenant="tenant1", session="regular", industry="plumbing", message="Can I get a quote?")
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.source, "deterministic")

    def test_invalid_scope_never_reaches_inference(self):
        calls = []
        def infer(payload):
            calls.append(payload)
            return None
        adapter = GenesisCandidateAdapter(infer=infer)
        for kwargs in [
            {"tenant": "bad tenant", "session": "ok", "industry": "hvac", "message": "hello"},
            {"tenant": "ok", "session": "ok", "industry": "hvac", "message": "x" * 1001},
            {"tenant": "ok", "session": "ok", "industry": "hvac", "message": "hello", "verified_facts": {"private": "secret"}},
        ]:
            with self.assertRaises(ValueError):
                adapter.respond(**kwargs)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
