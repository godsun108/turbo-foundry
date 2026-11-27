"""WP-27 mainspring barrel, usable-energy and power-delivery model.

All spring torque/angle, operating-window, winding and load inputs are
explicit. Calculations are engineering bookkeeping aids, not a spring or
barrel design and not a validated reserve prediction.
"""
from __future__ import annotations

from math import isfinite
from typing import Any


def _number(value: Any, field: str, *, positive: bool = False,
            nonnegative: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not isfinite(result):
        raise ValueError(f"{field} must be finite")
    if positive and result <= 0:
        raise ValueError(f"{field} must be positive")
    if nonnegative and result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def _unique(items: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [item.get(field) for item in items]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"every {label} requires {field}")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} {field} values must be unique")
    return set(values)


def integrate_torque_angle(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Integrate a measured torque-angle curve using trapezoidal quadrature.

    Angle is radians, torque is N·m, work is joules. The caller must supply
    one monotonic loading or unloading branch, not a mixed hysteresis loop.
    """
    if not isinstance(samples, list) or len(samples) < 2:
        raise ValueError("at least two torque-angle samples are required")
    points = []
    for i, sample in enumerate(samples):
        angle = _number(sample.get("angle_rad"), f"sample {i} angle_rad")
        torque = _number(sample.get("torque_nm"), f"sample {i} torque_nm",
                         nonnegative=True)
        if points and angle <= points[-1][0]:
            raise ValueError("sample angles must be strictly increasing")
        points.append((angle, torque))
    energy = sum((points[i][1] + points[i + 1][1]) * 0.5 *
                 (points[i + 1][0] - points[i][0])
                 for i in range(len(points) - 1))
    torques = [p[1] for p in points]
    mean_torque = sum(torques) / len(torques)
    return {
        "sample_count": len(points),
        "angle_start_rad": points[0][0],
        "angle_end_rad": points[-1][0],
        "angular_span_rad": points[-1][0] - points[0][0],
        "integrated_work_j": energy,
        "minimum_sampled_torque_nm": min(torques),
        "maximum_sampled_torque_nm": max(torques),
        "mean_sampled_torque_nm": mean_torque,
        "sampled_torque_range_nm": max(torques) - min(torques),
        "sampled_torque_range_over_mean": (
            (max(torques) - min(torques)) / mean_torque
            if mean_torque > 0 else None
        ),
        "integration_method": "trapezoidal",
        "branch_semantics": "single_monotonic_branch_required",
    }


def _interpolate(points: list[tuple[float, float]], angle: float) -> float:
    if angle < points[0][0] or angle > points[-1][0]:
        raise ValueError("operating angle lies outside measured curve")
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= angle <= x1:
            if angle == x0:
                return y0
            if angle == x1:
                return y1
            fraction = (angle - x0) / (x1 - x0)
            return y0 + fraction * (y1 - y0)
    raise ValueError("operating angle could not be interpolated")


def evaluate_usable_barrel_window(data: dict[str, Any]) -> dict[str, Any]:
    """Integrate measured spring work between explicitly approved endpoints."""
    curve = data.get("torque_angle_samples")
    if not isinstance(curve, list) or len(curve) < 2:
        raise ValueError("torque_angle_samples requires at least two points")
    base = integrate_torque_angle(curve)
    points = [(float(x["angle_rad"]), float(x["torque_nm"])) for x in curve]
    start = _number(data.get("operating_start_angle_rad"), "operating_start_angle_rad")
    end = _number(data.get("operating_end_angle_rad"), "operating_end_angle_rad")
    if end <= start:
        raise ValueError("operating end angle must exceed start angle")
    if start < points[0][0] or end > points[-1][0]:
        raise ValueError("operating window must be contained in measured curve")
    # Include measured knots strictly inside the operating window.
    interior = [(x, y) for x, y in points if start < x < end]
    window = [(start, _interpolate(points, start)), *interior,
              (end, _interpolate(points, end))]
    usable = sum((window[i][1] + window[i + 1][1]) * 0.5 *
                 (window[i + 1][0] - window[i][0])
                 for i in range(len(window) - 1))
    start_torque, end_torque = window[0][1], window[-1][1]
    result = {
        "model": "steward.c01.barrel.usable-energy.v1",
        "measured_curve": base,
        "operating_start_angle_rad": start,
        "operating_end_angle_rad": end,
        "start_torque_nm": start_torque,
        "end_torque_nm": end_torque,
        "usable_spring_energy_j": usable,
        "operating_window_torque_samples": len(window),
        "energy_is_curve_integral": True,
        "physical_barrel_design_validated": False,
    }
    return result


def power_at_barrel_interface(torque_nm: Any, angular_speed_rad_s: Any) -> dict[str, float]:
    """Compute ideal instantaneous mechanical power at a declared shaft plane."""
    torque = _number(torque_nm, "torque_nm", nonnegative=True)
    speed = _number(angular_speed_rad_s, "angular_speed_rad_s", nonnegative=True)
    return {"torque_nm": torque, "angular_speed_rad_s": speed,
            "ideal_shaft_power_w": torque * speed}


def evaluate_winding_capture(data: dict[str, Any]) -> dict[str, float | bool]:
    """Compare measured rotor-side input and barrel stored-energy gain."""
    rotor_input = _number(data.get("rotor_input_energy_j"), "rotor_input_energy_j",
                          positive=True)
    barrel_gain = _number(data.get("barrel_energy_gain_j"), "barrel_energy_gain_j",
                          nonnegative=True)
    if barrel_gain > rotor_input:
        raise ValueError("barrel energy gain cannot exceed rotor-side input energy")
    revolutions = _number(data.get("rotor_revolutions"), "rotor_revolutions",
                          positive=True)
    elapsed = _number(data.get("elapsed_seconds"), "elapsed_seconds", positive=True)
    efficiency = barrel_gain / rotor_input
    return {
        "rotor_input_energy_j": rotor_input,
        "barrel_energy_gain_j": barrel_gain,
        "measured_winding_efficiency": efficiency,
        "barrel_energy_gain_per_rotor_revolution_j": barrel_gain / revolutions,
        "average_barrel_energy_gain_w": barrel_gain / elapsed,
    }


def compare_chronograph_energy(stopped: dict[str, Any],
                               running: dict[str, Any]) -> dict[str, float]:
    """Paired chronograph-state comparison over a matched interval/boundary."""
    for state, name in ((stopped, "stopped"), (running, "running")):
        for field in ("boundary_id", "interval_id"):
            if not isinstance(state.get(field), str) or not state[field].strip():
                raise ValueError(f"{name}.{field} is required")
    if stopped["boundary_id"] != running["boundary_id"]:
        raise ValueError("chronograph states must share a measurement boundary")
    if stopped["interval_id"] != running["interval_id"]:
        raise ValueError("chronograph states must share a measurement interval")
    stop_time = _number(stopped.get("interval_seconds"), "stopped.interval_seconds",
                        positive=True)
    run_time = _number(running.get("interval_seconds"), "running.interval_seconds",
                       positive=True)
    if abs(stop_time - run_time) > max(stop_time, run_time) * 1e-9:
        raise ValueError("chronograph states must use matched durations")
    stop_energy = _number(stopped.get("energy_demand_j"), "stopped.energy_demand_j",
                          nonnegative=True)
    run_energy = _number(running.get("energy_demand_j"), "running.energy_demand_j",
                         nonnegative=True)
    delta = run_energy - stop_energy
    return {
        "stopped_energy_j": stop_energy,
        "running_energy_j": run_energy,
        "interval_seconds": stop_time,
        "chronograph_incremental_energy_j": delta,
        "chronograph_incremental_average_power_w": delta / stop_time,
        "stopped_average_power_w": stop_energy / stop_time,
        "running_average_power_w": run_energy / run_time,
    }


def evaluate_energy_case(data: dict[str, Any]) -> dict[str, Any]:
    """Compare barrel usable energy with non-overlapping same-interval loads.

    Every load must be incremental and measured at a common defined boundary.
    Do not add subsystem energy values that already include another listed
    subsystem; the measurement plan must explicitly prevent double counting.
    """
    boundary = data.get("boundary_id")
    interval_id = data.get("interval_id")
    if not isinstance(boundary, str) or not boundary.strip():
        raise ValueError("boundary_id is required")
    if not isinstance(interval_id, str) or not interval_id.strip():
        raise ValueError("interval_id is required")
    duration = _number(data.get("interval_seconds"), "interval_seconds", positive=True)
    usable = _number(data.get("usable_barrel_energy_j"), "usable_barrel_energy_j",
                     positive=True)
    loads = data.get("loads")
    if not isinstance(loads, list) or not loads:
        raise ValueError("loads must be a non-empty list")
    _unique(loads, "component", "load")
    normalized = []
    for load in loads:
        if load.get("boundary_id") != boundary or load.get("interval_id") != interval_id:
            raise ValueError(f"load {load['component']} has mismatched boundary or interval")
        normalized.append({"component": load["component"],
                           "energy_j": _number(load.get("energy_j"),
                                               f"{load['component']}.energy_j",
                                               nonnegative=True)})
    total = sum(item["energy_j"] for item in normalized)
    margin = usable - total
    power = total / duration
    reserve = usable / power / 3600.0 if power > 0 else None
    target = data.get("reserve_target_hours")
    result = {
        "model": "steward.c01.barrel-energy-case.v1",
        "boundary_id": boundary,
        "interval_id": interval_id,
        "interval_seconds": duration,
        "usable_barrel_energy_j": usable,
        "loads": normalized,
        "total_load_energy_j": total,
        "energy_margin_j": margin,
        "energy_margin_fraction": margin / usable,
        "average_load_power_w": power,
        "idealized_reserve_hours_at_measured_average_load": reserve,
        "energy_budget_nonnegative": margin >= 0,
        "reserve_estimate_is_extrapolation": True,
        "reserve_target_hours": None,
        "meets_supplied_reserve_target": None,
    }
    if target is not None:
        target_value = _number(target, "reserve_target_hours", positive=True)
        result["reserve_target_hours"] = target_value
        result["meets_supplied_reserve_target"] = (
            reserve is not None and reserve >= target_value
        )
    return result
