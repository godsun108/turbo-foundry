import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "arrange_project.py"
spec = importlib.util.spec_from_file_location("project_arranger", SCRIPT)
arranger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arranger)


class ProjectArrangementTests(unittest.TestCase):
    def test_full_arrangement_exports_four_midi_parts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = arranger.make(tmp, 127)
            for name in ("chords", "bass", "lead", "drums"):
                data = (out / f"{name}.mid").read_bytes()
                self.assertTrue(data.startswith(b"MThd"))
                self.assertIn(b"MTrk", data)
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["bpm"], 127)
            self.assertEqual(manifest["bars"], 56)
            self.assertEqual(len(manifest["arrangement"]), 8)
            self.assertEqual(manifest["tracks"], ["chords", "bass", "lead", "drums"])

    def test_invalid_tempo_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                arranger.make(tmp, 0)


if __name__ == "__main__":
    unittest.main()
