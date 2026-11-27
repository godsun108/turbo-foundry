"""WP-32 design-freeze and prototype-configuration control."""
from __future__ import annotations
from typing import Any

DECISION_STATES = {"open", "proposed", "selected", "approved", "rejected", "superseded"}
EVIDENCE_STATES = {"missing", "partial", "complete"}

def _text(record: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    for field in fields:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}.{field} is required")

def _unique(rows: list[dict[str, Any]], field: str, label: str) -> None:
    values = [r.get(field) for r in rows]
    if any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError(f"{label}.{field} must be non-empty")
    if len(values) != len(set(values)):
        raise ValueError(f"{label}.{field} must be unique")

def validate_decision_register(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("decision register must be non-empty")
    _unique(decisions, "decision_id", "decision register")
    for i, d in enumerate(decisions):
        _text(d, ("title", "scope", "owner", "state", "evidence_status",
                  "affected_documents", "decision_record_id"), f"decision[{i}]")
        if d["state"] not in DECISION_STATES:
            raise ValueError(f"{d['decision_id']}.state is invalid")
        if d["evidence_status"] not in EVIDENCE_STATES:
            raise ValueError(f"{d['decision_id']}.evidence_status is invalid")
        if d["state"] == "approved":
            _text(d, ("selected_option", "rationale", "approval_authority",
                      "approval_date", "decision_record_id"), d["decision_id"])
            if d["evidence_status"] != "complete":
                raise ValueError(f"{d['decision_id']} cannot be approved with incomplete evidence")
    return {
        "decision_count": len(decisions),
        "approved_count": sum(d["state"] == "approved" for d in decisions),
        "unresolved_ids": [d["decision_id"] for d in decisions if d["state"] != "approved"],
        "freeze_ready": all(d["state"] == "approved" for d in decisions),
    }

def validate_configuration_baseline(baseline: dict[str, Any]) -> dict[str, Any]:
    _text(baseline, ("baseline_id", "movement_name", "revision", "article_class",
                     "requirements_revision", "architecture_revision", "bom_revision",
                     "drawing_register_revision", "software_model_revision",
                     "configuration_owner", "status"), "baseline")
    if baseline["article_class"] not in ("P0", "P1", "P2", "production_intent"):
        raise ValueError("article_class is invalid")
    if baseline["status"] not in ("draft", "under_review", "approved", "superseded"):
        raise ValueError("baseline.status is invalid")
    components = baseline.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("components must be a non-empty list")
    _unique(components, "component_id", "components")
    for i, c in enumerate(components):
        _text(c, ("name", "part_revision", "configuration_status",
                  "source_record_id"), f"component[{i}]")
        if c["configuration_status"] not in ("candidate", "selected", "released", "not_applicable"):
            raise ValueError(f"{c['component_id']}.configuration_status is invalid")
    if baseline["status"] == "approved":
        _text(baseline, ("approval_record_id", "approval_authority", "approval_date"),
              "baseline")
        if any(c["configuration_status"] not in ("released", "not_applicable")
               for c in components):
            raise ValueError("approved baseline requires released or justified N/A components")
    return {"baseline_id": baseline["baseline_id"],
            "component_count": len(components),
            "status": baseline["status"],
            "approved": baseline["status"] == "approved"}

def validate_interface_baseline(interfaces: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(interfaces, list) or not interfaces:
        raise ValueError("interface baseline must be non-empty")
    _unique(interfaces, "interface_id", "interfaces")
    for i, item in enumerate(interfaces):
        _text(item, ("from_component", "to_component", "interface_type",
                     "definition_revision", "verification_reference",
                     "status", "evidence_status"), f"interface[{i}]")
        if item["from_component"] == item["to_component"]:
            raise ValueError(f"{item['interface_id']} cannot connect a component to itself")
        if item["status"] not in ("candidate", "controlled", "released", "deferred"):
            raise ValueError(f"{item['interface_id']}.status is invalid")
        if item["evidence_status"] not in EVIDENCE_STATES:
            raise ValueError(f"{item['interface_id']}.evidence_status is invalid")
        if item["status"] == "released" and item["evidence_status"] != "complete":
            raise ValueError(f"{item['interface_id']} cannot be released with incomplete evidence")
    return {"interface_count": len(interfaces),
            "unreleased_ids": [x["interface_id"] for x in interfaces if x["status"] != "released"],
            "all_released": all(x["status"] == "released" for x in interfaces)}

def evaluate_design_freeze(packet: dict[str, Any]) -> dict[str, Any]:
    _text(packet, ("project", "movement_revision", "requirements_baseline_id",
                   "architecture_baseline_id", "configuration_baseline_id",
                   "decision_register_id", "interface_register_id",
                   "risk_register_id", "verification_baseline_id",
                   "change_control_record_id", "design_authority"), "freeze_packet")
    required = ("requirements_approved", "architecture_approved",
                "all_required_decisions_approved", "configuration_baseline_approved",
                "interfaces_released", "geometry_and_tolerances_reviewed",
                "energy_and_load_interfaces_reviewed", "verification_plan_approved",
                "risks_dispositioned", "manufacturing_review_complete",
                "independent_design_review_complete")
    gates = packet.get("gates")
    if not isinstance(gates, dict):
        raise ValueError("gates must be a mapping")
    missing = [name for name in required if gates.get(name) is not True]
    approved = not missing and isinstance(packet.get("freeze_approval_record_id"), str) and bool(packet["freeze_approval_record_id"].strip())
    return {"project": packet["project"], "movement_revision": packet["movement_revision"],
            "missing_or_unapproved_gates": missing,
            "design_freeze_packet_ready_for_authority": approved,
            "design_is_frozen_by_this_evaluator": False,
            "note": "Only the named design authority may approve and issue a controlled freeze."}
