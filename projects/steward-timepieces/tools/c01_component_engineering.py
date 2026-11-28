"""WP-62 evidence-gated chronograph component engineering register.

No C-01 dimensions, materials, profiles or tolerances are defaulted. The model
validates controlled component definitions and performs only explicit-input
dimensional screening.
"""
from __future__ import annotations
import math

class ComponentEngineeringError(ValueError):
    pass

CANDIDATES = {"CW", "CL"}
REQUIRED_ROLES = {
    "drive_source", "drive_coupling", "clutch", "central_seconds",
    "minute_counter", "hour_counter", "stopped_retention",
    "reset_hammer", "heart_cam", "pusher", "running_reset_interlock",
    "main_plate", "bridge_support", "bearing_support"
}
CONTROL_ROLE = {"CW": "column_wheel_control", "CL": "cam_lever_control"}
FAMILIES = {
    "drive_train", "clutch", "arbor", "counter", "retention",
    "control", "reset", "interlock", "structure", "bearing", "external_input"
}
UNITS = {"mm", "deg", "N", "N_mm", "N_per_mm", "g", "mm3", "mg"}

def _text(v, name):
    if not isinstance(v, str) or not v.strip():
        raise ComponentEngineeringError(f"{name} is required")
    return v

def _number(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ComponentEngineeringError(f"{name} must be finite numeric")
    return float(v)

def _nonnegative(v, name):
    x = _number(v, name)
    if x < 0:
        raise ComponentEngineeringError(f"{name} must be non-negative")
    return x

def dimension_interval(nominal, lower_deviation, upper_deviation, require_positive=False):
    n = _number(nominal, "nominal")
    lo = _nonnegative(lower_deviation, "lower_deviation")
    hi = _nonnegative(upper_deviation, "upper_deviation")
    lower, upper = n-lo, n+hi
    if require_positive and lower <= 0:
        raise ComponentEngineeringError("positive dimension interval must remain above zero")
    return {"minimum": lower, "nominal": n, "maximum": upper}

def journal_clearance(*, shaft_min_mm, shaft_max_mm, bore_min_mm, bore_max_mm,
                      evidence_id, source_revision):
    """Worst-case diametral clearance from explicit finished-size limits."""
    for k, v in (("shaft_min_mm", shaft_min_mm), ("shaft_max_mm", shaft_max_mm),
                 ("bore_min_mm", bore_min_mm), ("bore_max_mm", bore_max_mm)):
        _number(v, k)
        if v <= 0:
            raise ComponentEngineeringError(f"{k} must be positive")
    if shaft_min_mm > shaft_max_mm or bore_min_mm > bore_max_mm:
        raise ComponentEngineeringError("minimum size cannot exceed maximum size")
    _text(evidence_id, "evidence_id")
    _text(source_revision, "source_revision")
    return {
        "minimum_diametral_clearance_mm": bore_min_mm-shaft_max_mm,
        "maximum_diametral_clearance_mm": bore_max_mm-shaft_min_mm,
        "evidence_id": evidence_id, "source_revision": source_revision,
        "physical_fit_certified": False
    }

def validate_dimension_register(rows, component_id):
    if not isinstance(rows, list):
        raise ComponentEngineeringError(f"{component_id}.dimensions must be a list")
    ids = []
    evaluated = []
    for row in rows:
        did = _text(row.get("dimension_id"), "dimension_id")
        ids.append(did)
        for f in ("characteristic", "unit", "evidence_id", "source_revision", "drawing_ref"):
            _text(row.get(f), f"{did}.{f}")
        if row["unit"] not in UNITS:
            raise ComponentEngineeringError(f"{did} has unsupported unit")
        if row.get("status") not in ("tbd", "candidate", "reviewed", "approved"):
            raise ComponentEngineeringError(f"{did} has invalid status")
        interval = dimension_interval(row.get("nominal"), row.get("lower_deviation"),
                                      row.get("upper_deviation"),
                                      row.get("require_positive") is True)
        evaluated.append({"dimension_id": did, **interval, "status": row["status"]})
    if len(ids) != len(set(ids)):
        raise ComponentEngineeringError(f"{component_id} dimension IDs must be unique")
    return evaluated

def validate_component(component, candidate_id):
    cid = _text(component.get("component_id"), "component_id")
    role = _text(component.get("role"), f"{cid}.role")
    family = _text(component.get("family"), f"{cid}.family")
    if family not in FAMILIES:
        raise ComponentEngineeringError(f"{cid} has unsupported engineering family")
    scope = component.get("candidate_scope")
    if scope not in ("shared", "CW", "CL"):
        raise ComponentEngineeringError(f"{cid} candidate_scope must be shared, CW or CL")
    if scope not in ("shared", candidate_id):
        raise ComponentEngineeringError(f"{cid} is assigned to the wrong candidate")
    for f in ("function", "geometry_definition", "material_status", "drawing_ref",
              "evidence_id", "source_revision"):
        _text(component.get(f), f"{cid}.{f}")
    for f, allowed in (
        ("geometry_status", {"not_started", "concept", "candidate", "reviewed", "approved"}),
        ("material_status", {"tbd", "candidate", "reviewed", "approved"}),
        ("manufacturing_status", {"not_started", "process_study", "candidate", "reviewed", "approved"})
    ):
        if component.get(f) not in allowed:
            raise ComponentEngineeringError(f"{cid}.{f} has invalid status")
    dimensions = validate_dimension_register(component.get("dimensions", []), cid)
    interfaces = component.get("interface_refs", [])
    if not isinstance(interfaces, list):
        raise ComponentEngineeringError(f"{cid}.interface_refs must be a list")
    for ref in interfaces:
        _text(ref.get("interface_id"), f"{cid}.interface_id")
        _text(ref.get("source_revision"), f"{cid}.interface_source_revision")
    analyses = component.get("analysis_refs", [])
    if not isinstance(analyses, list):
        raise ComponentEngineeringError(f"{cid}.analysis_refs must be a list")
    for ref in analyses:
        for f in ("analysis_id", "method", "evidence_id", "source_revision", "status"):
            _text(ref.get(f), f"{cid}.analysis.{f}")
    return {
        "component_id": cid, "role": role, "family": family, "candidate_scope": scope,
        "dimension_count": len(dimensions),
        "approved_dimension_count": sum(d["status"] == "approved" for d in dimensions),
        "geometry_defined": component["geometry_status"] in ("candidate", "reviewed", "approved"),
        "geometry_approved": component["geometry_status"] == "approved",
        "material_approved": component["material_status"] == "approved",
        "manufacturing_approved": component["manufacturing_status"] == "approved",
        "dimension_results": dimensions
    }

def evaluate_candidate(candidate):
    cid = candidate.get("candidate_id")
    if cid not in CANDIDATES:
        raise ComponentEngineeringError("candidate_id must be CW or CL")
    for f in ("configuration_revision", "requirements_revision", "datum_revision",
              "interface_baseline_revision", "evidence_id", "source_revision", "owner"):
        _text(candidate.get(f), f"candidate.{f}")
    rows = candidate.get("components")
    if not isinstance(rows, list) or not rows:
        raise ComponentEngineeringError(f"{cid}.components must be non-empty")
    results = [validate_component(c, cid) for c in rows]
    ids = [r["component_id"] for r in results]
    if len(ids) != len(set(ids)):
        raise ComponentEngineeringError(f"{cid} component IDs must be unique")
    roles = {r["role"] for r in results}
    missing = sorted((REQUIRED_ROLES | {CONTROL_ROLE[cid]}) - roles)
    if missing:
        raise ComponentEngineeringError(f"{cid} missing component roles: {missing}")
    interfaces = candidate.get("interfaces")
    if not isinstance(interfaces, list) or not interfaces:
        raise ComponentEngineeringError(f"{cid}.interfaces must be non-empty")
    interface_ids = [_text(x.get("interface_id"), "interface_id") for x in interfaces]
    if len(interface_ids) != len(set(interface_ids)):
        raise ComponentEngineeringError(f"{cid} interface IDs must be unique")
    for x in interfaces:
        for f in ("interface_type", "from_component_id", "to_component_id",
                  "definition", "evidence_id", "source_revision"):
            _text(x.get(f), f"interface.{f}")
        if x["from_component_id"] not in ids or x["to_component_id"] not in ids:
            raise ComponentEngineeringError("interface references undeclared component")
        if x["from_component_id"] == x["to_component_id"]:
            raise ComponentEngineeringError("interface endpoints must differ")
    decisions = candidate.get("open_decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ComponentEngineeringError("open_decisions must be retained")
    for d in decisions:
        for f in ("decision_id", "topic", "status", "evidence_id"):
            _text(d.get(f), f"decision.{f}")
    return {
        "candidate_id": cid, "component_count": len(results),
        "interface_count": len(interfaces), "component_results": results,
        "missing_roles": [], "all_roles_present": True,
        "geometry_approved_component_count": sum(r["geometry_approved"] for r in results),
        "material_approved_component_count": sum(r["material_approved"] for r in results),
        "components_with_dimensions": sum(r["dimension_count"] > 0 for r in results),
        "physical_design_complete": False, "prototype_release_authorized": False
    }

def evaluate_engineering_package(packet):
    for f in ("package_id", "revision", "evidence_id", "source_revision", "owner"):
        _text(packet.get(f), f"package.{f}")
    baseline = packet.get("common_baseline")
    if not isinstance(baseline, dict):
        raise ComponentEngineeringError("common_baseline required")
    for f in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
        _text(baseline.get(f), f"common_baseline.{f}")
    candidates = packet.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != CANDIDATES:
        raise ComponentEngineeringError("separate CW and CL component packages required")
    out = {}
    for cid in ("CW", "CL"):
        c = candidates[cid]
        if c.get("candidate_id") != cid:
            raise ComponentEngineeringError("candidate key mismatch")
        for f in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
            if c.get(f) != baseline[f]:
                raise ComponentEngineeringError(f"{cid} baseline mismatch: {f}")
        out[cid] = evaluate_candidate(c)
    return {
        "package_id": packet["package_id"], "candidate_results": out,
        "common_baseline_match": True, "architecture_selected": False,
        "design_frozen": False, "physical_fit_certified": False,
        "manufacturing_release_authorized": False
    }
