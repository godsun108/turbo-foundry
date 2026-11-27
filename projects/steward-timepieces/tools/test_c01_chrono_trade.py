"""Synthetic tests for the C-01 chronograph trade evaluator."""
import unittest
from c01_chrono_trade import evaluate_trade


class TradeEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.criteria = [
            {"id": "jump", "weight": 0.6, "source": "synthetic review plan",
             "acceptance_basis": "approved optical hand-jump limit"},
            {"id": "service", "weight": 0.4, "source": "synthetic review plan",
             "acceptance_basis": "approved service access criteria"},
        ]
        self.candidates = [
            {"id": "vertical", "scores": {"jump": 4, "service": 3},
             "evidence": {"jump": "synthetic test report", "service": "synthetic review"}},
            {"id": "lateral", "scores": {"jump": 3, "service": 4},
             "evidence": {"jump": "synthetic test report", "service": "synthetic review"}},
        ]

    def test_weighted_results_are_calculated_without_claiming_selection(self):
        result = evaluate_trade(self.criteria, self.candidates)
        self.assertEqual(result["results"][0]["candidate_id"], "vertical")
        self.assertAlmostEqual(result["results"][0]["weighted_score"], 3.6)
        self.assertTrue(result["approval_required"])
        self.assertTrue(result["ranking_is_provisional"])

    def test_weights_must_sum_to_one(self):
        self.criteria[0]["weight"] = 0.5
        with self.assertRaisesRegex(ValueError, "sum to 1.0"):
            evaluate_trade(self.criteria, self.candidates)

    def test_missing_evidence_rejected(self):
        del self.candidates[0]["evidence"]["jump"]
        with self.assertRaisesRegex(ValueError, "requires evidence"):
            evaluate_trade(self.criteria, self.candidates)

    def test_missing_score_rejected(self):
        del self.candidates[0]["scores"]["jump"]
        with self.assertRaisesRegex(ValueError, "missing scores"):
            evaluate_trade(self.criteria, self.candidates)

    def test_out_of_range_score_rejected(self):
        self.candidates[0]["scores"]["jump"] = 6
        with self.assertRaisesRegex(ValueError, "<= 5"):
            evaluate_trade(self.criteria, self.candidates)

    def test_single_candidate_is_not_a_trade_study(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            evaluate_trade(self.criteria, self.candidates[:1])


if __name__ == "__main__":
    unittest.main()
