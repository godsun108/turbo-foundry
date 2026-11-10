import json
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import song_pipeline


class SongPipelineTests(unittest.TestCase):
    def make_project(self, root: Path):
        project = root / "project"
        project.mkdir()
        (project / "lyrics.md").write_text("# Lyrics\n", encoding="utf-8")
        (project / "production-brief.md").write_text("# Brief\n", encoding="utf-8")
        (project / "generation-prompt.txt").write_text("Original song prompt\n", encoding="utf-8")
        (project / "project.json").write_text(json.dumps({
            "title": "Test Song", "project_id": "test-song", "bpm": 126,
            "arrangement_bars": 32, "target_duration_seconds": 61,
            "lyrics": "lyrics.md", "production_brief": "production-brief.md",
            "generation_prompt": "generation-prompt.txt"
        }), encoding="utf-8")
        return project

    def test_preflight_reports_missing_score_and_local_model_without_failing(self):
        with tempfile.TemporaryDirectory() as temp:
            project = self.make_project(Path(temp))
            report = song_pipeline.inspect_project(project, None)
            self.assertEqual(report["stages"]["creative_source"]["status"], "ready")
            self.assertEqual(report["stages"]["vocal_direction"]["status"], "blocked")
            self.assertEqual(report["stages"]["vocal_score"]["status"], "blocked")
            self.assertEqual(report["stages"]["soulx_runtime"]["status"], "blocked")
            self.assertFalse(report["ready_for_local_singing_render"])
            self.assertTrue(report["policy"]["no_hosted_provider"])

    def test_reviewed_score_still_requires_model_and_reference_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            project = self.make_project(Path(temp))
            score = {
                "score_status": "reviewed", "tempo_status": "locked",
                "phrases": [{"delivery": "sung", "alignment_status": "reviewed",
                             "lyric_units": [{"text": "Hello"}]}]
            }
            (project / "vocal_score.json").write_text(json.dumps(score), encoding="utf-8")
            report = song_pipeline.inspect_project(project, None)
            self.assertEqual(report["stages"]["vocal_score"]["status"], "ready")
            self.assertFalse(report["ready_for_local_singing_render"])
            self.assertEqual(report["stages"]["singing_reference"]["status"], "blocked")

    def test_midi_execution_calls_existing_generator(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = self.make_project(root)
            output = root / "out"
            with patch("song_pipeline.subprocess.run") as run_mock:
                run_mock.return_value.returncode = 0
                run_mock.return_value.stdout = "generated"
                run_mock.return_value.stderr = ""
                report = song_pipeline.run(project, output, execute_midi=True)
            self.assertEqual(report["stages"]["midi"]["status"], "completed")
            self.assertTrue((output / "pipeline-report.json").is_file())
            self.assertIn("--bars", run_mock.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
