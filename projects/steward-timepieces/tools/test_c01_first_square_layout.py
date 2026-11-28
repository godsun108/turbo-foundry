import unittest
from c01_first_square_layout import SVG

class FirstSquareLayoutTests(unittest.TestCase):
    def test_contains_both_layout_layers(self):
        self.assertIn("Movement-side functional topology", SVG)
        self.assertIn("Dial-side display and user interface topology", SVG)

    def test_contains_required_indications(self):
        for label in ("30-minute", "Weekday / date", "Running seconds", "12-hour", "Central"):
            self.assertIn(label, SVG)

    def test_is_explicitly_non_scale(self):
        self.assertIn("NOT TO SCALE", SVG)
        self.assertIn("axes TBD", SVG)

    def test_does_not_claim_dimensions_or_component_centers(self):
        self.assertIn("No component centers, dimensions", SVG)
        self.assertNotIn("30.00 mm", SVG)

if __name__ == "__main__":
    unittest.main()
