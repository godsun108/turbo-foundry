import tempfile
import unittest
from pathlib import Path

from c01_dial_layout import CANDIDATES, render_candidate, write_all


class DialLayoutTests(unittest.TestCase):
    def test_three_candidates_are_defined(self):
        self.assertEqual([item.key for item in CANDIDATES], ["A", "B", "C"])

    def test_svg_is_dimensionless_and_labels_candidate(self):
        svg = render_candidate(CANDIDATES[0])
        self.assertIn("<svg", svg)
        self.assertIn("Layout A", svg)
        self.assertIn("NORMALIZED COORDINATES, R = 1", svg)
        self.assertIn("Not a dimensioned dial", svg)

    def test_scale_must_be_positive(self):
        with self.assertRaises(ValueError):
            render_candidate(CANDIDATES[0], px_per_radius=0)

    def test_writes_three_svg_sheets(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_all(Path(tmp))
            self.assertEqual(len(paths), 3)
            self.assertTrue(all(path.exists() for path in paths))


if __name__ == "__main__":
    unittest.main()
