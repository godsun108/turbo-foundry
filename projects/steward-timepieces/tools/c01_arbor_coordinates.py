"""Evidence-gated C-01 arbor coordinates and gear-center definition.

Coordinates are candidate inputs, never defaults. The module provides exact
spur-gear center-distance relationships, coordinate constraints, two-circle
solutions, and traceable arbor/support registers. It does not choose a layout.
"""
from __future__ import annotations

from math import cos, hypot, isfinite, radians, sin, sqrt
from typing import Any


def _number(value: Any, field: str, *, positive: bool = False,
            nonnegative: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not isfinite(result):
        raise ValueError(f"{field} must be finite")
    if positive and result <= 0:
        raise ValueError(f"{field} must be positive")
    if nonnegative and result < 0:
        raise ValueError(f"{field} must be non-negative")
    return result


def _point(value: Any, field: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must be [x_mm, y_mm]")
    return (_number(value[0], field + ".x"), _number(value[1], field + ".y"))


def gear_center_distance(module_mm: Any, driver_teeth: int,
                         driven_teeth: int, mesh: str = "external") -> float:
    """Nominal standard spur-gear center distance for supplied geometry.

    External: m(z1+z2)/2. Internal: m*abs(zring-zpinion)/2.
    Internal gear inputs must identify ring and pinion in that order.
    Profile shift, backlash, tooth corrections and manufacturing tolerances
    are outside this nominal relationship.
    """
    module = _number(module_mm, "module_mm", positive=True)
    for value, name in ((driver_teeth, "driver_teeth"),
                        (driven_teeth, "driven_teeth")):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if mesh == "external":
        tooth_sum = driver_teeth + driven_teeth
    elif mesh == "internal":
        tooth_sum = abs(driver_teeth - driven_teeth)
        if tooth_sum == 0:
            raise ValueError("internal ring and pinion tooth counts must differ")
    else:
        raise ValueError("mesh must be 'external' or 'internal'")
    return module * tooth_sum / 2.0


def solve_axis_from_polar(anchor_xy_mm: Any, center_distance_mm: Any,
                          angle_deg_from_positive_x: Any) -> dict[str, Any]:
    """Solve one axis from an explicitly supplied anchor, radius and angle."""
    x, y = _point(anchor_xy_mm, "anchor_xy_mm")
    radius = _number(center_distance_mm, "center_distance_mm", positive=True)
    angle = _number(angle_deg_from_positive_x, "angle_deg_from_positive_x")
    theta = radians(angle)
    point = [x + radius * cos(theta), y + radius * sin(theta)]
    return {
        "xy_mm": point,
        "anchor_xy_mm": [x, y],
        "center_distance_mm": radius,
        "angle_deg_from_positive_x": angle,
        "solution_count": 1,
        "selection_basis": "explicit user-supplied polar constraint",
        "candidate_only": True,
    }


def solve_two_circle_intersections(center_a_xy_mm: Any, radius_a_mm: Any,
                                   center_b_xy_mm: Any, radius_b_mm: Any,
                                   tolerance_mm: Any = 1e-9) -> dict[str, Any]:
    """Return zero, one or two intersections of two center-distance loci.

    Both solutions are retained. No arbitrary branch is selected.
    """
    ax, ay = _point(center_a_xy_mm, "center_a_xy_mm")
    bx, by = _point(center_b_xy_mm, "center_b_xy_mm")
    ra = _number(radius_a_mm, "radius_a_mm", positive=True)
    rb = _number(radius_b_mm, "radius_b_mm", positive=True)
    tol = _number(tolerance_mm, "tolerance_mm", nonnegative=True)
    dx, dy = bx - ax, by - ay
    d = hypot(dx, dy)
    if d <= tol:
        if abs(ra - rb) <= tol:
            return {"solutions_xy_mm": [], "solution_count": 0,
                    "status": "coincident_loci_underdetermined",
                    "candidate_only": True}
        return {"solutions_xy_mm": [], "solution_count": 0,
                "status": "concentric_nonintersecting_loci",
                "candidate_only": True}
    if d > ra + rb + tol or d < abs(ra - rb) - tol:
        return {"solutions_xy_mm": [], "solution_count": 0,
                "status": "no_intersection", "candidate_only": True}
    along = (ra * ra - rb * rb + d * d) / (2 * d)
    h2 = ra * ra - along * along
    if h2 < -tol * max(1.0, ra * ra):
        return {"solutions_xy_mm": [], "solution_count": 0,
                "status": "no_intersection", "candidate_only": True}
    h = sqrt(max(0.0, h2))
    ux, uy = dx / d, dy / d
    px, py = ax + along * ux, ay + along * uy
    candidates = [[px - h * uy, py + h * ux]]
    if h > tol:
        candidates.append([px + h * uy, py - h * ux])
    return {
        "solutions_xy_mm": candidates,
        "solution_count": len(candidates),
        "status": "tangent" if len(candidates) == 1 else "two_candidates",
        "candidate_only": True,
        "selection_basis": "none; both geometric branches retained",
    }


def evaluate_mesh(mesh: dict[str, Any]) -> dict[str, Any]:
    """Compare supplied arbor centers with nominal spur-gear center distance."""
    required = ("id", "arbor_a_id", "arbor_b_id", "module_mm",
                "gear_a_teeth", "gear_b_teeth", "mesh", "xy_a_mm",
                "xy_b_mm", "center_distance_tolerance_mm", "evidence",
                "source_revision")
    missing = [key for key in required if key not in mesh or mesh[key] in (None, "")]
    if missing:
        raise ValueError("gear mesh missing: " + ", ".join(missing))
    nominal = gear_center_distance(mesh["module_mm"], mesh["gear_a_teeth"],
                                    mesh["gear_b_teeth"], mesh["mesh"])
    a = _point(mesh["xy_a_mm"], "xy_a_mm")
    b = _point(mesh["xy_b_mm"], "xy_b_mm")
    actual = hypot(b[0] - a[0], b[1] - a[1])
    tolerance = _number(mesh["center_distance_tolerance_mm"],
                        "center_distance_tolerance_mm", nonnegative=True)
    deviation = actual - nominal
    return {
        "id": mesh["id"], "nominal_center_distance_mm": nominal,
        "actual_center_distance_mm": actual,
        "signed_deviation_mm": deviation,
        "absolute_deviation_mm": abs(deviation),
        "passes_supplied_center_distance_tolerance": abs(deviation) <= tolerance,
        "tolerance_mm": tolerance,
        "mesh_direction": "opposite" if mesh["mesh"] == "external" else "same",
        "geometry_status": "nominal_center_distance_check_only",
        "candidate_only": True,
    }


def validate_register(data: dict[str, Any],
                      known_component_ids: set[str] | None = None) -> dict[str, Any]:
    """Validate traceable arbor, support and mesh references."""
    arbors, supports, meshes = (data.get("arbors"), data.get("supports"),
                                data.get("gear_meshes"))
    if not isinstance(arbors, list) or not isinstance(supports, list) or not isinstance(meshes, list):
        raise ValueError("arbors, supports and gear_meshes must be lists")
    def unique(items: list[dict[str, Any]], field: str, label: str) -> set[str]:
        vals = [item.get(field) for item in items]
        if any(not isinstance(v, str) or not v.strip() for v in vals):
            raise ValueError(f"every {label} requires {field}")
        if len(vals) != len(set(vals)):
            raise ValueError(f"{label} {field} values must be unique")
        return set(vals)
    arbor_ids = unique(arbors, "id", "arbor") if arbors else set()
    support_ids = unique(supports, "id", "support") if supports else set()
    unique(meshes, "id", "gear mesh") if meshes else set()
    for arbor in arbors:
        for field in ("role", "component_id", "axis_id", "evidence", "source_revision"):
            if not arbor.get(field):
                raise ValueError(f"arbor {arbor['id']} requires {field}")
        if known_component_ids is not None and arbor["component_id"] not in known_component_ids:
            raise ValueError(f"arbor {arbor['id']} references unknown component")
        if arbor.get("xy_mm") is not None:
            _point(arbor["xy_mm"], f"arbor {arbor['id']}.xy_mm")
        if arbor.get("z_interval_mm") is not None:
            z = arbor["z_interval_mm"]
            if not isinstance(z, (list, tuple)) or len(z) != 2:
                raise ValueError(f"arbor {arbor['id']} z_interval_mm must be [min, max]")
            if _number(z[1], "z_max") <= _number(z[0], "z_min"):
                raise ValueError(f"arbor {arbor['id']} axial interval must have positive extent")
        for support_id in arbor.get("support_ids", []):
            if support_id not in support_ids:
                raise ValueError(f"arbor {arbor['id']} references unknown support {support_id}")
    for support in supports:
        for field in ("arbor_id", "structure_id", "support_type", "evidence", "source_revision"):
            if not support.get(field):
                raise ValueError(f"support {support['id']} requires {field}")
        if support["arbor_id"] not in arbor_ids:
            raise ValueError(f"support {support['id']} references unknown arbor")
    for mesh in meshes:
        if mesh.get("arbor_a_id") not in arbor_ids or mesh.get("arbor_b_id") not in arbor_ids:
            raise ValueError(f"gear mesh {mesh['id']} references unknown arbor")
        if mesh["arbor_a_id"] == mesh["arbor_b_id"]:
            raise ValueError(f"gear mesh {mesh['id']} must connect distinct arbors")
    return {"arbor_count": len(arbor_ids), "support_count": len(support_ids),
            "gear_mesh_count": len(meshes), "all_references_resolve": True}


def evaluate_candidate(data: dict[str, Any],
                       known_component_ids: set[str] | None = None) -> dict[str, Any]:
    """Evaluate only fully supplied arbor coordinates and mesh constraints."""
    summary = validate_register(data, known_component_ids)
    by_id = {item["id"]: item for item in data["arbors"]}
    mesh_results = []
    incomplete = []
    for mesh in data["gear_meshes"]:
        a, b = by_id[mesh["arbor_a_id"]], by_id[mesh["arbor_b_id"]]
        if a.get("xy_mm") is None or b.get("xy_mm") is None:
            incomplete.append(mesh["id"])
        else:
            enriched = dict(mesh, xy_a_mm=a["xy_mm"], xy_b_mm=b["xy_mm"])
            mesh_results.append(evaluate_mesh(enriched))
    return {
        "schema": "steward.c01.arbor-coordinate-evaluation.v1",
        "candidate_id": data.get("candidate_id", "unnamed_candidate"),
        "register_summary": summary,
        "gear_mesh_results": mesh_results,
        "gear_meshes_missing_axis_coordinates": incomplete,
        "evaluated_mesh_count": len(mesh_results),
        "all_evaluated_meshes_within_supplied_tolerance": all(
            item["passes_supplied_center_distance_tolerance"] for item in mesh_results),
        "overall_fit_status": "not_certified",
        "limitations": [
            "Nominal spur-gear center distance only; no profile shift or tooth-form analysis.",
            "No undercut, contact ratio, strength, backlash, wear, lubrication or efficiency analysis.",
            "No plate containment, edge distance, bearing fit, tolerance stack or dynamic envelope proof.",
            "Coordinate solutions are geometric candidates, not architecture selections.",
        ],
    }


def cad_bore_register(arbors: list[dict[str, Any]],
                      bore_definitions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Map positioned arbors to WP-22 bore inputs only with explicit bore data.

    bore_definitions is keyed by arbor id and must supply diameter_mm,
    evidence and source_revision. No bore diameter is inferred.
    """
    result = []
    for arbor in arbors:
        if arbor.get("xy_mm") is None or arbor["id"] not in bore_definitions:
            continue
        spec = bore_definitions[arbor["id"]]
        result.append({
            "id": spec.get("id", "bore_" + arbor["id"]),
            "component_id": arbor["component_id"],
            "axis_id": arbor["axis_id"],
            "xy_mm": list(_point(arbor["xy_mm"], "arbor.xy_mm")),
            "diameter_mm": _number(spec.get("diameter_mm"), "diameter_mm", positive=True),
            "evidence": spec.get("evidence"),
            "source_revision": spec.get("source_revision"),
        })
        if not spec.get("evidence") or not spec.get("source_revision"):
            raise ValueError(f"CAD bore for {arbor['id']} requires evidence and source_revision")
    return result
