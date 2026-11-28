"""WP-59 evidence-gated parametric CAD assembly model for C-01 control candidates.

Coordinates are explicit global placements in the WP-14/WP-20 XY and WP-21 M0 frame.
Parent links organize the assembly tree; they do not implicitly transform child poses.
"""
from __future__ import annotations
import math
import re

class AssemblyDefinitionError(ValueError):
    pass

SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
CANDIDATES = {"CW", "CL"}
GEOMETRY_TYPES = {"cylinder", "annulus", "extruded_polygon"}
MATE_TYPES = {"coaxial", "planar", "fixed_distance", "angular", "contact_reference"}

def _text(v, name):
    if not isinstance(v, str) or not v.strip():
        raise AssemblyDefinitionError(f"{name} must be non-empty text")
    return v

def _id(v, name):
    _text(v, name)
    if not SAFE_ID.fullmatch(v):
        raise AssemblyDefinitionError(f"{name} must be a safe identifier")
    return v

def _num(v, name):
    if isinstance(v, bool):
        raise AssemblyDefinitionError(f"{name} must be finite numeric")
    try:
        x = float(v)
    except (TypeError, ValueError) as exc:
        raise AssemblyDefinitionError(f"{name} must be finite numeric") from exc
    if not math.isfinite(x):
        raise AssemblyDefinitionError(f"{name} must be finite numeric")
    return x

def _positive(v, name):
    x = _num(v, name)
    if x <= 0:
        raise AssemblyDefinitionError(f"{name} must be positive")
    return x

def _vec(v, keys, name):
    if not isinstance(v, dict):
        raise AssemblyDefinitionError(f"{name} must be an object")
    return tuple(_num(v.get(k), f"{name}.{k}") for k in keys)

def _pose(pose, name):
    return {
        "translation": _vec(pose.get("translation_mm"), ("x", "y", "z"), name+".translation_mm"),
        "rotation": _vec(pose.get("rotation_deg"), ("x", "y", "z"), name+".rotation_deg"),
    }

def _validate_geometry(g, name):
    if not isinstance(g, dict):
        raise AssemblyDefinitionError(f"{name}.geometry must be an object")
    kind = g.get("type")
    if kind not in GEOMETRY_TYPES:
        raise AssemblyDefinitionError(f"{name} has unsupported geometry type")
    p = g.get("parameters")
    if not isinstance(p, dict):
        raise AssemblyDefinitionError(f"{name}.geometry.parameters required")
    if kind == "cylinder":
        _positive(p.get("radius_mm"), name+".radius_mm")
        _positive(p.get("height_mm"), name+".height_mm")
    elif kind == "annulus":
        outer = _positive(p.get("outer_radius_mm"), name+".outer_radius_mm")
        inner = _positive(p.get("inner_radius_mm"), name+".inner_radius_mm")
        if inner >= outer:
            raise AssemblyDefinitionError(f"{name} annulus inner radius must be smaller")
        _positive(p.get("height_mm"), name+".height_mm")
    else:
        pts = p.get("outline_xy_mm")
        if not isinstance(pts, list) or len(pts) < 3:
            raise AssemblyDefinitionError(f"{name} polygon requires at least three points")
        clean = []
        for i, pt in enumerate(pts):
            if not isinstance(pt, (list, tuple)) or len(pt) != 2:
                raise AssemblyDefinitionError(f"{name} polygon point must be XY")
            clean.append((_num(pt[0], f"{name}.x{i}"), _num(pt[1], f"{name}.y{i}")))
        if len(set(clean)) != len(clean):
            raise AssemblyDefinitionError(f"{name} polygon points must be unique")
        area = sum(clean[i][0]*clean[(i+1)%len(clean)][1] -
                    clean[(i+1)%len(clean)][0]*clean[i][1] for i in range(len(clean))) / 2
        if abs(area) <= 1e-12:
            raise AssemblyDefinitionError(f"{name} polygon area must be nonzero")
        _positive(p.get("height_mm"), name+".height_mm")
    return kind

def _axis_direction(rotation):
    # Local +Z axis after explicit Euler rotations, applied X then Y then Z.
    rx, ry, rz = (math.radians(v) for v in rotation)
    # Rz * Ry * Rx applied to (0,0,1).
    return (math.sin(ry)*math.cos(rz) + math.sin(rx)*math.sin(rz)*math.cos(ry),
            math.sin(ry)*math.sin(rz) - math.sin(rx)*math.cos(ry),
            math.cos(rx)*math.cos(ry))

def _distance(a, b):
    return math.dist(a, b)

def validate_components(components):
    if not isinstance(components, list) or not components:
        raise AssemblyDefinitionError("components must be a non-empty list")
    ids = []
    by_id = {}
    for c in components:
        if not isinstance(c, dict):
            raise AssemblyDefinitionError("component record must be an object")
        cid = _id(c.get("component_id"), "component_id")
        ids.append(cid)
        for field in ("role", "evidence_id", "source_revision", "drawing_ref"):
            _text(c.get(field), f"{cid}.{field}")
        if c.get("status") not in ("tbd", "candidate", "reviewed", "approved"):
            raise AssemblyDefinitionError(f"{cid} has invalid geometry status")
        _validate_geometry(c.get("geometry"), cid)
        pose = _pose(c.get("pose", {}), cid+".pose")
        parent = c.get("parent_id")
        if parent is not None:
            _id(parent, cid+".parent_id")
        by_id[cid] = {**c, "_pose": pose}
    if len(ids) != len(set(ids)):
        raise AssemblyDefinitionError("component IDs must be unique")
    for cid, c in by_id.items():
        parent = c.get("parent_id")
        if parent is not None and parent not in by_id:
            raise AssemblyDefinitionError(f"{cid} references unknown parent")
        if parent == cid:
            raise AssemblyDefinitionError(f"{cid} cannot parent itself")
    # Detect hierarchy cycles; hierarchy is organizational, not a pose transform.
    for start in by_id:
        seen, node = set(), start
        while node is not None:
            if node in seen:
                raise AssemblyDefinitionError("assembly parent hierarchy contains a cycle")
            seen.add(node)
            node = by_id[node].get("parent_id")
    return by_id

def validate_mates(mates, components):
    if not isinstance(mates, list):
        raise AssemblyDefinitionError("mates must be a list")
    ids = []
    results = []
    for m in mates:
        mid = _id(m.get("mate_id"), "mate_id")
        ids.append(mid)
        kind = m.get("type")
        if kind not in MATE_TYPES:
            raise AssemblyDefinitionError(f"{mid} has unsupported mate type")
        a, b = m.get("component_a"), m.get("component_b")
        if a not in components or b not in components or a == b:
            raise AssemblyDefinitionError(f"{mid} endpoints must be distinct assembly components")
        for f in ("evidence_id", "source_revision", "definition"):
            _text(m.get(f), f"{mid}.{f}")
        pa, pb = components[a]["_pose"], components[b]["_pose"]
        delta = _distance(pa["translation"], pb["translation"])
        result = {"mate_id": mid, "type": kind, "component_a": a, "component_b": b,
                  "evidence_id": m["evidence_id"], "source_revision": m["source_revision"]}
        if kind == "coaxial":
            tol = _positive(m.get("tolerance_mm"), mid+".tolerance_mm")
            da, db = _axis_direction(pa["rotation"]), _axis_direction(pb["rotation"])
            parallel_error = math.sqrt(sum((da[i]-db[i])**2 for i in range(3)))
            # Axis line separation, invariant to translation along axis A.
            cross = (da[1]*(pb["translation"][2]-pa["translation"][2])-da[2]*(pb["translation"][1]-pa["translation"][1]),
                     da[2]*(pb["translation"][0]-pa["translation"][0])-da[0]*(pb["translation"][2]-pa["translation"][2]),
                     da[0]*(pb["translation"][1]-pa["translation"][1])-da[1]*(pb["translation"][0]-pa["translation"][0]))
            offset = math.sqrt(sum(x*x for x in cross))
            result.update(axis_direction_error=parallel_error, axis_offset_mm=offset,
                          within_tolerance=parallel_error <= tol and offset <= tol)
        elif kind == "planar":
            tol = _positive(m.get("tolerance_mm"), mid+".tolerance_mm")
            result.update(axial_separation_mm=abs(pa["translation"][2]-pb["translation"][2]),
                          within_tolerance=abs(pa["translation"][2]-pb["translation"][2]) <= tol)
        elif kind == "fixed_distance":
            target = _positive(m.get("target_distance_mm"), mid+".target_distance_mm")
            tol = _positive(m.get("tolerance_mm"), mid+".tolerance_mm")
            result.update(actual_distance_mm=delta, target_distance_mm=target,
                          error_mm=delta-target, within_tolerance=abs(delta-target) <= tol)
        elif kind == "angular":
            target = _num(m.get("target_angle_deg"), mid+".target_angle_deg")
            tol = _positive(m.get("tolerance_deg"), mid+".tolerance_deg")
            actual = pa["rotation"][2]-pb["rotation"][2]
            error = (actual-target+180) % 360 - 180
            result.update(actual_relative_angle_deg=actual, target_angle_deg=target,
                          error_deg=error, within_tolerance=abs(error) <= tol)
        else:
            _text(m.get("contact_feature_a"), mid+".contact_feature_a")
            _text(m.get("contact_feature_b"), mid+".contact_feature_b")
            result.update(contact_geometry_verified=False, within_tolerance=None,
                          limitation="reference-only mate; contact is not solved")
        results.append(result)
    if len(ids) != len(set(ids)):
        raise AssemblyDefinitionError("mate IDs must be unique")
    return results

def evaluate_candidate(candidate):
    cid = candidate.get("candidate_id")
    if cid not in CANDIDATES:
        raise AssemblyDefinitionError("candidate_id must be CW or CL")
    for f in ("configuration_revision", "requirements_revision", "datum_revision",
              "interface_baseline_revision", "evidence_id", "source_revision", "owner"):
        _text(candidate.get(f), f"candidate.{f}")
    components = validate_components(candidate.get("components"))
    mates = validate_mates(candidate.get("mates", []), components)
    unresolved = [k for k, v in components.items() if v.get("status") != "approved"]
    return {
        "candidate_id": cid, "component_count": len(components), "mate_count": len(mates),
        "mate_results": mates, "unapproved_component_ids": unresolved,
        "all_component_geometry_approved": not unresolved,
        "all_numeric_mates_within_tolerance": all(
            x.get("within_tolerance") is True for x in mates if x["type"] != "contact_reference"),
        "contact_references_present": sum(x["type"] == "contact_reference" for x in mates),
        "physical_fit_certified": False, "swept_motion_clearance_certified": False,
        "manufacturing_release_authorized": False,
        "limitations": [
            "parent links are organizational; all poses are explicit global placements",
            "primitive solids are neutral envelopes, not detailed teeth, cams, springs or contact surfaces",
            "mate checks are nominal mathematical screens only",
            "no swept-solid, continuous collision, tolerance, load, deflection, wear or fatigue analysis",
            "OpenSCAD output is source generation only; no rendering or physical fit certification"
        ]
    }

def evaluate_assembly_set(packet):
    for f in ("assembly_set_id", "revision", "evidence_id", "source_revision", "owner"):
        _text(packet.get(f), f"assembly_set.{f}")
    baseline = packet.get("common_baseline")
    if not isinstance(baseline, dict):
        raise AssemblyDefinitionError("common_baseline required")
    for f in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
        _text(baseline.get(f), "common_baseline."+f)
    candidates = packet.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != CANDIDATES:
        raise AssemblyDefinitionError("separate CW and CL assembly packages are both required")
    results = {}
    for cid in sorted(CANDIDATES):
        c = candidates[cid]
        if c.get("candidate_id") != cid:
            raise AssemblyDefinitionError("candidate key and candidate_id mismatch")
        for field in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
            if c.get(field) != baseline[field]:
                raise AssemblyDefinitionError(f"{cid} common baseline mismatch: {field}")
        results[cid] = evaluate_candidate(c)
    return {
        "assembly_set_id": packet["assembly_set_id"], "candidate_results": results,
        "common_baseline_match": True, "physical_equivalence_proven": False,
        "architecture_selected": False, "clutch_selected": False, "design_frozen": False,
        "manufacturing_release_authorized": False
    }

def _f(value):
    return format(float(value), ".12g")

def _solid_scad(c):
    g, p = c["geometry"], c["geometry"]["parameters"]
    if g["type"] == "cylinder":
        return f"cylinder(h={_f(p['height_mm'])},r={_f(p['radius_mm'])},center=true);"
    if g["type"] == "annulus":
        return ("difference() { "
                f"cylinder(h={_f(p['height_mm'])},r={_f(p['outer_radius_mm'])},center=true); "
                f"cylinder(h={_f(float(p['height_mm'])+0.02)},r={_f(p['inner_radius_mm'])},center=true); }}")
    points = "[" + ",".join("["+_f(x)+","+_f(y)+"]" for x,y in p["outline_xy_mm"]) + "]"
    return f"linear_extrude(height={_f(p['height_mm'])},center=true) polygon(points={points});"

def generate_assembly_scad(candidate):
    components = validate_components(candidate.get("components"))
    validate_mates(candidate.get("mates", []), components)
    cid = candidate.get("candidate_id")
    if cid not in CANDIDATES:
        raise AssemblyDefinitionError("candidate_id must be CW or CL")
    lines = [
        "// STEWARD C-01 WP-59 neutral parametric assembly envelope",
        "// Candidate visualization source only; not a manufacturing model.",
        f"// Candidate: {cid}",
        f"// Configuration: {candidate['configuration_revision']}",
        f"// Evidence: {candidate['evidence_id']}",
        f"// Source revision: {candidate['source_revision']}",
        "$fn=96;", ""
    ]
    for key, c in components.items():
        t, r = c["_pose"]["translation"], c["_pose"]["rotation"]
        lines += [f"// {key} | {c['role']} | drawing {c['drawing_ref']} | evidence {c['evidence_id']} | source {c['source_revision']}",
                  f"module part_{key}() {{",
                  f"  translate([{','.join(_f(x) for x in t)}]) rotate([{','.join(_f(x) for x in r)}]) {{",
                  f"    {_solid_scad(c)}", "  }", "}", ""]
    lines += ["// Explicit assembly calls; all component poses are global in the declared datum frame."]
    for key in components:
        lines.append(f"part_{key}();")
    return "\n".join(lines) + "\n"
