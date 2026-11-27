import unittest
from c01_test_engineering import (
    validate_instrument_register, evaluate_uncertainty, validate_test_procedure,
    evaluate_result, build_verification_matrix, required_test_domains,
)

class TestEngineeringTests(unittest.TestCase):
    def instrument(self):
        return {"instrument_id":"I-01","description":"Synthetic test instrument",
                "serial_or_asset_id":"FIXTURE-01","calibration_record_id":"CAL-01",
                "calibration_due_date":"2099-01-01","range_and_resolution":"fixture range",
                "measurement_unit":"unit","calibration_status":"in_calibration"}
    def procedure(self,status="approved"):
        p={"procedure_id":"TP-01","revision":"A","objective":"Synthetic verification fixture",
           "requirement_ids":"REQ-FIXTURE","setup_and_boundary":"Synthetic boundary",
           "preconditions":"Fixture only","steps":"Fixture steps","data_fields":"Measured fixture value",
           "safety_and_stop_conditions":"Stop on fixture fault",
           "acceptance_criteria_reference":"Fixture criterion","instrument_ids":"I-01",
           "uncertainty_budget_id":"U-01","responsible_approver":"Fixture approver",
           "approval_status":status}
        if status=="approved": p["approval_record_id"]="APR-01"
        return p
    def result(self,**overrides):
        r={"test_id":"T-01","procedure_id":"TP-01","procedure_revision":"A",
           "movement_revision":"FIXTURE-REV","test_condition_id":"FIXTURE-COND",
           "source_record_id":"RAW-01","instrument_ids":"I-01",
           "calibration_record_ids":"CAL-01","uncertainty_budget_id":"U-01",
           "requirement_id":"REQ-FIXTURE","unit":"fixture-unit","approval_status":"approved",
           "measured_value":5,"lower_limit":0,"upper_limit":10,"expanded_uncertainty":1}
        r.update(overrides); return r
    def test_instrument_register(self):
        self.assertTrue(validate_instrument_register([self.instrument()])["register_complete"])
    def test_duplicate_instrument_rejected(self):
        with self.assertRaises(ValueError):
            validate_instrument_register([self.instrument(),self.instrument()])
    def test_uncertainty_rss_and_coverage(self):
        u={"measurand":"fixture","unit":"u","method_reference":"fixture method",
           "coverage_factor":2,"approved":True,
           "components":[{"component_id":"a","standard_uncertainty":3,"source_or_rationale":"fixture"},
                         {"component_id":"b","standard_uncertainty":4,"source_or_rationale":"fixture"}]}
        r=evaluate_uncertainty(u)
        self.assertAlmostEqual(r["combined_standard_uncertainty"],5)
        self.assertAlmostEqual(r["expanded_uncertainty"],10)
    def test_uncertainty_duplicate_component_rejected(self):
        u={"measurand":"fixture","unit":"u","method_reference":"m","coverage_factor":2,
           "components":[{"component_id":"a","standard_uncertainty":1,"source_or_rationale":"x"},
                         {"component_id":"a","standard_uncertainty":1,"source_or_rationale":"x"}]}
        with self.assertRaises(ValueError): evaluate_uncertainty(u)
    def test_guard_banded_pass(self):
        self.assertEqual(evaluate_result(self.result())["guard_banded_status"],"pass")
    def test_guard_banded_indeterminate(self):
        self.assertEqual(evaluate_result(self.result(measured_value=0.5,expanded_uncertainty=1))["guard_banded_status"],"indeterminate")
    def test_guard_banded_fail(self):
        self.assertEqual(evaluate_result(self.result(measured_value=12,expanded_uncertainty=1))["guard_banded_status"],"fail")
    def test_reject_unapproved_procedure_result(self):
        with self.assertRaises(ValueError): evaluate_result(self.result(approval_status="draft"))
    def test_matrix_revision_traceability(self):
        p=self.procedure()
        m=build_verification_matrix([p],[self.result()])
        self.assertEqual(m["status_counts"]["pass"],1)
        self.assertFalse(m["engineering_release_approved"])
        with self.assertRaises(ValueError):
            build_verification_matrix([p],[self.result(procedure_revision="B")])
    def test_draft_procedure_cannot_be_executed(self):
        with self.assertRaises(ValueError):
            build_verification_matrix([self.procedure("draft")],[self.result()])
    def test_domain_coverage_register(self):
        domains=required_test_domains()
        self.assertGreaterEqual(len(domains),10)
        self.assertEqual(len({x["domain"] for x in domains}),len(domains))

if __name__ == "__main__":
    unittest.main()
