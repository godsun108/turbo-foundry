"""WP-25 exact-ratio going-train architecture and kinematic closure.

A shaft/arbor is represented separately from gears fixed to it. Each mesh
connects two gear IDs on distinct arbors. All gears on one arbor share speed.
No tooth counts, input RPM, target tolerances or topology are defaulted.
"""
from __future__ import annotations

from fractions import Fraction
from math import isfinite
from typing import Any


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _fraction(value: Any, field: str, *, positive: bool = False,
              nonnegative: bool = False) -> Fraction:
    try:
        result = Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"{field} must be a rational numeric value") from exc
    if positive and result <= 0:
        raise ValueError(f"{field} must be positive")
    if nonnegative and result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def target_speed_rpm(period_seconds: Any) -> Fraction:
    period = _positive_int(period_seconds, "period_seconds")
    return Fraction(60, period)


def _unique(items: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [item.get(field) for item in items]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"every {label} requires a non-empty {field}")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} {field} values must be unique")
    return set(values)


def validate_train(data: dict[str, Any]) -> dict[str, Any]:
    arbors, gears, meshes = (data.get("arbors"), data.get("gears"),
                             data.get("meshes"))
    if not all(isinstance(x, list) for x in (arbors, gears, meshes)):
        raise ValueError("arbors, gears and meshes must be lists")
    if not arbors or not gears:
        raise ValueError("at least one arbor and one gear are required")
    arbor_ids = _unique(arbors, "id", "arbor")
    gear_ids = _unique(gears, "id", "gear")
    mesh_ids = _unique(meshes, "id", "mesh") if meshes else set()
    gear_by_id = {item["id"]: item for item in gears}
    for arbor in arbors:
        for field in ("role", "evidence", "source_revision"):
            if not arbor.get(field):
                raise ValueError(f"arbor {arbor['id']} requires {field}")
    for gear in gears:
        for field in ("arbor_id", "role", "evidence", "source_revision"):
            if not gear.get(field):
                raise ValueError(f"gear {gear['id']} requires {field}")
        if gear["arbor_id"] not in arbor_ids:
            raise ValueError(f"gear {gear['id']} references unknown arbor")
        _positive_int(gear.get("teeth"), f"gear {gear['id']} teeth")
    adjacency: dict[str, list[dict[str, Any]]] = {key: [] for key in arbor_ids}
    for mesh in meshes:
        for field in ("driver_gear_id", "driven_gear_id", "mesh_type",
                      "evidence", "source_revision"):
            if not mesh.get(field):
                raise ValueError(f"mesh {mesh['id']} requires {field}")
        if mesh["driver_gear_id"] not in gear_ids or mesh["driven_gear_id"] not in gear_ids:
            raise ValueError(f"mesh {mesh['id']} references unknown gear")
        if mesh["mesh_type"] not in {"external", "internal"}:
            raise ValueError(f"mesh {mesh['id']} has invalid mesh_type")
        driver, driven = gear_by_id[mesh["driver_gear_id"]], gear_by_id[mesh["driven_gear_id"]]
        if driver["arbor_id"] == driven["arbor_id"]:
            raise ValueError(f"mesh {mesh['id']} cannot connect gears on the same arbor")
        adjacency[driver["arbor_id"]].append({
            "mesh_id": mesh["id"],
            "to_arbor_id": driven["arbor_id"],
            "driver_gear_id": driver["id"],
            "driven_gear_id": driven["id"],
            "driver_teeth": driver["teeth"],
            "driven_teeth": driven["teeth"],
            "mesh_type": mesh["mesh_type"],
        })
    return {
        "arbor_ids": arbor_ids,
        "gear_ids": gear_ids,
        "mesh_ids": mesh_ids,
        "adjacency": adjacency,
        "gear_by_id": gear_by_id,
        "arbor_count": len(arbor_ids),
        "gear_count": len(gear_ids),
        "mesh_count": len(mesh_ids),
    }


def _paths(adjacency: dict[str, list[dict[str, Any]]],
           source: str, target: str, max_paths: int = 2) -> list[list[dict[str, Any]]]:
    found: list[list[dict[str, Any]]] = []
    def walk(node: str, visited: set[str], path: list[dict[str, Any]]) -> None:
        if len(found) >= max_paths:
            return
        if node == target:
            found.append(path[:])
            return
        for edge in adjacency.get(node, []):
            nxt = edge["to_arbor_id"]
            if nxt not in visited:
                walk(nxt, visited | {nxt}, path + [edge])
    walk(source, {source}, [])
    return found


def evaluate_path(data: dict[str, Any], source_arbor_id: str,
                  target_arbor_id: str, input_rpm: Any) -> dict[str, Any]:
    validated = validate_train(data)
    if source_arbor_id not in validated["arbor_ids"] or target_arbor_id not in validated["arbor_ids"]:
        raise ValueError("source and target arbor IDs must exist")
    if source_arbor_id == target_arbor_id:
        raise ValueError("source and target arbors must differ")
    rpm = _fraction(input_rpm, "input_rpm")
    paths = _paths(validated["adjacency"], source_arbor_id, target_arbor_id)
    if not paths:
        return {"status": "no_path", "source_arbor_id": source_arbor_id,
                "target_arbor_id": target_arbor_id, "candidate_only": True}
    if len(paths) > 1:
        return {"status": "multiple_paths", "path_count_at_least": len(paths),
                "source_arbor_id": source_arbor_id,
                "target_arbor_id": target_arbor_id, "candidate_only": True}
    path = paths[0]
    ratio = Fraction(1, 1)
    stages = []
    for edge in path:
        magnitude = Fraction(edge["driver_teeth"], edge["driven_teeth"])
        signed = magnitude if edge["mesh_type"] == "internal" else -magnitude
        ratio *= signed
        stages.append({
            "mesh_id": edge["mesh_id"],
            "driver_gear_id": edge["driver_gear_id"],
            "driven_gear_id": edge["driven_gear_id"],
            "driver_teeth": edge["driver_teeth"],
            "driven_teeth": edge["driven_teeth"],
            "mesh_type": edge["mesh_type"],
            "signed_stage_ratio": str(signed),
        })
    output = rpm * ratio
    return {
        "status": "unique_path",
        "source_arbor_id": source_arbor_id,
        "target_arbor_id": target_arbor_id,
        "input_rpm": str(rpm),
        "signed_compound_speed_ratio": str(ratio),
        "output_rpm": str(output),
        "output_speed_magnitude_rpm": str(abs(output)),
        "output_direction": "same" if output >= 0 else "opposite",
        "mesh_count": len(stages),
        "stages": stages,
        "candidate_only": True,
    }


def evaluate_outputs(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate declared outputs from one explicitly supplied source arbor."""
    source = data.get("input")
    outputs = data.get("outputs")
    if not isinstance(source, dict) or not source.get("arbor_id") or "rpm" not in source:
        raise ValueError("input requires arbor_id and explicit rpm")
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("at least one output target is required")
    _unique(outputs, "id", "output")
    results = []
    for output in outputs:
        if not output.get("arbor_id") or "period_seconds" not in output:
            raise ValueError(f"output {output['id']} requires arbor_id and period_seconds")
        target = target_speed_rpm(output["period_seconds"])
        path = evaluate_path(data, source["arbor_id"], output["arbor_id"], source["rpm"])
        item = {"id": output["id"], "target_period_seconds": output["period_seconds"],
                "target_speed_rpm": str(target), "path_evaluation": path}
        if path["status"] == "unique_path":
            actual = abs(Fraction(path["output_rpm"]))
            error = abs(actual - target) / target
            item["fractional_absolute_speed_error"] = str(error)
            if output.get("max_fractional_error") is not None:
                tolerance = _fraction(output["max_fractional_error"],
                                      f"{output['id']} max_fractional_error",
                                      nonnegative=True)
                item["passes_supplied_speed_tolerance"] = error <= tolerance
            else:
                item["passes_supplied_speed_tolerance"] = None
        else:
            item["fractional_absolute_speed_error"] = None
            item["passes_supplied_speed_tolerance"] = None
        results.append(item)
    return {
        "schema": "steward.c01.going-train-kinematics.v1",
        "candidate_id": data.get("candidate_id", "unnamed_candidate"),
        "train_validation": {k: v for k, v in validate_train(data).items()
                             if k not in {"adjacency", "gear_by_id"}},
        "input": {"arbor_id": source["arbor_id"],
                  "rpm": str(_fraction(source["rpm"], "input rpm"))},
        "outputs": results,
        "no_physical_train_selected": True,
        "limitations": [
            "Exact ideal kinematics only; no torque, efficiency, tooth strength or friction analysis.",
            "No gear center distance, profile, backlash, interference or manufacturability proof.",
            "No barrel speed curve or escapement wheel speed inferred from balance frequency.",
            "Balance oscillator is not modeled as a downstream gear-train arbor.",
        ],
    }


def compare_escapement_frequency(balance_hz: Any, beats_per_balance_cycle: Any,
                                  escape_wheel_teeth: Any,
                                  lock_events_per_escape_revolution: Any) -> dict[str, Any]:
    """Conditional escapement rate relationship; requires explicit geometry semantics.

    This helper does not assume the common convention for impulses/locks.
    """
    hz = _fraction(balance_hz, "balance_hz", positive=True)
    beats = _positive_int(beats_per_balance_cycle, "beats_per_balance_cycle")
    teeth = _positive_int(escape_wheel_teeth, "escape_wheel_teeth")
    events = _positive_int(lock_events_per_escape_revolution,
                           "lock_events_per_escape_revolution")
    balance_events_per_second = hz * beats
    escape_revolutions_per_second = balance_events_per_second / events
    escape_rpm = escape_revolutions_per_second * 60
    return {
        "balance_frequency_hz": str(hz),
        "beats_per_balance_cycle": beats,
        "balance_events_per_second": str(balance_events_per_second),
        "escape_wheel_teeth": teeth,
        "lock_events_per_escape_revolution": events,
        "conditional_escape_wheel_speed_rpm": str(escape_rpm),
        "status": "conditional_on_explicit_event_definition",
        "candidate_only": True,
        "note": "Tooth count is recorded but does not alone define lock events per revolution.",
    }
