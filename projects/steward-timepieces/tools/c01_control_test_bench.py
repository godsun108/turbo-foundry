"""WP-46 evidence-gated chronograph control test-bench planning and evaluation.

This module validates plans and supplied measurements. It does not operate hardware,
select an architecture, create test results, or authorize prototype operation.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any, Iterable


REQUIRED_ARCHITECTURES = {"column_wheel", "cam_lever"}
REQUIRED_TESTS = {
    "pusher_force_travel",
    "start_stop_observation",
    "state_transition_repeatability",
    "partial_stroke",
    "reset_zero_repeatability",
    "running_reset_interlock",
    "wear_endurance",
}
REQUIRED_INSTRUMENT_FIELDS = {
    "instrument_id", "asset_serial", "measurand", "unit", "range_min",
    "range_max", "resolution", "calibration_id", "calibration_status",
    "calibration_due", "evidence_id",
}
REQUIRED_PROCEDURE_FIELDS = {
    "procedure_id", "revision", "architecture", "test_type", "status",
    "configuration_revision", "test_condition_id", "safety_review_id",
    "acceptance_requirement_id", "sample_plan_id", "data_schema_revision",
}


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def validate_instrument_register(instruments: list[dict]) -> dict:
    errors, seen = [], set()
    for i, item in enumerate(instruments):
        missing = REQUIRED_INSTRUMENT_FIELDS - set(item)
        if missing:
            errors.append(f"instrument[{i}] missing {sorted(missing)}")
            continue
        ident = item["instrument_id"]
        if not ident or ident in seen:
            errors.append(f"instrument[{i}] duplicate/blank instrument_id")
        seen.add(ident)
        for key in ("range_min", "range_max", "resolution"):
            if not _finite(item[key]):
                errors.append(f"instrument[{i}] {key} must be finite")
        if all(_finite(item[k]) for k in ("range_min", "range_max", "resolution")):
            if item["range_max"] <= item["range_min"] or item["resolution"] <= 0:
                errors.append(f"instrument[{i}] invalid range or resolution")
        if item["calibration_status"] not in {"current", "approved_deviation", "exempt"}:
            errors.append(f"instrument[{i}] calibration status not acceptable")
        if item["calibration_status"] == "approved_deviation" and not item.get("deviation_approval_id"):
            errors.append(f"instrument[{i}] missing deviation approval")
        if item["calibration_status"] == "exempt" and not item.get("exemption_rationale_id"):
            errors.append(f"instrument[{i}] missing exemption rationale")
        if not item["evidence_id"] or not item["calibration_id"]:
            errors.append(f"instrument[{i}] missing calibration/evidence traceability")
    return {"valid": not errors, "errors": errors, "instrument_count": len(instruments)}


def validate_procedure(procedure: dict, instruments: list[dict]) -> dict:
    errors = []
    missing = REQUIRED_PROCEDURE_FIELDS - set(procedure)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    if errors:
        return {"ready_for_review": False, "errors": errors, "hardware_test_authorized": False}
    if procedure["architecture"] not in REQUIRED_ARCHITECTURES:
        errors.append("architecture must be column_wheel or cam_lever")
    if procedure["test_type"] not in REQUIRED_TESTS:
        errors.append("unsupported test_type")
    if procedure["status"] != "approved":
        errors.append("procedure is not approved")
    if not all(procedure[k] for k in (
        "procedure_id", "revision", "configuration_revision", "test_condition_id",
        "safety_review_id", "acceptance_requirement_id", "sample_plan_id",
        "data_schema_revision"
    )):
        errors.append("required traceability references must be nonblank")
    if not instruments:
        errors.append("at least one instrument must be assigned")
    return {
        "ready_for_review": not errors,
        "errors": errors,
        # A software validator never authorizes a physical test.
        "hardware_test_authorized": False,
    }


def combine_uncertainty(contributions: list[dict], coverage_factor: float) -> dict:
    """RSS expanded uncertainty; caller must justify independence and coefficients."""
    if not _finite(coverage_factor) or coverage_factor <= 0:
        raise ValueError("coverage_factor must be finite and positive")
    if not contributions:
        raise ValueError("at least one uncertainty contribution is required")
    total = 0.0
    for item in contributions:
        if not all(_finite(item.get(k)) for k in ("standard_uncertainty", "sensitivity_coefficient")):
            raise ValueError("uncertainty terms must be finite")
        if item["standard_uncertainty"] < 0:
            raise ValueError("standard uncertainty cannot be negative")
        total += (item["sensitivity_coefficient"] * item["standard_uncertainty"]) ** 2
    uc = sqrt(total)
    return {"combined_standard_uncertainty": uc, "expanded_uncertainty": coverage_factor * uc,
            "coverage_factor": coverage_factor,
            "method": "RSS; independence/covariance treatment requires approved justification"}


def evaluate_two_sided(value: float, expanded_uncertainty: float,
                       lower: float, upper: float) -> dict:
    """Guard-band a measured value against an explicitly approved two-sided interval."""
    vals = (value, expanded_uncertainty, lower, upper)
    if not all(_finite(v) for v in vals) or expanded_uncertainty < 0 or lower > upper:
        raise ValueError("invalid measurement, uncertainty, or requirement interval")
    lo, hi = value - expanded_uncertainty, value + expanded_uncertainty
    if lo >= lower and hi <= upper:
        status = "pass"
    elif hi < lower or lo > upper:
        status = "fail"
    else:
        status = "indeterminate"
    return {"status": status, "measurement_interval": [lo, hi],
            "requirement_interval": [lower, upper]}


def validate_raw_record(record: dict) -> dict:
    required = {
        "record_id", "architecture", "procedure_id", "procedure_revision",
        "configuration_revision", "test_condition_id", "timestamp_utc",
        "operator_id", "instrument_ids", "calibration_record_ids",
        "raw_source_uri", "raw_sha256", "data_schema_revision", "review_status",
    }
    errors = []
    missing = required - set(record)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    else:
        if record["architecture"] not in REQUIRED_ARCHITECTURES:
            errors.append("invalid architecture")
        if not record["instrument_ids"] or not record["calibration_record_ids"]:
            errors.append("instrument and calibration references are required")
        if not record["raw_source_uri"] or not record["raw_sha256"]:
            errors.append("immutable raw source and checksum are required")
        if record["review_status"] not in {"unreviewed", "reviewed", "rejected"}:
            errors.append("invalid review status")
    return {"valid": not errors, "errors": errors}


def compare_architectures(results: list[dict]) -> dict:
    """Only compare matched procedure/configuration/condition/units and approved limits."""
    errors = []
    by_arch = {r.get("architecture"): r for r in results}
    if set(by_arch) != REQUIRED_ARCHITECTURES or len(results) != 2:
        errors.append("exactly one column_wheel and one cam_lever result are required")
    if errors:
        return {"comparable": False, "errors": errors}
    a, b = by_arch["column_wheel"], by_arch["cam_lever"]
    keys = ("procedure_id", "procedure_revision", "test_condition_id", "unit",
            "acceptance_requirement_id", "measurement_method_revision")
    for key in keys:
        if a.get(key) != b.get(key):
            errors.append(f"mismatched {key}")
    if a.get("configuration_revision") == b.get("configuration_revision"):
        errors.append("candidate configuration revisions must be distinct and identified")
    if not all(_finite(r.get("value")) and _finite(r.get("expanded_uncertainty")) for r in (a, b)):
        errors.append("both results require finite value and expanded uncertainty")
    if errors:
        return {"comparable": False, "errors": errors}
    ia = [a["value"] - a["expanded_uncertainty"], a["value"] + a["expanded_uncertainty"]]
    ib = [b["value"] - b["expanded_uncertainty"], b["value"] + b["expanded_uncertainty"]]
    if ia[1] < ib[0]:
        relation = "column_wheel_lower"
    elif ib[1] < ia[0]:
        relation = "cam_lever_lower"
    else:
        relation = "indeterminate_overlap"
    return {"comparable": True, "column_wheel_interval": ia,
            "cam_lever_interval": ib, "interval_relation": relation,
            "architecture_selected": False}


def validate_bench_plan(plan: dict) -> dict:
    errors = []
    if plan.get("plan_id") is None or not plan.get("revision"):
        errors.append("plan ID and revision required")
    if set(plan.get("architectures", [])) != REQUIRED_ARCHITECTURES:
        errors.append("plan must cover both column_wheel and cam_lever")
    tests = set(plan.get("test_types", []))
    missing = REQUIRED_TESTS - tests
    if missing:
        errors.append(f"missing test coverage: {sorted(missing)}")
    if not plan.get("fixture_design_revision"):
        errors.append("fixture design revision required")
    if not plan.get("risk_assessment_id") or not plan.get("safety_approval_id"):
        errors.append("risk assessment and safety approval references required")
    if not plan.get("data_schema_revision") or not plan.get("calibration_plan_id"):
        errors.append("data schema and calibration plan references required")
    if not plan.get("stop_conditions_id"):
        errors.append("stop conditions reference required")
    return {"complete_for_engineering_review": not errors, "errors": errors,
            "hardware_test_authorized": False}


def validate_interlock_test(record: dict) -> dict:
    """Require a dedicated physical proof record; logical state-machine evidence is insufficient."""
    required = ("test_id", "movement_or_fixture_id", "configuration_revision",
                "approved_procedure_id", "independent_observer_id", "instrumented_observation_id",
                "attempted_reset_while_running", "chronograph_remained_running",
                "physical_block_or_disengagement_observed", "raw_evidence_id", "review_status")
    missing = [k for k in required if k not in record]
    if missing:
        return {"complete": False, "errors": [f"missing {missing}"], "interlock_proven": False}
    passed = (
        record["attempted_reset_while_running"] is True
        and record["chronograph_remained_running"] is True
        and record["physical_block_or_disengagement_observed"] is True
        and record["review_status"] == "approved"
        and all(record[k] for k in ("test_id", "movement_or_fixture_id", "configuration_revision",
                                     "approved_procedure_id", "independent_observer_id",
                                     "instrumented_observation_id", "raw_evidence_id"))
    )
    return {"complete": True, "errors": [], "interlock_proven": bool(passed),
            "note": "Proof applies only to the identified tested configuration and procedure."}
