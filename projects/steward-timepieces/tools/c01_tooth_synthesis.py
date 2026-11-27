"""Bounded integer-tooth-ratio synthesis for STEWARD C-01 concept studies.

This enumerates mathematical external spur-gear ratio candidates only. It does
not certify tooth form, undercut, strength, backlash, center-distance fit,
manufacturability, torque, efficiency, or watch-scale feasibility.
"""
from __future__ import annotations

from bisect import bisect_left
from fractions import Fraction
from math import isfinite
from typing import Any


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _fraction(value: Any, name: str, *, positive: bool = False) -> Fraction:
    try:
        result = Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be a rational numeric value") from exc
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def pair_candidates(min_teeth: int, max_teeth: int,
                    min_stage_ratio: Any, max_stage_ratio: Any) -> list[dict[str, Any]]:
    """Build external driver/driven pairs; ratio magnitude = driver/driven."""
    low = _positive_int(min_teeth, "min_teeth")
    high = _positive_int(max_teeth, "max_teeth")
    if high < low:
        raise ValueError("max_teeth must be >= min_teeth")
    rmin = _fraction(min_stage_ratio, "min_stage_ratio", positive=True)
    rmax = _fraction(max_stage_ratio, "max_stage_ratio", positive=True)
    if rmax < rmin:
        raise ValueError("max_stage_ratio must be >= min_stage_ratio")
    result = []
    for driver in range(low, high + 1):
        for driven in range(low, high + 1):
            ratio = Fraction(driver, driven)
            if rmin <= ratio <= rmax:
                result.append({
                    "driver_teeth": driver,
                    "driven_teeth": driven,
                    "speed_ratio_magnitude": ratio,
                    "direction_reversed": True,
                })
    return result


def _candidate(stages: list[dict[str, Any]], target: Fraction,
               module_mm: Fraction | None) -> dict[str, Any]:
    ratio = Fraction(1, 1)
    stage_data = []
    for stage in stages:
        driver = stage["driver_teeth"]
        driven = stage["driven_teeth"]
        stage_ratio = Fraction(driver, driven)
        ratio *= stage_ratio
        item = {
            "driver_teeth": driver,
            "driven_teeth": driven,
            "speed_ratio_magnitude": str(stage_ratio),
            "direction_reversed": True,
        }
        if module_mm is not None:
            item["center_distance_mm"] = str(module_mm * (driver + driven) / 2)
        stage_data.append(item)
    error = abs(ratio - target) / target
    return {
        "stage_count": len(stages),
        "stages": stage_data,
        "compound_speed_ratio_magnitude": str(ratio),
        "target_ratio_magnitude": str(target),
        "fractional_absolute_ratio_error": str(error),
        "external_mesh_direction_reversals": len(stages),
        "output_direction_relative_to_input": "same" if len(stages) % 2 == 0 else "opposite",
        "mathematical_candidate_only": True,
    }


def synthesize(data: dict[str, Any]) -> dict[str, Any]:
    """Search one- and two-stage external compound paths within explicit bounds.

    Required: target_ratio, min_teeth, max_teeth, min_stage_ratio,
    max_stage_ratio, max_fractional_error, max_results.
    Optional: module_mm. A common module is used for each external pair.
    """
    target = _fraction(data["target_ratio"], "target_ratio", positive=True)
    min_teeth = _positive_int(data["min_teeth"], "min_teeth")
    max_teeth = _positive_int(data["max_teeth"], "max_teeth")
    max_error = _fraction(data["max_fractional_error"], "max_fractional_error")
    if max_error < 0 or max_error >= 1:
        raise ValueError("max_fractional_error must be in [0, 1)")
    max_results = _positive_int(data["max_results"], "max_results")
    module = None
    if data.get("module_mm") is not None:
        module = _fraction(data["module_mm"], "module_mm", positive=True)

    pairs = pair_candidates(
        min_teeth, max_teeth,
        data["min_stage_ratio"], data["max_stage_ratio"],
    )
    # Sort exact ratios once; for each first stage, inspect only neighbours
    # around the ideal second-stage ratio using binary search.
    ordered = sorted(pairs, key=lambda item: item["speed_ratio_magnitude"])
    ratios = [item["speed_ratio_magnitude"] for item in ordered]
    found: dict[tuple[tuple[int, int], ...], dict[str, Any]] = {}

    def retain(stages: list[dict[str, Any]]) -> None:
        candidate = _candidate(stages, target, module)
        if Fraction(candidate["fractional_absolute_ratio_error"]) <= max_error:
            key = tuple((s["driver_teeth"], s["driven_teeth"]) for s in stages)
            found[key] = candidate

    for pair in pairs:
        retain([pair])
        first_ratio = pair["speed_ratio_magnitude"]
        desired_second = target / first_ratio
        pos = bisect_left(ratios, desired_second)
        # Exact nearest candidates suffice for error-ranked bounded search.
        for index in range(max(0, pos - 2), min(len(ordered), pos + 3)):
            retain([pair, ordered[index]])

    ranked = sorted(
        found.values(),
        key=lambda item: (
            Fraction(item["fractional_absolute_ratio_error"]),
            item["stage_count"],
            tuple((s["driver_teeth"], s["driven_teeth"]) for s in item["stages"]),
        ),
    )
    selected = ranked[:max_results]
    return {
        "schema": "steward.c01.tooth-synthesis.v1",
        "status": "bounded mathematical candidates; no physical design selected",
        "target_ratio_magnitude": str(target),
        "search_bounds": {
            "min_teeth": min_teeth,
            "max_teeth": max_teeth,
            "min_stage_ratio": str(_fraction(data["min_stage_ratio"], "min_stage_ratio", positive=True)),
            "max_stage_ratio": str(_fraction(data["max_stage_ratio"], "max_stage_ratio", positive=True)),
            "max_fractional_error": str(max_error),
            "module_mm": str(module) if module is not None else None,
        },
        "pair_count": len(pairs),
        "candidate_count_within_tolerance": len(ranked),
        "returned_candidates": selected,
        "limitations": [
            "External spur mesh mathematical ratios only.",
            "No undercut, contact ratio, tooth form, strength, wear or manufacturability certification.",
            "Center distance is a preliminary pitch-circle calculation only when module is supplied.",
            "No shared-arbor, plate-layout, interference, tolerance or serviceability proof.",
            "No torque, efficiency, transient-load or rate-performance proof.",
        ],
    }
