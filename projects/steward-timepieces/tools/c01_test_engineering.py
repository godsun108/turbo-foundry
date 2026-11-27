"""WP-30 controlled test engineering and evidence validation.

Validates test definitions and recorded evidence. It does not operate
instruments, calibrate hardware, or certify a physical movement.
"""
from __future__ import annotations
from math import isfinite, sqrt
from typing import Any


def _text(v: Any, name: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{name} is required")
    return v


def _num(v: Any, name: str, *, positive: bool = False,
         nonnegative: bool = False) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(x):
        raise ValueError(f"{name} must be finite")
    if positive and x <= 0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and x < 0:
        raise ValueError(f"{name} must be non-negative")
    return x


def validate_instrument_register(instruments: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(instruments, list) or not instruments:
        raise ValueError("instruments must be a non-empty list")
    ids, normalized = [], []
    for i, item in enumerate(instruments):
        iid = _text(item.get("instrument_id"), f"instruments[{i}].instrument_id")
        ids.append(iid)
        for field in ("description", "serial_or_asset_id", "calibration_record_id",
                      "calibration_due_date", "range_and_resolution", "measurement_unit"):
            _text(item.get(field), f"{iid}.{field}")
        status = _text(item.get("calibration_status"), f"{iid}.calibration_status")
        if status not in ("in_calibration", "not_in_calibration", "not_required_justified"):
            raise ValueError(f"{iid}.calibration_status is not an allowed controlled status")
        if status == "not_in_calibration" and item.get("approved_deviation_id") is None:
            raise ValueError(f"{iid} requires approved_deviation_id or must be in calibration")
        if status == "not_required_justified":
            _text(item.get("calibration_exemption_rationale"), f"{iid}.calibration_exemption_rationale")
        normalized.append({"instrument_id": iid, "calibration_status": status,
                           "calibration_record_id": item["calibration_record_id"],
                           "calibration_due_date": item["calibration_due_date"]})
    if len(ids) != len(set(ids)):
        raise ValueError("instrument_id values must be unique")
    return {"instrument_count": len(normalized), "instruments": normalized,
            "register_complete": True}


def evaluate_uncertainty(budget: dict[str, Any]) -> dict[str, Any]:
    """Combine independent standard uncertainty components by root-sum-square."""
    _text(budget.get("measurand"), "measurand")
    unit = _text(budget.get("unit"), "unit")
    _text(budget.get("method_reference"), "method_reference")
    components = budget.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("uncertainty components must be a non-empty list")
    ids, squares, rows = [], [], []
    for i, c in enumerate(components):
        cid = _text(c.get("component_id"), f"components[{i}].component_id")
        ids.append(cid)
        value = _num(c.get("standard_uncertainty"), f"{cid}.standard_uncertainty",
                     nonnegative=True)
        _text(c.get("source_or_rationale"), f"{cid}.source_or_rationale")
        divisor = _num(c.get("sensitivity_coefficient", 1.0),
                       f"{cid}.sensitivity_coefficient")
        contribution = abs(divisor) * value
        squares.append(contribution ** 2)
        rows.append({"component_id": cid, "standard_uncertainty": value,
                     "sensitivity_coefficient": divisor,
                     "standard_contribution": contribution})
    if len(ids) != len(set(ids)):
        raise ValueError("uncertainty component IDs must be unique")
    combined = sqrt(sum(squares))
    coverage = _num(budget.get("coverage_factor"), "coverage_factor", positive=True)
    return {"measurand": budget["measurand"], "unit": unit,
            "components": rows, "combined_standard_uncertainty": combined,
            "coverage_factor": coverage, "expanded_uncertainty": coverage*combined,
            "combination_method": "root_sum_square_independent_components",
            "independence_assumption_requires_justification": True,
            "uncertainty_budget_is_approved": budget.get("approved") is True}


def validate_test_procedure(procedure: dict[str, Any]) -> dict[str, Any]:
    pid = _text(procedure.get("procedure_id"), "procedure_id")
    _text(procedure.get("revision"), f"{pid}.revision")
    _text(procedure.get("objective"), f"{pid}.objective")
    _text(procedure.get("requirement_ids"), f"{pid}.requirement_ids")
    _text(procedure.get("setup_and_boundary"), f"{pid}.setup_and_boundary")
    _text(procedure.get("preconditions"), f"{pid}.preconditions")
    _text(procedure.get("steps"), f"{pid}.steps")
    _text(procedure.get("data_fields"), f"{pid}.data_fields")
    _text(procedure.get("safety_and_stop_conditions"), f"{pid}.safety_and_stop_conditions")
    _text(procedure.get("acceptance_criteria_reference"), f"{pid}.acceptance_criteria_reference")
    _text(procedure.get("instrument_ids"), f"{pid}.instrument_ids")
    _text(procedure.get("uncertainty_budget_id"), f"{pid}.uncertainty_budget_id")
    _text(procedure.get("responsible_approver"), f"{pid}.responsible_approver")
    if procedure.get("approval_status") not in ("draft", "approved", "superseded"):
        raise ValueError(f"{pid}.approval_status must be draft, approved or superseded")
    if procedure.get("approval_status") == "approved":
        _text(procedure.get("approval_record_id"), f"{pid}.approval_record_id")
    return {"procedure_id": pid, "revision": procedure["revision"],
            "approval_status": procedure["approval_status"],
            "execution_authorized_by_definition": procedure["approval_status"] == "approved"}


def evaluate_result(result: dict[str, Any]) -> dict[str, Any]:
    """Apply a supplied two-sided limit with a conservative uncertainty guard band."""
    for field in ("test_id", "procedure_id", "procedure_revision", "movement_revision",
                  "test_condition_id", "source_record_id", "instrument_ids",
                  "calibration_record_ids", "uncertainty_budget_id", "requirement_id",
                  "unit"):
        _text(result.get(field), field)
    if result.get("approval_status") != "approved":
        raise ValueError("result cannot be accepted against an unapproved procedure")
    value = _num(result.get("measured_value"), "measured_value")
    lower = _num(result.get("lower_limit"), "lower_limit")
    upper = _num(result.get("upper_limit"), "upper_limit")
    if upper < lower:
        raise ValueError("upper_limit must be greater than or equal to lower_limit")
    expanded = _num(result.get("expanded_uncertainty"), "expanded_uncertainty",
                    nonnegative=True)
    low_bound, high_bound = value-expanded, value+expanded
    within = low_bound >= lower and high_bound <= upper
    outside = high_bound < lower or low_bound > upper
    status = "pass" if within else ("fail" if outside else "indeterminate")
    return {"test_id": result["test_id"], "measured_value": value, "unit": result["unit"],
            "lower_limit": lower, "upper_limit": upper,
            "expanded_uncertainty": expanded,
            "uncertainty_interval": [low_bound, high_bound],
            "guard_banded_status": status,
            "requirement_id": result["requirement_id"],
            "physical_test_evidence_reviewed": False}


def build_verification_matrix(procedures: list[dict[str, Any]],
                              results: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(procedures, list) or not procedures:
        raise ValueError("procedures must be a non-empty list")
    if not isinstance(results, list):
        raise ValueError("results must be a list")
    p = [validate_test_procedure(x) for x in procedures]
    pids = [x["procedure_id"] for x in p]
    if len(pids) != len(set(pids)):
        raise ValueError("procedure IDs must be unique")
    r = [evaluate_result(x) for x in results]
    tids = [x["test_id"] for x in r]
    if len(tids) != len(set(tids)):
        raise ValueError("test IDs must be unique")
    known = {x["procedure_id"]: x for x in p}
    for raw, checked in zip(results, r):
        if raw["procedure_id"] not in known:
            raise ValueError(f"result {checked['test_id']} references unknown procedure")
        proc = known[raw["procedure_id"]]
        if proc["revision"] != raw["procedure_revision"]:
            raise ValueError(f"result {checked['test_id']} uses a mismatched procedure revision")
        if proc["approval_status"] != "approved":
            raise ValueError(f"result {checked['test_id']} references a procedure not approved for execution")
    counts = {status: sum(x["guard_banded_status"] == status for x in r)
              for status in ("pass", "fail", "indeterminate")}
    return {"procedure_count": len(p), "result_count": len(r),
            "results": r, "status_counts": counts,
            "verification_complete": bool(r) and counts["fail"] == 0 and counts["indeterminate"] == 0,
            "engineering_release_approved": False}


def required_test_domains() -> list[dict[str, str]]:
    """Controlled coverage checklist; detailed methods and limits remain to approve."""
    return [
        {"domain":"dimensional_and_geometric_inspection","evidence":"calibrated dimensional report and CAD revision"},
        {"domain":"gear_train_kinematics_and_efficiency","evidence":"speed, torque and energy measurements at named interfaces"},
        {"domain":"mainspring_torque_angle_and_barrel_output","evidence":"loading/unloading curves and approved operating endpoints"},
        {"domain":"automatic_winding_and_bridle","evidence":"rotor input, stored-energy gain and slip-onset trials"},
        {"domain":"escapement_and_balance","evidence":"amplitude, rate, beat error, positional and reserve-state data"},
        {"domain":"chronograph_start_stop_reset","evidence":"functional cycles, hand return, engagement and measured load"},
        {"domain":"chronograph_timekeeping_interaction","evidence":"matched chrono-off/on timing and power trials"},
        {"domain":"calendar_weekday_date","evidence":"day transition, month-length rollover and safe correction tests"},
        {"domain":"power_reserve_and_duty_cycle","evidence":"full run-down with declared chrono/calendar duty profiles"},
        {"domain":"environmental_and_durability","evidence":"approved temperature, shock, wear and cycle protocols"},
        {"domain":"serviceability_and_reassembly","evidence":"documented disassembly, reassembly and post-service verification"},
    ]
