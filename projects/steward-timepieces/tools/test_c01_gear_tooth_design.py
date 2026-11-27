import math
import unittest
from c01_gear_tooth_design import (
    GearDesignInputError, involute_function, gear_parameters, involute_points,
    external_mesh_screen, backlash_record
)

class InvoluteGearTests(unittest.TestCase):
    def gear(self,z):
        return gear_parameters(module_mm=0.5,teeth=z,pressure_angle_deg=20,
            addendum_coefficient=1.0,dedendum_coefficient=1.25,profile_shift=0.0,
            evidence_id="SYNTHETIC-FIXTURE",source_revision="test-only")

    def test_involute_function_known_value(self):
        self.assertAlmostEqual(involute_function(0),0.0)
        self.assertAlmostEqual(involute_function(math.radians(20)),math.tan(math.radians(20))-math.radians(20))

    def test_reference_base_addendum_and_root_geometry(self):
        g=self.gear(40)
        self.assertAlmostEqual(g["pitch_diameter_mm"],20.0)
        self.assertAlmostEqual(g["base_diameter_mm"],20*math.cos(math.radians(20)))
        self.assertAlmostEqual(g["addendum_diameter_mm"],21.0)
        self.assertAlmostEqual(g["root_diameter_mm"],18.75)
        self.assertGreater(g["calculated_tip_thickness_mm"],0)

    def test_profile_shift_is_explicit_input(self):
        g=gear_parameters(module_mm=.5,teeth=40,pressure_angle_deg=20,
            addendum_coefficient=1,dedendum_coefficient=1.25,profile_shift=.2,
            evidence_id="SYN",source_revision="fixture")
        self.assertAlmostEqual(g["addendum_radius_mm"],10.6)

    def test_involute_points_are_monotonic_and_bounded(self):
        g=self.gear(40)
        r=involute_points(base_radius_mm=g["base_radius_mm"],addendum_radius_mm=g["addendum_radius_mm"],flank_points=12)
        self.assertEqual(r["point_count"],12)
        self.assertAlmostEqual(math.hypot(*r["points_xy_mm"][0]),g["base_radius_mm"])
        self.assertAlmostEqual(math.hypot(*r["points_xy_mm"][-1]),g["addendum_radius_mm"])
        self.assertIn("NOT_COMPLETE_TOOTH",r["profile_status"])

    def test_external_pair_contact_ratio(self):
        a,b=self.gear(40),self.gear(20)
        r=external_mesh_screen(gear_a=a,gear_b=b,minimum_contact_ratio=1.0)
        self.assertAlmostEqual(r["nominal_reference_center_distance_mm"],15.0)
        self.assertGreater(r["transverse_contact_ratio"],1.0)
        self.assertEqual(r["contact_ratio_screen"],"AT_OR_ABOVE_THRESHOLD")

    def test_zero_shift_undercut_screen_flags_low_tooth_count(self):
        small=self.gear(8); large=self.gear(40)
        r=external_mesh_screen(gear_a=small,gear_b=large)
        self.assertEqual(r["gear_a_zero_shift_undercut_screen"]["zero_shift_screen"],"POTENTIAL_UNDERCUT_RISK")

    def test_backlash_requires_measured_and_approved_values(self):
        r=backlash_record(target_backlash_mm=.02,measured_backlash_mm=.021,tolerance_mm=.005,
            evidence_id="MEAS-1",source_revision="revA")
        self.assertEqual(r["status"],"WITHIN_DECLARED_TOLERANCE")

    def test_invalid_tooth_geometry_fails_closed(self):
        with self.assertRaises(GearDesignInputError):
            gear_parameters(module_mm=.5,teeth=0,pressure_angle_deg=20,addendum_coefficient=1,
                dedendum_coefficient=1.25,profile_shift=0,evidence_id="S",source_revision="r")
        with self.assertRaises(GearDesignInputError):
            involute_points(base_radius_mm=1,addendum_radius_mm=1,flank_points=10)

    def test_incompatible_pair_and_bad_provenance_fail(self):
        a,b=self.gear(20),self.gear(40)
        b=dict(b); b["module_mm"]=.6
        with self.assertRaises(GearDesignInputError):
            external_mesh_screen(gear_a=a,gear_b=b)
        b=dict(self.gear(40)); b["pressure_angle_deg"]=25
        with self.assertRaises(GearDesignInputError):
            external_mesh_screen(gear_a=a,gear_b=b)
        with self.assertRaises(GearDesignInputError):
            gear_parameters(module_mm=.5,teeth=20,pressure_angle_deg=20,addendum_coefficient=1,
                dedendum_coefficient=1.25,profile_shift=0,evidence_id="",source_revision="r")

if __name__=="__main__":
    unittest.main()
