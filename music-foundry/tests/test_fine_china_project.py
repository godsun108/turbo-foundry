import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fine_china_arrangement", ROOT / "fine_china_arrangement.py")
ARRANGEMENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARRANGEMENT)


class FineChinaProjectTests(unittest.TestCase):
    def test_full_arrangement_is_120_bars_at_126_bpm(self):
        self.assertEqual(sum(length for _, length in ARRANGEMENT.SECTIONS), 120)
        self.assertEqual(ARRANGEMENT.BPM, 126)
        self.assertEqual(
            [name for name, _ in ARRANGEMENT.SECTIONS],
            ["intro", "verse_1", "pre_chorus_1", "chorus_1", "verse_2",
             "pre_chorus_2", "chorus_2", "bridge", "final_chorus", "outro"]
        )

    def test_original_progression_and_track_lanes(self):
        tracks, arrangement = ARRANGEMENT.build_notes()
        self.assertEqual(set(tracks), {"chords", "bass", "lead", "drums", "texture"})
        self.assertEqual([name for name in ARRANGEMENT.CHORDS], ["Am", "F", "C", "G"])
        self.assertEqual(len(arrangement), 10)
        self.assertTrue(tracks["bass"])
        self.assertTrue(tracks["drums"])

    def test_fine_china_chorus_score_has_73_placed_syllables(self):
        score_path = ROOT / "projects" / "fine-china" / "vocal_score_draft.json"
        score = json.loads(score_path.read_text(encoding="utf-8"))
        self.assertEqual(score["project_id"], "fine-china")
        self.assertEqual(score["tempo_bpm"], 126)
        events = [
            syllable for phrase in score["phrases"]
            if phrase.get("layer") != "rest"
            for syllable in phrase.get("syllables", [])
            if syllable.get("text") and syllable.get("text") != "<SP>"
        ]
        self.assertEqual(len(events), 73)
        self.assertTrue(all(isinstance(item.get("midi_pitch"), int) for item in events))
        self.assertTrue(all(isinstance(item.get("onset_beats"), (int, float)) for item in events))


if __name__ == "__main__":
    unittest.main()
