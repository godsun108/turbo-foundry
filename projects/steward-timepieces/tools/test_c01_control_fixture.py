import unittest

from c01_control_fixture import generate_openscad, validate_fixture


def synthetic_fixture():
    provenance = {"evidence_id": "SYN-EVIDENCE", "source_revision": "SYN-REV"}
    base = {
        "outline_xy_mm": [[0, 0], [100, 0], [100, 80], [0, 80]],
        "thickness_mm": 8, "top_z_mm": 8, **provenance,
        "mounting_holes": [{"id": "BH1", "xy_mm": [10, 10], "diameter_mm": 5, **provenance}],
    }
    carriers = []
    for architecture, ident in (("column_wheel", "SYN-CW"), ("cam_lever", "SYN-CL")):
        carriers.append({
            "architecture": architecture, "carrier_id": ident,
            "outline_xy_mm": [[20, 20], [80, 20], [80, 60], [20, 60]],
            "thickness_mm": 4, "top_z_mm": 12,
            "registration_scheme_id": "SYN-REG", **provenance,
            "mounting_holes": [{"id": ident+"-H1", "xy_mm": [25, 25],
                                "diameter_mm": 4, **provenance}],
        })
    mounts = []
    roles = ("pusher_actuator", "force_transducer", "travel_sensor", "optical_view")
    for i, role in enumerate(roles):
        mounts.append({
            "mount_id": "SYN-M"+str(i), "role": role,
            "origin_xyz_mm": [0, 0, 20 if role != "force_transducer" else 10],
            "axis_xyz": [0, 0, 1], "envelope_radius_mm": 3,
            "envelope_length_mm": 20, **provenance,
        })
    return {
        "fixture_id": "SYN-WP47", "revision": "SYN-A", "provenance": provenance,
        "base": base, "carriers": carriers, "instrument_mounts": mounts,
        "actuator_alignment_tolerance": {"max_axis_offset_mm": 0.1, "max_axis_angle_deg": 0.5},
        "guard_envelope": {"min_xyz_mm": [-5, -5, 0], "max_xyz_mm": [105, 85, 40], **provenance},
    }


class TestControlFixture(unittest.TestCase):
    def test_validates_both_interchangeable_carriers(self):
        result = validate_fixture(synthetic_fixture())
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(set(result["carrier_architectures"]), {"column_wheel", "cam_lever"})
        self.assertFalse(result["construction_authorized"])

    def test_detects_axis_misalignment(self):
        cfg = synthetic_fixture()
        cfg["instrument_mounts"][1]["origin_xyz_mm"] = [2, 0, 10]
        result = validate_fixture(cfg)
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(result["actuator_alignment"]["within_supplied_tolerances"])

    def test_alignment_not_claimed_without_tolerance(self):
        cfg = synthetic_fixture()
        del cfg["actuator_alignment_tolerance"]
        result = validate_fixture(cfg)
        self.assertFalse(result["actuator_alignment"]["evaluated"])

    def test_requires_both_architecture_carriers(self):
        cfg = synthetic_fixture()
        cfg["carriers"].pop()
        self.assertFalse(validate_fixture(cfg)["valid"])

    def test_rejects_missing_provenance(self):
        cfg = synthetic_fixture()
        del cfg["base"]["evidence_id"]
        self.assertFalse(validate_fixture(cfg)["valid"])

    def test_openscad_generation_is_parametric_and_gated(self):
        source = generate_openscad(synthetic_fixture())
        self.assertIn("show_column_wheel_carrier", source)
        self.assertIn("carrier_column_wheel", source)
        self.assertIn("carrier_cam_lever", source)
        self.assertIn("guard_envelope", source)
        with self.assertRaises(ValueError):
            generate_openscad({"fixture_id": "invalid"})


if __name__ == "__main__":
    unittest.main()
