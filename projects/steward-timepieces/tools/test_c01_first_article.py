import unittest

from c01_first_article import (
    REQUIRED_FUNCTIONS, validate_article_definition, validate_candidate_pair,
    validate_bom, validate_drawing_register, validate_interface_register,
    validate_inspection_plan, validate_first_article_packet,
)


def article(candidate, article_id, config):
    return {
        "article_id": article_id, "candidate_id": candidate,
        "candidate_revision": "A", "configuration_revision": config,
        "requirements_baseline_id": "REQ-1", "architecture_candidate_id": candidate,
        "control_definition_revision": "CTRL-A", "clutch_definition_revision": "CLUTCH-TBD",
        "interface_baseline_id": "IF-1", "fixture_interface_revision": "FIX-IF-A",
        "source_revision": "SRC-A", "prepared_by": "engineer", "review_status": "draft",
    }


def bom():
    return [{
        "item_id": "ITEM-1", "description": "Synthetic example item",
        "quantity": 1, "unit": "each", "part_or_document_ref": "REF-TBD",
        "revision": "A", "make_buy_status": "TBD",
        "configuration_status": "TBD", "source_evidence_id": "EV-SYN",
    }]


def drawings():
    return [{
        "drawing_id": "DWG-1", "drawing_type": "assembly", "title": "Candidate assembly definition",
        "revision": "A", "configuration_id": "CFG-1", "source_evidence_id": "EV-1",
        "prepared_by": "engineer", "review_status": "draft",
    }]


def interfaces():
    rows = []
    for i, function in enumerate(sorted(REQUIRED_FUNCTIONS)):
        for candidate in ("column_wheel", "cam_lever"):
            rows.append({
                "interface_id": f"IF-{i}-{candidate}", "function": function,
                "candidate_id": candidate, "article_interface_ref": "ARTICLE-IF-TBD",
                "fixture_interface_ref": "FIXTURE-IF-TBD", "datum_reference": "DATUM-TBD",
                "measurement_method": "METHOD-TBD", "source_evidence_id": "EV-1",
                "source_revision": "SRC-A", "common_interface_revision": "IF-A",
            })
    return rows


def inspections():
    return [{
        "characteristic_id": "IC-1", "article_feature_ref": "FEATURE-TBD",
        "measurand": "position", "unit": "mm", "method_reference": "METHOD-TBD",
        "instrument_requirement": "INSTRUMENT-TBD",
        "calibration_requirement": "CALIBRATION-TBD",
        "acceptance_requirement_ref": "REQ-APPROVED-TBD",
        "source_evidence_id": "EV-1", "record_template_id": "RECORD-1",
    }]


class FirstArticleTests(unittest.TestCase):
    def test_article_definition_does_not_claim_approval(self):
        result = validate_article_definition(article("column_wheel", "CW-1", "CW-A"))
        self.assertTrue(result["definition_structurally_complete"])
        self.assertFalse(result["design_approved"])

    def test_article_requires_unique_identity_and_candidate(self):
        a = article("unknown", "CW-1", "CW-A")
        self.assertFalse(validate_article_definition(a)["definition_structurally_complete"])

    def test_candidate_pair_requires_common_baseline_and_distinct_articles(self):
        pair = {
            "column_wheel": article("column_wheel", "SAME", "CW-A"),
            "cam_lever": article("cam_lever", "SAME", "CL-A"),
        }
        self.assertFalse(validate_candidate_pair(pair)["pair_structurally_comparable"])

    def test_bom_rejects_duplicate_ids_and_unapproved_defined_item(self):
        row = bom()[0]
        row["configuration_status"] = "defined"
        self.assertFalse(validate_bom([row])["valid"])
        self.assertFalse(validate_bom([bom()[0], bom()[0]])["valid"])

    def test_drawing_register_requires_approval_reference_for_approved_drawing(self):
        row = drawings()[0]
        row["review_status"] = "approved"
        self.assertFalse(validate_drawing_register([row])["valid"])
        row["approval_record_id"] = "APR-1"
        self.assertTrue(validate_drawing_register([row])["valid"])

    def test_interface_register_requires_common_revision_and_functions(self):
        rows = interfaces()
        rows[0]["common_interface_revision"] = "OLD"
        self.assertFalse(validate_interface_register(rows, "IF-A")["valid"])
        self.assertFalse(validate_interface_register([], "IF-A")["valid"])

    def test_inspection_plan_requires_traceable_acceptance_source(self):
        row = inspections()[0]
        row["acceptance_requirement_ref"] = ""
        self.assertFalse(validate_inspection_plan([row])["valid"])
        row["acceptance_requirement_ref"] = "REQ-1"
        row["acceptance_limit"] = 0.1
        self.assertFalse(validate_inspection_plan([row])["valid"])

    def test_complete_packet_is_only_structurally_complete(self):
        packet = {
            "packet_id": "FA-1", "revision": "A",
            "article_definition": article("column_wheel", "CW-1", "CW-A"),
            "bom": bom(), "drawing_register": drawings(),
            "interface_register": interfaces(), "inspection_plan": inspections(),
            "risk_review_id": "RISK-1", "assembly_instruction_id": "ASM-TBD",
            "lubrication_instruction_id": "LUBE-TBD", "configuration_audit_id": "AUDIT-1",
            "deviation_register_id": "DEV-1", "independent_review_id": "REV-1",
            "common_interface_revision": "IF-A",
        }
        result = validate_first_article_packet(packet)
        self.assertTrue(result["packet_structurally_complete"])
        self.assertFalse(result["first_article_build_authorized"])
        self.assertFalse(result["WP52_test_release_authorized"])

    def test_packet_missing_required_document_fails_closed(self):
        packet = {"packet_id": "FA-2", "revision": "A"}
        result = validate_first_article_packet(packet)
        self.assertFalse(result["packet_structurally_complete"])
        self.assertFalse(result["first_article_build_authorized"])


if __name__ == "__main__":
    unittest.main()
