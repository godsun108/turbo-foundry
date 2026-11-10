import json
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import song_pipeline
import vocal_score_midi


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

    def test_approved_vocal_direction_profile_is_reported_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            project = self.make_project(Path(temp))
            profile = {
                "verse_delivery": "spoken",
                "pre_chorus_delivery": "rhythmic sung",
                "chorus_delivery": "soulful melodic",
                "bridge_delivery": "spoken",
                "gang_response": "layered group shouts"
            }
            (project / "vocal_direction.json").write_text(json.dumps(profile), encoding="utf-8")
            report = song_pipeline.inspect_project(project, None)
            self.assertEqual(report["stages"]["vocal_direction"]["status"], "ready")

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

    def test_vocal_score_midi_builds_draft_guide_without_external_dependencies(self):
        score = {
            "project_id": "fine-china",
            "tempo_bpm": 126,
            "ppq": 480,
            "score_status": "composition_draft",
            "phrases": [{
                "id": "hook",
                "delivery": "sung",
                "start_beat": 128,
                "duration_beats": 2,
                "lyric_units": [
                    {"text": "Fine", "onset_beats": 0, "duration_beats": 1,
                     "midi_pitch": 69, "note_type": "normal"},
                    {"text": "China", "onset_beats": 1, "duration_beats": 1,
                     "midi_pitch": 67, "note_type": "normal"}
                ]
            }]
        }
        midi, report = vocal_score_midi.build_midi(score)
        self.assertTrue(midi.startswith(b"MThd"))
        self.assertEqual(report["status"], "draft_preview_only")
        self.assertEqual(report["note_events"], 2)
        self.assertEqual(report["duration_beats"], 2)
        self.assertEqual(report["start_beat_in_source"], 128)

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
