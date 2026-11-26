"""Input-driven C-01 barrel energy and reserve estimator.

Requires measured/sourced torque samples and explicit load/efficiency inputs.
It does not provide default movement values or infer physical performance.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TorqueSample:
    angle_rad: float
    torque_nm: float


def _positive(value: float, name: str, *, zero_ok: bool = False) -> None:
    if not isfinite(value) or (value < 0 if zero_ok else value <= 0):
        raise ValueError(f"{name} must be finite and {'non-negative' if zero_ok else 'positive'}")


def integrate_energy(samples: list[TorqueSample]) -> float:
    """Trapezoidal integral of barrel torque over usable unwind angle (joules)."""
    if len(samples) < 2:
        raise ValueError("At least two measured torque samples are required")
    energy = 0.0
    previous = samples[0]
    _positive(previous.angle_rad, "angle_rad", zero_ok=True)
    _positive(previous.torque_nm, "torque_nm", zero_ok=True)
    for current in samples[1:]:
        _positive(current.angle_rad, "angle_rad", zero_ok=True)
        _positive(current.torque_nm, "torque_nm", zero_ok=True)
        delta = current.angle_rad - previous.angle_rad
        if delta <= 0:
            raise ValueError("Torque sample angles must be strictly increasing")
        energy += 0.5 * (previous.torque_nm + current.torque_nm) * delta
        previous = current
    return energy


def _efficiency(value: float, name: str) -> None:
    if not isfinite(value) or not 0 < value <= 1:
        raise ValueError(f"{name} must be finite and in (0, 1]")


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    """Calculate theoretical reserve for chrono-off and chrono-on load cases.

    base_load_w and chrono_incremental_load_w are loads at the useful train
    output reference plane. train_efficiency converts barrel energy to that
    plane. Calendar event energy is specified at the same output plane and
    averaged using events_per_day; it is an approximation, not a transient
    simulation of midnight torque or rate disturbance.
    """
    samples = [TorqueSample(**item) for item in data["torque_samples"]]
    energy_barrel = integrate_energy(samples)
    efficiency = float(data["train_efficiency"])
    _efficiency(efficiency, "train_efficiency")
    base = float(data["base_load_w"])
    chrono_extra = float(data["chrono_incremental_load_w"])
    calendar_event = float(data.get("calendar_event_energy_j", 0.0))
    events_per_day = float(data.get("calendar_events_per_day", 0.0))
    for value, name in [
        (base, "base_load_w"),
        (chrono_extra, "chrono_incremental_load_w"),
        (calendar_event, "calendar_event_energy_j"),
        (events_per_day, "calendar_events_per_day"),
    ]:
        _positive(value, name, zero_ok=True)
    if base == 0:
        raise ValueError("base_load_w must be greater than zero")
    if (calendar_event == 0) != (events_per_day == 0):
        raise ValueError("Calendar event energy and events/day must both be zero or both be positive")

    calendar_average_w = calendar_event * events_per_day / 86400.0
    base_total_w = base + calendar_average_w
    chrono_total_w = base_total_w + chrono_extra
    delivered_energy_j = energy_barrel * efficiency

    def reserve_hours(load_w: float) -> float:
        return delivered_energy_j / load_w / 3600.0

    return {
        "model": "steward.c01.barrel-energy.v1",
        "units": {"energy": "J", "power": "W", "reserve": "h", "angle": "rad", "torque": "N.m"},
        "usable_barrel_energy_j": energy_barrel,
        "train_efficiency_input": efficiency,
        "energy_at_output_reference_plane_j": delivered_energy_j,
        "calendar_average_load_w": calendar_average_w,
        "chrono_stopped": {
            "total_average_load_w": base_total_w,
            "estimated_reserve_hours": reserve_hours(base_total_w),
        },
        "chrono_running": {
            "incremental_chronograph_load_w": chrono_extra,
            "total_average_load_w": chrono_total_w,
            "estimated_reserve_hours": reserve_hours(chrono_total_w),
        },
        "assumptions_and_limits": [
            "Torque samples must cover only the approved usable unwind interval.",
            "Constant average loads are a first-order approximation.",
            "Calendar event energy is averaged over a day; peak changeover load is not modeled.",
            "Chronograph incremental load is assumed constant while engaged.",
            "Train efficiency is a single aggregate input; component losses are not resolved.",
            "This does not predict amplitude, rate, torque curve stability, stoppage margin, or real-world reserve.",
            "All numeric inputs must be measured, supplier-confirmed, or explicitly justified and documented.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", help="JSON file containing measured/source-backed inputs")
    parser.add_argument("--output", help="Optional path for JSON results")
    args = parser.parse_args()
    result = calculate(json.loads(Path(args.input_json).read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
