import unittest
from c01_chrono_architecture import (
    validate_candidates, evaluate_trade_study, validate_state_transition,
    validate_measurement_plan, REQUIRED_CRITERIA,
)

class ChronographArchitectureTests(unittest.TestCase):
    def candidates(self):
        return [
            dict(candidate_id="A", clutch="vertical", control="column_wheel", status="candidate", evidence_register_id="E-A"),
            dict(candidate_id="B", clutch="vertical", control="cam_lever", status="candidate", evidence_register_id="E-B"),
            dict(candidate_id="C", clutch="horizontal", control="column_wheel", status="candidate", evidence_register_id="E-C"),
            dict(candidate_id="D", clutch="horizontal", control="cam_lever", status="candidate", evidence_register_id="E-D"),
        ]

    def test_four_combinations_validated_without_selecting_winner(self):
        result = validate_candidates(self.candidates())
        self.assertFalse(result["winner_selected"])

    def test_wrong_combination_rejected(self):
        rows = self.candidates()
        rows[0]["control"] = "cam_lever"
        with self.assertRaises(ValueError):
            validate_candidates(rows)

    def test_weights_must_sum_exactly_to_one(self):
        criteria = [dict(criterion_id=k, weight="0.1", definition="test", approval_record_id="APP") for k in sorted(REQUIRED_CRITERIA)]
        scores = [dict(candidate_id=k, criterion_scores={c: 4 for c in REQUIRED_CRITERIA},
            evidence_ids={c: "EV-" + c for c in REQUIRED_CRITERIA}, review_status="approved")
            for k in "ABCD"]
        with self.assertRaises(ValueError):
            evaluate_trade_study(criteria, scores)

    def test_trade_study_returns_advisory_ranking_only(self):
        criteria = [dict(criterion_id=k, weight="0.125", definition="test", approval_record_id="APP") for k in sorted(REQUIRED_CRITERIA)]
        scores = [dict(candidate_id=k, criterion_scores={c: 4 for c in REQUIRED_CRITERIA},
            evidence_ids={c: "EV-" + c for c in REQUIRED_CRITERIA}, review_status="approved")
            for k in "ABCD"]
        result = evaluate_trade_study(criteria, scores)
        self.assertFalse(result["decision_authorized"])
        self.assertTrue(result["top_score_tie"])

    def test_reset_while_running_requires_physical_evidence(self):
        with self.assertRaises(ValueError):
            validate_state_transition("running", "reset", "running")

    def test_reset_while_running_must_be_blocked(self):
        result = validate_state_transition("running", "reset", "running", "TEST-INTERLOCK")
        self.assertTrue(result["reset_blocked"])

    def test_invalid_transition_rejected(self):
        with self.assertRaises(ValueError):
            validate_state_transition("running", "start", "running")

    def test_measurement_plan_requires_all_domains(self):
        plan = dict(plan_id="TEST", candidate_id="A", test_condition="fixture",
            measurement_boundary="fixture", instrument_ids=["TEST"],
            sampling_method="fixture", acceptance_reference="TEST",
            procedure_revision="A", review_status="draft",
            measurements=["start_hand_jump"])
        with self.assertRaises(ValueError):
            validate_measurement_plan(plan)

if __name__ == "__main__":
    unittest.main()
