"""WP-29 integrated dynamic power and operating-envelope evaluator.

Measurement-driven reducers only. This module does not synthesize a virtual
movement, interpolate between reserve states, or predict physical dynamics.
"""
from __future__ import annotations

from math import isfinite
from typing import Any


def _num(value: Any, field: str, *, positive: bool = False,
         nonnegative: bool = False) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not isfinite(x):
        raise ValueError(f"{field} must be finite")
    if positive and x <= 0:
        raise ValueError(f"{field} must be positive")
    if nonnegative and x < 0:
        raise ValueError(f"{field} must be non-negative")
    return x


def _id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty identifier")
    return value


def _common(data: dict[str, Any]) -> tuple[str, str, str]:
    return (_id(data.get("movement_revision"), "movement_revision"),
            _id(data.get("boundary_id"), "boundary_id"),
            _id(data.get("test_condition_id"), "test_condition_id"))


def evaluate_reserve_profile(data: dict[str, Any]) -> dict[str, Any]:
    """Summarize measured reserve states; never interpolate or infer hours."""
    revision, boundary, condition = _common(data)
    samples = data.get("samples")
    if not isinstance(samples, list) or len(samples) < 2:
        raise ValueError("at least two measured reserve samples are required")
    ids, rows = [], []
    for i, s in enumerate(samples):
        sid = _id(s.get("state_id"), f"samples[{i}].state_id")
        ids.append(sid)
        fraction = _num(s.get("reserve_state_fraction"), f"{sid}.reserve_state_fraction")
        if not 0 <= fraction <= 1:
            raise ValueError(f"{sid}.reserve_state_fraction must be within [0, 1]")
        row = {"state_id": sid, "reserve_state_fraction": fraction}
        for field in ("elapsed_seconds", "barrel_torque_nm", "barrel_speed_rad_s",
                      "amplitude_deg", "rate_s_per_day", "beat_error_ms",
                      "measured_power_w"):
            if s.get(field) is not None:
                row[field] = _num(s[field], f"{sid}.{field}",
                                  nonnegative=field not in ("rate_s_per_day",))
        if s.get("source_record_id") is None:
            raise ValueError(f"{sid}.source_record_id is required")
        row["source_record_id"] = _id(s["source_record_id"], f"{sid}.source_record_id")
        rows.append(row)
    if len(ids) != len(set(ids)):
        raise ValueError("state_id values must be unique")
    if len({r["source_record_id"] for r in rows}) != len(rows):
        raise ValueError("each reserve state requires a distinct source_record_id")
    rows.sort(key=lambda r: r["reserve_state_fraction"], reverse=True)
    fractions = [r["reserve_state_fraction"] for r in rows]
    if len(set(fractions)) != len(fractions):
        raise ValueError("reserve_state_fraction values must be unique")
    return {
        "model": "steward.c01.dynamic.reserve-profile.v1",
        "movement_revision": revision, "boundary_id": boundary,
        "test_condition_id": condition, "states": rows, "state_count": len(rows),
        "measured_fraction_span": [min(fractions), max(fractions)],
        "hours_remaining_inferred": False, "interpolation_performed": False,
        "physical_performance_validated": False,
    }


def evaluate_operating_load(data: dict[str, Any]) -> dict[str, Any]:
    """Sum disjoint measured load-energy records on one common boundary/window."""
    revision, boundary, condition = _common(data)
    interval = _id(data.get("interval_id"), "interval_id")
    duration = _num(data.get("interval_seconds"), "interval_seconds", positive=True)
    loads = data.get("loads")
    if not isinstance(loads, list) or not loads:
        raise ValueError("loads must be a non-empty list")
    ids, categories, rows = [], [], []
    allowed = {"baseline", "chronograph_increment", "calendar_increment", "other_increment"}
    for i, load in enumerate(loads):
        lid = _id(load.get("load_id"), f"loads[{i}].load_id")
        category = _id(load.get("category"), f"{lid}.category")
        if category not in allowed:
            raise ValueError(f"{lid}.category is not an allowed load category")
        if load.get("boundary_id") != boundary or load.get("interval_id") != interval:
            raise ValueError(f"{lid} has mismatched boundary or interval")
        if load.get("test_condition_id") != condition:
            raise ValueError(f"{lid} has mismatched test condition")
        if load.get("incremental") is not (category != "baseline"):
            raise ValueError(f"{lid} incremental flag conflicts with category")
        if load.get("includes_other_loads", False):
            raise ValueError(f"{lid} overlaps another load and cannot be summed")
        energy = _num(load.get("energy_j"), f"{lid}.energy_j", nonnegative=True)
        rows.append({"load_id": lid, "category": category, "energy_j": energy})
        ids.append(lid); categories.append(category)
    if len(ids) != len(set(ids)):
        raise ValueError("load_id values must be unique")
    if len(categories) != len(set(categories)):
        raise ValueError("only one non-overlapping record per load category is accepted")
    if "baseline" not in categories:
        raise ValueError("a measured baseline load record is required")
    total = sum(r["energy_j"] for r in rows)
    return {
        "model": "steward.c01.dynamic.operating-load.v1",
        "movement_revision": revision, "boundary_id": boundary,
        "test_condition_id": condition, "interval_id": interval,
        "interval_seconds": duration, "loads": rows,
        "total_energy_j": total, "average_power_w": total / duration,
        "load_count": len(rows), "double_counting_screen_passed": True,
        "reserve_prediction_made": False,
    }


def evaluate_event_increment(baseline: dict[str, Any],
                             event_window: dict[str, Any]) -> dict[str, Any]:
    """Subtract matched baseline energy from a complete event-window trial."""
    for label, r in (("baseline", baseline), ("event_window", event_window)):
        for f in ("movement_revision", "boundary_id", "test_condition_id",
                  "interval_id", "source_record_id"):
            _id(r.get(f), f"{label}.{f}")
    for f in ("movement_revision", "boundary_id", "test_condition_id", "interval_id"):
        if baseline[f] != event_window[f]:
            raise ValueError(f"event and baseline must share {f}")
    if baseline["source_record_id"] == event_window["source_record_id"]:
        raise ValueError("baseline and event window require distinct source records")
    if event_window.get("event_complete") is not True:
        raise ValueError("event_window must explicitly confirm complete event capture")
    t0 = _num(baseline.get("interval_seconds"), "baseline.interval_seconds", positive=True)
    t1 = _num(event_window.get("interval_seconds"), "event_window.interval_seconds", positive=True)
    if abs(t0-t1) > max(t0,t1)*1e-9:
        raise ValueError("event and baseline durations must match")
    e0 = _num(baseline.get("energy_j"), "baseline.energy_j", nonnegative=True)
    e1 = _num(event_window.get("energy_j"), "event_window.energy_j", nonnegative=True)
    return {"movement_revision": baseline["movement_revision"],
            "boundary_id": baseline["boundary_id"], "interval_id": baseline["interval_id"],
            "interval_seconds": t0, "baseline_energy_j": e0, "event_window_energy_j": e1,
            "event_incremental_energy_j": e1-e0,
            "event_incremental_average_power_w": (e1-e0)/t0,
            "event_complete_capture_confirmed": True,
            "transient_waveform_modelled": False}


def evaluate_transition(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Report measured before/during/after values without fitting a transient."""
    if not isinstance(samples, list) or len(samples) != 3:
        raise ValueError("exactly before, during and after samples are required")
    expected = ("before", "during", "after")
    values = []
    common = None
    for label, s in zip(expected, samples):
        if s.get("phase") != label:
            raise ValueError("transition phases must be before, during, after in order")
        key = tuple(_id(s.get(f), f"{label}.{f}") for f in
                    ("movement_revision", "boundary_id", "test_condition_id"))
        if common is None: common = key
        if key != common: raise ValueError("transition samples must share revision, boundary and condition")
        values.append({k: _num(s.get(k), f"{label}.{k}")
                       for k in ("timestamp_seconds", "measured_power_w", "amplitude_deg",
                                 "rate_s_per_day")})
    if any(v["timestamp_seconds"] < 0 for v in values):
        raise ValueError("transition timestamps must be non-negative")
    if any(v["measured_power_w"] < 0 or v["amplitude_deg"] < 0 for v in values):
        raise ValueError("measured power and amplitude must be non-negative")
    if not values[0]["timestamp_seconds"] < values[1]["timestamp_seconds"] < values[2]["timestamp_seconds"]:
        raise ValueError("transition timestamps must be strictly increasing")
    return {"movement_revision": common[0], "boundary_id": common[1],
            "test_condition_id": common[2],
            "during_minus_before": {k: values[1][k]-values[0][k]
                                    for k in ("measured_power_w", "amplitude_deg", "rate_s_per_day")},
            "after_minus_before": {k: values[2][k]-values[0][k]
                                   for k in ("measured_power_w", "amplitude_deg", "rate_s_per_day")},
            "samples_are_measured": True, "transient_interpolation_performed": False}


def friction_sensitivity(input_energy_j: Any, loss_fraction: Any,
                         evidence_id: Any) -> dict[str, float | str | bool]:
    """Explicit scenario calculation; supplied loss fraction is never a default."""
    energy = _num(input_energy_j, "input_energy_j", nonnegative=True)
    loss = _num(loss_fraction, "loss_fraction", nonnegative=True)
    if loss >= 1:
        raise ValueError("loss_fraction must be less than one")
    evidence = _id(evidence_id, "evidence_id")
    return {"input_energy_j": energy, "loss_fraction": loss,
            "scenario_loss_energy_j": energy*loss,
            "scenario_downstream_energy_j": energy*(1-loss),
            "evidence_id": evidence, "is_measured_c01_result": False}


def acceptance_summary(reserve_profile: dict[str, Any],
                       operating_load: dict[str, Any]) -> dict[str, Any]:
    """Join only matching revision/boundary/condition; does not claim reserve."""
    for f in ("movement_revision", "boundary_id", "test_condition_id"):
        if reserve_profile.get(f) != operating_load.get(f):
            raise ValueError(f"reserve profile and load case must share {f}")
    return {"movement_revision": reserve_profile["movement_revision"],
            "boundary_id": reserve_profile["boundary_id"],
            "test_condition_id": reserve_profile["test_condition_id"],
            "reserve_state_count": reserve_profile["state_count"],
            "measured_load_average_power_w": operating_load["average_power_w"],
            "measurement_join_passed": True,
            "full_run_down_proven": False,
            "60_to_70_hour_target_proven": False,
            "engineering_release_approved": False}
