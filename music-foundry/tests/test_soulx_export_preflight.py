import json
import unittest
from pathlib import Path

from soulx_export_preflight import build_metadata


SCORE_PATH = Path(__file__).parents[1] / "projects" / "somebodys-gotta-do-it" / "vocal_score.json"


class SoulXExportPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scaffold = json.loads(SCORE_PATH.read_text(encoding="utf-8"))

    def test_current_scaffold_is_blocked_without_writing_metadata(self):
        with self.assertRaisesRegex(ValueError, "tempo_status must be locked"):
            build_metadata(self.scaffold)

    def test_unreviewed_sung_phrase_is_blocked(self):
        score = json.loads(json.dumps(self.scaffold))
        score["tempo_status"] = "locked"
        score["score_status"] = "reviewed"
        with self.assertRaisesRegex(ValueError, "alignment_status"):
            build_metadata(score)

    def test_spoken_only_score_has_no_singing_target(self):
        score = json.loads(json.dumps(self.scaffold))
        score["tempo_status"] = "locked"
        score["score_status"] = "reviewed"
        for phrase in score["phrases"]:
            phrase["delivery"] = "spoken"
        with self.assertRaisesRegex(ValueError, "no sung or chant"):
            build_metadata(score)


if __name__ == "__main__":
    unittest.main()
