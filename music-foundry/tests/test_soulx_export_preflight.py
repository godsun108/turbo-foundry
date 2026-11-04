import copy
import json
import unittest
from pathlib import Path

from soulx_export_preflight import preflight


SCORE_PATH = Path(__file__).parents[1] / "projects" / "somebodys-gotta-do-it" / "vocal_score.json"


class SoulXExportPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scaffold = json.loads(SCORE_PATH.read_text(encoding="utf-8"))

    def test_current_scaffold_is_blocked_without_generating_metadata(self):
        blockers = preflight(self.scaffold)
        self.assertTrue(any("tempo_status must be locked" in item for item in blockers))
        self.assertTrue(any("syllable map is missing" in item for item in blockers))
        self.assertTrue(any("word-boundary segmentation" in item for item in blockers))
        self.assertTrue(any("note_type mapping" in item for item in blockers))

    def test_unreviewed_sung_phrase_is_blocked(self):
        score = copy.deepcopy(self.scaffold)
        score["tempo_status"] = "locked"
        score["score_status"] = "reviewed"
        blockers = preflight(score)
        self.assertTrue(any("phrase must be human-reviewed" in item for item in blockers))

    def test_spoken_only_score_has_no_singing_target(self):
        score = copy.deepcopy(self.scaffold)
        for phrase in score["phrases"]:
            phrase["delivery"] = "spoken"
        blockers = preflight(score)
        self.assertTrue(any("no sung or chant phrases" in item for item in blockers))


if __name__ == "__main__":
    unittest.main()
