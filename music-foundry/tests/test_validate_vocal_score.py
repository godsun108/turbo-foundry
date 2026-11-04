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
        self.assertTrue(any("lacks start_beat or duration_beats" in error
                            for error in validate_score(score)))

    def test_invalid_midi_pitch_rejected(self):
        score = copy.deepcopy(self.scaffold)
        phrase = score["phrases"][0]
        phrase["syllables"] = [{
            "text": "Some", "phoneme": "s ʌ m", "onset_beats": 0,
            "duration_beats": 1, "notes": [{
                "midi_pitch": 200, "duration_beats": 1, "note_type": "normal"
            }]
        }]
        errors = validate_score(score)
        self.assertTrue(any("midi_pitch" in error for error in errors))

    def test_reviewed_sung_phrase_requires_complete_syllables_and_notes(self):
        score = copy.deepcopy(self.scaffold)
        score["tempo_status"] = "locked"
        score["score_status"] = "reviewed"
        for other in (score["phrases"][3], score["phrases"][5], score["phrases"][7]):
            other["delivery"] = "gang_shout"
        phrase = score["phrases"][1]
        phrase.update({
            "alignment_status": "reviewed",
            "start_beat": 0,
            "duration_beats": 4,
            "syllables": [{
                "text": "Make", "phoneme": None, "onset_beats": None,
                "duration_beats": None, "notes": []
            }]
        })
        errors = validate_score(score, require_singing_ready=True)
        self.assertTrue(any("lacks phoneme" in error for error in errors))
        self.assertTrue(any("lacks onset/duration" in error for error in errors))
        self.assertTrue(any("no note events" in error for error in errors))

    def test_reviewed_sung_phrase_passes_when_fully_specified(self):
        score = copy.deepcopy(self.scaffold)
        score["tempo_status"] = "locked"
        score["score_status"] = "reviewed"
        for other in (score["phrases"][3], score["phrases"][5], score["phrases"][7]):
            other["delivery"] = "gang_shout"
        phrase = score["phrases"][1]
        phrase.update({
            "alignment_status": "reviewed",
            "start_beat": 0,
            "duration_beats": 1,
            "syllables": [{
                "text": "Make", "phoneme": "m eɪ k", "onset_beats": 0,
                "duration_beats": 1, "notes": [{
                    "midi_pitch": 60, "duration_beats": 1,
                    "note_type": "normal", "f0_hz": None
                }]
            }]
        })
        self.assertEqual(validate_score(score, require_singing_ready=True), [])


if __name__ == "__main__":
    unittest.main()
