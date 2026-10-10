import importlib.util
import tempfile
import unittest
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "generate.py"
spec = importlib.util.spec_from_file_location("music_generator", module_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GeneratorTests(unittest.TestCase):
    def test_midi_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod.make(tmp, 122, 4)
            for name in ("chords", "bass", "lead", "drums"):
                data = (Path(tmp) / (name + ".mid")).read_bytes()
                self.assertTrue(data.startswith(b"MThd"))
                self.assertIn(b"MTrk", data)
                self.assertTrue(data.endswith(b"\x00\xff\x2f\x00"))
            self.assertTrue((Path(tmp) / "manifest.json").exists())

    def test_invalid_bpm(self):
        with self.assertRaises(ValueError):
            mod.make("unused", 0, 4)

if __name__ == "__main__":
    unittest.main()
