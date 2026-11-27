import unittest
from c01_control_analysis import (
    AnalysisError, descriptive_statistics, expanded_uncertainty_interval,
    force_travel_curve, event_latency_summary, reset_repeatability,
    state_transition_reliability, validate_matched_runs, build_dashboard,
)

class TestControlAnalysis(unittest.TestCase):
    def test_descriptive_statistics(self):
        r = descriptive_statistics([1, 2, 3])
        self.assertEqual(r["count"], 3)
        self.assertEqual(r["mean"], 2)
        self.assertEqual(r["range"], 2)

    def test_uncertainty_requires_independence(self):
        with self.assertRaises(AnalysisError):
            expanded_uncertainty_interval(10, .2, 2, False)
        r = expanded_uncertainty_interval(10, .2, 2, True)
        self.assertAlmostEqual(r["lower"], 9.6)
        self.assertAlmostEqual(r["upper"], 10.4)

    def test_force_travel_curve_and_signed_work(self):
        r = force_travel_curve([
            {"time_s": 0, "travel_mm": 0, "force_n": 2},
            {"time_s": 1, "travel_mm": 2, "force_n": 4},
            {"time_s": 2, "travel_mm": 0, "force_n": 2},
        ], "R1", "E1", "S1")
        self.assertEqual(len(r["points"]), 3)
        self.assertAlmostEqual(r["signed_path_work_j"], 0)
        self.assertEqual(r["peak_sampled_force_n"], 4)

    def test_force_curve_rejects_nonmonotonic_time(self):
        with self.assertRaises(AnalysisError):
            force_travel_curve([
                {"time_s": 1, "travel_mm": 0, "force_n": 1},
                {"time_s": 1, "travel_mm": 1, "force_n": 1},
            ], "R", "E", "S")

    def test_latency_summary(self):
        r = event_latency_summary([.1, .2, .3])
        self.assertEqual(r["unit"], "s")
        self.assertAlmostEqual(r["median"], .2)

    def test_reset_wrap_and_repeatability(self):
        r = reset_repeatability([359, 1], 0)
        self.assertAlmostEqual(r["circular_mean_error_deg"], 0, places=6)
        self.assertAlmostEqual(r["maximum_absolute_error_deg"], 1)

    def test_state_reliability(self):
        r = state_transition_reliability([
            {"expected_state": "running", "observed_state": "running"},
            {"expected_state": "stopped", "observed_state": "running"},
        ], 1.96)
        self.assertEqual(r["successful_transitions"], 1)
        self.assertEqual(r["failed_transitions"], 1)
        self.assertLess(r["wilson_interval"][0], .5)
        self.assertGreater(r["wilson_interval"][1], .5)

    def test_matched_run_metadata(self):
        a = {"run_id":"A","candidate_id":"CW","procedure_revision":"P1",
             "test_condition_id":"T1","fixture_revision":"F1","evidence_id":"E1","source_revision":"S1"}
        b = {**a, "run_id":"B", "candidate_id":"CL"}
        self.assertTrue(validate_matched_runs(a,b)["metadata_match"])
        b["fixture_revision"] = "F2"
        self.assertFalse(validate_matched_runs(a,b)["metadata_match"])

    def test_dashboard_is_provenance_preserving_and_neutral(self):
        base = {"procedure_revision":"P1","test_condition_id":"T1","fixture_revision":"F1",
                "evidence_id":"E","source_revision":"S","zero_datum_deg":0}
        runs = [
            {**base, "run_id":"R1","candidate_id":"CW",
             "start_stop_latency_s":[.1,.2],
             "reset_observations_deg":[359,1]},
            {**base, "run_id":"R2","candidate_id":"CL",
             "state_trials":[{"expected_state":"running","observed_state":"running"}]},
        ]
        d = build_dashboard(runs, 1.96)
        self.assertEqual(d["candidate_count"], 2)
        self.assertEqual(d["decision_status"], "NO_ARCHITECTURE_SELECTED")
        self.assertEqual(d["candidate_runs"]["CW"][0]["evidence_id"], "E")

    def test_dashboard_requires_provenance(self):
        with self.assertRaises(AnalysisError):
            build_dashboard([{"run_id":"R"}], 1.96)

if __name__ == "__main__":
    unittest.main()
