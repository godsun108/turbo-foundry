"""WP-67 integrated movement power and reserve campaign validator.

This module validates supplied campaign definitions and measured evidence. It
never synthesizes measurements, predicts reserve duration, selects hardware,
or authorizes a physical test, design freeze, or manufacture.
"""
from __future__ import annotations

from math import isfinite
from typing import Any

REQUIRED_GATES = {
    "requirements_approved", "movement_configuration_approved",
    "test_fixture_qualified", "instrument_calibration_current",
    "measurement_boundaries_approved", "timebase_synchronization_approved",
    "uncertainty_budget_approved", "test_procedure_approved",
    "safety_review_approved", "independent_review_complete",
}
MODES = {"chronograph_stopped", "chronograph_running"}


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty identifier")
    return value


def _number(value: Any, field: str, *, nonnegative: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be finite numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite numeric") from exc
    if not isfinite(result):
        raise ValueError(f"{field} must be finite numeric")
    if nonnegative and result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def validate_campaign_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Validate a controlled campaign matrix without inventing sample counts."""
    for field in ("campaign_id", "campaign_revision", "movement_revision",
                  "requirements_revision", "procedure_revision",
                  "fixture_revision", "test_condition_ids", "reserve_state_ids",
                  "required_modes", "gates"):
        if field not in plan:
            raise ValueError(f"campaign plan missing {field}")
    for field in ("campaign_id", "campaign_revision", "movement_revision",
                  "requirements_revision", "procedure_revision", "fixture_revision"):
        _text(plan[field], field)
    for field in ("test_condition_ids", "reserve_state_ids", "required_modes"):
        values = plan[field]
        if not isinstance(values, list) or not values:
            raise ValueError(f"{field} must be a non-empty list")
        if any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f"{field} entries must be non-empty identifiers")
        if len(values) != len(set(values)):
            raise ValueError(f"{field} entries must be unique")
    if not set(plan["required_modes"]).issubset(MODES):
        raise ValueError("required_modes contains an unsupported chronograph mode")
    if not MODES.issubset(set(plan["required_modes"])):
        raise ValueError("campaign must include chronograph stopped and running modes")
    gates = plan["gates"]
    if not isinstance(gates, dict):
        raise ValueError("gates must be a mapping")
    missing = REQUIRED_GATES - set(gates)
    if missing:
        raise ValueError(f"campaign gates missing: {sorted(missing)}")
    for gate in REQUIRED_GATES:
        record = gates[gate]
        if not isinstance(record, dict):
            raise ValueError(f"{gate} must be a gate record")
        if record.get("status") not in {"approved", "not_approved"}:
            raise ValueError(f"{gate}.status must be approved or not_approved")
        _text(record.get("evidence_id"), f"{gate}.evidence_id")
    return {
        "campaign_id": plan["campaign_id"],
        "plan_valid": True,
        "all_release_gates_approved": all(
            plan["gates"][gate]["status"] == "approved" for gate in REQUIRED_GATES
        ),
        "reserve_states_declared": len(plan["reserve_state_ids"]),
        "test_conditions_declared": len(plan["test_condition_ids"]),
        "sample_count_policy": "DEFINED_BY_APPROVED_PROCEDURE_NOT_ASSUMED_HERE",
        "physical_test_authorized": False,
    }


def validate_observations(plan: dict[str, Any],
                          observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate raw result summaries and their matched stopped/running pairs."""
    validate_campaign_plan(plan)
    if not isinstance(observations, list) or not observations:
        raise ValueError("observations must be a non-empty list")
    ids: list[str] = []
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(observations):
        prefix = f"observations[{index}]"
        required = ("observation_id", "reserve_state_id", "chrono_mode",
                    "test_condition_id", "boundary_id", "timebase_id",
                    "interval_id", "evidence_id", "source_revision",
                    "measurements", "expanded_uncertainty")
        for field in required:
            if field not in row:
                raise ValueError(f"{prefix} missing {field}")
        oid = _text(row["observation_id"], f"{prefix}.observation_id")
        ids.append(oid)
        if row["reserve_state_id"] not in plan["reserve_state_ids"]:
            raise ValueError(f"{oid} references undeclared reserve state")
        if row["chrono_mode"] not in plan["required_modes"]:
            raise ValueError(f"{oid} references undeclared chronograph mode")
        if row["test_condition_id"] not in plan["test_condition_ids"]:
            raise ValueError(f"{oid} references undeclared test condition")
        for field in ("boundary_id", "timebase_id", "interval_id",
                      "evidence_id", "source_revision"):
            _text(row[field], f"{oid}.{field}")
        measurements = row["measurements"]
        uncertainty = row["expanded_uncertainty"]
        if not isinstance(measurements, dict) or not measurements:
            raise ValueError(f"{oid}.measurements must be a non-empty mapping")
        if not isinstance(uncertainty, dict):
            raise ValueError(f"{oid}.expanded_uncertainty must be a mapping")
        clean_measurements = {}
        clean_uncertainty = {}
        for metric, value in measurements.items():
            _text(metric, f"{oid}.measurement metric")
            clean_measurements[metric] = _number(value, f"{oid}.{metric}")
            if metric not in uncertainty:
                raise ValueError(f"{oid} lacks expanded uncertainty for {metric}")
            clean_uncertainty[metric] = _number(
                uncertainty[metric], f"{oid}.{metric} expanded uncertainty",
                nonnegative=True)
        if len(clean_measurements) != len(clean_uncertainty):
            raise ValueError(f"{oid} uncertainty keys do not match measurements")
        normalized.append({**row, "measurements": clean_measurements,
                           "expanded_uncertainty": clean_uncertainty})
    if len(ids) != len(set(ids)):
        raise ValueError("observation_id values must be unique")

    pair_groups: dict[tuple[str, ...], set[str]] = {}
    for row in normalized:
        key = (row["reserve_state_id"], row["test_condition_id"],
               row["boundary_id"], row["timebase_id"], row["interval_id"],
               row["source_revision"])
        pair_groups.setdefault(key, set()).add(row["chrono_mode"])
    incomplete = [key for key, modes in pair_groups.items()
                  if not MODES.issubset(modes)]
    return {
        "observations_valid": True,
        "observation_count": len(normalized),
        "matched_pair_group_count": sum(
            1 for modes in pair_groups.values() if MODES.issubset(modes)),
        "unmatched_pair_groups": len(incomplete),
        "pairing_key": [
            "reserve_state_id", "test_condition_id", "boundary_id",
            "timebase_id", "interval_id", "source_revision"
        ],
        "evidence_ids_preserved": True,
    }


def evaluate_acceptance(observations: list[dict[str, Any]],
                        requirements: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply approved two-sided limits using expanded-uncertainty guard bands.

    A result passes only when its entire uncertainty interval is inside the
    approved interval. A result wholly outside fails; overlap is indeterminate.
    """
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("requirements must be a non-empty list")
    by_id = {row["observation_id"]: row for row in observations}
    if len(by_id) != len(observations):
        raise ValueError("observation IDs must be unique")
    results = []
    seen = set()
    for index, req in enumerate(requirements):
        rid = _text(req.get("requirement_id"), f"requirements[{index}].requirement_id")
        if rid in seen:
            raise ValueError("requirement IDs must be unique")
        seen.add(rid)
        if req.get("approval_status") != "approved":
            raise ValueError(f"{rid} is not an approved acceptance requirement")
        _text(req.get("requirements_revision"), f"{rid}.requirements_revision")
        _text(req.get("observation_id"), f"{rid}.observation_id")
        _text(req.get("metric"), f"{rid}.metric")
        _text(req.get("unit"), f"{rid}.unit")
        _text(req.get("evidence_id"), f"{rid}.evidence_id")
        obs = by_id.get(req["observation_id"])
        if obs is None:
            raise ValueError(f"{rid} references unknown observation")
        metric = req["metric"]
        if metric not in obs["measurements"]:
            raise ValueError(f"{rid} metric is absent from observation")
        lower = _number(req.get("lower_limit"), f"{rid}.lower_limit")
        upper = _number(req.get("upper_limit"), f"{rid}.upper_limit")
        if lower > upper:
            raise ValueError(f"{rid} lower_limit exceeds upper_limit")
        value = obs["measurements"][metric]
        uncertainty = obs["expanded_uncertainty"][metric]
        interval = (value - uncertainty, value + uncertainty)
        if interval[0] >= lower and interval[1] <= upper:
            verdict = "PASS"
        elif interval[1] < lower or interval[0] > upper:
            verdict = "FAIL"
        else:
            verdict = "INDETERMINATE"
        results.append({
            "requirement_id": rid, "observation_id": obs["observation_id"],
            "metric": metric, "unit": req["unit"], "measured_value": value,
            "expanded_uncertainty": uncertainty,
            "guard_banded_interval": list(interval),
            "approved_limits": [lower, upper], "verdict": verdict,
            "requirement_evidence_id": req["evidence_id"],
            "measurement_evidence_id": obs["evidence_id"],
        })
    verdicts = {r["verdict"] for r in results}
    overall = ("FAIL" if "FAIL" in verdicts else
               "INDETERMINATE" if "INDETERMINATE" in verdicts else "PASS")
    return {
        "acceptance_results": results,
        "overall_guard_banded_verdict": overall,
        "verdict_scope": "ONLY_THE_SUPPLIED_APPROVED_REQUIREMENTS_AND_OBSERVATIONS",
        "design_frozen": False,
        "prototype_test_authorized": False,
        "manufacturing_release_authorized": False,
    }


def evaluate_campaign(plan: dict[str, Any], observations: list[dict[str, Any]],
                      requirements: list[dict[str, Any]]) -> dict[str, Any]:
    """Fail-closed integrated campaign summary; no reserve-hour extrapolation."""
    plan_result = validate_campaign_plan(plan)
    evidence_result = validate_observations(plan, observations)
    acceptance = evaluate_acceptance(observations, requirements)
    gates_approved = plan_result["all_release_gates_approved"]
    paired = evidence_result["unmatched_pair_groups"] == 0
    requirements_pass = acceptance["overall_guard_banded_verdict"] == "PASS"
    campaign_status = (
        "EVIDENCE_REVIEW_READY" if gates_approved and paired and requirements_pass
        else "HOLD_FOR_REVIEW_OR_ADDITIONAL_EVIDENCE"
    )
    return {
        "campaign_id": plan["campaign_id"],
        "campaign_status": campaign_status,
        "plan": plan_result,
        "evidence": evidence_result,
        "acceptance": acceptance,
        "reserve_duration_hours": None,
        "reserve_duration_statement":
            "NO_DURATION_INFERRED; report only a separately approved, directly measured endurance result",
        "sixty_to_seventy_hour_target": "UNVERIFIED_UNLESS_DIRECTLY_MEASURED_AND_APPROVED",
        "architecture_selected": False,
        "design_frozen": False,
        "physical_test_authorized": False,
        "manufacturing_release_authorized": False,
    }
