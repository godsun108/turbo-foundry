"""Synthetic WP-56 tests only; no C-01 measurements or decisions."""
import unittest
from c01_control_architecture_selection import (
 SelectionError, REQUIRED_CRITERIA, REQUIRED_GATES, validate_criteria,
 validate_scores, validate_measured_comparisons, validate_gates,
 evaluate_decision_packet, COMBINATIONS
)

def criteria():
 return [{"criterion_id":cid,"definition":"synthetic criterion","measurement_method":"synthetic method",
  "acceptance_reference":"synthetic reference","evidence_id":"SYNTHETIC","source_revision":"TEST",
  "direction":"lower_is_better","approval_id":"TEST-APPROVAL","approved":True,"weight":"1/10"}
  for cid in sorted(REQUIRED_CRITERIA)]

def scores():
 return {cid:[{"criterion_id":k,"score_1_to_5":3 if cid=="column_wheel" else 4,
  "evidence_id":"SYNTHETIC","source_revision":"TEST","review_id":"TEST-REVIEW",
  "rationale":"synthetic fixture only","approved":True} for k in sorted(REQUIRED_CRITERIA)]
  for cid in ("column_wheel","cam_lever")}

def gates(disposition="pass"):
 return [{"gate_id":k,"evidence_id":"SYNTHETIC","source_revision":"TEST",
  "reviewer":"TEST-REVIEWER","disposition":disposition} for k in sorted(REQUIRED_GATES)]

def packet():
 cand={k:{"candidate_id":k,"configuration_revision":"TEST-REV-"+k,"article_id":"TEST-ARTICLE-"+k,
  "requirements_revision":"TEST-REQ","evidence_id":"SYNTHETIC","source_revision":"TEST",
  "clutch_compatibility_review_id":"TEST-COMPAT","physical_article_status":"tested",
  "approved_configuration":True} for k in ("column_wheel","cam_lever")}
 comparisons=[{"comparison_id":"CMP-1","criterion_id":"actuation_force_travel",
  "cw_run_id":"CW-RUN","cl_run_id":"CL-RUN","procedure_revision":"TEST-PROC",
  "test_condition_id":"TEST-COND","fixture_revision":"TEST-FIX",
  "evidence_id":"SYNTHETIC","source_revision":"TEST","unit":"N",
  "cw_value":5.0,"cl_value":7.0,"cw_expanded_uncertainty":0.1,
  "cl_expanded_uncertainty":0.1,"direction":"lower_is_better"}]
 return {"decision_id":"TEST-DECISION","requirements_revision":"TEST-REQ",
  "decision_revision":"TEST-DEC-REV","evidence_id":"SYNTHETIC","source_revision":"TEST",
  "decision_authority":"TEST-AUTHORITY","criteria":criteria(),"candidates":cand,
  "scores":scores(),"measured_comparisons":comparisons,"gates":gates(),
  "evidence_index":[{"evidence_id":"SYNTHETIC"}]}

class WP56Tests(unittest.TestCase):
 def test_criteria_complete(self): self.assertTrue(validate_criteria(criteria())["criteria_approved"])
 def test_weights_must_sum_one(self):
  c=criteria(); c[0]["weight"]="1/2"
  with self.assertRaises(SelectionError): validate_criteria(c)
 def test_missing_criterion_rejected(self):
  with self.assertRaises(SelectionError): validate_criteria(criteria()[:-1])
 def test_both_candidate_scores_required(self):
  with self.assertRaises(SelectionError): validate_scores(criteria(),{"column_wheel":[]})
 def test_scores_bounds(self):
  s=scores(); s["cam_lever"][0]["score_1_to_5"]=6
  with self.assertRaises(SelectionError): validate_scores(criteria(),s)
 def test_comparison_clear_winner_for_single_measure_only(self):
  r=validate_measured_comparisons(packet()["measured_comparisons"])[0]
  self.assertEqual(r["outcome"],"CW_better")
  self.assertFalse(r["physical_equivalence_proven"])
 def test_overlapping_uncertainty_indeterminate(self):
  c=packet()["measured_comparisons"]; c[0]["cw_expanded_uncertainty"]=2
  self.assertEqual(validate_measured_comparisons(c)[0]["outcome"],"indeterminate_overlap")
 def test_gate_open_blocks(self):
  g=validate_gates(gates("open"))
  self.assertFalse(g["all_pass"])
 def test_missing_gate_rejected(self):
  with self.assertRaises(SelectionError): validate_gates(gates()[:-1])
 def test_full_packet_never_selects_automatically(self):
  r=evaluate_decision_packet(packet())
  self.assertEqual(r["recommendation"],"READY_FOR_DESIGN_AUTHORITY_REVIEW")
  self.assertFalse(r["architecture_selected"])
  self.assertIsNone(r["selected_control"])
  self.assertFalse(r["design_frozen"])
 def test_failed_gate_not_ready(self):
  p=packet(); p["gates"]=gates("fail")
  self.assertEqual(evaluate_decision_packet(p)["recommendation"],"NOT_READY")
 def test_missing_evidence_index_not_ready(self):
  p=packet(); p["evidence_index"]=[]
  self.assertEqual(evaluate_decision_packet(p)["recommendation"],"NOT_READY")
 def test_approval_record_does_not_freeze_design(self):
  p=packet(); p["decision_approval"]={"status":"approved","approval_id":"DA-TEST",
   "signatory":"TEST","date":"TEST-DATE","selected_control":"cam_lever","rationale":"test"}
  r=evaluate_decision_packet(p)
  self.assertEqual(r["selected_control"],"cam_lever")
  self.assertFalse(r["architecture_selected"])
  self.assertFalse(r["manufacturing_release_authorized"])
 def test_combination_matrix_keeps_clutch_separate(self):
  self.assertEqual(COMBINATIONS["A"]["control"],"column_wheel")
  self.assertEqual(COMBINATIONS["D"]["clutch"],"horizontal_lateral")

if __name__=="__main__": unittest.main()
