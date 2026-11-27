import unittest

from c01_experimental_protocol import (
    REQUIRED_TESTS, validate_sample_plan, validate_candidate_pair,
    validate_run_order, validate_campaign_plan, validate_run_record,
    validate_failure_record, validate_campaign_ledger,
    validate_physical_interlock_evidence,
)


def sample_plan(test_type):
    return {
        "plan_id": f"SP-{test_type}", "revision": "A", "test_type": test_type,
        "population_definition": "Defined prototype article population",
        "sample_size_per_candidate": 12,
        "sample_size_rationale": "Synthetic fixture only; value is not a C-01 recommendation",
        "statistical_or_engineering_basis": "Approved analysis basis reference",
        "acceptance_plan_id": "AP-1", "approval_record_id": "APR-1",
        "approved_by": "reviewer", "approval_date": "2026-11-27",
        "candidate_scope": ["cam_lever", "column_wheel"],
    }


def pair():
    return {
        "column_wheel": {
            "candidate_revision": "CW-A", "article_id": "CW-01",
            "configuration_revision": "CFG-CW-A", "clutch_configuration_revision": "CLUTCH-1",
            "assembly_record_id": "ASM-CW", "lubrication_record_id": "LUBE-CW",
        },
        "cam_lever": {
            "candidate_revision": "CL-A", "article_id": "CL-01",
            "configuration_revision": "CFG-CL-A", "clutch_configuration_revision": "CLUTCH-1",
            "assembly_record_id": "ASM-CL", "lubrication_record_id": "LUBE-CL",
        },
        "common_fixture_id": "FIX-1", "common_fixture_revision": "A",
        "common_procedure_revision": "A", "common_test_condition_id": "TC-1",
    }


def run(run_id, candidate="column_wheel"):
    return {
        "run_id": run_id, "candidate_id": candidate, "candidate_revision": "A",
        "article_id": "ARTICLE-1", "configuration_revision": "CFG-1",
        "fixture_id": "FIX-1", "fixture_revision": "A",
        "procedure_id": "TP-1", "procedure_revision": "A",
        "test_type": "pusher_force_travel", "test_condition_id": "TC-1",
        "operator_id": "OP-1", "started_at_utc": "2026-11-27T12:00:00Z",
        "raw_evidence_uri": "evidence://raw/run-1", "raw_sha256": "a" * 64,
        "evidence_id": "EV-1", "source_revision": "SRC-1",
    }


class ExperimentalProtocolTests(unittest.TestCase):
    def test_sample_size_is_never_defaulted(self):
        p = sample_plan("pusher_force_travel")
        del p["sample_size_per_candidate"]
        result = validate_sample_plan(p)
        self.assertFalse(result["complete_for_review"])
        self.assertFalse(result["sample_size_selected_by_software"])

    def test_sample_plan_requires_explicit_approval(self):
        p = sample_plan("pusher_force_travel")
        p["sample_size_per_candidate"] = 0
        p["approval_record_id"] = ""
        self.assertFalse(validate_sample_plan(p)["complete_for_review"])

    def test_candidate_pair_requires_common_controls(self):
        p = pair()
        p["common_fixture_revision"] = ""
        self.assertFalse(validate_candidate_pair(p)["matched_pair_complete"])

    def test_run_order_requires_both_candidates_per_block(self):
        blocks = [{"block_id": "B1", "test_type": "pusher_force_travel"}]
        order = [
            {"block_id": "B1", "candidate_id": "column_wheel", "order_assignment_record_id": "R1"}
        ]
        self.assertFalse(validate_run_order(order, blocks)["valid"])

    def test_run_order_records_counterbalance_assignment(self):
        blocks = [{"block_id": "B1", "test_type": "pusher_force_travel"}]
        order = [
            {"block_id": "B1", "candidate_id": "column_wheel", "order_assignment_record_id": "R1"},
            {"block_id": "B1", "candidate_id": "cam_lever", "order_assignment_record_id": "R2"},
        ]
        result = validate_run_order(order, blocks)
        self.assertTrue(result["valid"])
        self.assertTrue(result["randomization_or_counterbalance_recorded"])

    def test_run_record_checksum_and_immutability(self):
        r = run("RUN-1")
        r["raw_sha256"] = "bad"
        self.assertFalse(validate_run_record(r)["valid"])
        r = run("RUN-2")
        r["raw_data_modified"] = True
        self.assertFalse(validate_run_record(r)["valid"])

    def test_failure_requires_taxonomy_and_disposition(self):
        f = {
            "failure_id": "F-1", "run_id": "RUN-1",
            "failure_class": "missed_transition", "observed_at_utc": "2026-11-27T12:01:00Z",
            "description": "Synthetic test fixture failure",
            "raw_evidence_uri": "evidence://raw/f1", "raw_sha256": "b" * 64,
            "disposition_status": "closed", "disposition_record_id": "DISP-1",
        }
        self.assertTrue(validate_failure_record(f)["valid"])
        del f["disposition_record_id"]
        self.assertFalse(validate_failure_record(f)["valid"])

    def test_ledger_rejects_duplicate_run_ids(self):
        r = run("RUN-1")
        result = validate_campaign_ledger([r, dict(r)], [])
        self.assertFalse(result["ledger_structurally_valid"])

    def test_physical_interlock_requires_approved_physical_evidence(self):
        record = {
            "test_id": "IT-1", "article_id": "ARTICLE-1", "configuration_revision": "CFG-1",
            "approved_procedure_id": "TP-INT-1", "article_release_record_id": "REL-1",
            "independent_observer_id": "OBS-1", "instrumented_observation_id": "DAQ-1",
            "raw_video_or_encoder_evidence_id": "RAW-1", "attempted_reset_while_running": True,
            "chronograph_remained_running": True, "physical_block_or_disengagement_observed": True,
            "post_test_inspection_id": "POST-1", "review_status": "approved",
        }
        self.assertTrue(validate_physical_interlock_evidence(record)[
            "physical_interlock_proven_for_identified_configuration"])
        record["raw_video_or_encoder_evidence_id"] = ""
        self.assertFalse(validate_physical_interlock_evidence(record)[
            "physical_interlock_proven_for_identified_configuration"])

    def test_simulation_does_not_prove_interlock(self):
        result = validate_physical_interlock_evidence({"simulation_passed": True})
        self.assertFalse(result["physical_interlock_proven_for_identified_configuration"])
        self.assertFalse(result["simulation_counts_as_physical_proof"])

    def test_campaign_requires_all_test_families_and_approved_sample_plans(self):
        plans = [sample_plan(t) for t in sorted(REQUIRED_TESTS)]
        blocks = [{"block_id": f"B-{t}", "test_type": t} for t in sorted(REQUIRED_TESTS)]
        order = []
        for block in blocks:
            order.extend([
                {"block_id": block["block_id"], "candidate_id": "column_wheel",
                 "order_assignment_record_id": f"{block['block_id']}-1"},
                {"block_id": block["block_id"], "candidate_id": "cam_lever",
                 "order_assignment_record_id": f"{block['block_id']}-2"},
            ])
        plan = {
            "campaign_id": "CAMP-1", "revision": "A", "requirements_baseline_id": "REQ-1",
            "risk_assessment_id": "RISK-1", "safety_approval_id": "SAFE-1",
            "fixture_qualification_id": "FIXQ-1", "calibration_plan_id": "CAL-1",
            "uncertainty_budget_id": "UNC-1", "data_schema_revision": "A",
            "stop_conditions_id": "STOP-1", "independent_reviewer_id": "REV-1",
            "design_authority_review_id": "DA-1", "test_types": sorted(REQUIRED_TESTS),
            "sample_plans": plans, "candidate_pair": pair(),
            "planned_blocks": blocks, "run_order": order,
        }
        result = validate_campaign_plan(plan)
        self.assertTrue(result["complete_for_independent_review"])
        self.assertFalse(result["hardware_test_authorized"])
        self.assertFalse(result["architecture_selected"])


if __name__ == "__main__":
    unittest.main()
