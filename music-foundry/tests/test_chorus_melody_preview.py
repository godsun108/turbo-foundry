import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "build_chorus_melody_preview.py"
SPEC = importlib.util.spec_from_file_location("chorus_melody_preview", SCRIPT)
preview = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preview)


class ChorusMelodyPreviewTests(unittest.TestCase):
    def test_preview_has_four_response_phrases_and_expected_notes(self):
        notes = preview.build_notes()
        self.assertEqual(len(notes), 18)
        self.assertEqual([note[0] for note in notes[:4]], [69, 69, 72, 77])
        self.assertEqual(notes[0][1], preview.BAR)
        self.assertEqual(notes[-1][1] + notes[-1][2], 32 * preview.PPQ)

    def test_builds_standalone_type_one_midi_without_changing_score(self):
        with tempfile.TemporaryDirectory() as directory:
            path = preview.make(Path(directory) / "chorus.mid")
            data = path.read_bytes()
            self.assertEqual(data[:4], b"MThd")
            self.assertEqual(int.from_bytes(data[4:8], "big"), 6)
            self.assertEqual(int.from_bytes(data[8:10], "big"), 1)
            self.assertEqual(int.from_bytes(data[10:12], "big"), 2)
            self.assertEqual(int.from_bytes(data[12:14], "big"), preview.PPQ)
            self.assertIn(b"\x00\xff\x51\x03", data)
            self.assertEqual(len(data.split(b"MTrk")) - 1, 2)


if __name__ == "__main__":
    unittest.main()
