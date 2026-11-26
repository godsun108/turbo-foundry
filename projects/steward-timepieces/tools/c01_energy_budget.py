"""First-pass C-01 energy calculations.

All inputs are SI units. This module deliberately does not invent movement
parameters: measured torque/angle data and verified efficiency values must be
provided by the engineer. Values returned are engineering estimates, not
validated movement performance.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class TorquePoint:
    """One measured barrel torque sample: angle in radians, torque in N·m."""

    angle_rad: float
    torque_nm: float


def _finite_positive(value: float, name: str, *, allow_zero: bool = False) -> None:
    if not isfinite(value) or (value < 0 if allow_zero else value <= 0):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be finite and {qualifier}")


def integrate_usable_barrel_energy(points: Sequence[TorquePoint]) -> float:
    """Integrate usable spring energy by trapezoidal integration, in joules.

    Samples must cover only the approved usable unwind interval and be ordered
    by strictly increasing angle. Torque must be non-negative.
    """
    if len(points) < 2:
        raise ValueError("At least two torque samples are required")

    energy = 0.0
    previous = points[0]
    _finite_positive(previous.angle_rad, "angle_rad", allow_zero=True)
    _finite_positive(previous.torque_nm, "torque_nm", allow_zero=True)

    for current in points[1:]:
        _finite_positive(current.angle_rad, "angle_rad", allow_zero=True)
        _finite_positive(current.torque_nm, "torque_nm", allow_zero=True)
        delta_angle = current.angle_rad - previous.angle_rad
        if delta_angle <= 0:
            raise ValueError("Torque samples must have strictly increasing angles")
        energy += 0.5 * (previous.torque_nm + current.torque_nm) * delta_angle
        previous = current

    return energy


def average_power_w(energy_j: float, reserve_hours: float) -> float:
    """Average power corresponding to usable energy over a reserve interval."""
    _finite_positive(energy_j, "energy_j")
    _finite_positive(reserve_hours, "reserve_hours")
    return energy_j / (reserve_hours * 3600.0)


def required_energy_j(average_power_w_value: float, reserve_hours: float) -> float:
    """Energy required for a specified average power and reserve time."""
    _finite_positive(average_power_w_value, "average_power_w")
    _finite_positive(reserve_hours, "reserve_hours")
    return average_power_w_value * reserve_hours * 3600.0


def reserve_change_percent(reference_hours: float, target_hours: float) -> float:
    """Elapsed-time change relative to a reference reserve, in percent."""
    _finite_positive(reference_hours, "reference_hours")
    _finite_positive(target_hours, "target_hours")
    return (target_hours / reference_hours - 1.0) * 100.0


def series_efficiency(stage_efficiencies: Sequence[float]) -> float:
    """Combined efficiency of sequential stages, each between 0 and 1."""
    if not stage_efficiencies:
        raise ValueError("At least one stage efficiency is required")
    total = 1.0
    for efficiency in stage_efficiencies:
        if not isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
            raise ValueError("Each efficiency must be finite and in (0, 1]")
        total *= efficiency
    return total


def output_power_w(input_power_w: float, efficiency: float) -> float:
    """Power after a modeled transmission stage."""
    _finite_positive(input_power_w, "input_power_w")
    if not isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
        raise ValueError("efficiency must be finite and in (0, 1]")
    return input_power_w * efficiency
