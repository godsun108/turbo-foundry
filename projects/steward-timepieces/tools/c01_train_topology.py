"""C-01 going-train and chronograph topology calculator.

Defines required display speeds and evaluates explicitly supplied gear stages.
No tooth counts or efficiency values are invented. Exact ratios use Fraction.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from pathlib import Path
from typing import Any


OUTPUT_PERIOD_SECONDS = {
    "running_seconds": 60,
    "central_chronograph_seconds": 60,
    "minute_hand": 3600,
    "hour_hand": 43200,
    "chronograph_30_minute_register": 1800,
    "chronograph_12_hour_register": 43200,
}


@dataclass(frozen=True)
class GearStage:
    driver_teeth: int
    driven_teeth: int
    mesh: str = "external"

    def ratio(self) -> Fraction:
        if self.driver_teeth <= 0 or self.driven_teeth <= 0:
            raise ValueError("Gear tooth counts must be positive integers")
        if self.mesh not in {"external", "internal"}:
            raise ValueError("mesh must be 'external' or 'internal'")
        sign = -1 if self.mesh == "external" else 1
        return Fraction(sign * self.driver_teeth, self.driven_teeth)


def required_speed_rpm(period_seconds: int) -> Fraction:
    if not isinstance(period_seconds, int) or period_seconds <= 0:
        raise ValueError("period_seconds must be a positive integer")
    return Fraction(60, period_seconds)


def compound_ratio(stages: list[GearStage]) -> Fraction:
    if not stages:
        raise ValueError("At least one gear stage is required")
    result = Fraction(1, 1)
    for stage in stages:
        result *= stage.ratio()
    return result


def evaluate_path(input_rpm: Fraction, stages: list[GearStage]) -> dict[str, Any]:
    ratio = compound_ratio(stages)
    output_rpm = input_rpm * ratio
    return {
        "input_rpm": str(input_rpm),
        "signed_compound_speed_ratio": str(ratio),
        "output_rpm": str(output_rpm),
        "output_direction": "same" if output_rpm > 0 else "opposite",
        "stage_count": len(stages),
    }


def ideal_torque_after_path(input_torque_nm: float, stages: list[GearStage],
                            stage_efficiencies: list[float] | None = None) -> float:
    """Ideal/output torque magnitude; optional efficiencies are explicit inputs."""
    if not isfinite(input_torque_nm) or input_torque_nm < 0:
        raise ValueError("input_torque_nm must be finite and non-negative")
    ratio = abs(float(compound_ratio(stages)))
    if stage_efficiencies is None:
        total_efficiency = 1.0
    else:
        if len(stage_efficiencies) != len(stages):
            raise ValueError("One efficiency input is required per gear stage")
        total_efficiency = 1.0
        for efficiency in stage_efficiencies:
            if not isfinite(efficiency) or not 0 < efficiency <= 1:
                raise ValueError("Each stage efficiency must be in (0, 1]")
            total_efficiency *= efficiency
    return input_torque_nm / ratio * total_efficiency


def build_requirements() -> dict[str, Any]:
    speeds = {
        name: {
            "period_seconds_per_revolution": period,
            "required_speed_rpm": str(required_speed_rpm(period)),
        }
        for name, period in OUTPUT_PERIOD_SECONDS.items()
    }
    return {
        "schema": "steward.c01.train-topology.v1",
        "status": "requirements and topology alternatives; no gear train selected",
        "outputs": speeds,
        "required_speed_ratio_magnitudes": {
            "running_seconds_to_minute_hand": "1/60",
            "minute_hand_to_hour_hand": "1/12",
            "central_chrono_seconds_to_30m_register": "1/30",
            "central_chrono_seconds_to_12h_register": "1/720",
        },
        "power_path_candidates": [
            {
                "id": "P1_fourth_wheel_takeoff",
                "path": "barrel -> going train -> fourth-wheel/seconds axis -> chronograph clutch -> chrono seconds and totalizers",
                "status": "candidate_not_selected",
                "advantage_to_test": "Potentially direct 1 rpm source for seconds indication and chrono drive.",
                "risk_to_test": "Chronograph engagement load is applied at the seconds wheel/arbor and may disturb the going train.",
                "required_evidence": ["fourth-wheel torque margin", "amplitude chrono off/on", "start transient", "reserve chrono off/on"],
            },
            {
                "id": "P2_dedicated_chronograph_drive",
                "path": "barrel -> going train -> defined drive takeoff -> dedicated chrono drive train -> clutch -> chrono seconds and totalizers",
                "status": "candidate_not_selected",
                "advantage_to_test": "Allows deliberate ratio, isolation and service layout around the chronograph drive.",
                "risk_to_test": "Additional meshes, pivots and components add friction, packaging demand and adjustment burden.",
                "required_evidence": ["takeoff torque margin", "mesh loss", "amplitude chrono off/on", "start transient", "reserve chrono off/on"],
            },
        ],
        "functional_subsystems": [
            "barrel and winding train",
            "going train",
            "escapement and balance",
            "motion works and time display",
            "running seconds",
            "chronograph drive and clutch",
            "chronograph control and brake",
            "30-minute and 12-hour totalizers",
            "calendar drive and weekday/date mechanism",
        ],
        "unresolved": [
            "barrel arbor speed and usable torque curve",
            "going-train wheel topology and escapement tooth count",
            "actual chronograph takeoff wheel and torque margin",
            "clutch type and engagement geometry",
            "register indexing/jumper loads and reset loads",
            "gear tooth counts, module, center distances and materials",
            "measured mesh, pivot and escapement losses",
        ],
    }


def analyze_supplied_stages(data: dict[str, Any]) -> dict[str, Any]:
    input_rpm = Fraction(str(data["input_rpm"]))
    if input_rpm <= 0:
        raise ValueError("input_rpm must be positive")
    stages = [GearStage(**item) for item in data["stages"]]
    result = evaluate_path(input_rpm, stages)
    result["note"] = "Only valid for the explicitly supplied ideal gear-stage data."
    if "input_torque_nm" in data:
        efficiencies = data.get("stage_efficiencies")
        result["output_torque_nm_estimate"] = ideal_torque_after_path(
            float(data["input_torque_nm"]), stages, efficiencies
        )
        result["torque_note"] = (
            "Ideal ratio plus explicitly supplied efficiency factors; excludes "
            "bearing, lubricant, elastic, transient and escapement effects."
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", action="store_true",
                        help="Print C-01 required output speeds and open topology candidates")
    parser.add_argument("--stages", help="JSON file with input_rpm and explicit gear stages")
    args = parser.parse_args()
    if args.stages:
        result = analyze_supplied_stages(json.loads(Path(args.stages).read_text(encoding="utf-8")))
    else:
        result = build_requirements()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
