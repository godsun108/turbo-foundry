"""WP-61 integrated chronograph mechanism assembly and CAD handoff.

Composes the explicit neutral component geometry and CAD source generator from
WP-59 with WP-41 functional roles/interfaces. No C-01 geometry is supplied here.
"""
from __future__ import annotations
try:
    from c01_control_cad_assembly import (
        AssemblyDefinitionError, evaluate_assembly_set, generate_assembly_scad
    )
except ImportError:
    from .c01_control_cad_assembly import (
        AssemblyDefinitionError, evaluate_assembly_set, generate_assembly_scad
    )

class IntegratedChronographError(ValueError):
    pass

COMMON_ROLES = {
    "drive_source", "drive_coupling", "clutch", "central_seconds",
    "minute_counter", "hour_counter", "stopped_retention", "reset_hammer",
    "heart_cam", "pusher", "running_reset_interlock", "main_plate",
    "bridge_support", "bearing_support"
}
CANDIDATE_CONTROL_ROLE = {"CW": "column_wheel_control", "CL": "cam_lever_control"}
REQUIRED_INTERFACES = {
    "drive_coupling", "seconds_output", "minute_counter_drive", "hour_counter_drive",
    "stopped_retention_control", "clutch_control", "reset_hammer_actuation",
    "seconds_reset", "minute_counter_reset", "hour_counter_reset",
    "running_reset_interlock", "pusher_input", "control_indexing",
    "structural_support", "bearing_support"
}

def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise IntegratedChronographError(f"{label} must be non-empty text")
    return value

def _unique(records, key, label):
    if not isinstance(records, list) or not records:
        raise IntegratedChronographError(f"{label} must be a non-empty list")
    values = [_text(r.get(key), f"{label}.{key}") for r in records]
    if len(values) != len(set(values)):
        raise IntegratedChronographError(f"{label}.{key} values must be unique")
    return set(values)

def validate_integrated_candidate(candidate):
    cid = candidate.get("candidate_id")
    if cid not in ("CW", "CL"):
        raise IntegratedChronographError("candidate_id must be CW or CL")
    # WP-59 owns geometry, global placements, parent hierarchy and mate screening.
    try:
        base = evaluate_assembly_set({
            "assembly_set_id": "WP61-single-candidate-check",
            "revision": "validation-only",
            "evidence_id": candidate.get("evidence_id"),
            "source_revision": candidate.get("source_revision"),
            "owner": candidate.get("owner"),
            "common_baseline": {
                "requirements_revision": candidate.get("requirements_revision"),
                "datum_revision": candidate.get("datum_revision"),
                "interface_baseline_revision": candidate.get("interface_baseline_revision")
            },
            "candidates": {
                "CW": candidate if cid == "CW" else _placeholder_candidate("CW", candidate),
                "CL": candidate if cid == "CL" else _placeholder_candidate("CL", candidate)
            }
        })
    except (AssemblyDefinitionError, KeyError, TypeError) as exc:
        raise IntegratedChronographError(f"WP-59 assembly validation failed: {exc}") from exc
    components = candidate.get("components")
    by_id = {c["component_id"]: c for c in components}
    roles = set()
    for c in components:
        roles.add(c["role"])
        extras = c.get("functional_roles", [])
        if not isinstance(extras, list):
            raise IntegratedChronographError(f"{c['component_id']}.functional_roles must be a list")
        for role in extras:
            roles.add(_text(role, f"{c['component_id']}.functional_roles"))
    required_roles = COMMON_ROLES | {CANDIDATE_CONTROL_ROLE[cid]}
    missing_roles = sorted(required_roles - roles)
    if missing_roles:
        raise IntegratedChronographError(f"{cid} missing functional roles: {missing_roles}")
    interfaces = candidate.get("interfaces")
    interface_ids = _unique(interfaces, "interface_id", "interface")
    types = set()
    for item in interfaces:
        for field in ("interface_type", "from_component_id", "to_component_id",
                      "definition", "evidence_id", "source_revision"):
            _text(item.get(field), f"interface.{field}")
        a, b = item["from_component_id"], item["to_component_id"]
        if a == b or a not in by_id or b not in by_id:
            raise IntegratedChronographError("interface endpoints must be distinct declared components")
        types.add(item["interface_type"])
    missing_interfaces = sorted(REQUIRED_INTERFACES - types)
    if missing_interfaces:
        raise IntegratedChronographError(f"{cid} missing functional interfaces: {missing_interfaces}")
    decisions = candidate.get("open_decisions")
    if not isinstance(decisions, list) or not decisions:
        raise IntegratedChronographError("open_decisions must preserve unresolved decisions")
    decision_ids = _unique(decisions, "decision_id", "open_decisions")
    for d in decisions:
        for field in ("topic", "status", "evidence_id"):
            _text(d.get(field), f"decision.{field}")
        if d["status"] not in ("open", "under_review", "approved", "deferred"):
            raise IntegratedChronographError("invalid open decision status")
    return {
        "candidate_id": cid, "component_count": len(components),
        "interface_count": len(interfaces), "mate_count": len(candidate.get("mates", [])),
        "functional_roles_present": sorted(roles),
        "functional_interfaces_present": sorted(types),
        "missing_roles": [], "missing_interfaces": [],
        "open_decision_ids": sorted(decision_ids),
        "wp59_geometry_and_mates_validated": True,
        "physical_mechanism_verified": False,
        "continuous_clearance_certified": False,
        "prototype_release_authorized": False
    }

def _placeholder_candidate(cid, source):
    # Internal structural adapter only; it reuses supplied geometry and does not
    # create geometry. Candidate-specific control role is intentionally absent.
    return {
        "candidate_id": cid,
        "configuration_revision": "validation-adapter-"+cid,
        "requirements_revision": source.get("requirements_revision"),
        "datum_revision": source.get("datum_revision"),
        "interface_baseline_revision": source.get("interface_baseline_revision"),
        "evidence_id": source.get("evidence_id"),
        "source_revision": source.get("source_revision"),
        "owner": source.get("owner"),
        "components": source.get("components"),
        "mates": source.get("mates", [])
    }

def evaluate_integrated_package(packet):
    for field in ("assembly_set_id", "revision", "evidence_id", "source_revision", "owner"):
        _text(packet.get(field), "package."+field)
    baseline = packet.get("common_baseline")
    if not isinstance(baseline, dict):
        raise IntegratedChronographError("common_baseline required")
    for field in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
        _text(baseline.get(field), "common_baseline."+field)
    candidates = packet.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != {"CW", "CL"}:
        raise IntegratedChronographError("separate CW and CL candidate packages are required")
    results = {}
    for cid in ("CW", "CL"):
        c = candidates[cid]
        if c.get("candidate_id") != cid:
            raise IntegratedChronographError("candidate key and candidate_id mismatch")
        for field in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
            if c.get(field) != baseline[field]:
                raise IntegratedChronographError(f"{cid} common baseline mismatch: {field}")
        results[cid] = validate_integrated_candidate(c)
    return {
        "assembly_set_id": packet["assembly_set_id"],
        "candidate_results": results, "common_baseline_match": True,
        "architecture_selected": False, "clutch_selected": False,
        "design_frozen": False, "physical_fit_certified": False,
        "continuous_motion_clearance_certified": False,
        "manufacturing_release_authorized": False
    }

def generate_integrated_cad_sources(packet):
    evaluation = evaluate_integrated_package(packet)
    outputs = {}
    for cid in ("CW", "CL"):
        candidate = packet["candidates"][cid]
        try:
            source = generate_assembly_scad(candidate)
        except AssemblyDefinitionError as exc:
            raise IntegratedChronographError(f"{cid} CAD source generation failed: {exc}") from exc
        outputs[cid] = (
            "// STEWARD C-01 WP-61 integrated chronograph assembly envelope\n"
            "// Source generated only from supplied WP-59 neutral geometry.\n"
            f"// Assembly set: {packet['assembly_set_id']} | revision: {packet['revision']}\n"
            f"// Candidate: {cid} | architecture intentionally unselected\n"
            f"// WP-61 evidence: {packet['evidence_id']} | source: {packet['source_revision']}\n"
            "// Functional interface registers are controlled separately; no kinematic solver.\n"
            + source
        )
    return {
        "evaluation": evaluation,
        "cad_sources": outputs,
        "rendered": False, "physical_fit_certified": False,
        "manufacturing_release_authorized": False
    }
