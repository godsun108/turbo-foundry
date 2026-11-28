"""Synthetic regression tests for WP-67; fixtures are not C-01 design data."""
import unittest

from c01_integrated_power_campaign import (
    evaluate_acceptance, evaluate_campaign, validate_campaign_plan,
    validate_observations,
)


def plan():
    gates = {
        key: {"status": "approved", "evidence_id": f"gate-{key}"}
        for key in (
            "requirements_approved", "movement_configuration_approved",
            "test_fixture_qualified", "instrument_calibration_current",
            "measurement_boundaries_approved", "timebase_synchronization_approved",
            "uncertainty_budget_approved", "test_procedure_approved",
            "safety_review_approved", "independent_review_complete",
        )
    }
    return {
        "campaign_id": "SYNTHETIC-CAMPAIGN",
        "campaign_revision": "SYN-REV-A",
        "movement_revision": "SYN-MOV-A",
        "requirements_revision": "SYN-REQ-A",
        "procedure_revision": "SYN-PROC-A",
        "fixture_revision": "SYN-FIX-A",
        "test_condition_ids": ["SYN-COND"],
        "reserve_state_ids": ["SYN-STATE-HIGH"],
        "required_modes": ["chronograph_stopped", "chronograph_running"],
        "gates": gates,
    }


def observations():
    base = {
        "reserve_state_id": "SYN-STATE-HIGH",
        "test_condition_id": "SYN-COND",
        "boundary_id": "SYN-BOUNDARY",
        "timebase_id": "SYN-TIMEBASE",
        "interval_id": "SYN-INTERVAL",
        "source_revision": "SYN-MOV-A",
        "measurements": {"rate_s_per_day": 1.0, "amplitude_deg": 270.0},
        "expanded_uncertainty": {"rate_s_per_day": 0.2, "amplitude_deg": 2.0},
    }
    return [
        {**base, "observation_id": "SYN-OFF", "chrono_mode": "chronograph_stopped",
         "evidence_id": "SYN-EVIDENCE-OFF"},
        {**base, "observation_id": "SYN-ON", "chrono_mode": "chronograph_running",
         "evidence_id": "SYN-EVIDENCE-ON"},
    ]


def requirements():
    return [{
        "requirement_id": "SYN-RATE-LIMIT",
        "requirements_revision": "SYN-REQ-A",
        "observation_id": "SYN-OFF",
        "metric": "rate_s_per_day",
        "unit": "s/day",
        "lower_limit": -4.0,
        "upper_limit": 6.0,
        "approval_status": "approved",
        "evidence_id": "SYN-APPROVAL",
    }]


class IntegratedPowerCampaignTests(unittest.TestCase):
    def test_valid_plan_does_not_authorize_test(self):
        result = validate_campaign_plan(plan())
        self.assertTrue(result["plan_valid"])
        self.assertTrue(result["all_release_gates_approved"])
        self.assertFalse(result["physical_test_authorized"])

    def test_missing_gate_rejected(self):
        data = plan()
        del data["gates"]["safety_review_approved"]
        with self.assertRaises(ValueError):
            validate_campaign_plan(data)

    def test_campaign_requires_both_chrono_modes(self):
        data = plan()
        data["required_modes"] = ["chronograph_stopped"]
        with self.assertRaises(ValueError):
            validate_campaign_plan(data)

    def test_matched_stopped_running_pair(self):
        result = validate_observations(plan(), observations())
        self.assertEqual(result["matched_pair_group_count"], 1)
        self.assertEqual(result["unmatched_pair_groups"], 0)

    def test_mismatched_interval_is_unmatched(self):
        rows = observations()
        rows[1]["interval_id"] = "OTHER-INTERVAL"
        result = validate_observations(plan(), rows)
        self.assertEqual(result["unmatched_pair_groups"], 2)

    def test_duplicate_observation_rejected(self):
        rows = observations()
        rows[1]["observation_id"] = rows[0]["observation_id"]
        with self.assertRaises(ValueError):
            validate_observations(plan(), rows)

    def test_guard_banded_pass(self):
        result = evaluate_acceptance(observations(), requirements())
        self.assertEqual(result["overall_guard_banded_verdict"], "PASS")

    def test_guard_banded_indeterminate(self):
        req = requirements()
        req[0]["lower_limit"] = 0.9
        req[0]["upper_limit"] = 1.1
        result = evaluate_acceptance(observations(), req)
        self.assertEqual(result["overall_guard_banded_verdict"], "INDETERMINATE")

    def test_guard_banded_fail(self):
        req = requirements()
        req[0]["lower_limit"] = 3.0
        req[0]["upper_limit"] = 4.0
        result = evaluate_acceptance(observations(), req)
        self.assertEqual(result["overall_guard_banded_verdict"], "FAIL")

    def test_unapproved_requirement_rejected(self):
        req = requirements()
        req[0]["approval_status"] = "draft"
        with self.assertRaises(ValueError):
            evaluate_acceptance(observations(), req)

    def test_integrated_campaign_never_infers_reserve_or_freezes_design(self):
        result = evaluate_campaign(plan(), observations(), requirements())
        self.assertEqual(result["campaign_status"], "EVIDENCE_REVIEW_READY")
        self.assertIsNone(result["reserve_duration_hours"])
        self.assertFalse(result["design_frozen"])
        self.assertFalse(result["physical_test_authorized"])
        self.assertFalse(result["manufacturing_release_authorized"])

    def test_unapproved_gate_holds_campaign(self):
        data = plan()
        data["gates"]["safety_review_approved"]["status"] = "not_approved"
        result = evaluate_campaign(data, observations(), requirements())
        self.assertEqual(result["campaign_status"], "HOLD_FOR_REVIEW_OR_ADDITIONAL_EVIDENCE")

    def test_source_revision_must_match_campaign(self):
        rows = observations()
        rows[0]["source_revision"] = "WRONG-REVISION"
        with self.assertRaises(ValueError):
            validate_observations(plan(), rows)

    def test_requirement_revision_must_match_campaign(self):
        req = requirements()
        req[0]["requirements_revision"] = "WRONG-REVISION"
        with self.assertRaises(ValueError):
            evaluate_campaign(plan(), observations(), req)


if __name__ == "__main__":
    unittest.main()
