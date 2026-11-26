"""Input-driven STEWARD C-01 automatic-winding measurement model.

Calculates measured winding efficiency from rotor-side input energy and
mainspring/barrel stored-energy gain. It does not simulate rotor dynamics,
invent winding ratios, or select a reversing architecture.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class WindingTrial:
    rotor_input_energy_j: float
    barrel_energy_gain_j: float
    rotor_revolutions: float
    elapsed_hours: float


def _finite_positive(value: float, name: str, *, zero_ok: bool = False) -> None:
    if not isfinite(value) or (value < 0 if zero_ok else value <= 0):
        qualifier = "non-negative" if zero_ok else "positive"
        raise ValueError(f"{name} must be finite and {qualifier}")


def evaluate_trial(data: dict[str, Any]) -> dict[str, float | str]:
    """Evaluate one instrumented trial using measured energies.

    Input energy must be measured at the defined rotor/winding input plane.
    Barrel energy gain must be measured or integrated over the same trial
    interval and include the actual bridle/slipping behavior.
    """
    trial = WindingTrial(
        rotor_input_energy_j=float(data["rotor_input_energy_j"]),
        barrel_energy_gain_j=float(data["barrel_energy_gain_j"]),
        rotor_revolutions=float(data["rotor_revolutions"]),
        elapsed_hours=float(data["elapsed_hours"]),
    )
    _finite_positive(trial.rotor_input_energy_j, "rotor_input_energy_j")
    _finite_positive(trial.barrel_energy_gain_j, "barrel_energy_gain_j", zero_ok=True)
    _finite_positive(trial.rotor_revolutions, "rotor_revolutions")
    _finite_positive(trial.elapsed_hours, "elapsed_hours")
    if trial.barrel_energy_gain_j > trial.rotor_input_energy_j:
        raise ValueError("barrel energy gain cannot exceed measured input energy")

    efficiency = trial.barrel_energy_gain_j / trial.rotor_input_energy_j
    return {
        "model": "steward.c01.automatic-winding.v1",
        "measured_winding_efficiency": efficiency,
        "input_energy_j": trial.rotor_input_energy_j,
        "barrel_energy_gain_j": trial.barrel_energy_gain_j,
        "rotor_revolutions": trial.rotor_revolutions,
        "barrel_energy_gain_per_rotor_revolution_j": (
            trial.barrel_energy_gain_j / trial.rotor_revolutions
        ),
        "elapsed_hours": trial.elapsed_hours,
        "average_barrel_energy_gain_w": (
            trial.barrel_energy_gain_j / (trial.elapsed_hours * 3600.0)
        ),
    }


def compare_trials(trials: list[dict[str, Any]]) -> dict[str, float | int]:
    """Aggregate multiple trials without hiding trial-to-trial variation."""
    if not trials:
        raise ValueError("At least one measured trial is required")
    results = [evaluate_trial(trial) for trial in trials]
    efficiencies = [float(result["measured_winding_efficiency"]) for result in results]
    total_input = sum(float(result["input_energy_j"]) for result in results)
    total_gain = sum(float(result["barrel_energy_gain_j"]) for result in results)
    return {
        "trial_count": len(results),
        "aggregate_efficiency": total_gain / total_input,
        "minimum_trial_efficiency": min(efficiencies),
        "maximum_trial_efficiency": max(efficiencies),
    }


def evaluate_slipping_bridle(data: dict[str, Any]) -> dict[str, float | bool]:
    """Check measured slip onset against an externally defined safe limit.

    The limit must come from the selected spring/barrel design and supplier or
    prototype evidence. This function is a comparison, not a bridle design.
    """
    slip_torque = float(data["measured_slip_onset_torque_nm"])
    safe_limit = float(data["approved_maximum_barrel_torque_nm"])
    _finite_positive(slip_torque, "measured_slip_onset_torque_nm")
    _finite_positive(safe_limit, "approved_maximum_barrel_torque_nm")
    return {
        "measured_slip_onset_torque_nm": slip_torque,
        "approved_maximum_barrel_torque_nm": safe_limit,
        "within_approved_limit": slip_torque <= safe_limit,
    }
