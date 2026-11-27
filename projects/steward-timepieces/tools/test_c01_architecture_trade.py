import unittest
from c01_architecture_trade import (ArchitectureTradeError, validate_criteria, compare_measurement,
 evaluate_candidate_scores, validate_gates, evaluate_trade_study, compatibility_matrix, REQUIRED_CRITERIA, REQUIRED_GATES)

class WP45Tests(unittest.TestCase):
    def criteria(self):
        return [{"criterion_id":k,"definition":"approved synthetic criterion","measurement_method":"synthetic fixture",
          "acceptance_reference":"fixture","evidence_id":"SYNTHETIC","status":"approved","weight":"1/10",
          "direction":"lower_is_better"} for k in sorted(REQUIRED_CRITERIA)]
    def scores(self,offset=0):
        return [{"criterion_id":k,"score":3+offset,"evidence_id":"SYNTHETIC","review_record_id":"FIXTURE"}
          for k in sorted(REQUIRED_CRITERIA)]
    def gates(self,status="open"):
        return [{"gate_id":k,"status":status,"evidence_id":"TBD" if status=="open" else "EV-001",
          "review_record_id":"TBD" if status=="open" else "REV-001"} for k in sorted(REQUIRED_GATES)]
    def study(self):
        return {"study_id":"WP45-SYNTHETIC","evidence_id":"SYNTHETIC","source_revision":"fixture",
          "review_status":"draft","requirements_revision":"fixture",
          "candidate_cw":{"candidate_id":"CW","control_type":"column_wheel","configuration_revision":"CW-fixture","evidence_id":"SYNTHETIC","source_revision":"fixture","status":"candidate"},
          "candidate_cl":{"candidate_id":"CL","control_type":"cam_lever","configuration_revision":"CL-fixture","evidence_id":"SYNTHETIC","source_revision":"fixture","status":"candidate"},
          "criteria":self.criteria(),"scores_cw":self.scores(),"scores_cl":self.scores(-1),"gates":self.gates()}
    def test_criteria_exact_weight_sum(self): self.assertEqual(validate_criteria(self.criteria())["weight_sum"],"1")
    def test_incomplete_criteria_rejected(self):
        with self.assertRaises(ArchitectureTradeError): validate_criteria(self.criteria()[:-1])
    def test_weights_must_sum_one(self):
        d=self.criteria(); d[0]["weight"]="1/5"
        with self.assertRaises(ArchitectureTradeError): validate_criteria(d)
    def test_unapproved_criteria_rejected(self):
        d=self.criteria(); d[0]["status"]="draft"
        with self.assertRaises(ArchitectureTradeError): validate_criteria(d)
    def test_measurement_uncertainty_overlap_is_indeterminate(self):
        a={"value":10,"expanded_uncertainty":1,"unit":"N","evidence_id":"A","procedure_revision":"P1","condition_id":"C1","configuration_revision":"CW"}
        b={"value":10.5,"expanded_uncertainty":1,"unit":"N","evidence_id":"B","procedure_revision":"P1","condition_id":"C1","configuration_revision":"CL"}
        self.assertEqual(compare_measurement(a,b,"lower_is_better")["provisional_result"],"INDETERMINATE_OR_OVERLAPPING")
    def test_measurement_comparison_requires_same_conditions(self):
        a={"value":10,"expanded_uncertainty":0.1,"unit":"N","evidence_id":"A","procedure_revision":"P1","condition_id":"C1","configuration_revision":"CW"}
        b={**a,"configuration_revision":"CL","condition_id":"C2"}
        with self.assertRaises(ArchitectureTradeError): compare_measurement(a,b,"lower_is_better")
    def test_score_requires_evidence(self):
        d=self.scores(); d[0]["evidence_id"]=""
        with self.assertRaises(ArchitectureTradeError): evaluate_candidate_scores(self.criteria(),d)
    def test_gate_set_complete(self): self.assertEqual(validate_gates(self.gates())["gate_count"],len(REQUIRED_GATES))
    def test_pass_gate_requires_evidence(self):
        d=self.gates("pass"); d[0]["evidence_id"]="TBD"
        with self.assertRaises(ArchitectureTradeError): validate_gates(d)
    def test_trade_study_only_provisional(self):
        r=evaluate_trade_study(self.study())
        self.assertEqual(r["provisional_comparison"],"CW_PROVISIONALLY_HIGHER")
        self.assertFalse(r["architecture_selected"]); self.assertFalse(r["prototype_release_authorized"])
    def test_all_gates_and_review_only_authorize_review_readiness(self):
        d=self.study(); d["gates"]=self.gates("pass"); d["review_status"]="approved"
        r=evaluate_trade_study(d)
        self.assertTrue(r["decision_ready_for_authority_review"])
        self.assertFalse(r["architecture_selected"])
    def test_compatibility_keeps_four_combinations_open(self):
        self.assertEqual(len(compatibility_matrix()["combinations"]),4)

if __name__=="__main__": unittest.main()
