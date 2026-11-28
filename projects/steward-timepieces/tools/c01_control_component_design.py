"""WP-54 evidence-gated CW/CL component-definition and CAD handoff.

All dimensions are explicit caller inputs in millimetres/degrees. No defaults
represent C-01 design values. Geometry checks are screening only; this module
cannot select an architecture, prove physical fit, or release manufacture.
"""
from __future__ import annotations
import math

class ComponentDesignError(ValueError):
    pass

CANDIDATES = {"column_wheel", "cam_lever"}
GEOMETRY_TYPES = {"circle", "annulus", "polygon"}
REQUIRED_CW_ROLES = {"wheel_body", "indexing_columns", "pivot_or_bore", "jumper_interface"}
REQUIRED_CL_ROLES = {"cam_profile", "follower", "operating_lever", "state_retention"}
REQUIRED_SHARED_ROLES = {"reset_hammer", "heart_cam", "running_reset_interlock"}
REQUIRED_INTERFACES = {
    "pusher_to_control", "control_to_clutch", "control_to_retention",
    "control_to_reset", "reset_hammer_to_heart", "running_reset_block",
}

def _text(v, name):
    if not isinstance(v, str) or not v.strip():
        raise ComponentDesignError(f"{name} is required")
    return v

def _num(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ComponentDesignError(f"{name} must be finite numeric")
    return float(v)

def _positive(v, name):
    x = _num(v, name)
    if x <= 0:
        raise ComponentDesignError(f"{name} must be positive")
    return x

def _provenance(row, label):
    _text(row.get("evidence_id"), f"{label}.evidence_id")
    _text(row.get("source_revision"), f"{label}.source_revision")

def column_wheel_indexing(column_count, indexing_radius_mm, phase_deg, evidence_id, source_revision):
    """Return theoretical equal angular pitch and chord from explicit inputs.

    This is geometric arithmetic, not a selected column count or indexer design.
    """
    if isinstance(column_count, bool) or not isinstance(column_count, int) or column_count < 2:
        raise ComponentDesignError("column_count must be an integer >= 2")
    r = _positive(indexing_radius_mm, "indexing_radius_mm")
    phase = _num(phase_deg, "phase_deg")
    _text(evidence_id, "evidence_id"); _text(source_revision, "source_revision")
    step = 360.0 / column_count
    chord = 2.0 * r * math.sin(math.radians(step / 2.0))
    return {
        "column_count": column_count, "indexing_radius_mm": r,
        "phase_deg": phase, "angular_pitch_deg": step,
        "adjacent_column_chord_mm": chord,
        "column_angles_deg": [((phase + i * step) % 360.0) for i in range(column_count)],
        "evidence_id": evidence_id, "source_revision": source_revision,
        "architecture_selected": False,
    }

def validate_profile(points, evidence_id, source_revision, label="profile"):
    """Validate a closed-by-implicit-closure XY polygon; no curve fitting/contact solution."""
    _text(evidence_id, f"{label}.evidence_id"); _text(source_revision, f"{label}.source_revision")
    if not isinstance(points, list) or len(points) < 3:
        raise ComponentDesignError(f"{label} needs at least three XY points")
    pts = []
    for i, p in enumerate(points):
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ComponentDesignError(f"{label} point {i} must be [x_mm, y_mm]")
        pts.append((_num(p[0], f"{label}.x_mm"), _num(p[1], f"{label}.y_mm")))
    if len(set(pts)) != len(pts):
        raise ComponentDesignError(f"{label} points must be unique")
    if any(math.dist(pts[i], pts[(i+1) % len(pts)]) <= 1e-12 for i in range(len(pts))):
        raise ComponentDesignError(f"{label} has a zero-length edge")
    area2 = sum(pts[i][0]*pts[(i+1)%len(pts)][1] - pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
    if abs(area2) <= 1e-12:
        raise ComponentDesignError(f"{label} polygon area must be non-zero")
    return {"point_count": len(pts), "signed_area_mm2": area2/2.0,
            "closed_by_implicit_last_to_first_edge": True,
            "evidence_id": evidence_id, "source_revision": source_revision,
            "self_intersection_checked": False}

def validate_component(component):
    if not isinstance(component, dict):
        raise ComponentDesignError("component must be an object")
    for f in ("component_id", "candidate_id", "role", "geometry_type", "evidence_id", "source_revision", "unit"):
        _text(component.get(f), f"component.{f}")
    if component["candidate_id"] not in CANDIDATES:
        raise ComponentDesignError("candidate_id must be column_wheel or cam_lever")
    if component["unit"] != "mm":
        raise ComponentDesignError("component geometry unit must be mm")
    if component["geometry_type"] not in GEOMETRY_TYPES:
        raise ComponentDesignError("unsupported geometry_type")
    _positive(component.get("z_thickness_mm"), "z_thickness_mm")
    if component["geometry_type"] == "circle":
        _positive(component.get("radius_mm"), "radius_mm")
    elif component["geometry_type"] == "annulus":
        outer = _positive(component.get("outer_radius_mm"), "outer_radius_mm")
        inner = _positive(component.get("inner_radius_mm"), "inner_radius_mm")
        if inner >= outer:
            raise ComponentDesignError("annulus inner radius must be less than outer radius")
    else:
        validate_profile(component.get("points"), component["evidence_id"], component["source_revision"], component["component_id"])
    return {"component_id": component["component_id"], "candidate_id": component["candidate_id"],
            "role": component["role"], "geometry_valid": True,
            "manufacturing_release_authorized": False}

def validate_candidate_definition(definition):
    if not isinstance(definition, dict):
        raise ComponentDesignError("definition must be an object")
    for f in ("candidate_id", "configuration_revision", "evidence_id", "source_revision"):
        _text(definition.get(f), f"definition.{f}")
    if definition["candidate_id"] not in CANDIDATES:
        raise ComponentDesignError("candidate_id must be column_wheel or cam_lever")
    components = definition.get("components")
    if not isinstance(components, list) or not components:
        raise ComponentDesignError("components must be a non-empty list")
    ids = [c.get("component_id") for c in components]
    if any(not isinstance(x, str) or not x.strip() for x in ids) or len(ids) != len(set(ids)):
        raise ComponentDesignError("component IDs must be present and unique")
    roles = set()
    for c in components:
        result = validate_component(c)
        if result["candidate_id"] != definition["candidate_id"]:
            raise ComponentDesignError("component candidate does not match definition")
        roles.add(c["role"])
    required = (REQUIRED_CW_ROLES if definition["candidate_id"] == "column_wheel" else REQUIRED_CL_ROLES) | REQUIRED_SHARED_ROLES
    missing = required - roles
    if missing:
        raise ComponentDesignError(f"required component roles missing: {sorted(missing)}")
    interfaces = definition.get("interfaces")
    if not isinstance(interfaces, list) or not interfaces:
        raise ComponentDesignError("interfaces must be a non-empty list")
    iids = [i.get("interface_id") for i in interfaces]
    if any(not isinstance(x, str) or not x.strip() for x in iids) or len(iids) != len(set(iids)):
        raise ComponentDesignError("interface IDs must be present and unique")
    for i in interfaces:
        for f in ("interface_id", "interface_type", "from_component_id", "to_component_id", "definition", "evidence_id", "source_revision"):
            _text(i.get(f), f"interface.{f}")
        if i["from_component_id"] not in ids or i["to_component_id"] not in ids or i["from_component_id"] == i["to_component_id"]:
            raise ComponentDesignError("interface endpoints must be distinct declared components")
    kinds = {i["interface_type"] for i in interfaces}
    missing_i = REQUIRED_INTERFACES - kinds
    if missing_i:
        raise ComponentDesignError(f"required interfaces missing: {sorted(missing_i)}")
    return {"candidate_id": definition["candidate_id"], "component_count": len(components),
            "interface_count": len(interfaces), "roles": sorted(roles),
            "definition_complete_for_review": True, "winner_selected": False,
            "design_frozen": False, "manufacturing_release_authorized": False}

def validate_spring_curve(samples, displacement_unit, force_unit, evidence_id, source_revision):
    """Validate measured/approved force-deflection points without fitting a spring."""
    _text(evidence_id, "evidence_id"); _text(source_revision, "source_revision")
    _text(displacement_unit, "displacement_unit"); _text(force_unit, "force_unit")
    if not isinstance(samples, list) or len(samples) < 2:
        raise ComponentDesignError("spring curve requires at least two measured points")
    parsed = []
    for i, p in enumerate(samples):
        x = _num(p.get("displacement"), f"samples[{i}].displacement")
        y = _num(p.get("force"), f"samples[{i}].force")
        parsed.append((x, y))
    if any(b[0] <= a[0] for a, b in zip(parsed, parsed[1:])):
        raise ComponentDesignError("spring displacement must strictly increase")
    return {"sample_count": len(parsed), "displacement_unit": displacement_unit,
            "force_unit": force_unit, "evidence_id": evidence_id,
            "source_revision": source_revision, "spring_rate_fitted": False,
            "design_approved": False}

def validate_interlock_definition(record):
    for f in ("interlock_id", "blocked_member_id", "blocking_member_id",
              "blocked_state", "required_safe_state", "evidence_id", "source_revision"):
        _text(record.get(f), f"interlock.{f}")
    if record["blocked_member_id"] == record["blocking_member_id"]:
        raise ComponentDesignError("interlock members must be distinct")
    if record["blocked_state"] != "running":
        raise ComponentDesignError("running state must be explicitly protected")
    return {"interlock_id": record["interlock_id"], "functional_definition_complete": True,
            "physical_interlock_verified": False, "test_evidence_required": True}

def _scad_component(c):
    validate_component(c)
    if c["geometry_type"] == "circle":
        shape = f'cylinder(h={c["z_thickness_mm"]}, r={c["radius_mm"]}, $fn=96);'
    elif c["geometry_type"] == "annulus":
        shape = (f'difference() {{ cylinder(h={c["z_thickness_mm"]}, r={c["outer_radius_mm"]}, $fn=96); '
                 f'translate([0,0,-0.01]) cylinder(h={c["z_thickness_mm"]}+0.02, r={c["inner_radius_mm"]}, $fn=96); }}')
    else:
        pts = ",".join(f'[{x},{y}]' for x,y in c["points"])
        shape = f'linear_extrude(height={c["z_thickness_mm"]}) polygon(points=[{pts}]);'
    return f'module {c["component_id"]}() {{ {shape} }}'

def generate_openscad(definition):
    """Generate source only from explicit geometry; caller must use SCAD-safe IDs."""
    validate_candidate_definition(definition)
    modules = []
    for c in definition["components"]:
        if not c["component_id"].replace("_", "").isalnum() or c["component_id"][0].isdigit():
            raise ComponentDesignError("component_id must be a SCAD-safe identifier")
        modules.append(_scad_component(c))
    return ("// WP-54 envelope/source geometry only; not a manufacturing drawing.\n"
            f"// Candidate: {definition['candidate_id']} | revision: {definition['configuration_revision']}\n"
            + "\n".join(modules) + "\n")
