import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from soulx_prepare_prompt import prepare_prompt


class SoulXPromptPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.engine = self.root / "soulx"
        pipeline = self.engine / "preprocess" / "pipeline.py"
        pipeline.parent.mkdir(parents=True)
        pipeline.write_text("# official pipeline fixture", encoding="utf-8")
        self.source = self.root / "reference.wav"
        self.source.write_bytes(b"reference audio fixture")

    def tearDown(self):
        self.temp.cleanup()

    def test_prepares_english_prompt_in_isolated_output_directory(self):
        output = self.root / "prepared"
        def fake_run(command, **kwargs):
            self.assertIn("--language", command)
            self.assertEqual(command[command.index("--language") + 1], "English")
            self.assertEqual(command[command.index("--vocal_sep") + 1], "False")
            self.assertEqual(command[command.index("--midi_transcribe") + 1], "True")
            self.assertEqual(kwargs["cwd"], str(self.engine.resolve()))
            (output / "metadata.json").write_text(json.dumps([{"text": "hello"}]), encoding="utf-8")
            (output / "vocal.wav").write_bytes(b"prepared vocal fixture")
            class Result:
                returncode = 0
                stdout = "preprocess ok"
                stderr = ""
            return Result()
        with patch("soulx_prepare_prompt.subprocess.run", side_effect=fake_run):
            result = prepare_prompt(
                source_audio=self.source, engine_root=self.engine, output_dir=output
            )
        self.assertEqual(result["status"], "prepared")
        self.assertEqual(result["segments"], 1)
        self.assertTrue((output / "singing_prompt_manifest.json").is_file())
        self.assertTrue((output / "reference_prompt.wav").is_file())

    def test_refuses_to_overwrite_existing_output(self):
        output = self.root / "occupied"
        output.mkdir()
        (output / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "never overwritten"):
            prepare_prompt(
                source_audio=self.source, engine_root=self.engine, output_dir=output
            )

    def test_rejects_empty_preprocessor_metadata(self):
        output = self.root / "empty"
        def fake_run(command, **kwargs):
            (output / "metadata.json").write_text("[]", encoding="utf-8")
            (output / "vocal.wav").write_bytes(b"wav")
            class Result:
                returncode = 0
                stdout = ""
                stderr = ""
            return Result()
        with patch("soulx_prepare_prompt.subprocess.run", side_effect=fake_run):
            with self.assertRaisesRegex(ValueError, "non-empty array"):
                prepare_prompt(
                    source_audio=self.source, engine_root=self.engine, output_dir=output
                )

    def test_rejects_unsupported_source_audio_extension(self):
        unsupported = self.root / "reference.aac"
        unsupported.write_bytes(b"audio")
        with self.assertRaisesRegex(ValueError, "WAV, MP3, or FLAC"):
            prepare_prompt(
                source_audio=unsupported, engine_root=self.engine,
                output_dir=self.root / "unsupported",
            )


if __name__ == "__main__":
    unittest.main()
