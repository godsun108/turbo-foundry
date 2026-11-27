"""Evidence-gated C-01 architecture envelope and stack calculations.

Inputs must come from measured, supplier-confirmed, or controlled CAD data.
Synthetic fixtures belong only in unit tests. This module does not create CAD
or certify mechanical fit.
"""
from __future__ import annotations

from math import hypot, isfinite
from typing import Any


ALLOWED_EVIDENCE = {"measured", "calculated", "supplier_confirmed", "provisional", "TBD"}


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


def normalized_point_to_mm(x_over_r: float, y_over_r: float,
                            opening_radius_mm: float) -> dict[str, float]:
    """Convert normalized dial coordinates to mm using a supplied measured radius."""
    x = _finite(x_over_r, "x_over_r")
    y = _finite(y_over_r, "y_over_r")
    radius = _finite(opening_radius_mm, "opening_radius_mm", positive=True)
    return {"x_mm": x * radius, "y_mm": y * radius,
            "radial_distance_mm": hypot(x * radius, y * radius)}


def evaluate_planar_zone(zone: dict[str, Any], opening_radius_mm: float) -> dict[str, Any]:
    """Check a rectangular XY reservation against a circular dial opening.

    The conservative check uses the rectangle's four corners. This only tests
    the supplied 2D reservation; it does not prove fit against neighboring
    parts, hands, case geometry, tolerances, or other Z layers.
    """
    required = ("name", "x_over_r", "y_over_r", "width_over_r", "height_over_r", "evidence")
    missing = [key for key in required if key not in zone]
    if missing:
        raise ValueError("missing zone fields: " + ", ".join(missing))
    name = zone["name"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("zone name must be non-empty")
    evidence = zone["evidence"]
    if evidence not in ALLOWED_EVIDENCE:
        raise ValueError("unsupported evidence status")
    x = _finite(zone["x_over_r"], "x_over_r")
    y = _finite(zone["y_over_r"], "y_over_r")
    width = _finite(zone["width_over_r"], "width_over_r", positive=True)
    height = _finite(zone["height_over_r"], "height_over_r", positive=True)
    radius = _finite(opening_radius_mm, "opening_radius_mm", positive=True)
    corners = [
        (x - width / 2, y - height / 2),
        (x - width / 2, y + height / 2),
        (x + width / 2, y - height / 2),
        (x + width / 2, y + height / 2),
    ]
    corner_radii = [hypot(cx, cy) for cx, cy in corners]
    max_radius_mm = max(corner_radii) * radius
    return {
        "name": name,
        "evidence": evidence,
        "max_corner_radius_mm": max_radius_mm,
        "opening_radius_mm": radius,
        "within_circular_opening_by_corner_test": max_radius_mm <= radius,
        "corner_clearance_mm": radius - max_radius_mm,
        "method": "conservative rectangle-corner radial check",
        "fit_certified": False,
    }


def evaluate_axial_intervals(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Check Z-interval intersections for supplied components.

    Each item needs name, z_min_mm, z_max_mm, layer, evidence. Intervals are
    closed and measured from the same documented datum. Intersections are
    flagged only between components on the same layer unless the caller
    assigns a common physical interaction group via shared layer names.
    """
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a non-empty list")
    normalized = []
    names = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"item {index} must be an object")
        for key in ("name", "z_min_mm", "z_max_mm", "layer", "evidence"):
            if key not in item:
                raise ValueError(f"item {index} missing {key}")
        name, layer, evidence = item["name"], item["layer"], item["evidence"]
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("component names must be non-empty and unique")
        if not isinstance(layer, str) or not layer.strip():
            raise ValueError(f"{name}: layer must be non-empty")
        if evidence not in ALLOWED_EVIDENCE:
            raise ValueError(f"{name}: unsupported evidence status")
        z0 = _finite(item["z_min_mm"], f"{name}.z_min_mm")
        z1 = _finite(item["z_max_mm"], f"{name}.z_max_mm")
        if z1 <= z0:
            raise ValueError(f"{name}: z_max_mm must exceed z_min_mm")
        names.add(name)
        normalized.append({"name": name, "layer": layer, "z_min_mm": z0,
                           "z_max_mm": z1, "evidence": evidence})
    intersections = []
    for i, a in enumerate(normalized):
        for b in normalized[i + 1:]:
            if a["layer"] != b["layer"]:
                continue
            overlap = min(a["z_max_mm"], b["z_max_mm"]) - max(a["z_min_mm"], b["z_min_mm"])
            if overlap > 0:
                intersections.append({"components": [a["name"], b["name"]],
                                       "layer": a["layer"],
                                       "overlap_mm": overlap})
    return {
        "component_count": len(normalized),
        "same_layer_intersections": intersections,
        "has_same_layer_intersections": bool(intersections),
        "fit_certified": False,
        "datum_requirement": "All Z intervals must reference the same controlled datum.",
    }


def validate_axis_register(axes: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate completeness and evidence labels for critical arbor-axis records."""
    if not isinstance(axes, list) or not axes:
        raise ValueError("axes must be a non-empty list")
    seen = set()
    unresolved = []
    records = []
    for index, axis in enumerate(axes):
        for key in ("name", "x_mm", "y_mm", "evidence", "source_id"):
            if key not in axis:
                raise ValueError(f"axis {index} missing {key}")
        name = axis["name"]
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise ValueError("axis names must be non-empty and unique")
        seen.add(name)
        evidence = axis["evidence"]
        if evidence not in ALLOWED_EVIDENCE:
            raise ValueError(f"{name}: unsupported evidence status")
        if axis["x_mm"] is None or axis["y_mm"] is None or evidence == "TBD":
            unresolved.append(name)
            records.append({"name": name, "resolved": False, "evidence": evidence})
            continue
        x = _finite(axis["x_mm"], f"{name}.x_mm")
        y = _finite(axis["y_mm"], f"{name}.y_mm")
        if evidence in {"measured", "supplier_confirmed", "calculated"} and not (
            isinstance(axis["source_id"], str) and axis["source_id"].strip()
        ):
            raise ValueError(f"{name}: traceable source_id required for {evidence} data")
        records.append({"name": name, "resolved": True, "x_mm": x,
                        "y_mm": y, "evidence": evidence,
                        "source_id": axis["source_id"]})
    return {"axis_count": len(records), "resolved_count": len(records) - len(unresolved),
            "unresolved_axes": unresolved, "axes": records,
            "architecture_ready": not unresolved}
