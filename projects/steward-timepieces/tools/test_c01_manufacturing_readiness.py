"""Synthetic unit tests for WP-31 register and release-gate validators."""
import unittest
from c01_manufacturing_readiness import (
    validate_bom, validate_drawing_register, validate_supplier_qualification,
    validate_material_qualification, validate_work_instruction,
    evaluate_prototype_release,
)

class ManufacturingReadinessTests(unittest.TestCase):
    def bom(self):
        return [dict(item_id="PART-TEST-01", part_name="Synthetic test part",
            functional_description="Fixture only", quantity_per_movement=1,
            unit_of_measure="each", configuration_status="candidate",
            drawing_or_spec_id="DWG-TEST", revision="TEST-A",
            material_status="open", supplier_status="open", evidence_status="partial")]

    def test_bom_candidate_does_not_authorize_build(self):
        self.assertFalse(validate_bom(self.bom())["build_release_authorized"])

    def test_bom_rejects_duplicate_ids(self):
        rows = self.bom() * 2
        with self.assertRaises(ValueError):
            validate_bom(rows)

    def test_released_bom_requires_approval_records(self):
        row = self.bom()[0]
        row.update(configuration_status="released", material_status="approved",
                   supplier_status="approved", evidence_status="complete")
        with self.assertRaises(ValueError):
            validate_bom([row])

    def test_drawing_approval_requires_record(self):
        row = dict(drawing_id="DWG-TEST", title="Synthetic", part_or_assembly_id="P-TEST",
            revision="A", drawing_type="detail", units="mm", datum_reference="TEST",
            source_geometry_revision="TEST", tolerance_status="open",
            review_status="approved", approval_record_id="")
        with self.assertRaises(ValueError):
            validate_drawing_register([row])

    def test_supplier_qualified_requires_approval_and_scope(self):
        row = dict(supplier_id="SUP-TEST", supplier_name="Synthetic supplier",
            part_scope="fixture", process_scope="fixture", quality_system_evidence="TEST",
            capability_evidence="TEST", traceability_method="TEST",
            nonconformance_process="TEST", audit_or_assessment_record="TEST",
            qualification_status="qualified")
        with self.assertRaises(ValueError):
            validate_supplier_qualification(row)

    def test_material_approved_requires_approval_scope(self):
        row = dict(material_id="MAT-TEST", material_designation="Synthetic",
            supplier_or_source="TEST", specification_revision="TEST",
            certificate_or_test_evidence="TEST", condition_and_heat_treatment="TEST",
            critical_properties="TEST", process_compatibility_review="TEST",
            qualification_status="approved")
        with self.assertRaises(ValueError):
            validate_material_qualification(row)

    def test_work_instruction_requires_ordered_steps(self):
        row = dict(instruction_id="WI-TEST", revision="A", operation="fixture",
            applicable_part_revisions="TEST", required_tools_and_fixtures="TEST",
            preconditions="TEST", ordered_steps=[], critical_controls="TEST",
            inspection_points="TEST", safety_controls="TEST", rework_disposition="TEST",
            author="TEST", approval_status="draft")
        with self.assertRaises(ValueError):
            validate_work_instruction(row)

    def test_work_instruction_approved_requires_record(self):
        row = dict(instruction_id="WI-TEST", revision="A", operation="fixture",
            applicable_part_revisions="TEST", required_tools_and_fixtures="TEST",
            preconditions="TEST", ordered_steps=[dict(step_id="1", action="test",
            acceptance_or_record="record")], critical_controls="TEST",
            inspection_points="TEST", safety_controls="TEST", rework_disposition="TEST",
            author="TEST", approval_status="approved", approval_record_id="",
            effective_date="TEST")
        with self.assertRaises(ValueError):
            validate_work_instruction(row)

    def test_release_packet_fails_closed(self):
        packet = dict(prototype_id="C01-P0", movement_revision="TBD",
            requirements_baseline_id="TBD", architecture_baseline_id="TBD",
            bom_register_id="TBD", drawing_register_id="TBD",
            material_register_id="TBD", supplier_register_id="TBD",
            assembly_instruction_id="TBD", lubrication_instruction_id="TBD",
            inspection_plan_id="TBD", risk_review_id="TBD",
            deviation_register_id="TBD", verification_plan_id="TBD",
            responsible_approver="TBD", gates={})
        result = evaluate_prototype_release(packet)
        self.assertFalse(result["document_packet_complete"])
        self.assertFalse(result["physical_build_authorized_by_this_evaluator"])
        self.assertGreater(len(result["missing_or_unapproved_gates"]), 0)

    def test_even_complete_document_gate_does_not_self_authorize_build(self):
        names = ("requirements_frozen", "architecture_frozen", "drawings_approved",
            "materials_approved", "suppliers_approved", "assembly_instructions_approved",
            "lubrication_instructions_approved", "inspection_plan_approved",
            "risks_reviewed", "deviations_dispositioned", "verification_plan_approved",
            "independent_review_complete")
        packet = dict(prototype_id="C01-P0", movement_revision="TBD",
            requirements_baseline_id="REQ", architecture_baseline_id="ARCH",
            bom_register_id="BOM", drawing_register_id="DRAW",
            material_register_id="MAT", supplier_register_id="SUP",
            assembly_instruction_id="ASM", lubrication_instruction_id="LUBE",
            inspection_plan_id="INS", risk_review_id="RISK",
            deviation_register_id="DEV", verification_plan_id="VER",
            responsible_approver="Approver", approval_record_id="REL",
            gates={name: True for name in names})
        result = evaluate_prototype_release(packet)
        self.assertTrue(result["document_packet_complete"])
        self.assertFalse(result["physical_build_authorized_by_this_evaluator"])

if __name__ == "__main__":
    unittest.main()
