"""WP-31 prototype manufacturing-readiness register validators.

This module validates controlled records; it does not generate production
geometry, qualify suppliers, approve materials, or release a physical build.
"""
from __future__ import annotations
from typing import Any

def _required(record: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    for field in fields:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}.{field} is required")

def _unique(records: list[dict[str, Any]], key: str, label: str) -> None:
    values = [r.get(key) for r in records]
    if any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError(f"{label}.{key} must be a non-empty string")
    if len(values) != len(set(values)):
        raise ValueError(f"{label}.{key} values must be unique")

def validate_bom(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate identity, configuration and sourcing traceability for BOM rows."""
    if not isinstance(items, list) or not items:
        raise ValueError("BOM must contain at least one item")
    _unique(items, "item_id", "BOM")
    required = ("part_name", "functional_description", "quantity_per_movement",
                "unit_of_measure", "configuration_status", "drawing_or_spec_id",
                "revision", "material_status", "supplier_status", "evidence_status")
    allowed = {
        "configuration_status": {"candidate", "selected", "released", "superseded"},
        "material_status": {"open", "proposed", "qualified", "approved", "not_applicable"},
        "supplier_status": {"open", "candidate", "qualified", "approved", "not_applicable"},
        "evidence_status": {"missing", "partial", "complete"}
    }
    for i, row in enumerate(items):
        _required(row, required, f"BOM[{i}]")
        q = row["quantity_per_movement"]
        if not isinstance(q, int) or isinstance(q, bool) or q <= 0:
            raise ValueError(f"{row['item_id']}.quantity_per_movement must be a positive integer")
        for field, values in allowed.items():
            if row[field] not in values:
                raise ValueError(f"{row['item_id']}.{field} is not an allowed status")
        if row["configuration_status"] == "released":
            _required(row, ("approved_part_baseline_id", "release_record_id"), row["item_id"])
        if row["material_status"] == "approved":
            _required(row, ("material_qualification_record_id",), row["item_id"])
        if row["supplier_status"] == "approved":
            _required(row, ("supplier_qualification_record_id",), row["item_id"])
    return {"item_count": len(items), "unique_item_ids": True,
            "build_release_authorized": all(
                r["configuration_status"] == "released" and
                r["material_status"] in ("approved", "not_applicable") and
                r["supplier_status"] in ("approved", "not_applicable") and
                r["evidence_status"] == "complete" for r in items)}

def validate_drawing_register(drawings: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(drawings, list) or not drawings:
        raise ValueError("drawing register must be non-empty")
    _unique(drawings, "drawing_id", "drawing register")
    fields = ("title", "part_or_assembly_id", "revision", "drawing_type",
              "units", "datum_reference", "source_geometry_revision",
              "tolerance_status", "review_status", "approval_record_id")
    for i, d in enumerate(drawings):
        _required(d, fields, f"drawings[{i}]")
        if d["drawing_type"] not in ("concept", "interface", "detail", "assembly", "inspection"):
            raise ValueError(f"{d['drawing_id']}.drawing_type is invalid")
        if d["review_status"] not in ("draft", "in_review", "approved", "superseded"):
            raise ValueError(f"{d['drawing_id']}.review_status is invalid")
        if d["review_status"] == "approved" and not d["approval_record_id"].strip():
            raise ValueError(f"{d['drawing_id']} requires approval evidence")
    return {"drawing_count": len(drawings),
            "approved_count": sum(d["review_status"] == "approved" for d in drawings),
            "drawing_release_requires_geometry_and_tolerance_review": True}

def validate_supplier_qualification(record: dict[str, Any]) -> dict[str, Any]:
    _required(record, ("supplier_id", "supplier_name", "part_scope",
                       "process_scope", "quality_system_evidence",
                       "capability_evidence", "traceability_method",
                       "nonconformance_process", "audit_or_assessment_record",
                       "qualification_status"), "supplier")
    if record["qualification_status"] not in ("candidate", "conditional", "qualified", "rejected"):
        raise ValueError("supplier.qualification_status is invalid")
    if record["qualification_status"] == "qualified":
        _required(record, ("approval_record_id", "approved_scope"), "supplier")
    return {"supplier_id": record["supplier_id"],
            "qualification_status": record["qualification_status"],
            "qualified": record["qualification_status"] == "qualified"}

def validate_material_qualification(record: dict[str, Any]) -> dict[str, Any]:
    _required(record, ("material_id", "material_designation", "supplier_or_source",
                       "specification_revision", "certificate_or_test_evidence",
                       "condition_and_heat_treatment", "critical_properties",
                       "process_compatibility_review", "qualification_status"), "material")
    if record["qualification_status"] not in ("open", "proposed", "tested", "approved", "rejected"):
        raise ValueError("material.qualification_status is invalid")
    if record["qualification_status"] == "approved":
        _required(record, ("approval_record_id", "approved_application_scope"), "material")
    return {"material_id": record["material_id"],
            "qualification_status": record["qualification_status"],
            "approved": record["qualification_status"] == "approved"}

def validate_work_instruction(instruction: dict[str, Any]) -> dict[str, Any]:
    _required(instruction, ("instruction_id", "revision", "operation",
             "applicable_part_revisions", "required_tools_and_fixtures",
             "preconditions", "ordered_steps", "critical_controls",
             "inspection_points", "safety_controls", "rework_disposition",
             "author", "approval_status"), "work_instruction")
    steps = instruction["ordered_steps"]
    if not isinstance(steps, list) or not steps:
        raise ValueError("ordered_steps must be a non-empty list")
    for i, step in enumerate(steps):
        _required(step, ("step_id", "action", "acceptance_or_record"), f"step[{i}]")
    if instruction["approval_status"] not in ("draft", "approved", "superseded"):
        raise ValueError("approval_status is invalid")
    if instruction["approval_status"] == "approved":
        _required(instruction, ("approval_record_id", "effective_date"), "work_instruction")
    return {"instruction_id": instruction["instruction_id"],
            "step_count": len(steps),
            "execution_ready_by_record": instruction["approval_status"] == "approved"}

def evaluate_prototype_release(packet: dict[str, Any]) -> dict[str, Any]:
    """A fail-closed document gate; passing means packet completeness only."""
    _required(packet, ("prototype_id", "movement_revision", "requirements_baseline_id",
                       "architecture_baseline_id", "bom_register_id",
                       "drawing_register_id", "material_register_id",
                       "supplier_register_id", "assembly_instruction_id",
                       "lubrication_instruction_id", "inspection_plan_id",
                       "risk_review_id", "deviation_register_id",
                       "verification_plan_id", "responsible_approver"), "release_packet")
    gates = packet.get("gates")
    required_gates = ("requirements_frozen", "architecture_frozen",
                      "drawings_approved", "materials_approved",
                      "suppliers_approved", "assembly_instructions_approved",
                      "lubrication_instructions_approved", "inspection_plan_approved",
                      "risks_reviewed", "deviations_dispositioned",
                      "verification_plan_approved", "independent_review_complete")
    if not isinstance(gates, dict):
        raise ValueError("gates must be a mapping of explicit boolean decisions")
    missing = [g for g in required_gates if gates.get(g) is not True]
    approved = not missing and isinstance(packet.get("approval_record_id"), str) and bool(packet["approval_record_id"].strip())
    return {"prototype_id": packet["prototype_id"],
            "movement_revision": packet["movement_revision"],
            "missing_or_unapproved_gates": missing,
            "document_packet_complete": approved,
            "physical_build_authorized_by_this_evaluator": False,
            "note": "Human engineering, quality and safety authorization remains mandatory."}
