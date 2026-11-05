import copy
import json
import unittest
from pathlib import Path

from validate_vocal_score import validate_score


SCORE_PATH = Path(__file__).parents[1] / "projects" / "somebodys-gotta-do-it" / "vocal_score.json"


class VocalScoreValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scaffold = json.loads(SCORE_PATH.read_text(encoding="utf-8"))

    def test_canonical_scaffold_is_structurally_valid(self):
        self.assertEqual(validate_score(self.scaffold), [])

    def test_singing_gate_rejects_unaligned_scaffold(self):
        errors = validate_score(self.scaffold, require_singing_ready=True)
        self.assertTrue(any("not human-reviewed" in error for error in errors))
        self.assertTrue(any("tempo_status must be locked" in error for error in errors))

    def test_duplicate_phrase_ids_rejected(self):
        score = copy.deepcopy(self.scaffold)
        score["phrases"][1]["id"] = score["phrases"][0]["id"]
        self.assertTrue(any("duplicated" in error for error in validate_score(score)))

    def test_phrase_alignment_requires_anchor_timing(self):
        score = copy.deepcopy(self.scaffold)
        phrase = score["phrases"][0]
        phrase["alignment_status"] = "phrase_aligned"
        self.assertTrue(any("lacks start_beat or duration_beats" in error for error in validate_score(score)))

    def test_invalid_midi_pitch_rejected(self):
        score = copy.deepcopy(self.scaffold)
        phrase = score["phrases"][0]
        phrase["syllables"] = [{"text": "Some", "phoneme": "s ʌ m", "onset_beats": 0, "duration_beats": 1,
                               "notes": [{"midi_pitch": 200, "duration_beats": 1, "note_type": "normal"}]}]
        errors = validate_score(score)
        self.assertTrue(any("midi_pitch" in error for error in errors))

    def test_reviewed_sung_phrase_requires_complete_canonical_lyric_units(self):
        score = copy.deepcopy(self.scaffold)
        score["tempo_status"] = "locked"
        score["score_status"] = "reviewed"
        for index, other in enumerate(score["phrases"]):
            if index != 1:
                other["delivery"] = "spoken"
        phrase = score["phrases"][1]
        phrase.update({"alignment_status": "reviewed", "start_beat": 0, "duration_beats": 1,
                       "lyric_units": [{"text": "Make", "phonemes": [], "onset_beats": 0,
                                        "duration_beats": 1, "midi_pitch": 60, "note_type": "normal"}]})
        errors = validate_score(score, require_singing_ready=True)
        self.assertTrue(any("explicit phoneme array is required" in error for error in errors))

    def test_reviewed_sung_phrase_passes_when_canonical_lyric_units_are_complete(self):
        score = copy.deepcopy(self.scaffold)
        score["tempo_status"] = "locked"
        score["score_status"] = "reviewed"
        for index, other in enumerate(score["phrases"]):
            if index != 1:
                other["delivery"] = "spoken"
        phrase = score["phrases"][1]
        phrase.update({"alignment_status": "reviewed", "start_beat": 0, "duration_beats": 1,
                       "lyric_units": [
                           {"text": "Make", "phonemes": ["M", "EY1", "K"], "onset_beats": 0,
                            "duration_beats": 0.25, "midi_pitch": 60, "note_type": "normal"},
                           {"text": "the", "phonemes": ["DH", "AH0"], "onset_beats": 0.25,
                            "duration_beats": 0.25, "midi_pitch": 62, "note_type": "normal"},
                           {"text": "speakers", "phonemes": ["S", "P", "IY1", "K", "ER0", "Z"], "onset_beats": 0.5,
                            "duration_beats": 0.25, "midi_pitch": 64, "note_type": "normal"},
                           {"text": "scream", "phonemes": ["S", "K", "R", "IY1", "M"], "onset_beats": 0.75,
                            "duration_beats": 0.25, "midi_pitch": 67, "note_type": "normal"}
                       ]})
        self.assertEqual(validate_score(score, require_singing_ready=True), [])


if __name__ == "__main__":
    unittest.main()
