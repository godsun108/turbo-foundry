"""Release-gate tests: no operational claim from code passing alone."""
import unittest

from src.autopilot.commercial_release_gate import (
    EvidenceItem, REQUIRED_FOR_DISCOVERY, REQUIRED_FOR_LIVE_PILOT,
    assess_release,
)


class CommercialReleaseGateTests(unittest.TestCase):
    def test_empty_evidence_is_no_go(self):
        outcome = assess_release({})
        self.assertFalse(outcome.discovery_ready)
        self.assertFalse(outcome.live_pilot_ready)
        self.assertEqual(outcome.missing_discovery, REQUIRED_FOR_DISCOVERY)
        self.assertEqual(outcome.missing_live_pilot, REQUIRED_FOR_LIVE_PILOT)

    def test_discovery_only_never_entitles_live_pilot(self):
        evidence = {k: EvidenceItem(True, "manual-review-ticket", "human-reviewer")
                    for k in REQUIRED_FOR_DISCOVERY}
        outcome = assess_release(evidence)
        self.assertTrue(outcome.discovery_ready)
        self.assertFalse(outcome.live_pilot_ready)

    def test_missing_reference_and_reviewer_fail_closed(self):
        evidence = {k: EvidenceItem(True, "valid-ref", "reviewer")
                    for k in REQUIRED_FOR_DISCOVERY + REQUIRED_FOR_LIVE_PILOT}
        evidence["consent_and_optout_review"] = EvidenceItem(True, "", "reviewer")
        self.assertFalse(assess_release(evidence).live_pilot_ready)
        evidence["consent_and_optout_review"] = EvidenceItem(True, "ref", "")
        self.assertFalse(assess_release(evidence).live_pilot_ready)
        evidence["consent_and_optout_review"] = EvidenceItem(False, "ref", "reviewer")
        self.assertFalse(assess_release(evidence).live_pilot_ready)

    def test_complete_synthetic_register_is_logic_test_not_real_approval(self):
        # Fictional evidence tests decision logic; it DOES NOT authorize operations.
        register = {k: EvidenceItem(True, "synthetic-test-ref", "test-runner")
                    for k in REQUIRED_FOR_DISCOVERY + REQUIRED_FOR_LIVE_PILOT}
        self.assertTrue(assess_release(register).live_pilot_ready)


if __name__ == "__main__":
    unittest.main()
