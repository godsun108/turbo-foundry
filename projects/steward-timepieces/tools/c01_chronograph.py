"""Measurement-driven STEWARD C-01 chronograph logic and load tools.

This module models control-state sequencing and ideal display ratios. It does
not simulate physical clutch dynamics, tooth geometry, hand inertia, or wear.
All energy inputs must be measured over matched boundaries and intervals.
"""
from __future__ import annotations

from math import isfinite
from typing import Any

STOPPED = "stopped"
RUNNING = "running"
VALID_STATES = {STOPPED, RUNNING}


def _finite(value: Any, name: str, *, positive: bool = False,
            nonnegative: bool = False) -> float:
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


def transition(state: str, command: str) -> dict[str, str]:
    """Apply a valid user command; reset is allowed only while stopped."""
    if state not in VALID_STATES:
        raise ValueError("state must be 'stopped' or 'running'")
    if command == "start" and state == STOPPED:
        return {"state": RUNNING, "action": "engage"}
    if command == "stop" and state == RUNNING:
        return {"state": STOPPED, "action": "disengage"}
    if command == "reset" and state == STOPPED:
        return {"state": STOPPED, "action": "hammer_release"}
    raise ValueError(f"invalid command {command!r} for state {state!r}")


def validate_command_sequence(commands: list[str]) -> list[dict[str, str]]:
    """Validate a sequence from stopped; return each resulting transition."""
    state = STOPPED
    results = []
    for command in commands:
        result = transition(state, command)
        results.append({"command": command, **result})
        state = result["state"]
    return results


def display_speed_ratio(driver_teeth: int, driven_teeth: int) -> float:
    """Ideal driven revs per driver rev for a simple external gear pair."""
    if (isinstance(driver_teeth, bool) or isinstance(driven_teeth, bool)
            or not isinstance(driver_teeth, int)
            or not isinstance(driven_teeth, int)):
        raise ValueError("tooth counts must be integers")
    if driver_teeth <= 0 or driven_teeth <= 0:
        raise ValueError("tooth counts must be positive")
    return driver_teeth / driven_teeth


def display_revolutions(input_revolutions: float, stages: list[dict[str, Any]]) -> float:
    """Calculate ideal output revolutions through supplied gear stages."""
    revolutions = _finite(input_revolutions, "input_revolutions", nonnegative=True)
    if not stages:
        raise ValueError("at least one stage is required")
    for index, stage in enumerate(stages):
        try:
            ratio = display_speed_ratio(stage["driver_teeth"], stage["driven_teeth"])
        except KeyError as exc:
            raise ValueError(f"stage {index} missing {exc.args[0]}") from exc
        revolutions *= ratio
    return revolutions


def energy_comparison(stopped_energy_j: float, running_energy_j: float,
                      stopped_interval_s: float, running_interval_s: float,
                      minimum_efficiency: float | None = None) -> dict[str, float | bool]:
    """Compare measured chrono-off/on energy over equal-duration intervals.

    Energy values must represent the same measurement boundary and test setup.
    The incremental demand may be negative; that is reported, not concealed.
    """
    off_e = _finite(stopped_energy_j, "stopped_energy_j", nonnegative=True)
    on_e = _finite(running_energy_j, "running_energy_j", nonnegative=True)
    off_t = _finite(stopped_interval_s, "stopped_interval_s", positive=True)
    on_t = _finite(running_interval_s, "running_interval_s", positive=True)
    if abs(off_t - on_t) > max(off_t, on_t) * 1e-9:
        raise ValueError("measurement intervals must match")
    delta = on_e - off_e
    result: dict[str, float | bool] = {
        "stopped_average_power_w": off_e / off_t,
        "running_average_power_w": on_e / on_t,
        "incremental_energy_j": delta,
        "incremental_average_power_w": delta / off_t,
    }
    if minimum_efficiency is not None:
        limit = _finite(minimum_efficiency, "minimum_efficiency",
                        nonnegative=True)
        if limit > 1:
            raise ValueError("minimum_efficiency cannot exceed 1")
        # A load comparison is not an efficiency measurement. Keep the
        # supplied limit out of this result to avoid a false pass/fail claim.
        raise ValueError("efficiency limits do not apply to chrono load comparison")
    return result
