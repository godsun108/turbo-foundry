import unittest

from c01_control_test_bench import (
    compare_architectures, combine_uncertainty, evaluate_two_sided,
    validate_bench_plan, validate_instrument_register, validate_interlock_test,
    validate_procedure, validate_raw_record,
)


class TestControlTestBench(unittest.TestCase):
    def instrument(self):
        return {
            "instrument_id": "SYN-INST-01", "asset_serial": "SYN-SERIAL",
            "measurand": "force", "unit": "N", "range_min": 0.0,
            "range_max": 10.0, "resolution": 0.01,
            "calibration_id": "SYN-CAL-01", "calibration_status": "current",
            "calibration_due": "2099-01-01", "evidence_id": "SYN-EVIDENCE-01",
        }

    def test_instrument_register(self):
        self.assertTrue(validate_instrument_register([self.instrument()])["valid"])
        self.assertFalse(validate_instrument_register([self.instrument(), self.instrument()])["valid"])

    def test_procedure_never_authorizes_hardware(self):
        p = {
            "procedure_id": "SYN-PROC", "revision": "A", "architecture": "column_wheel",
            "test_type": "pusher_force_travel", "status": "approved",
            "configuration_revision": "SYN-CFG", "test_condition_id": "SYN-COND",
            "safety_review_id": "SYN-SAFE", "acceptance_requirement_id": "SYN-REQ",
            "sample_plan_id": "SYN-SAMPLE", "data_schema_revision": "A",
        }
        result = validate_procedure(p, [self.instrument()])
        self.assertTrue(result["ready_for_review"])
        self.assertFalse(result["hardware_test_authorized"])

    def test_uncertainty_and_guard_band(self):
        u = combine_uncertainty([
            {"standard_uncertainty": 0.3, "sensitivity_coefficient": 1.0},
            {"standard_uncertainty": 0.4, "sensitivity_coefficient": 1.0},
        ], 2)
        self.assertAlmostEqual(u["expanded_uncertainty"], 1.0)
        self.assertEqual(evaluate_two_sided(5, 1, 0, 10)["status"], "pass")
        self.assertEqual(evaluate_two_sided(0.5, 1, 0, 10)["status"], "indeterminate")
        self.assertEqual(evaluate_two_sided(-2, 0.5, 0, 10)["status"], "fail")

    def test_matched_architecture_comparison(self):
        common = {
            "procedure_id": "P", "procedure_revision": "A", "test_condition_id": "C",
            "unit": "N", "acceptance_requirement_id": "R",
            "measurement_method_revision": "M", "expanded_uncertainty": 0.1,
        }
        a = dict(common, architecture="column_wheel", configuration_revision="CW-A", value=2.0)
        b = dict(common, architecture="cam_lever", configuration_revision="CL-A", value=3.0)
        result = compare_architectures([a, b])
        self.assertTrue(result["comparable"])
        self.assertEqual(result["interval_relation"], "column_wheel_lower")
        self.assertFalse(result["architecture_selected"])
        b["test_condition_id"] = "different"
        self.assertFalse(compare_architectures([a, b])["comparable"])

    def test_raw_record_requires_checksum_and_traceability(self):
        record = {
            "record_id": "R", "architecture": "cam_lever", "procedure_id": "P",
            "procedure_revision": "A", "configuration_revision": "CL-A",
            "test_condition_id": "C", "timestamp_utc": "2026-11-27T00:00:00Z",
            "operator_id": "OP", "instrument_ids": ["I"], "calibration_record_ids": ["CAL"],
            "raw_source_uri": "controlled://raw/1", "raw_sha256": "abc123",
            "data_schema_revision": "A", "review_status": "unreviewed",
        }
        self.assertTrue(validate_raw_record(record)["valid"])
        del record["raw_sha256"]
        self.assertFalse(validate_raw_record(record)["valid"])

    def test_bench_plan_coverage(self):
        plan = {
            "plan_id": "WP46-SYN", "revision": "A",
            "architectures": ["column_wheel", "cam_lever"],
            "test_types": [
                "pusher_force_travel", "start_stop_observation",
                "state_transition_repeatability", "partial_stroke",
                "reset_zero_repeatability", "running_reset_interlock", "wear_endurance",
            ],
            "fixture_design_revision": "SYN-FIX-A", "risk_assessment_id": "SYN-RISK",
            "safety_approval_id": "SYN-SAFE", "data_schema_revision": "A",
            "calibration_plan_id": "SYN-CAL-PLAN", "stop_conditions_id": "SYN-STOP",
        }
        result = validate_bench_plan(plan)
        self.assertTrue(result["complete_for_engineering_review"])
        self.assertFalse(result["hardware_test_authorized"])

    def test_interlock_requires_physical_observation(self):
        record = {
            "test_id": "T", "movement_or_fixture_id": "FIX", "configuration_revision": "A",
            "approved_procedure_id": "P", "independent_observer_id": "OBS",
            "instrumented_observation_id": "VID", "attempted_reset_while_running": True,
            "chronograph_remained_running": True, "physical_block_or_disengagement_observed": True,
            "raw_evidence_id": "RAW", "review_status": "approved",
        }
        self.assertTrue(validate_interlock_test(record)["interlock_proven"])
        record["physical_block_or_disengagement_observed"] = False
        self.assertFalse(validate_interlock_test(record)["interlock_proven"])


if __name__ == "__main__":
    unittest.main()
