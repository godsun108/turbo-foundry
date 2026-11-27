"""Evidence-gated C-01 chronograph kinematics.

All gear geometry and source speeds are explicit inputs. No C-01 tooth counts,
source RPM, counter indexing method, or physical performance is selected here.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class GearStage:
    driver_teeth: int
    driven_teeth: int
    mesh: str = "external"

    def signed_ratio(self) -> Fraction:
        for value in (self.driver_teeth, self.driven_teeth):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError("tooth counts must be positive integers")
        if self.mesh not in {"external", "internal"}:
            raise ValueError("mesh must be 'external' or 'internal'")
        sign = -1 if self.mesh == "external" else 1
        return Fraction(sign * self.driver_teeth, self.driven_teeth)


def _fraction(value: Any, name: str, *, positive: bool = False) -> Fraction:
    try:
        result = Fraction(str(value))
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        raise ValueError(f"{name} must be a finite numeric value") from exc
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def path_ratio(stages: list[GearStage]) -> Fraction:
    if not stages:
        raise ValueError("at least one gear stage is required")
    result = Fraction(1, 1)
    for stage in stages:
        result *= stage.signed_ratio()
    return result


def evaluate_train(input_rpm: Any, stages: list[GearStage]) -> dict[str, Any]:
    source = _fraction(input_rpm, "input_rpm", positive=True)
    ratio = path_ratio(stages)
    output = source * ratio
    return {
        "input_rpm": str(source),
        "signed_speed_ratio": str(ratio),
        "output_rpm": str(output),
        "output_direction": "same" if output > 0 else "opposite",
        "stage_count": len(stages),
    }


def required_ratio(input_rpm: Any, target_period_seconds: Any) -> dict[str, Any]:
    source = _fraction(input_rpm, "input_rpm", positive=True)
    period = _fraction(target_period_seconds, "target_period_seconds", positive=True)
    target_rpm = Fraction(60, 1) / period
    ratio = target_rpm / source
    return {
        "input_rpm": str(source),
        "target_period_seconds_per_revolution": str(period),
        "target_rpm": str(target_rpm),
        "required_speed_ratio_magnitude": str(ratio),
        "note": "Magnitude only; gear topology determines rotation direction.",
    }


def compare_output_to_target(actual_rpm: Any, target_period_seconds: Any,
                             tolerance_fraction: Any = 0) -> dict[str, Any]:
    actual = _fraction(actual_rpm, "actual_rpm", positive=True)
    period = _fraction(target_period_seconds, "target_period_seconds", positive=True)
    tolerance = _fraction(tolerance_fraction, "tolerance_fraction")
    if tolerance < 0 or tolerance >= 1:
        raise ValueError("tolerance_fraction must be in [0, 1)")
    target = Fraction(60, 1) / period
    error = (actual - target) / target
    return {
        "actual_rpm": str(actual),
        "target_rpm": str(target),
        "fractional_speed_error": str(error),
        "absolute_error_fraction": str(abs(error)),
        "passes_supplied_tolerance": abs(error) <= tolerance,
        "tolerance_fraction": str(tolerance),
    }


def counter_index_spec(events_per_hour: Any, divisions_per_revolution: Any) -> dict[str, Any]:
    """Describe a jumping counter's event cadence and angular step."""
    events = _fraction(events_per_hour, "events_per_hour", positive=True)
    divisions = _fraction(divisions_per_revolution, "divisions_per_revolution", positive=True)
    if divisions.denominator != 1:
        raise ValueError("divisions_per_revolution must be a whole number")
    if events.denominator != 1:
        raise ValueError("events_per_hour must be a whole number")
    return {
        "events_per_hour": int(events),
        "event_interval_seconds": str(Fraction(3600, 1) / events),
        "divisions_per_revolution": int(divisions),
        "angular_step_degrees": str(Fraction(360, 1) / divisions),
        "continuous_rotation_assumed": False,
        "note": "Indexing cadence is an explicit design input, not selected C-01 geometry.",
    }


def counter_architecture_comparison() -> dict[str, Any]:
    return {
        "continuous": {
            "principle": "Register hand rotates continuously at the required average speed.",
            "advantages_to_test": ["smooth indication", "simple average-speed definition"],
            "risks_to_test": ["continuous drive load", "readability between graduations", "friction and backlash"],
        },
        "jumping": {
            "principle": "Register advances by a discrete angular step at each indexing event.",
            "advantages_to_test": ["stable displayed value between events", "clear elapsed-unit transition"],
            "risks_to_test": ["instantaneous indexing torque", "jumper energy", "overshoot, bounce and incomplete indexing"],
        },
        "decision": "open; requires dial convention, load measurements, packaging and reliability evidence",
    }


def target_display_speeds() -> dict[str, dict[str, str]]:
    periods = {
        "central_chronograph_seconds": 60,
        "chronograph_30_minute_register_continuous_convention": 1800,
        "chronograph_12_hour_register_continuous_convention": 43200,
    }
    return {
        name: {
            "period_seconds_per_revolution": str(period),
            "required_rpm": str(Fraction(60, period)),
        }
        for name, period in periods.items()
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate an explicitly supplied source and gear path against one target."""
    stages = [
        GearStage(**stage) for stage in data["stages"]
    ]
    result = evaluate_train(data["input_rpm"], stages)
    target = compare_output_to_target(
        abs(Fraction(result["output_rpm"])),
        data["target_period_seconds"],
        data.get("tolerance_fraction", 0),
    )
    return {
        "train": result,
        "target_comparison": target,
        "direction_note": "Direction is reported separately and must match the hand/dial convention.",
    }
