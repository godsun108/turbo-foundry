"""Integrated C-01 bearing and structural support architecture checks.

Composes WP-21 structural member references, WP-23 arbor/support/gear registers,
and WP-22 CAD bore input validation. This is a register/interface validator,
not a bearing design, structural analysis or physical-fit certification.
"""
from __future__ import annotations

from math import isfinite
from typing import Any

try:
    from c01_arbor_coordinates import cad_bore_register, evaluate_candidate as evaluate_arbors
except ImportError:
    from .c01_arbor_coordinates import cad_bore_register, evaluate_candidate as evaluate_arbors

try:
    from c01_cad_skeleton import validate_config as validate_cad_config
except ImportError:
    from .c01_cad_skeleton import validate_config as validate_cad_config


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be finite numeric data")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite numeric data") from exc
    if not isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _unique(items: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [item.get(field) for item in items]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"every {label} requires a non-empty {field}")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} {field} values must be unique")
    return set(values)


def validate_structural_members(members: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate the structural member identity/provenance register."""
    if not isinstance(members, list) or not members:
        raise ValueError("structural_members must be a non-empty list")
    ids = _unique(members, "id", "structural member")
    allowed = {"main_plate", "bridge", "cock", "other"}
    for member in members:
        if member.get("member_type") not in allowed:
            raise ValueError(f"structural member {member['id']} has invalid member_type")
        if not member.get("evidence") or not member.get("source_revision"):
            raise ValueError(f"structural member {member['id']} requires evidence and source_revision")
        if member["member_type"] in {"bridge", "cock"}:
            supported = member.get("supported_components")
            if not isinstance(supported, list) or not supported:
                raise ValueError(f"{member['id']} requires supported_components")
    return {"structural_member_count": len(ids), "all_members_traceable": True}


def validate_support_architecture(data: dict[str, Any],
                                  known_component_ids: set[str] | None = None) -> dict[str, Any]:
    """Check arbor/support/member links without imposing a universal support count."""
    arbors = data.get("arbors")
    supports = data.get("supports")
    members = data.get("structural_members")
    if not isinstance(arbors, list) or not isinstance(supports, list):
        raise ValueError("arbors and supports must be lists")
    member_summary = validate_structural_members(members)
    arbor_ids = _unique(arbors, "id", "arbor") if arbors else set()
    support_ids = _unique(supports, "id", "support") if supports else set()
    member_by_id = {item["id"]: item for item in members}
    arbor_by_id = {item["id"]: item for item in arbors}

    for arbor in arbors:
        for field in ("component_id", "axis_id", "role", "evidence", "source_revision"):
            if not arbor.get(field):
                raise ValueError(f"arbor {arbor['id']} requires {field}")
        if known_component_ids is not None and arbor["component_id"] not in known_component_ids:
            raise ValueError(f"arbor {arbor['id']} references unknown component")
        declared = arbor.get("support_ids", [])
        if not isinstance(declared, list):
            raise ValueError(f"arbor {arbor['id']} support_ids must be a list")
        unknown = set(declared) - support_ids
        if unknown:
            raise ValueError(f"arbor {arbor['id']} references unknown supports: {sorted(unknown)}")

    supports_by_arbor: dict[str, list[dict[str, Any]]] = {key: [] for key in arbor_ids}
    for support in supports:
        for field in ("arbor_id", "structure_id", "support_type", "evidence", "source_revision"):
            if not support.get(field):
                raise ValueError(f"support {support['id']} requires {field}")
        arbor_id = support["arbor_id"]
        if arbor_id not in arbor_ids:
            raise ValueError(f"support {support['id']} references unknown arbor")
        structure_id = support["structure_id"]
        if structure_id not in member_by_id:
            raise ValueError(f"support {support['id']} references unknown structural member")
        arbor = arbor_by_id[arbor_id]
        if support.get("axis_id") is not None and support["axis_id"] != arbor["axis_id"]:
            raise ValueError(f"support {support['id']} axis_id does not match its arbor")
        member = member_by_id[structure_id]
        if member["member_type"] in {"bridge", "cock"}:
            if arbor["component_id"] not in member["supported_components"]:
                raise ValueError(f"{structure_id} does not declare support for {arbor['component_id']}")
        if support.get("z_mm") is not None:
            _finite(support["z_mm"], f"support {support['id']} z_mm")
        supports_by_arbor[arbor_id].append(support)

    for arbor in arbors:
        declared = set(arbor.get("support_ids", []))
        actual = {item["id"] for item in supports_by_arbor[arbor["id"]]}
        if declared and declared != actual:
            raise ValueError(f"arbor {arbor['id']} support_ids do not match support register")
        if not declared and actual:
            raise ValueError(f"arbor {arbor['id']} must list its support_ids")

    topology = []
    for arbor_id, items in supports_by_arbor.items():
        z_values = sorted({_finite(item["z_mm"], "support z_mm")
                           for item in items if item.get("z_mm") is not None})
        topology.append({
            "arbor_id": arbor_id,
            "declared_support_count": len(items),
            "support_planes_with_z": len(z_values),
            "axial_support_span_mm": z_values[-1] - z_values[0] if len(z_values) >= 2 else None,
            "topology_status": (
                "multiple_support_planes_located" if len(z_values) >= 2 else
                "support_records_present_but_axial_span_incomplete" if items else
                "support_not_defined"
            ),
            "engineering_disposition_required": True,
        })
    return {
        **member_summary,
        "arbor_count": len(arbor_ids),
        "support_count": len(support_ids),
        "all_support_references_resolve": True,
        "support_topology": topology,
        "note": "No minimum support count is imposed; topology requires design-specific engineering disposition.",
    }


def evaluate_candidate(data: dict[str, Any],
                       known_component_ids: set[str] | None = None) -> dict[str, Any]:
    """Integrate WP-23 arbor/mesh checks, structural supports and WP-22 CAD inputs."""
    if not isinstance(data, dict):
        raise ValueError("candidate data must be an object")
    provenance = data.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("evidence") or not provenance.get("source_revision"):
        raise ValueError("candidate provenance requires evidence and source_revision")

    structural = validate_support_architecture(data, known_component_ids)
    arbor_result = evaluate_arbors({
        "candidate_id": data.get("candidate_id", "unnamed_candidate"),
        "arbors": data["arbors"],
        "supports": data["supports"],
        "gear_meshes": data.get("gear_meshes", []),
    }, known_component_ids)

    bore_specs = data.get("bearing_bore_specs", {})
    if not isinstance(bore_specs, dict):
        raise ValueError("bearing_bore_specs must be a mapping keyed by arbor id")
    bore_register = cad_bore_register(data["arbors"], bore_specs)
    bore_ids = _unique(bore_register, "id", "CAD bore") if bore_register else set()

    cad_summary = None
    cad_missing_bores = []
    cad_config = data.get("cad_config")
    if cad_config is not None:
        cad_summary = validate_cad_config(cad_config)
        configured = {item["id"]: item for item in cad_config["bearing_bores"]}
        for bore in bore_register:
            target = configured.get(bore["id"])
            if target is None:
                cad_missing_bores.append(bore["id"])
                continue
            for field in ("component_id", "axis_id", "xy_mm", "diameter_mm",
                          "evidence", "source_revision"):
                if target.get(field) != bore[field]:
                    raise ValueError(f"CAD bore {bore['id']} does not match arbor handoff field {field}")

    return {
        "schema": "steward.c01.bearing-architecture-evaluation.v1",
        "candidate_id": data.get("candidate_id", "unnamed_candidate"),
        "structural_support_evaluation": structural,
        "arbor_and_gear_evaluation": arbor_result,
        "cad_bore_handoff": {
            "bore_count": len(bore_ids),
            "bore_register": bore_register,
            "cad_config_supplied": cad_config is not None,
            "cad_config_summary": cad_summary,
            "bore_ids_missing_from_cad_config": cad_missing_bores,
            "status": "register_export_only" if cad_config is None else
                      "cad_config_validated" if not cad_missing_bores else
                      "cad_config_missing_handoff_bores",
        },
        "overall_status": "candidate_interface_review_only",
        "overall_fit_status": "not_certified",
        "limitations": [
            "No jewel dimensions, pivot dimensions, press fits, endshake or side shake are calculated.",
            "No bearing loads, Hertzian contact, pivot bending, friction, wear or lubrication model.",
            "Support topology records do not prove structural stiffness or adequate load paths.",
            "No bridge deflection, screw preload, shock response, tolerance stack or thermal analysis.",
            "WP-22 CAD validation checks input structure only; no CAD solid is rendered or certified.",
        ],
    }
