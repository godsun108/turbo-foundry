import unittest
from c01_chrono_cad_simulation import (
    validate_assembly, screen_motion_clearance, generate_envelope_scad,
    validate_sequence,
)

class ChronographCadSimulationTests(unittest.TestCase):
    def assembly(self):
        return {"candidate_id":"SYNTHETIC-ONLY","evidence_id":"FIXTURE",
            "source_revision":"TEST",
            "bodies":[
                {"id":"fixed","kind":"fixed","radius_mm":2,"z_min_mm":0,"z_max_mm":1,
                 "evidence_id":"FIXTURE","source_revision":"TEST",
                 "poses":[{"x_mm":0,"y_mm":0},{"x_mm":0,"y_mm":0}]},
                {"id":"moving","kind":"rotating","radius_mm":1,"z_min_mm":0,"z_max_mm":1,
                 "evidence_id":"FIXTURE","source_revision":"TEST",
                 "poses":[{"x_mm":4,"y_mm":0},{"x_mm":2.5,"y_mm":0}]}
            ]}
    def test_validates_explicit_assembly(self):
        self.assertEqual(validate_assembly(self.assembly())["body_count"],2)
    def test_detects_sampled_interference(self):
        self.assertTrue(screen_motion_clearance(self.assembly())["sampled_interference_found"])
    def test_clearance_is_not_continuous_proof(self):
        self.assertFalse(screen_motion_clearance(self.assembly())["continuous_motion_proven"])
    def test_rejects_mismatched_time_bases(self):
        a=self.assembly(); a["bodies"][1]["poses"].pop()
        with self.assertRaises(ValueError): screen_motion_clearance(a)
    def test_scad_requires_traceable_geometry(self):
        self.assertIn("candidate envelope visualization",generate_envelope_scad(self.assembly()))
    def test_sequence_requires_physical_interlock_reference(self):
        seq=[{"state":s,"command":c} for s,c in zip(
            ["stopped_zero","running","stopped_retained","running","stopped_zero"],
            ["initial","start","stop","start","reset"])]
        with self.assertRaises(ValueError): validate_sequence(seq)
    def test_valid_sequence_is_only_logical(self):
        seq=[{"state":s,"command":c} for s,c in zip(
            ["stopped_zero","running","stopped_retained","running","stopped_zero"],
            ["initial","start","stop","start","reset"])]
        seq[-1]["reset_interlock_test_id"]="TEST-INTERLOCK"
        self.assertFalse(validate_sequence(seq)["physical_sequence_verified"])

if __name__ == "__main__": unittest.main()
