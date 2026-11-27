"""Integrated, measurement-driven STEWARD C-01 system checks.

This module aggregates measured subsystem loads only when they share a
measurement boundary and time interval. It does not infer missing loads,
allocate subsystem losses, or claim physical movement performance.
"""
from __future__ import annotations

from math import isfinite
from typing import Any


def _number(value: Any, name: str, *, positive: bool = False,
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


def evaluate_integrated_energy(data: dict[str, Any]) -> dict[str, Any]:
    """Aggregate non-overlapping measured loads over one common test interval.

    Required: boundary_id, interval_id, interval_seconds,
    usable_barrel_energy_j, and loads=[{component, energy_j,
    boundary_id, interval_id}]. Every load must use the same defined
    measurement boundary and interval. Component names must be unique to
    prevent accidental double counting. All energy values are joules.
    """
    for key in ("boundary_id", "interval_id"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"{key} must be a non-empty identifier")
    boundary = data["boundary_id"]
    interval_id = data["interval_id"]
    duration = _number(data.get("interval_seconds"), "interval_seconds",
                       positive=True)
    usable = _number(data.get("usable_barrel_energy_j"),
                     "usable_barrel_energy_j", positive=True)
    loads = data.get("loads")
    if not isinstance(loads, list) or not loads:
        raise ValueError("loads must be a non-empty list")

    seen: set[str] = set()
    normalized = []
    for index, load in enumerate(loads):
        if not isinstance(load, dict):
            raise ValueError(f"load {index} must be an object")
        component = load.get("component")
        if not isinstance(component, str) or not component.strip():
            raise ValueError(f"load {index} requires a component identifier")
        if component in seen:
            raise ValueError(f"duplicate component risks double counting: {component}")
        seen.add(component)
        if load.get("boundary_id") != boundary:
            raise ValueError(f"load {component} has a mismatched measurement boundary")
        if load.get("interval_id") != interval_id:
            raise ValueError(f"load {component} has a mismatched measurement interval")
        energy = _number(load.get("energy_j"), f"{component}.energy_j",
                         nonnegative=True)
        normalized.append({"component": component, "energy_j": energy})

    total = sum(item["energy_j"] for item in normalized)
    margin = usable - total
    average_power = total / duration
    reserve_hours = usable / average_power / 3600.0 if average_power > 0 else None
    return {
        "model": "steward.c01.system-integration.energy.v1",
        "boundary_id": boundary,
        "interval_id": interval_id,
        "interval_seconds": duration,
        "usable_barrel_energy_j": usable,
        "loads": normalized,
        "total_measured_load_energy_j": total,
        "energy_margin_j": margin,
        "energy_margin_nonnegative": margin >= 0,
        "average_measured_system_power_w": average_power,
        "idealized_reserve_hours_at_measured_average_load": reserve_hours,
        "reserve_is_extrapolation": True,
    }


def evaluate_axial_stack(components: list[dict[str, Any]]) -> dict[str, float | int]:
    """Calculate a worst-case axial stack from supplied measured/CAD values.

    Each component requires unique name, nominal_mm, tolerance_plus_mm and
    tolerance_minus_mm. Tolerances are non-negative magnitudes. This simple
    arithmetic stack does not model datum strategy, geometric tolerances,
    elastic deformation, thermal growth, or statistical RSS.
    """
    if not isinstance(components, list) or not components:
        raise ValueError("components must be a non-empty list")
    seen: set[str] = set()
    nominal = upper = lower = 0.0
    for index, item in enumerate(components):
        if not isinstance(item, dict):
            raise ValueError(f"component {index} must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"component {index} requires a name")
        if name in seen:
            raise ValueError(f"duplicate component name: {name}")
        seen.add(name)
        n = _number(item.get("nominal_mm"), f"{name}.nominal_mm",
                    nonnegative=True)
        plus = _number(item.get("tolerance_plus_mm"),
                       f"{name}.tolerance_plus_mm", nonnegative=True)
        minus = _number(item.get("tolerance_minus_mm"),
                        f"{name}.tolerance_minus_mm", nonnegative=True)
        nominal += n
        upper += n + plus
        lower += n - minus
    return {
        "component_count": len(components),
        "nominal_stack_mm": nominal,
        "worst_case_upper_mm": upper,
        "worst_case_lower_mm": lower,
        "worst_case_total_tolerance_band_mm": upper - lower,
    }
