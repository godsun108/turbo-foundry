"""WP-53 first-article engineering definition validators.

Record-completeness checks only. No dimensions/specifications are invented;
this module cannot release, build, inspect, or authorize a physical article.
"""
from __future__ import annotations

CANDIDATES = {"column_wheel", "cam_lever"}
REQUIRED_FUNCTIONS = {
    "pusher_input", "control_state_indexing", "clutch_command",
    "stopped_retention_command", "reset_hammer_command",
    "running_reset_interlock", "return_or_reset",
}
REQUIRED_DRAWING_TYPES = {
    "assembly", "component", "interface_control", "inspection",
}
REQUIRED_BOM_FIELDS = (
    "item_id", "description", "quantity", "unit", "part_or_document_ref",
    "revision", "make_buy_status", "configuration_status", "source_evidence_id",
)
REQUIRED_ARTICLE_FIELDS = (
    "article_id", "candidate_id", "candidate_revision", "configuration_revision",
    "requirements_baseline_id", "architecture_candidate_id", "control_definition_revision",
    "clutch_definition_revision", "interface_baseline_id", "fixture_interface_revision",
    "source_revision", "prepared_by", "review_status",
)


def _missing(record, fields):
    return [f"missing {name}" for name in fields if record.get(name) in (None, "", [])]


def validate_article_definition(article):
    errors = _missing(article, REQUIRED_ARTICLE_FIELDS)
    if article.get("candidate_id") not in CANDIDATES:
        errors.append("candidate_id must be column_wheel or cam_lever")
    if article.get("review_status") not in {"draft", "in_review", "approved", "rejected"}:
        errors.append("review_status must be draft, in_review, approved, or rejected")
    if article.get("physical_article_exists") is True and not article.get("physical_asset_record_id"):
        errors.append("physical article claim requires a physical asset record")
    return {
        "definition_structurally_complete": not errors,
        "errors": errors,
        "design_approved": False,
        "physical_article_exists_verified": False,
    }


def validate_candidate_pair(pair):
    errors = []
    for candidate in sorted(CANDIDATES):
        result = validate_article_definition(pair.get(candidate, {}))
        if not result["definition_structurally_complete"]:
            errors.extend(f"{candidate}: {e}" for e in result["errors"])
    cw, cl = pair.get("column_wheel", {}), pair.get("cam_lever", {})
    if cw.get("article_id") and cw.get("article_id") == cl.get("article_id"):
        errors.append("CW and CL must have distinct article IDs")
    if cw.get("configuration_revision") and cw.get("configuration_revision") == cl.get("configuration_revision"):
        errors.append("CW and CL configuration revisions must be distinct")
    for key in ("requirements_baseline_id", "interface_baseline_id", "fixture_interface_revision"):
        if cw.get(key) and cl.get(key) and cw[key] != cl[key]:
            errors.append(f"candidates must share the approved {key}")
    return {"pair_structurally_comparable": not errors, "errors": errors,
            "physical_equivalence_proven": False}


def validate_bom(rows):
    errors = []
    if not isinstance(rows, list) or not rows:
        return {"valid": False, "errors": ["BOM must contain at least one controlled row"]}
    ids = [r.get("item_id") for r in rows]
    if any(not x for x in ids):
        errors.append("every BOM row requires item_id")
    if len(ids) != len(set(ids)):
        errors.append("BOM item_id values must be unique")
    for i, row in enumerate(rows):
        errors.extend(f"row {i}: {e}" for e in _missing(row, REQUIRED_BOM_FIELDS))
        qty = row.get("quantity")
        if isinstance(qty, bool) or not isinstance(qty, (int, float)) or qty <= 0:
            errors.append(f"row {i}: quantity must be a positive numeric value")
        if row.get("make_buy_status") not in {"make", "buy", "existing_controlled", "TBD"}:
            errors.append(f"row {i}: invalid make_buy_status")
        if row.get("configuration_status") not in {"defined", "candidate", "TBD", "not_applicable"}:
            errors.append(f"row {i}: invalid configuration_status")
        if row.get("configuration_status") == "defined" and not row.get("approved_definition_ref"):
            errors.append(f"row {i}: defined item requires approved_definition_ref")
    return {"valid": not errors, "errors": errors,
            "manufacturing_release_authorized": False}


def validate_drawing_register(rows):
    errors = []
    if not isinstance(rows, list) or not rows:
        return {"valid": False, "errors": ["drawing register must not be empty"]}
    ids = [r.get("drawing_id") for r in rows]
    if any(not x for x in ids):
        errors.append("every drawing requires drawing_id")
    if len(ids) != len(set(ids)):
        errors.append("drawing_id values must be unique")
    for i, row in enumerate(rows):
        errors.extend(f"row {i}: {e}" for e in _missing(row, (
            "drawing_id", "drawing_type", "title", "revision", "configuration_id",
            "source_evidence_id", "prepared_by", "review_status",
        )))
        if row.get("drawing_type") not in REQUIRED_DRAWING_TYPES:
            errors.append(f"row {i}: unsupported drawing_type")
        if row.get("review_status") not in {"draft", "in_review", "approved", "rejected"}:
            errors.append(f"row {i}: invalid review_status")
        if row.get("review_status") == "approved" and not row.get("approval_record_id"):
            errors.append(f"row {i}: approved drawing requires approval_record_id")
    return {"valid": not errors, "errors": errors,
            "drawing_release_authorized": False}


def validate_interface_register(rows, common_interface_revision):
    errors = []
    if not isinstance(rows, list) or not rows:
        return {"valid": False, "errors": ["interface register must not be empty"]}
    ids = [r.get("interface_id") for r in rows]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        errors.append("interface IDs must be present and unique")
    functions = set()
    for i, row in enumerate(rows):
        errors.extend(f"row {i}: {e}" for e in _missing(row, (
            "interface_id", "function", "candidate_id", "article_interface_ref",
            "fixture_interface_ref", "datum_reference", "measurement_method",
            "source_evidence_id", "source_revision",
        )))
        if row.get("candidate_id") not in CANDIDATES:
            errors.append(f"row {i}: invalid candidate_id")
        functions.add(row.get("function"))
        if row.get("common_interface_revision") != common_interface_revision:
            errors.append(f"row {i}: common interface revision mismatch")
    missing = REQUIRED_FUNCTIONS - functions
    if missing:
        errors.append(f"required functions missing: {sorted(missing)}")
    return {"valid": not errors, "errors": errors,
            "physical_interface_fit_verified": False}


def validate_inspection_plan(rows):
    errors = []
    if not isinstance(rows, list) or not rows:
        return {"valid": False, "errors": ["inspection plan must not be empty"]}
    ids = [r.get("characteristic_id") for r in rows]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        errors.append("inspection characteristic IDs must be present and unique")
    for i, row in enumerate(rows):
        errors.extend(f"row {i}: {e}" for e in _missing(row, (
            "characteristic_id", "article_feature_ref", "measurand", "unit",
            "method_reference", "instrument_requirement", "calibration_requirement",
            "acceptance_requirement_ref", "source_evidence_id", "record_template_id",
        )))
        if row.get("acceptance_limit") is not None:
            errors.append(f"row {i}: numerical acceptance limit belongs in approved requirement, not invented here")
    return {"valid": not errors, "errors": errors,
            "inspection_pass_implied": False}


def validate_first_article_packet(packet):
    errors = []
    errors.extend(_missing(packet, (
        "packet_id", "revision", "article_definition", "bom", "drawing_register",
        "interface_register", "inspection_plan", "risk_review_id",
        "assembly_instruction_id", "lubrication_instruction_id",
        "configuration_audit_id", "deviation_register_id", "independent_review_id",
    )))
    article = validate_article_definition(packet.get("article_definition", {}))
    if not article["definition_structurally_complete"]:
        errors.extend(f"article: {e}" for e in article["errors"])
    for label, fn, key in (
        ("BOM", validate_bom, "bom"),
        ("drawing register", validate_drawing_register, "drawing_register"),
        ("interface register", lambda x: validate_interface_register(x, packet.get("common_interface_revision")), "interface_register"),
        ("inspection plan", validate_inspection_plan, "inspection_plan"),
    ):
        result = fn(packet.get(key, []))
        if not result["valid"]:
            errors.extend(f"{label}: {e}" for e in result["errors"])
    return {
        "packet_structurally_complete": not errors,
        "errors": errors,
        "first_article_build_authorized": False,
        "inspection_acceptance_implied": False,
        "WP52_test_release_authorized": False,
        "note": "Completeness is not engineering approval, manufacturing release, inspection acceptance, or test authorization.",
    }
