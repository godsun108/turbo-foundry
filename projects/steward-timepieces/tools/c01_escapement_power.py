"""WP-28 measured escapement power and barrel-to-balance matching.

This is an evidence-driven comparison of measured supply, demand and
timekeeping at explicitly declared interfaces/states. It is not a dynamic
watch simulation and does not infer amplitude from torque or power.
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


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty identifier")
    return value


def evaluate_interface_power(data: dict[str, Any]) -> dict[str, Any]:
    """Compare synchronized measured supply and demand at one shaft plane.

    Each sample is a matched operating state. Torque and angular speed for
    both supply and demand must refer to the same declared interface and
    instant/state. This arithmetic comparison does not model transients.
    """
    boundary = _text(data.get("boundary_id"), "boundary_id")
    speed_tolerance = _number(data.get("speed_match_tolerance_fraction"),
                               "speed_match_tolerance_fraction", nonnegative=True)
    samples = data.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("samples must be a non-empty list")
    ids = []
    results = []
    for index, sample in enumerate(samples):
        state = _text(sample.get("state_id"), f"samples[{index}].state_id")
        ids.append(state)
        reserve = _number(sample.get("reserve_state_fraction"),
                          f"{state}.reserve_state_fraction")
        if not 0 <= reserve <= 1:
            raise ValueError(f"{state}.reserve_state_fraction must be within [0, 1]")
        supplied_torque = _number(sample.get("supplied_torque_nm"),
                                  f"{state}.supplied_torque_nm", nonnegative=True)
        supplied_speed = _number(sample.get("supplied_speed_rad_s"),
                                 f"{state}.supplied_speed_rad_s", positive=True)
        required_torque = _number(sample.get("required_torque_nm"),
                                  f"{state}.required_torque_nm", nonnegative=True)
        required_speed = _number(sample.get("required_speed_rad_s"),
                                 f"{state}.required_speed_rad_s", positive=True)
        speed_error = abs(supplied_speed - required_speed) / max(
            supplied_speed, required_speed)
        supplied_power = supplied_torque * supplied_speed
        required_power = required_torque * required_speed
        torque_margin = supplied_torque - required_torque
        power_margin = supplied_power - required_power
        speed_match = speed_error <= speed_tolerance
        results.append({
            "state_id": state,
            "reserve_state_fraction": reserve,
            "supplied_torque_nm": supplied_torque,
            "required_torque_nm": required_torque,
            "supplied_speed_rad_s": supplied_speed,
            "required_speed_rad_s": required_speed,
            "supplied_ideal_shaft_power_w": supplied_power,
            "required_ideal_shaft_power_w": required_power,
            "torque_margin_nm": torque_margin,
            "ideal_power_margin_w": power_margin,
            "relative_speed_mismatch": speed_error,
            "speed_match_passed": speed_match,
            "torque_margin_nonnegative": torque_margin >= 0,
            "power_margin_nonnegative": power_margin >= 0,
            "state_passed": speed_match and torque_margin >= 0 and power_margin >= 0,
        })
    if len(ids) != len(set(ids)):
        raise ValueError("state_id values must be unique")
    ordered = sorted(results, key=lambda item: item["reserve_state_fraction"])
    return {
        "model": "steward.c01.escapement.interface-power.v1",
        "boundary_id": boundary,
        "speed_match_tolerance_fraction": speed_tolerance,
        "states": ordered,
        "state_count": len(ordered),
        "passed": all(item["state_passed"] for item in ordered),
        "minimum_torque_margin_nm": min(item["torque_margin_nm"] for item in ordered),
        "minimum_ideal_power_margin_w": min(item["ideal_power_margin_w"] for item in ordered),
        "limitations": [
            "shaft power is ideal torque-times-speed arithmetic",
            "no transient, impulse-shape, friction or efficiency model",
            "no amplitude or rate is inferred from power margin",
        ],
    }


def evaluate_balance_energy_per_event(data: dict[str, Any]) -> dict[str, float | int | str]:
    """Reduce a measured energy total over an explicitly counted event set."""
    boundary = _text(data.get("boundary_id"), "boundary_id")
    interval = _text(data.get("interval_id"), "interval_id")
    energy = _number(data.get("measured_energy_j"), "measured_energy_j",
                     nonnegative=True)
    events = data.get("measured_event_count")
    if isinstance(events, bool) or not isinstance(events, int) or events <= 0:
        raise ValueError("measured_event_count must be a positive integer")
    duration = _number(data.get("interval_seconds"), "interval_seconds",
                        positive=True)
    return {
        "boundary_id": boundary,
        "interval_id": interval,
        "measured_energy_j": energy,
        "measured_event_count": events,
        "measured_energy_per_event_j": energy / events,
        "interval_seconds": duration,
        "average_measured_power_w": energy / duration,
    }


def evaluate_chronograph_supply_effect(stopped: dict[str, Any],
                                       running: dict[str, Any]) -> dict[str, Any]:
    """Compare paired measured balance/escapement metrics by chrono state."""
    for label, record in (("stopped", stopped), ("running", running)):
        _text(record.get("boundary_id"), f"{label}.boundary_id")
        _text(record.get("interval_id"), f"{label}.interval_id")
    if stopped["boundary_id"] != running["boundary_id"]:
        raise ValueError("chronograph trials must share a measurement boundary")
    if stopped["interval_id"] != running["interval_id"]:
        raise ValueError("chronograph trials must share an interval definition")
    duration_a = _number(stopped.get("interval_seconds"), "stopped.interval_seconds",
                         positive=True)
    duration_b = _number(running.get("interval_seconds"), "running.interval_seconds",
                         positive=True)
    if abs(duration_a - duration_b) > max(duration_a, duration_b) * 1e-9:
        raise ValueError("chronograph trials must have matched durations")
    fields = ("amplitude_deg", "rate_s_per_day", "measured_power_w")
    a = {field: _number(stopped.get(field), f"stopped.{field}") for field in fields}
    b = {field: _number(running.get(field), f"running.{field}") for field in fields}
    if a["amplitude_deg"] < 0 or b["amplitude_deg"] < 0:
        raise ValueError("amplitude must be non-negative")
    return {
        "boundary_id": stopped["boundary_id"],
        "interval_id": stopped["interval_id"],
        "interval_seconds": duration_a,
        "amplitude_change_deg": b["amplitude_deg"] - a["amplitude_deg"],
        "rate_change_s_per_day": b["rate_s_per_day"] - a["rate_s_per_day"],
        "measured_power_change_w": b["measured_power_w"] - a["measured_power_w"],
        "chronograph_state_comparison_only": True,
    }


def evaluate_reserve_state_timekeeping(data: dict[str, Any]) -> dict[str, Any]:
    """Check measured amplitude/rate across reserve states against approved limits."""
    amp_min = _number(data.get("approved_amplitude_min_deg"),
                      "approved_amplitude_min_deg", nonnegative=True)
    amp_max = _number(data.get("approved_amplitude_max_deg"),
                      "approved_amplitude_max_deg", nonnegative=True)
    rate_min = _number(data.get("approved_rate_min_s_per_day"),
                       "approved_rate_min_s_per_day")
    rate_max = _number(data.get("approved_rate_max_s_per_day"),
                       "approved_rate_max_s_per_day")
    if amp_min > amp_max or rate_min > rate_max:
        raise ValueError("approved amplitude/rate limits are inverted")
    samples = data.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("reserve-state samples must be non-empty")
    normalized = []
    seen = set()
    for index, sample in enumerate(samples):
        state = _text(sample.get("state_id"), f"samples[{index}].state_id")
        if state in seen:
            raise ValueError("reserve state identifiers must be unique")
        seen.add(state)
        fraction = _number(sample.get("reserve_state_fraction"),
                           f"{state}.reserve_state_fraction")
        amplitude = _number(sample.get("amplitude_deg"), f"{state}.amplitude_deg",
                            nonnegative=True)
        rate = _number(sample.get("rate_s_per_day"), f"{state}.rate_s_per_day")
        if not 0 <= fraction <= 1:
            raise ValueError("reserve_state_fraction must be within [0, 1]")
        passed = amp_min <= amplitude <= amp_max and rate_min <= rate <= rate_max
        normalized.append({
            "state_id": state,
            "reserve_state_fraction": fraction,
            "amplitude_deg": amplitude,
            "rate_s_per_day": rate,
            "passed": passed,
        })
    normalized.sort(key=lambda item: item["reserve_state_fraction"])
    return {
        "samples": normalized,
        "sample_count": len(normalized),
        "passed": all(item["passed"] for item in normalized),
        "amplitude_span_deg": (max(x["amplitude_deg"] for x in normalized) -
                               min(x["amplitude_deg"] for x in normalized)),
        "rate_span_s_per_day": (max(x["rate_s_per_day"] for x in normalized) -
                                min(x["rate_s_per_day"] for x in normalized)),
        "remaining_hours_inferred": False,
    }
