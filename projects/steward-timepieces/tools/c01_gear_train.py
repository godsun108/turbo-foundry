"""Measurement-driven STEWARD C-01 gear-train and energy-budget tools.

Calculations are conditional on supplied geometry and measured data. This
module does not select tooth counts, modules, efficiencies, torque limits,
lubricants, or reserve performance.
"""
from __future__ import annotations

from math import isfinite
from typing import Any


def _num(value: Any, name: str, *, positive: bool = False, nonnegative: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and result < 0:
        raise ValueError(f"{name} must be non-negative")
    return result


def gear_pair_ratio(driver_teeth: int, driven_teeth: int) -> dict[str, float | int]:
    """Return ideal external gear-pair speed ratio and direction relationship."""
    if isinstance(driver_teeth, bool) or isinstance(driven_teeth, bool):
        raise ValueError("tooth counts must be integers")
    if not isinstance(driver_teeth, int) or not isinstance(driven_teeth, int):
        raise ValueError("tooth counts must be integers")
    if driver_teeth <= 0 or driven_teeth <= 0:
        raise ValueError("tooth counts must be positive")
    return {
        "driver_teeth": driver_teeth,
        "driven_teeth": driven_teeth,
        "driven_speed_per_driver_speed": driver_teeth / driven_teeth,
        "ideal_torque_multiplier": driven_teeth / driver_teeth,
        "external_mesh_direction_reversed": 1,
    }


def compound_train_ratio(stages: list[dict[str, Any]]) -> dict[str, float | int]:
    """Multiply ideal stage ratios. Each stage needs driver_teeth/driven_teeth."""
    if not stages:
        raise ValueError("at least one gear stage is required")
    speed_ratio = 1.0
    for index, stage in enumerate(stages):
        try:
            pair = gear_pair_ratio(stage["driver_teeth"], stage["driven_teeth"])
        except KeyError as exc:
            raise ValueError(f"stage {index} missing {exc.args[0]}") from exc
        speed_ratio *= float(pair["driven_speed_per_driver_speed"])
    return {
        "stage_count": len(stages),
        "output_speed_per_input_speed": speed_ratio,
        "ideal_torque_multiplier": 1.0 / speed_ratio,
    }


def wheel_speed_rpm(input_speed_rpm: float, train_speed_ratio: float) -> float:
    speed = _num(input_speed_rpm, "input_speed_rpm", nonnegative=True)
    ratio = _num(train_speed_ratio, "train_speed_ratio", positive=True)
    return speed * ratio


def integrate_torque_angle_energy(samples: list[dict[str, Any]]) -> dict[str, float | int]:
    """Trapezoidal integration of measured torque against angle in radians.

    Samples must be ordered by monotonically increasing angle and describe
    one consistent loading/unloading path. No extrapolation is performed.
    """
    if len(samples) < 2:
        raise ValueError("at least two torque-angle samples are required")
    points = []
    for index, sample in enumerate(samples):
        if "angle_rad" not in sample or "torque_nm" not in sample:
            raise ValueError(f"sample {index} requires angle_rad and torque_nm")
        angle = _num(sample["angle_rad"], f"sample {index} angle_rad")
        torque = _num(sample["torque_nm"], f"sample {index} torque_nm")
        if torque < 0:
            raise ValueError("torque_nm must be non-negative for this stored-energy integral")
        if points and angle <= points[-1][0]:
            raise ValueError("angle_rad samples must be strictly increasing")
        points.append((angle, torque))
    energy = sum(
        (points[i][1] + points[i + 1][1]) * 0.5 *
        (points[i + 1][0] - points[i][0])
        for i in range(len(points) - 1)
    )
    return {
        "sample_count": len(points),
        "angular_travel_rad": points[-1][0] - points[0][0],
        "integrated_work_j": energy,
    }


def evaluate_energy_transfer(data: dict[str, Any]) -> dict[str, float | bool]:
    """Compare measured input/output energy across a defined transmission boundary."""
    input_j = _num(data["input_energy_j"], "input_energy_j", positive=True)
    output_j = _num(data["output_energy_j"], "output_energy_j", nonnegative=True)
    if output_j > input_j:
        raise ValueError("output energy cannot exceed input energy at a passive boundary")
    efficiency = output_j / input_j
    limit = data.get("approved_minimum_efficiency")
    result: dict[str, float | bool] = {
        "input_energy_j": input_j,
        "output_energy_j": output_j,
        "measured_efficiency": efficiency,
        "measured_loss_j": input_j - output_j,
    }
    if limit is not None:
        minimum = _num(limit, "approved_minimum_efficiency", nonnegative=True)
        if minimum > 1.0:
            raise ValueError("approved_minimum_efficiency cannot exceed 1")
        result["approved_minimum_efficiency"] = minimum
        result["passes_efficiency_limit"] = efficiency >= minimum
    return result


def evaluate_energy_budget(data: dict[str, Any]) -> dict[str, float | bool]:
    """Compare available barrel energy with explicitly measured/estimated loads.

    Each load is energy_j over the same defined operating interval. Required
    fields: usable_barrel_energy_j, going_train_loss_j, escapement_demand_j,
    chronograph_incremental_demand_j, calendar_incremental_demand_j,
    other_incremental_demand_j, interval_seconds.
    """
    keys = (
        "going_train_loss_j", "escapement_demand_j",
        "chronograph_incremental_demand_j", "calendar_incremental_demand_j",
        "other_incremental_demand_j",
    )
    usable = _num(data["usable_barrel_energy_j"], "usable_barrel_energy_j", positive=True)
    interval = _num(data["interval_seconds"], "interval_seconds", positive=True)
    loads = {key: _num(data[key], key, nonnegative=True) for key in keys}
    total = sum(loads.values())
    margin = usable - total
    return {
        "usable_barrel_energy_j": usable,
        **loads,
        "total_required_energy_j": total,
        "energy_margin_j": margin,
        "energy_margin_fraction": margin / usable,
        "interval_seconds": interval,
        "average_required_power_w": total / interval,
        "average_available_power_w": usable / interval,
        "energy_budget_nonnegative": margin >= 0,
    }


def reserve_from_energy_and_power(usable_energy_j: float, average_power_w: float) -> float:
    """Idealized reserve estimate; only as credible as both supplied inputs."""
    energy = _num(usable_energy_j, "usable_energy_j", positive=True)
    power = _num(average_power_w, "average_power_w", positive=True)
    return energy / power / 3600.0


def compare_chronograph_states(
    stopped: dict[str, Any], running: dict[str, Any]
) -> dict[str, float]:
    """Compare paired energy-demand measurements over identical intervals."""
    stop_energy = _num(stopped["energy_demand_j"], "stopped.energy_demand_j", nonnegative=True)
    run_energy = _num(running["energy_demand_j"], "running.energy_demand_j", nonnegative=True)
    stop_time = _num(stopped["interval_seconds"], "stopped.interval_seconds", positive=True)
    run_time = _num(running["interval_seconds"], "running.interval_seconds", positive=True)
    if abs(stop_time - run_time) > max(stop_time, run_time) * 1e-9:
        raise ValueError("chronograph states must use matched measurement intervals")
    return {
        "chronograph_incremental_energy_j": run_energy - stop_energy,
        "chronograph_incremental_average_power_w": (run_energy - stop_energy) / stop_time,
        "stopped_average_power_w": stop_energy / stop_time,
        "running_average_power_w": run_energy / run_time,
    }
