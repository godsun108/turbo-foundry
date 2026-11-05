import copy
import json
import unittest
from pathlib import Path

from soulx_export import build_metadata


SCORE_PATH = Path(__file__).parents[1] / "projects" / "somebodys-gotta-do-it" / "vocal_score.json"


def aligned_fixture():
    score = json.loads(SCORE_PATH.read_text(encoding="utf-8"))
    score["tempo_status"] = "locked"
    score["score_status"] = "reviewed"
    for phrase in score["phrases"]:
        phrase["delivery"] = "gang_shout"
    phrase = score["phrases"][1]
    phrase.update({
        "delivery": "sung",
        "alignment_status": "reviewed",
        "start_beat": 8,
        "duration_beats": 4,
        "lyric_units": [
            {"text": "Make", "phonemes": ["M", "EY1", "K"], "onset_beats": 0, "duration_beats": 1, "midi_pitch": 60, "note_type": "normal"},
            {"text": "the", "phonemes": ["DH", "AH0"], "onset_beats": 1, "duration_beats": 1, "midi_pitch": 62, "note_type": "normal"},
            {"text": "speakers", "phonemes": ["S", "P", "IY1", "K", "ER0", "Z"], "onset_beats": 2, "duration_beats": 1, "midi_pitch": 64, "note_type": "tie"},
            {"text": "scream", "phonemes": ["S", "K", "R", "IY1", "M"], "onset_beats": 3, "duration_beats": 1, "midi_pitch": 65, "note_type": "normal"},
        ]
    })
    return score


class SoulXExportTests(unittest.TestCase):
    def test_current_scaffold_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "locked"):
            build_metadata(json.loads(SCORE_PATH.read_text(encoding="utf-8")))

    def test_explicit_reviewed_word_units_export_score_control_metadata(self):
        metadata = build_metadata(aligned_fixture())
        self.assertEqual(len(metadata), 1)
        segment = metadata[0]
        self.assertEqual(segment["time"], [3780, 5669])
        self.assertEqual(segment["text"], "Make the speakers scream")
        self.assertEqual(segment["phoneme"], "en_M-EY1-K en_DH-AH0 en_S-P-IY1-K-ER0-Z en_S-K-R-IY1-M")
        self.assertEqual(segment["note_pitch"], "60 62 64 65")
        self.assertEqual(segment["note_type"], "2 2 3 2")
        self.assertNotIn("f0", segment)

    def test_gang_shout_phrase_can_be_rendered_as_score_control_vocal(self):\n        score = aligned_fixture()\n        score["phrases"][1]["delivery"] = "gang_shout"\n        metadata = build_metadata(score)\n        self.assertEqual(len(metadata), 1)\n        self.assertEqual(metadata[0]["text"], "Make the speakers scream")\n\n    def test_missing_word_grouping_rejected(self):
        score = aligned_fixture()
        del score["phrases"][1]["lyric_units"]
        with self.assertRaisesRegex(ValueError, "lyric_units"):
            build_metadata(score)

    def test_unknown_note_type_rejected(self):
        score = aligned_fixture()
        score["phrases"][1]["lyric_units"][0]["note_type"] = "slur"
        with self.assertRaisesRegex(ValueError, "note_type"):
            build_metadata(score)

    def test_phoneme_must_exist_in_official_english_phone_set(self):
        score = aligned_fixture()
        score["phrases"][1]["lyric_units"][0]["phonemes"] = ["NOT_A_PHONE"]
        with self.assertRaisesRegex(ValueError, "explicit ARPABET"):
            build_metadata(score)

    def test_implicit_timing_gap_rejected(self):
        score = aligned_fixture()
        score["phrases"][1]["lyric_units"][1]["onset_beats"] = 1.25
        with self.assertRaisesRegex(ValueError, "contiguous"):
            build_metadata(score)

    def test_word_unit_cannot_contain_multiple_words(self):
        score = aligned_fixture()
        score["phrases"][1]["lyric_units"][0]["text"] = "Make the"
        with self.assertRaisesRegex(ValueError, "exactly one word"):
            build_metadata(score)

    def test_word_text_must_preserve_source_lyric(self):
        score = aligned_fixture()
        score["phrases"][1]["lyric_units"][0]["text"] = "Change"
        with self.assertRaisesRegex(ValueError, "exactly reproduce"):
            build_metadata(score)

    def test_rest_requires_explicit_silence_token(self):
        score = aligned_fixture()
        unit = score["phrases"][1]["lyric_units"][0]
        unit.update({"midi_pitch": 0, "note_type": "rest"})
        with self.assertRaisesRegex(ValueError, "rest must use text <SP>"):
            build_metadata(score)


if __name__ == "__main__":
    unittest.main()
