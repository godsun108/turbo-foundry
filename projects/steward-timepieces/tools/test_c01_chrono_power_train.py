"""Synthetic regression fixtures for WP-63; not C-01 design data."""
import unittest
from fractions import Fraction
from c01_chrono_power_train import (
    aggregate_measured_loads, analyze, evaluate_continuous_branch,
    evaluate_path, jumping_counter_spec, measured_shaft_power,
    validate_operating_sequence,
)

def stage(a, b, mesh="external"):
    return {"driver_teeth": a, "driven_teeth": b, "mesh_type": mesh,
            "evidence_id": "SYNTHETIC-TEST", "source_revision": "fixture-v1"}

class PowerTrainTests(unittest.TestCase):
    def test_central_seconds_ratio_closes_from_explicit_source(self):
        result = evaluate_continuous_branch("60", [stage(10, 600)], 60, 0)
        self.assertEqual(result["output_rpm"], "-1")
        self.assertTrue(result["passes_supplied_tolerance"])

    def test_compound_direction_and_exact_ratio(self):
        result = evaluate_path("120", [stage(12, 60), stage(10, 20)])
        self.assertEqual(result["signed_ratio"], "1/10")
        self.assertEqual(result["output_rpm"], "12")
        self.assertEqual(result["direction"], "same")

    def test_internal_mesh_preserves_direction(self):
        result = evaluate_path("30", [stage(10, 30, "internal")])
        self.assertEqual(result["output_rpm"], "10")
        self.assertEqual(result["direction"], "same")

    def test_invalid_mesh_and_missing_provenance_rejected(self):
        bad = stage(10, 20)
        bad["mesh_type"] = "bevel"
        with self.assertRaises(ValueError):
            evaluate_path(10, [bad])
        bad = stage(10, 20)
        del bad["evidence_id"]
        with self.assertRaises(ValueError):
            evaluate_path(10, [bad])

    def test_continuous_minute_register_example_is_conditional(self):
        result = evaluate_continuous_branch("1", [stage(10, 300)], 1800, 0)
        self.assertEqual(result["output_rpm"], "-1/30")
        self.assertTrue(result["passes_supplied_tolerance"])

    def test_jumping_counter_cadence_and_step_are_explicit(self):
        result = jumping_counter_spec(2, 30)
        self.assertEqual(result["event_interval_seconds"], "1800")
        self.assertEqual(result["angular_step_degrees"], "12")
        self.assertIn("not calculated", result["instantaneous_indexing_torque"])

    def test_power_uses_explicit_torque_and_speed(self):
        result = measured_shaft_power("0.1", "60", "TEST-EVIDENCE", "fixture-v1")
        self.assertAlmostEqual(result["shaft_power_w"], 0.1 * 2 * 3.141592653589793, places=10)

    def test_load_aggregation_requires_common_boundary_and_interval(self):
        rows = [
            {"load_id": "a", "power_w": "1/2", "measurement_boundary": "B1",
             "interval_id": "I1", "source_revision": "R1", "evidence_id": "E1"},
            {"load_id": "b", "power_w": "1/4", "measurement_boundary": "B1",
             "interval_id": "I1", "source_revision": "R1", "evidence_id": "E2"},
        ]
        self.assertEqual(aggregate_measured_loads(rows)["total_power_w"], "3/4")
        rows[1]["interval_id"] = "I2"
        with self.assertRaises(ValueError):
            aggregate_measured_loads(rows)

    def test_duplicate_load_ids_rejected(self):
        row = {"load_id": "same", "power_w": 1, "measurement_boundary": "B",
               "interval_id": "I", "source_revision": "R", "evidence_id": "E"}
        with self.assertRaises(ValueError):
            aggregate_measured_loads([row, dict(row)])

    def test_operating_sequence_and_retained_elapsed_time(self):
        result = validate_operating_sequence([
            {"command": "start", "result_state": "running"},
            {"command": "stop", "result_state": "stopped_retained"},
            {"command": "resume", "result_state": "running"},
            {"command": "stop", "result_state": "stopped_retained"},
            {"command": "reset", "result_state": "stopped_zero"},
        ])
        self.assertEqual(result["final_state"], "stopped_zero")
        self.assertFalse(result["physical_interlock_proven_by_software"])

    def test_running_reset_must_reference_physical_test_and_remain_running(self):
        with self.assertRaises(ValueError):
            validate_operating_sequence([
                {"command": "start", "result_state": "running"},
                {"command": "reset", "result_state": "stopped_zero"},
            ])
        result = validate_operating_sequence([
            {"command": "start", "result_state": "running"},
            {"command": "reset", "physical_interlock_test_id": "TEST-01",
             "result_state": "running"},
        ])
        self.assertEqual(result["final_state"], "running")

    def test_integrated_analysis_keeps_jumping_indexing_separate(self):
        result = analyze({
            "source": {"arbor_id": "SOURCE-OPEN", "rpm": "60"},
            "central_seconds": {"stages": [stage(10, 600)]},
            "counter_branches": [
                {"id": "minute", "mode": "continuous",
                 "period_seconds_per_revolution": 1800,
                 "stages": [stage(10, 30)]},
                {"id": "hour", "mode": "jumping",
                 "period_seconds_per_revolution": 43200,
                 "events_per_hour": 1, "divisions_per_revolution": 12},
            ],
        })
        self.assertFalse(result["physical_train_selected"])
        self.assertEqual(result["counter_branches"][0]["result"]["output_rpm"], "1/30")
        self.assertEqual(result["counter_branches"][1]["result"]["indexing"]["event_interval_seconds"], "3600")

if __name__ == "__main__":
    unittest.main()
