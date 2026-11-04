import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from build_vocal_score_worksheet import build_worksheet

SCORE_PATH = Path(__file__).parents[1] / "projects" / "somebodys-gotta-do-it" / "vocal_score.json"

class VocalScoreWorksheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.score = json.loads(SCORE_PATH.read_text(encoding="utf-8"))

    def test_worksheet_contains_only_sung_hook_phrases(self):
        worksheet = build_worksheet(self.score)
        for phrase_id in ("chorus_02", "chorus_04", "chorus_06", "chorus_08"):
            self.assertIn("## " + phrase_id, worksheet)
        self.assertNotIn("## chorus_01", worksheet)

    def test_word_tokens_preserve_source_lyrics_and_have_blank_score_fields(self):
        worksheet = build_worksheet(self.score)
        self.assertIn("| 1 | Make |  |  |  |  | normal / tie / rest |", worksheet)
        self.assertIn("| 3 | speakers |  |  |  |  | normal / tie / rest |", worksheet)
        self.assertIn("**Source lyric (verbatim):** And tonight that somebody's me", worksheet)

    def test_worksheet_refuses_missing_phrases(self):
        with self.assertRaisesRegex(ValueError, "phrases array"):
            build_worksheet({"project_id": "x"})

    def test_worksheet_refuses_empty_singing_set(self):
        score = {"phrases": [{"delivery": "spoken", "text": "hello"}]}
        with self.assertRaisesRegex(ValueError, "no sung or chant"):
            build_worksheet(score)

if __name__ == "__main__":
    unittest.main()
