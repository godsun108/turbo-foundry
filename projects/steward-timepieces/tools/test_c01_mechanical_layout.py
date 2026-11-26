import unittest

from c01_mechanical_layout import (
    CANDIDATES, Zone, build_model, overlaps, validate_zone,
)


class MechanicalLayoutTests(unittest.TestCase):
    def test_three_candidates_share_core_architecture(self):
        self.assertEqual(set(CANDIDATES), {"A", "B", "C"})
        core_names = {"barrel_reservation", "balance_reservation",
                      "going_train_corridor", "chronograph_reservation",
                      "rotor_sweep", "calendar_mechanism"}
        for candidate in CANDIDATES.values():
            self.assertTrue(core_names.issubset({z.name for z in candidate.zones}))

    def test_candidate_c_flags_upper_calendar_review(self):
        self.assertIn("Upper calendar/register interaction",
                      CANDIDATES["C"].calendar_note)

    def test_overlap_requires_same_layer(self):
        a = Zone("a", "dial_side", 0, 0, 1, 1)
        b = Zone("b", "dial_side", 0.2, 0.2, 1, 1)
        c = Zone("c", "movement_side", 0.2, 0.2, 1, 1)
        self.assertTrue(overlaps(a, b))
        self.assertFalse(overlaps(a, c))

    def test_invalid_dimensions_are_rejected(self):
        self.assertTrue(validate_zone(Zone("bad", "dial_side", 0, 0, 0, 1)))

    def test_model_marks_all_zones_provisional(self):
        model = build_model()
        self.assertEqual(model["units"], "normalized dial-opening radius (R=1); not millimetres")
        for candidate in model["candidates"].values():
            self.assertTrue(all(z["status"] == "provisional" for z in candidate["zones"]))

    def test_unknown_axes_remain_tbd(self):
        model = build_model()
        axes = model["shared_arbor_axes"]
        self.assertEqual(axes[1]["status"], "TBD")
        self.assertIsNone(axes[1]["x"])


if __name__ == "__main__":
    unittest.main()
