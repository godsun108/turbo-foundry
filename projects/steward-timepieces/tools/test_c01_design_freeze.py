import unittest
from c01_design_freeze import (
    validate_decision_register, validate_configuration_baseline,
    validate_interface_baseline, evaluate_design_freeze,
)

class DesignFreezeTests(unittest.TestCase):
    def test_open_decision_blocks_freeze(self):
        rows = [dict(decision_id="D-1", title="Clutch", scope="C01",
            owner="Design", state="open", evidence_status="missing",
            affected_documents="WP-16", decision_record_id="TBD")]
        result = validate_decision_register(rows)
        self.assertFalse(result["freeze_ready"])
        self.assertEqual(result["unresolved_ids"], ["D-1"])

    def test_approved_decision_requires_complete_evidence(self):
        row = dict(decision_id="D-1", title="Clutch", scope="C01",
            owner="Design", state="approved", evidence_status="partial",
            affected_documents="WP-16", decision_record_id="DEC-1",
            selected_option="Option A", rationale="Evidence", approval_authority="Lead",
            approval_date="2026-11-26")
        with self.assertRaises(ValueError):
            validate_decision_register([row])

    def test_duplicate_decision_rejected(self):
        row = dict(decision_id="D-1", title="x", scope="x", owner="x",
            state="open", evidence_status="missing", affected_documents="x",
            decision_record_id="x")
        with self.assertRaises(ValueError):
            validate_decision_register([row, row.copy()])

    def test_candidate_configuration_is_not_approved(self):
        baseline = dict(baseline_id="C01-P0", movement_name="STEWARD C-01",
            revision="A", article_class="P0", requirements_revision="TBD",
            architecture_revision="TBD", bom_revision="TBD",
            drawing_register_revision="TBD", software_model_revision="TBD",
            configuration_owner="Design", status="draft",
            components=[dict(component_id="C-TEST", name="fixture",
                part_revision="TBD", configuration_status="candidate",
                source_record_id="TEST")])
        self.assertFalse(validate_configuration_baseline(baseline)["approved"])

    def test_approved_configuration_requires_released_components(self):
        baseline = dict(baseline_id="C01-P0", movement_name="STEWARD C-01",
            revision="A", article_class="P0", requirements_revision="REQ",
            architecture_revision="ARCH", bom_revision="BOM",
            drawing_register_revision="DRW", software_model_revision="SW",
            configuration_owner="Design", status="approved",
            approval_record_id="APP", approval_authority="Lead",
            approval_date="2026-11-26",
            components=[dict(component_id="C-TEST", name="fixture",
                part_revision="A", configuration_status="candidate",
                source_record_id="TEST")])
        with self.assertRaises(ValueError):
            validate_configuration_baseline(baseline)

    def test_released_interface_requires_complete_evidence(self):
        row = dict(interface_id="I-1", from_component="A", to_component="B",
            interface_type="mechanical", definition_revision="TBD",
            verification_reference="TBD", status="released",
            evidence_status="partial")
        with self.assertRaises(ValueError):
            validate_interface_baseline([row])

    def test_self_interface_rejected(self):
        row = dict(interface_id="I-1", from_component="A", to_component="A",
            interface_type="mechanical", definition_revision="A",
            verification_reference="V-1", status="candidate",
            evidence_status="missing")
        with self.assertRaises(ValueError):
            validate_interface_baseline([row])

    def packet(self):
        return dict(project="STEWARD C-01", movement_revision="A",
            requirements_baseline_id="REQ", architecture_baseline_id="ARCH",
            configuration_baseline_id="CFG", decision_register_id="DEC",
            interface_register_id="INT", risk_register_id="RISK",
            verification_baseline_id="VER", change_control_record_id="CCR",
            design_authority="TBD", gates={})

    def test_freeze_gate_fails_closed(self):
        result = evaluate_design_freeze(self.packet())
        self.assertFalse(result["design_freeze_packet_ready_for_authority"])
        self.assertFalse(result["design_is_frozen_by_this_evaluator"])
        self.assertGreater(len(result["missing_or_unapproved_gates"]), 0)

    def test_evaluator_never_self_freezes(self):
        p = self.packet()
        names = ("requirements_approved", "architecture_approved",
            "all_required_decisions_approved", "configuration_baseline_approved",
            "interfaces_released", "geometry_and_tolerances_reviewed",
            "energy_and_load_interfaces_reviewed", "verification_plan_approved",
            "risks_dispositioned", "manufacturing_review_complete",
            "independent_design_review_complete")
        p["gates"] = {n: True for n in names}
        p["freeze_approval_record_id"] = "APP-1"
        result = evaluate_design_freeze(p)
        self.assertTrue(result["design_freeze_packet_ready_for_authority"])
        self.assertFalse(result["design_is_frozen_by_this_evaluator"])

if __name__ == "__main__":
    unittest.main()
