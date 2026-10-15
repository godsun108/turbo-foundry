import unittest

from src.autopilot.genesis_offline_boundary import GenesisOfflineBoundary


def candidate(reply="What kind of inspection do you need?"):
    return dict(schema="foundry.genesis.reply.v0", reply=reply, intent="appointment_request",
                disposition="collect_details", proposed_actions=[], evidence=[],
                verified_booking=False, real_message_sent=False)


class BoundaryTests(unittest.TestCase):
    def test_valid_candidate_and_isolation(self):
        b = GenesisOfflineBoundary()
        result = b.respond(tenant="a", session="one", industry="automotive", message="Friday?", candidate=candidate())
        self.assertEqual(result.source, "validated_candidate")
        self.assertEqual(len(b.context(tenant="a", session="one")), 2)
        self.assertEqual(b.context(tenant="b", session="one"), [])

    def test_fabricated_booking_falls_back(self):
        b = GenesisOfflineBoundary()
        fake = candidate("Booked!")
        fake["verified_booking"] = True
        result = b.respond(tenant="a", session="s", industry="hvac", message="Schedule a visit", candidate=fake)
        self.assertEqual(result.source, "deterministic")
        self.assertFalse("Booked!" in result.reply)

    def test_stop_overrides_candidate_and_closes(self):
        b = GenesisOfflineBoundary()
        result = b.respond(tenant="a", session="s", industry="general", message="STOP", candidate=candidate())
        self.assertEqual(result.disposition, "closed")
        self.assertEqual(b.respond(tenant="a", session="s", industry="general", message="Hello", candidate=candidate()).source, "deterministic")

    def test_urgent_overrides_candidate(self):
        b = GenesisOfflineBoundary()
        result = b.respond(tenant="a", session="s", industry="plumbing", message="There is a gas leak", candidate=candidate())
        self.assertEqual(result.disposition, "human_escalation")
        self.assertEqual(result.source, "deterministic")

    def test_bounded_context(self):
        b = GenesisOfflineBoundary()
        for _ in range(15):
            b.respond(tenant="a", session="s", industry="cleaning", message="Hello")
        self.assertEqual(len(b.context(tenant="a", session="s")), 20)

    def test_rejects_industry_switch(self):
        b = GenesisOfflineBoundary()
        b.respond(tenant="a", session="s", industry="cleaning", message="Hello")
        with self.assertRaises(ValueError):
            b.respond(tenant="a", session="s", industry="automotive", message="Hello")


if __name__ == "__main__":
    unittest.main()
