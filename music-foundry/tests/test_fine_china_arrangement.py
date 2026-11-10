import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fine_china_arrangement", ROOT / "fine_china_arrangement.py")
ARR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARR)


class FineChinaArrangementTests(unittest.TestCase):
    def test_locked_song_blueprint(self):
        self.assertEqual(ARR.BPM, 126)
        self.assertEqual(sum(bars for _, bars in ARR.SECTIONS), 120)
        self.assertEqual(ARR.CHORDS["Am"], (45, 48, 52))
        self.assertEqual(ARR.CHORDS["F"], (41, 45, 48))
        self.assertEqual(ARR.CHORDS["C"], (48, 52, 55))
        self.assertEqual(ARR.CHORDS["G"], (43, 47, 50))

    def test_arrangement_contains_groove_and_hook(self):
        tracks, sections = ARR.build_notes()
        self.assertEqual(len(sections), 10)
        self.assertTrue(all(tracks[name] for name in ("chords", "bass", "lead", "drums", "texture")))
        self.assertGreater(len(tracks["drums"]), 1000)
        self.assertGreater(len(tracks["bass"]), 500)
        # First chorus begins at beat 128: bar 32, matching the saved vocal score.
        chorus = next(s for s in sections if s["name"] == "chorus_1")
        self.assertEqual(chorus["start_bar"], 32)


if __name__ == "__main__":
    unittest.main()
