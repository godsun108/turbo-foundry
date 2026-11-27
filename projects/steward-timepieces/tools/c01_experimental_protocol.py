"""WP-52 controlled experimental campaign protocol validators.

This module validates planning and evidence records only. It does not control
hardware, choose sample sizes, authorize tests, or select a C-01 architecture.
"""
from __future__ import annotations

from collections import Counter

REQUIRED_TESTS = {
    "pusher_force_travel", "start_stop_observation", "state_transition_repeatability",
    "partial_stroke", "reset_to_zero", "running_reset_interlock", "wear_endurance",
}
CANDIDATES = {"column_wheel", "cam_lever"}
FAILURE_CLASSES = {
    "missed_transition", "double_transition", "incomplete_engagement",
    "unexpected_output_motion", "reset_zero_error", "running_reset_interlock_failure",
    "partial_stroke_ambiguous_state", "abnormal_force_or_travel", "jam_or_binding",
    "retention_loss", "fixture_or_instrument_fault", "data_integrity_failure",
    "visible_damage_or_wear", "other",
}
REQUIRED_RUN_FIELDS = (
    "run_id", "candidate_id", "candidate_revision", "article_id",
    "configuration_revision", "fixture_id", "fixture_revision",
    "procedure_id", "procedure_revision", "test_type", "test_condition_id",
    "operator_id", "started_at_utc", "raw_evidence_uri", "raw_sha256",
    "evidence_id", "source_revision",
)
REQUIRED_FAILURE_FIELDS = (
    "failure_id", "run_id", "failure_class", "observed_at_utc",
    "description", "raw_evidence_uri", "raw_sha256", "disposition_status",
)


def _errors_for_fields(record, fields):
    return [f"missing {field}" for field in fields if not record.get(field)]


def validate_sample_plan(plan):
    """Require an explicitly approved sample size; intentionally provide no default."""
    errors = _errors_for_fields(plan, (
        "plan_id", "revision", "test_type", "population_definition",
        "sample_size_per_candidate", "sample_size_rationale",
        "statistical_or_engineering_basis", "acceptance_plan_id",
        "approval_record_id", "approved_by", "approval_date",
    ))
    n = plan.get("sample_size_per_candidate")
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        errors.append("sample_size_per_candidate must be an explicitly approved positive integer")
    if plan.get("candidate_scope") != sorted(CANDIDATES):
        errors.append("candidate_scope must explicitly cover column_wheel and cam_lever")
    return {
        "complete_for_review": not errors,
        "errors": errors,
        "sample_size_selected_by_software": False,
        "hardware_test_authorized": False,
    }


def validate_candidate_pair(pair):
    errors = []
    for candidate in sorted(CANDIDATES):
        row = pair.get(candidate, {})
        errors.extend(f"{candidate}: {e}" for e in _errors_for_fields(row, (
            "candidate_revision", "article_id", "configuration_revision",
            "clutch_configuration_revision", "assembly_record_id",
            "lubrication_record_id",
        )))
    if pair.get("common_fixture_id") is None or not pair.get("common_fixture_revision"):
        errors.append("a controlled common fixture identity and revision are required")
    if pair.get("common_procedure_revision") is None:
        errors.append("a common procedure revision is required")
    if pair.get("common_test_condition_id") is None:
        errors.append("a common test-condition ID is required")
    a, b = pair.get("column_wheel", {}), pair.get("cam_lever", {})
    if a.get("configuration_revision") == b.get("configuration_revision") and a.get("configuration_revision"):
        errors.append("candidate configuration revisions must be distinct")
    return {"matched_pair_complete": not errors, "errors": errors}


def validate_run_order(order, planned_blocks):
    errors = []
    if not isinstance(order, list) or not order:
        return {"valid": False, "errors": ["run_order must be a non-empty list"]}
    if not isinstance(planned_blocks, list) or not planned_blocks:
        errors.append("planned_blocks must be explicitly defined")
    expected = Counter()
    for block in planned_blocks or []:
        if not block.get("block_id") or not block.get("test_type"):
            errors.append("each block requires block_id and test_type")
        if block.get("test_type") not in REQUIRED_TESTS:
            errors.append(f"unsupported test type in block: {block.get('test_type')}")
        expected[block.get("block_id")] += 1
    seen = Counter()
    for i, row in enumerate(order):
        if row.get("candidate_id") not in CANDIDATES:
            errors.append(f"run_order[{i}] has invalid candidate_id")
        if not row.get("block_id"):
            errors.append(f"run_order[{i}] missing block_id")
        seen[row.get("block_id")] += 1
    if seen != expected:
        errors.append("run order must contain exactly one CW and one CL run per planned block")
    for block_id in expected:
        candidates = [r.get("candidate_id") for r in order if r.get("block_id") == block_id]
        if Counter(candidates) != Counter({"column_wheel": 1, "cam_lever": 1}):
            errors.append(f"block {block_id} must include one run for each candidate")
    return {"valid": not errors, "errors": errors,
            "randomization_or_counterbalance_recorded": bool(order) and all(
                r.get("order_assignment_record_id") for r in order)}


def validate_campaign_plan(plan):
    errors = []
    errors.extend(_errors_for_fields(plan, (
        "campaign_id", "revision", "requirements_baseline_id",
        "risk_assessment_id", "safety_approval_id", "fixture_qualification_id",
        "calibration_plan_id", "uncertainty_budget_id", "data_schema_revision",
        "stop_conditions_id", "independent_reviewer_id", "design_authority_review_id",
    )))
    if set(plan.get("test_types", [])) != REQUIRED_TESTS:
        errors.append("campaign must explicitly cover all seven WP-46 test families")
    sample_plans = plan.get("sample_plans", [])
    covered = {p.get("test_type") for p in sample_plans}
    if covered != REQUIRED_TESTS:
        errors.append("one approved sample plan is required for each test family")
    for p in sample_plans:
        result = validate_sample_plan(p)
        if not result["complete_for_review"]:
            errors.append(f"sample plan {p.get('plan_id', '<unnamed>')} incomplete: {result['errors']}")
    pair = validate_candidate_pair(plan.get("candidate_pair", {}))
    if not pair["matched_pair_complete"]:
        errors.extend(pair["errors"])
    order = validate_run_order(plan.get("run_order", []), plan.get("planned_blocks", []))
    if not order["valid"]:
        errors.extend(order["errors"])
    if not order.get("randomization_or_counterbalance_recorded"):
        errors.append("each run requires a recorded randomized/counterbalanced order assignment")
    return {
        "complete_for_independent_review": not errors,
        "errors": errors,
        "hardware_test_authorized": False,
        "architecture_selected": False,
        "note": "Completeness is not approval. Separate article-specific release and test authorization remain mandatory.",
    }


def validate_run_record(record):
    errors = _errors_for_fields(record, REQUIRED_RUN_FIELDS)
    if record.get("candidate_id") not in CANDIDATES:
        errors.append("candidate_id must be column_wheel or cam_lever")
    if record.get("test_type") not in REQUIRED_TESTS:
        errors.append("test_type is not a defined WP-46 test family")
    checksum = record.get("raw_sha256")
    if checksum and (len(checksum) != 64 or any(c not in "0123456789abcdefABCDEF" for c in checksum)):
        errors.append("raw_sha256 must be a 64-character hexadecimal SHA-256 digest")
    if record.get("raw_data_modified") is True:
        errors.append("native raw evidence must remain immutable; create a derived record instead")
    return {"valid": not errors, "errors": errors, "acceptance_pass_implied": False}


def validate_failure_record(record):
    errors = _errors_for_fields(record, REQUIRED_FAILURE_FIELDS)
    if record.get("failure_class") not in FAILURE_CLASSES:
        errors.append("failure_class must use the controlled taxonomy")
    checksum = record.get("raw_sha256")
    if checksum and (len(checksum) != 64 or any(c not in "0123456789abcdefABCDEF" for c in checksum)):
        errors.append("raw_sha256 must be a 64-character hexadecimal SHA-256 digest")
    if record.get("disposition_status") not in {"open", "contained", "reviewed", "closed"}:
        errors.append("disposition_status must be open, contained, reviewed, or closed")
    if record.get("disposition_status") == "closed" and not record.get("disposition_record_id"):
        errors.append("closed failure requires a disposition_record_id")
    return {"valid": not errors, "errors": errors,
            "campaign_continuation_authorized": False}


def validate_campaign_ledger(runs, failures):
    errors = []
    if not isinstance(runs, list) or not runs:
        errors.append("at least one run record is required")
        runs = []
    ids = [r.get("run_id") for r in runs]
    if len(ids) != len(set(ids)):
        errors.append("run_id values must be unique")
    for r in runs:
        result = validate_run_record(r)
        if not result["valid"]:
            errors.append(f"run {r.get('run_id')}: {result['errors']}")
    run_ids = set(ids)
    for f in failures:
        result = validate_failure_record(f)
        if not result["valid"]:
            errors.append(f"failure {f.get('failure_id')}: {result['errors']}")
        if f.get("run_id") not in run_ids:
            errors.append(f"failure {f.get('failure_id')} references an unknown run")
    return {"ledger_structurally_valid": not errors, "errors": errors,
            "raw_evidence_overwritten": False, "architecture_selected": False}


def validate_physical_interlock_evidence(record):
    """Logical simulation or a drawing cannot satisfy this physical proof checklist."""
    required = (
        "test_id", "article_id", "configuration_revision", "approved_procedure_id",
        "article_release_record_id", "independent_observer_id",
        "instrumented_observation_id", "raw_video_or_encoder_evidence_id",
        "attempted_reset_while_running", "chronograph_remained_running",
        "physical_block_or_disengagement_observed", "post_test_inspection_id",
        "review_status",
    )
    errors = _errors_for_fields(record, required)
    if record.get("review_status") not in {"pending", "approved", "rejected"}:
        errors.append("review_status must be pending, approved, or rejected")
    passed = (
        not errors and record.get("attempted_reset_while_running") is True
        and record.get("chronograph_remained_running") is True
        and record.get("physical_block_or_disengagement_observed") is True
        and record.get("review_status") == "approved"
    )
    return {
        "record_complete": not errors,
        "errors": errors,
        "physical_interlock_proven_for_identified_configuration": bool(passed),
        "simulation_counts_as_physical_proof": False,
        "further_running_reset_testing_authorized": False,
    }
