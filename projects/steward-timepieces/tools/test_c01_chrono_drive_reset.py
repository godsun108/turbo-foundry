import unittest
from c01_chrono_drive_reset import (
    evaluate_drive_path, evaluate_branch, reset_work_from_samples,
    compare_reset_energy, validate_reset_definition,
)

class ChronographDriveResetTests(unittest.TestCase):
    def test_exact_signed_drive_path(self):
        r = evaluate_drive_path("1", [
            {"driver_teeth": 10, "driven_teeth": 60, "mesh_type": "external", "evidence_id": "S1"},
            {"driver_teeth": 12, "driven_teeth": 36, "mesh_type": "external", "evidence_id": "S2"},
        ])
        self.assertEqual(r["signed_ratio"], "1/18")
        self.assertEqual(r["output_rpm"], "1/18")
        self.assertEqual(r["direction"], "same")

    def test_bad_tooth_count_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_drive_path(1, [{"driver_teeth": 0, "driven_teeth": 5, "mesh_type": "external", "evidence_id": "S"}])

    def test_branch_compares_only_supplied_tolerance(self):
        r = evaluate_branch(1, [{"driver_teeth": 1, "driven_teeth": 60, "mesh_type": "external", "evidence_id": "S"}], 3600, 0)
        self.assertTrue(r["passes_supplied_tolerance"])

    def test_reset_work_trapezoidal_integration(self):
        r = reset_work_from_samples([
            {"angle_rad": 0, "torque_nm": 1, "evidence_id": "M1"},
            {"angle_rad": 1, "torque_nm": 1, "evidence_id": "M2"},
            {"angle_rad": 2, "torque_nm": 1, "evidence_id": "M3"},
        ])
        self.assertEqual(r["measured_reset_work_j"], "2")

    def test_non_monotonic_samples_rejected(self):
        with self.assertRaises(ValueError):
            reset_work_from_samples([
                {"angle_rad": 1, "torque_nm": 1, "evidence_id": "M1"},
                {"angle_rad": 0, "torque_nm": 1, "evidence_id": "M2"},
            ])

    def test_energy_comparison_requires_traceability(self):
        with self.assertRaises(ValueError):
            compare_reset_energy(1, 2, "", "EV")

    def test_energy_comparison_is_not_physical_proof(self):
        r = compare_reset_energy("0.5", "0.7", "BOUNDARY-1", "EV-1")
        self.assertTrue(r["nonnegative_margin"])
        self.assertFalse(r["losses_and_dynamic_peaks_included"])

    def test_reset_definition_requires_complete_interfaces(self):
        with self.assertRaises(ValueError):
            validate_reset_definition({"definition_id": "R1"})

if __name__ == "__main__":
    unittest.main()
