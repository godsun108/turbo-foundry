import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

from soulx_local_runner import run_render


class SoulXLocalRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.engine = self.root / "soulx"
        for relative in (
            "cli/inference.py",
            "soulxsinger/config/soulxsinger.yaml",
            "soulxsinger/utils/phoneme/phone_set.json",
            "pretrained_models/SoulX-Singer/model.pt",
        ):
            path = self.engine / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture", encoding="utf-8")
        self.prompt = self.root / "prompt.wav"
        with wave.open(str(self.prompt), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(24000)
            audio.writeframes(b"\x00\x00" * 240)
        self.prompt_meta = self.root / "prompt.json"
        self.prompt_meta.write_text(json.dumps([{"text": "hello"}]), encoding="utf-8")
        self.score = self.root / "score.json"
        self.score.write_text(json.dumps(self._reviewed_score()), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _reviewed_score():
        return {
            "project_id": "test-song",
            "tempo_bpm": 120,
            "tempo_status": "locked",
            "score_status": "reviewed",
            "phrases": [{
                "id": "hook", "delivery": "sung", "alignment_status": "reviewed",
                "start_beat": 0, "duration_beats": 1, "text": "Hey",
                "lyric_units": [{
                    "text": "Hey", "phonemes": ["HH", "EY1"],
                    "onset_beats": 0, "duration_beats": 1,
                    "midi_pitch": 64, "note_type": "normal",
                }],
            }],
        }

    def test_builds_score_control_command_and_validated_manifest(self):
        output = self.root / "render"
        def fake_run(command, **kwargs):
            self.assertIn("--control", command)
            self.assertEqual(command[command.index("--control") + 1], "score")
            self.assertNotIn("--fp16", command)
            self.assertEqual(kwargs["cwd"], str(self.engine.resolve()))
            with wave.open(str(output / "generated.wav"), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(24000)
                audio.writeframes(b"\x00\x00" * 2400)
            class Result:
                returncode = 0
                stdout = "render ok"
                stderr = ""
            return Result()
        with patch("soulx_local_runner.subprocess.run", side_effect=fake_run):
            result = run_render(
                score_path=self.score,
                engine_root=self.engine,
                prompt_wav=self.prompt,
                prompt_metadata=self.prompt_meta,
                output_dir=output,
                python_executable=sys.executable,
            )
        self.assertEqual(result["status"], "rendered")
        self.assertEqual(result["control"], "score")
        self.assertEqual(result["audio"]["sample_rate"], 24000)
        self.assertTrue((output / "singing_render_manifest.json").is_file())
        self.assertTrue((output / "target_metadata.json").is_file())

    def test_rejects_unreviewed_score_before_dispatch(self):
        data = self._reviewed_score()
        data["tempo_status"] = "provisional"
        self.score.write_text(json.dumps(data), encoding="utf-8")
        with patch("soulx_local_runner.subprocess.run") as execute:
            with self.assertRaisesRegex(ValueError, "tempo_status"):
                run_render(
                    score_path=self.score, engine_root=self.engine,
                    prompt_wav=self.prompt, prompt_metadata=self.prompt_meta,
                    output_dir=self.root / "blocked",
                )
            execute.assert_not_called()

    def test_refuses_nonempty_output_directory(self):
        output = self.root / "occupied"
        output.mkdir()
        (output / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "never overwritten"):
            run_render(
                score_path=self.score, engine_root=self.engine,
                prompt_wav=self.prompt, prompt_metadata=self.prompt_meta,
                output_dir=output,
            )

    def test_requires_nonempty_prompt_metadata(self):
        self.prompt_meta.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "non-empty JSON array"):
            run_render(
                score_path=self.score, engine_root=self.engine,
                prompt_wav=self.prompt, prompt_metadata=self.prompt_meta,
                output_dir=self.root / "blocked",
            )

    def test_rejects_wrong_output_sample_rate(self):
        output = self.root / "bad-render"
        def fake_run(command, **kwargs):
            with wave.open(str(output / "generated.wav"), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(44100)
                audio.writeframes(b"\x00\x00" * 240)
            class Result:
                returncode = 0
                stdout = ""
                stderr = ""
            return Result()
        with patch("soulx_local_runner.subprocess.run", side_effect=fake_run):
            with self.assertRaisesRegex(ValueError, "expected mono 24000 Hz"):
                run_render(
                    score_path=self.score, engine_root=self.engine,
                    prompt_wav=self.prompt, prompt_metadata=self.prompt_meta,
                    output_dir=output,
                )


if __name__ == "__main__":
    unittest.main()
