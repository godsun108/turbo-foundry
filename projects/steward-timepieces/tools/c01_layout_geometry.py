"""Evidence-gated C-01 planar and axial layout checks.

All dimensions and coordinates are caller-supplied. This module evaluates
candidate geometry; it does not create CAD or certify a watch movement.
"""
from __future__ import annotations

from math import hypot, isfinite
from typing import Any


def _number(value: Any, name: str, *, positive: bool = False,
            nonnegative: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
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


def gear_pitch_radius_mm(teeth: int, module_mm: float) -> float:
    if isinstance(teeth, bool) or not isinstance(teeth, int) or teeth <= 0:
        raise ValueError("teeth must be a positive integer")
    module = _number(module_mm, "module_mm", positive=True)
    return teeth * module / 2.0


def evaluate_gear_mesh(mesh: dict[str, Any]) -> dict[str, Any]:
    """Check supplied external spur-gear pitch-center distance."""
    required = ("id", "driver_teeth", "driven_teeth", "module_mm",
                "driver_xy_mm", "driven_xy_mm", "center_tolerance_mm")
    missing = [key for key in required if key not in mesh]
    if missing:
        raise ValueError("missing mesh fields: " + ", ".join(missing))
    a = mesh["driver_xy_mm"]
    b = mesh["driven_xy_mm"]
    if len(a) != 2 or len(b) != 2:
        raise ValueError("gear centers must be [x_mm, y_mm]")
    ax, ay = (_number(a[0], "driver_x"), _number(a[1], "driver_y"))
    bx, by = (_number(b[0], "driven_x"), _number(b[1], "driven_y"))
    module = _number(mesh["module_mm"], "module_mm", positive=True)
    tol = _number(mesh["center_tolerance_mm"], "center_tolerance_mm", nonnegative=True)
    r1 = gear_pitch_radius_mm(mesh["driver_teeth"], module)
    r2 = gear_pitch_radius_mm(mesh["driven_teeth"], module)
    actual = hypot(bx - ax, by - ay)
    nominal = r1 + r2
    delta = actual - nominal
    return {
        "id": mesh["id"],
        "nominal_pitch_center_distance_mm": nominal,
        "actual_center_distance_mm": actual,
        "center_distance_deviation_mm": delta,
        "center_tolerance_mm": tol,
        "within_supplied_center_tolerance": abs(delta) <= tol,
        "driver_pitch_radius_mm": r1,
        "driven_pitch_radius_mm": r2,
        "geometry_status": "preliminary_pitch_geometry_only",
    }


def evaluate_component_clearances(components: list[dict[str, Any]]) -> dict[str, Any]:
    """Check circular XY envelopes and Z intervals for supplied components.

    Components on different named layers are checked for planar clearance only
    when their Z intervals overlap. Touching envelopes count as zero clearance.
    """
    if not isinstance(components, list) or not components:
        raise ValueError("components must be a non-empty list")
    normalized = []
    ids = set()
    for i, item in enumerate(components):
        required = ("id", "x_mm", "y_mm", "envelope_radius_mm",
                    "z_min_mm", "z_max_mm", "layer")
        missing = [key for key in required if key not in item]
        if missing:
            raise ValueError(f"component {i} missing: " + ", ".join(missing))
        ident = item["id"]
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            raise ValueError("component ids must be non-empty and unique")
        layer = item["layer"]
        if not isinstance(layer, str) or not layer.strip():
            raise ValueError(f"{ident}: layer must be non-empty")
        x = _number(item["x_mm"], f"{ident}.x_mm")
        y = _number(item["y_mm"], f"{ident}.y_mm")
        radius = _number(item["envelope_radius_mm"], f"{ident}.envelope_radius_mm", positive=True)
        z0 = _number(item["z_min_mm"], f"{ident}.z_min_mm")
        z1 = _number(item["z_max_mm"], f"{ident}.z_max_mm")
        if z1 <= z0:
            raise ValueError(f"{ident}: z_max_mm must exceed z_min_mm")
        ids.add(ident)
        normalized.append({"id": ident, "x": x, "y": y, "r": radius,
                           "z0": z0, "z1": z1, "layer": layer})
    results = []
    for i, first in enumerate(normalized):
        for second in normalized[i + 1:]:
            z_overlap = min(first["z1"], second["z1"]) - max(first["z0"], second["z0"])
            center = hypot(first["x"] - second["x"], first["y"] - second["y"])
            clearance = center - first["r"] - second["r"]
            if z_overlap > 0:
                results.append({
                    "components": [first["id"], second["id"]],
                    "z_overlap_mm": z_overlap,
                    "planar_clearance_mm": clearance,
                    "planar_envelopes_clear": clearance >= 0,
                    "layer_pair": [first["layer"], second["layer"]],
                })
    return {
        "component_count": len(normalized),
        "checked_pairs_with_axial_overlap": len(results),
        "clearance_results": results,
        "has_envelope_interference": any(not r["planar_envelopes_clear"] for r in results),
        "fit_certified": False,
        "limitations": [
            "Circular envelopes are conservative simplified reservations, not exact component profiles.",
            "No tolerances, runout, endshake, deflection, hand sweep or assembly motion are included.",
            "All Z intervals must share one controlled datum.",
        ],
    }


def normalized_to_mm(x_over_r: float, y_over_r: float,
                      opening_radius_mm: float) -> dict[str, float]:
    radius = _number(opening_radius_mm, "opening_radius_mm", positive=True)
    x = _number(x_over_r, "x_over_r") * radius
    y = _number(y_over_r, "y_over_r") * radius
    return {"x_mm": x, "y_mm": y, "radial_distance_mm": hypot(x, y)}


def evaluate_layout(data: dict[str, Any]) -> dict[str, Any]:
    meshes = [evaluate_gear_mesh(m) for m in data.get("gear_meshes", [])]
    clearances = evaluate_component_clearances(data["components"]) if data.get("components") else None
    return {
        "schema": "steward.c01.layout-check.v1",
        "status": "candidate geometry review only",
        "gear_meshes": meshes,
        "component_clearances": clearances,
        "all_supplied_meshes_within_tolerance": all(
            m["within_supplied_center_tolerance"] for m in meshes
        ),
        "overall_fit_certified": False,
        "required_review": [
            "dimensioned CAD and exact tooth profiles",
            "tolerance stack, backlash, endshake and runout",
            "dynamic swept envelopes and hand clearances",
            "assembly and service access",
            "structural stiffness and deflection",
        ],
    }
