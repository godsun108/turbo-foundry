"""WP-63 evidence-gated chronograph power-train and counter design calculations.

Exact ideal kinematics only. All source speeds, gear counts, event cadences,
torques, power measurements, boundaries and evidence are explicit inputs.
No C-01 train, counter convention or physical architecture is selected.
"""
from __future__ import annotations
from fractions import Fraction
from math import isfinite, pi
from typing import Any

def _q(value: Any, name: str, positive: bool = False, nonnegative: bool = False) -> Fraction:
    try:
        result = Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be a finite rational value") from exc
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and result < 0:
        raise ValueError(f"{name} must be non-negative")
    return result

def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value

def target_rpm(period_seconds: Any) -> Fraction:
    return Fraction(60, 1) / _q(period_seconds, "period_seconds", positive=True)

def evaluate_path(source_rpm: Any, stages: list[dict[str, Any]]) -> dict[str, Any]:
    source = _q(source_rpm, "source_rpm", positive=True)
    if not isinstance(stages, list) or not stages:
        raise ValueError("stages must be a non-empty explicit list")
    ratio = Fraction(1, 1)
    for index, stage in enumerate(stages):
        for field in ("driver_teeth", "driven_teeth", "mesh_type", "evidence_id", "source_revision"):
            if stage.get(field) in (None, ""):
                raise ValueError(f"stage {index} requires {field}")
        driver = _positive_int(stage["driver_teeth"], "driver_teeth")
        driven = _positive_int(stage["driven_teeth"], "driven_teeth")
        if stage["mesh_type"] not in {"external", "internal"}:
            raise ValueError("mesh_type must be external or internal")
        ratio *= Fraction(driver, driven) * (-1 if stage["mesh_type"] == "external" else 1)
    output = source * ratio
    return {"source_rpm": str(source), "signed_ratio": str(ratio),
            "output_rpm": str(output), "speed_magnitude_rpm": str(abs(output)),
            "direction": "same" if output > 0 else "opposite",
            "mesh_count": len(stages), "candidate_only": True}

def evaluate_continuous_branch(source_rpm: Any, stages: list[dict[str, Any]],
                               target_period_seconds: Any,
                               max_fractional_error: Any | None = None) -> dict[str, Any]:
    path = evaluate_path(source_rpm, stages)
    target = target_rpm(target_period_seconds)
    actual = abs(Fraction(path["output_rpm"]))
    error = abs(actual - target) / target
    tolerance = None if max_fractional_error is None else _q(
        max_fractional_error, "max_fractional_error", nonnegative=True)
    if tolerance is not None and tolerance >= 1:
        raise ValueError("max_fractional_error must be less than one")
    return {**path, "target_period_seconds_per_revolution": str(_q(
                target_period_seconds, "target_period_seconds", positive=True)),
            "target_rpm": str(target), "absolute_fractional_speed_error": str(error),
            "max_fractional_error": None if tolerance is None else str(tolerance),
            "passes_supplied_tolerance": None if tolerance is None else error <= tolerance}

def jumping_counter_spec(events_per_hour: Any, divisions_per_revolution: Any) -> dict[str, Any]:
    events = _positive_int(events_per_hour, "events_per_hour")
    divisions = _positive_int(divisions_per_revolution, "divisions_per_revolution")
    return {"events_per_hour": events,
            "event_interval_seconds": str(Fraction(3600, events)),
            "divisions_per_revolution": divisions,
            "angular_step_degrees": str(Fraction(360, divisions)),
            "average_event_rate_per_second": str(Fraction(events, 3600)),
            "instantaneous_indexing_torque": "not calculated; requires measured/dynamic input",
            "jumper_energy": "not calculated; requires measured/dynamic input",
            "overshoot_bounce_and_phase": "requires physical verification",
            "candidate_only": True}

def compare_counter_modes(continuous_period_seconds: Any,
                          jumping_events_per_hour: Any | None = None,
                          jumping_divisions_per_revolution: Any | None = None) -> dict[str, Any]:
    period = _q(continuous_period_seconds, "continuous_period_seconds", positive=True)
    result = {"continuous_candidate": {"period_seconds_per_revolution": str(period),
                                       "average_rpm": str(Fraction(60, 1) / period)},
              "jumping_candidate": None,
              "selection": "open"}
    if jumping_events_per_hour is not None or jumping_divisions_per_revolution is not None:
        if jumping_events_per_hour is None or jumping_divisions_per_revolution is None:
            raise ValueError("both jumping cadence and divisions are required")
        result["jumping_candidate"] = jumping_counter_spec(
            jumping_events_per_hour, jumping_divisions_per_revolution)
    return result

def measured_shaft_power(torque_nm: Any, speed_rpm: Any,
                         evidence_id: str, source_revision: str) -> dict[str, Any]:
    torque = _q(torque_nm, "torque_nm", nonnegative=True)
    speed = _q(speed_rpm, "speed_rpm", nonnegative=True)
    if not evidence_id or not source_revision:
        raise ValueError("evidence_id and source_revision are required")
    power_w = float(torque) * float(speed) * 2.0 * pi / 60.0
    return {"torque_nm": str(torque), "speed_rpm": str(speed),
            "shaft_power_w": power_w, "evidence_id": evidence_id,
            "source_revision": source_revision,
            "status": "calculated_from_explicit_measured_or_approved_inputs"}

def aggregate_measured_loads(loads: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(loads, list) or not loads:
        raise ValueError("loads must be a non-empty list")
    ids = [x.get("load_id") for x in loads]
    if any(not isinstance(x, str) or not x.strip() for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("load IDs must be non-empty and unique; duplicate counting is prohibited")
    boundaries = {x.get("measurement_boundary") for x in loads}
    intervals = {x.get("interval_id") for x in loads}
    revisions = {x.get("source_revision") for x in loads}
    if len(boundaries) != 1 or None in boundaries or len(intervals) != 1 or None in intervals:
        raise ValueError("loads must share one explicit measurement boundary and interval")
    if len(revisions) != 1 or None in revisions:
        raise ValueError("loads must share one source revision")
    powers = [_q(x.get("power_w"), f"{x['load_id']} power", nonnegative=True) for x in loads]
    if any(not x.get("evidence_id") for x in loads):
        raise ValueError("each load requires evidence_id")
    total = sum(powers, Fraction(0, 1))
    return {"load_ids": ids, "total_power_w": str(total),
            "measurement_boundary": next(iter(boundaries)),
            "interval_id": next(iter(intervals)),
            "source_revision": next(iter(revisions)),
            "aggregation_is_valid": True}

def validate_operating_sequence(events: list[dict[str, Any]]) -> dict[str, Any]:
    allowed = {
        ("stopped_zero", "start"): "running",
        ("running", "stop"): "stopped_retained",
        ("stopped_retained", "resume"): "running",
        ("stopped_retained", "reset"): "stopped_zero",
    }
    if not isinstance(events, list) or not events:
        raise ValueError("events must be a non-empty sequence")
    state = "stopped_zero"
    trace = [state]
    for index, event in enumerate(events):
        command = event.get("command")
        if command == "reset" and state == "running":
            if event.get("physical_interlock_test_id") in (None, ""):
                raise ValueError("running reset attempt requires a physical interlock test reference")
            if event.get("result_state") != "running":
                raise ValueError("running reset attempt must leave the chronograph running")
            trace.append("running")
            continue
        key = (state, command)
        if key not in allowed:
            raise ValueError(f"invalid command {command!r} from state {state!r} at event {index}")
        state = allowed[key]
        if event.get("result_state") != state:
            raise ValueError(f"event {index} result_state must be {state}")
        trace.append(state)
    return {"state_trace": trace, "final_state": state,
            "physical_interlock_proven_by_software": False,
            "candidate_only": True}

def analyze(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate an explicit central-seconds path and declared counter branches."""
    source = data.get("source")
    if not isinstance(source, dict) or "rpm" not in source or not source.get("arbor_id"):
        raise ValueError("source requires arbor_id and explicit rpm")
    central = data.get("central_seconds")
    if not isinstance(central, dict) or not isinstance(central.get("stages"), list):
        raise ValueError("central_seconds requires explicit stages")
    central_result = evaluate_continuous_branch(
        source["rpm"], central["stages"], 60, central.get("max_fractional_error"))
    branches = data.get("counter_branches", [])
    if not isinstance(branches, list):
        raise ValueError("counter_branches must be a list")
    branch_results = []
    for branch in branches:
        if not branch.get("id") or branch.get("mode") not in {"continuous", "jumping"}:
            raise ValueError("each counter branch requires id and continuous/jumping mode")
        period = _q(branch.get("period_seconds_per_revolution"),
                    f"{branch['id']} period", positive=True)
        if branch["mode"] == "continuous":
            if not isinstance(branch.get("stages"), list):
                raise ValueError(f"{branch['id']} requires explicit stages")
            result = evaluate_continuous_branch(
                central_result["speed_magnitude_rpm"], branch["stages"],
                period, branch.get("max_fractional_error"))
        else:
            result = {"average_target_rpm": str(Fraction(60, 1) / period),
                      "indexing": jumping_counter_spec(
                          branch.get("events_per_hour"),
                          branch.get("divisions_per_revolution"))}
        branch_results.append({"id": branch["id"], "mode": branch["mode"],
                               "result": result})
    return {"schema": "steward.c01.wp63.power-train.v1",
            "source_arbor_id": source["arbor_id"],
            "central_seconds": central_result,
            "counter_branches": branch_results,
            "source_arbor_selected": False,
            "counter_modes_selected": False,
            "physical_train_selected": False,
            "limitations": [
                "Ideal kinematics do not establish torque capacity, efficiency, friction or durability.",
                "A jumping counter requires transient impulse, jumper, anti-bounce and phase analysis.",
                "No gear geometry, contact, tolerance, physical fit or manufacturability is certified.",
                "No energy reserve or rate-performance conclusion is produced.",
            ]}
