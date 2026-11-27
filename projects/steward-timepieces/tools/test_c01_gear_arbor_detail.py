import unittest
from fractions import Fraction
from c01_gear_arbor_detail import (
    EngineeringInputError, gear_geometry, mesh_center_distance, signed_ratio,
    fit_clearance, tolerance_stack, validate_arbor_register, validate_axial_stack
)

class GearArborDetailTests(unittest.TestCase):
    def test_gear_reference_geometry(self):
        g=gear_geometry(module_mm=0.5, teeth=40, pressure_angle_deg=20,
                        evidence_id="SYN", source_revision="fixture")
        self.assertEqual(g["pitch_diameter_mm"],20.0)
        self.assertAlmostEqual(g["base_diameter_mm"],20*__import__("math").cos(__import__("math").radians(20)))
        self.assertEqual(g["tooth_form_status"],"NOT_GENERATED")

    def test_optional_tip_root_require_explicit_coefficients(self):
        g=gear_geometry(module_mm=1,teeth=20,pressure_angle_deg=20,
                        profile_shift=0.1,addendum_coefficient=1,dedendum_coefficient=1.2,
                        evidence_id="SYN",source_revision="fixture")
        self.assertAlmostEqual(g["addendum_diameter_mm"],22.2)
        self.assertAlmostEqual(g["dedendum_diameter_mm"],17.8)

    def test_external_and_internal_center_distance(self):
        a={"module_mm":0.5,"teeth":40}; b={"module_mm":0.5,"teeth":10}
        self.assertEqual(mesh_center_distance(gear_a=a,gear_b=b,mesh_type="external")["nominal_center_distance_mm"],12.5)
        ring={"module_mm":0.5,"teeth":60}
        self.assertEqual(mesh_center_distance(gear_a=ring,gear_b=b,mesh_type="internal")["nominal_center_distance_mm"],12.5)

    def test_mesh_rejects_module_mismatch_and_bad_internal_pair(self):
        with self.assertRaises(EngineeringInputError):
            mesh_center_distance(gear_a={"module_mm":1,"teeth":20},gear_b={"module_mm":0.5,"teeth":10},mesh_type="external")
        with self.assertRaises(EngineeringInputError):
            mesh_center_distance(gear_a={"module_mm":1,"teeth":10},gear_b={"module_mm":1,"teeth":20},mesh_type="internal")

    def test_signed_exact_ratio(self):
        r=signed_ratio([{"driver_teeth":80,"driven_teeth":10,"mesh_type":"external"},
                        {"driver_teeth":60,"driven_teeth":10,"mesh_type":"external"}])
        self.assertEqual(r["output_over_input"],Fraction(48,1))

    def test_fit_worst_case_clearance(self):
        r=fit_clearance(bore_min_mm=1.01,bore_max_mm=1.02,shaft_min_mm=0.99,shaft_max_mm=1.00,
                        evidence_id="SYN",source_revision="fixture")
        self.assertAlmostEqual(r["minimum_diametral_clearance_mm"],0.01)
        self.assertAlmostEqual(r["maximum_diametral_clearance_mm"],0.03)
        self.assertEqual(r["fit_classification"],"NOT_ASSIGNED")

    def test_tolerance_stack_signed_arithmetic(self):
        r=tolerance_stack([{"nominal_mm":2,"tolerance_plus_mm":0.1,"tolerance_minus_mm":0.2,"sign":1},
                           {"nominal_mm":1,"tolerance_plus_mm":0.05,"tolerance_minus_mm":0.05,"sign":-1}])
        self.assertAlmostEqual(r["nominal_mm"],1)
        self.assertAlmostEqual(r["worst_case_min_mm"],0.75)
        self.assertAlmostEqual(r["worst_case_max_mm"],1.15)

    def test_arbor_support_traceability(self):
        r=validate_arbor_register([{"arbor_id":"A1"}],[{"support_id":"S1","arbor_id":"A1","support_type":"jewel_bearing",
            "bore_diameter_mm":0.5,"shaft_diameter_mm":0.4,"axial_position_mm":0,
            "evidence_id":"SYN","source_revision":"fixture"}])
        self.assertEqual(r["status"],"REGISTER_VALIDATION_ONLY")

    def test_axial_interval_overlap(self):
        r=validate_axial_stack([{"plane_id":"P1","z_min_mm":0,"z_max_mm":1,"evidence_id":"SYN","source_revision":"fixture"},
                                {"plane_id":"P2","z_min_mm":0.8,"z_max_mm":1.2,"evidence_id":"SYN","source_revision":"fixture"}])
        self.assertAlmostEqual(r["pairwise_intervals"][0]["overlap_mm"],0.2)
        self.assertFalse(r["clearance_certified"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(EngineeringInputError):
            gear_geometry(module_mm=0,teeth=20,pressure_angle_deg=20,evidence_id="S",source_revision="r")
        with self.assertRaises(EngineeringInputError):
            fit_clearance(bore_min_mm=1.1,bore_max_mm=1.0,shaft_min_mm=.9,shaft_max_mm=1,
                          evidence_id="S",source_revision="r")

if __name__ == "__main__":
    unittest.main()
