import importlib.util
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vocal_render_contract import make_render_request
from genesis_voice_adapter import (
    ENGINE_SCHEMA,
    VoiceRenderError,
    render_spoken,
    validate_engine_descriptor,
)


class GenesisVoiceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.model = self.root / "voice.onnx"
        self.model.write_bytes(b"test fixture; not a real model")
        self.output = self.root / "spoken.wav"
        self.descriptor = {
            "schema": ENGINE_SCHEMA,
            "engine": "piper-cli",
            "execution": "local",
            "modes": ["spoken"],
            "executable": sys.executable,
            "model_path": str(self.model),
            "timeout_seconds": 10,
            "credential_handling": "none",
        }
        self.request = make_render_request(
            project_id="somebodys-gotta-do-it",
            source_ref="projects/somebodys-gotta-do-it/cue-sheet.md",
            mode="spoken",
            layers=["dry_lead"],
            sample_rate=48000,
            bit_depth=16,
            channels=2,
        )

    def tearDown(self):
        self.temp.cleanup()

    def fake_runner(self, command, **kwargs):
        output = Path(command[command.index("--output_file") + 1])
        with wave.open(str(output), "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(22050)
            writer.writeframes(struct.pack("<" + "h" * 128, *range(128)))
        return Mock(returncode=0, stdout="", stderr="")

    def render(self, **overrides):
        args = {
            "text": "Somebody's gotta do it.",
            "request": self.request,
            "descriptor": self.descriptor,
            "output_path": self.output,
            "authorized": True,
            "runner": self.fake_runner,
        }
        args.update(overrides)
        return render_spoken(**args)

    def test_local_spoken_render_produces_normalized_wav(self):
        result = self.render()
        self.assertEqual(result["engine"], "piper-cli")
        self.assertEqual(result["execution"], "local")
        self.assertEqual(result["sample_rate"], 48000)
        self.assertEqual(result["bit_depth"], 16)
        self.assertEqual(result["channels"], 2)
        self.assertGreater(result["frames"], 0)
        with wave.open(str(self.output), "rb") as rendered:
            self.assertEqual(rendered.getframerate(), 48000)
            self.assertEqual(rendered.getnchannels(), 2)

    def test_dispatch_is_denied_by_default(self):
        with self.assertRaisesRegex(VoiceRenderError, "not authorized"):
            self.render(authorized=False)

    def test_singing_is_not_claimed_by_spoken_adapter(self):
        self.request["mode"] = "sung"
        with self.assertRaisesRegex(VoiceRenderError, "cannot render sung"):
            self.render()

    def test_non_16_bit_request_is_rejected(self):
        self.request["bit_depth"] = 24
        with self.assertRaisesRegex(VoiceRenderError, "16-bit"):
            self.render()

    def test_remote_engine_and_credential_fields_are_rejected(self):
        bad = dict(self.descriptor, execution="remote")
        self.assertTrue(validate_engine_descriptor(bad))
        bad = dict(self.descriptor, api_key="never-allow-this")
        self.assertTrue(validate_engine_descriptor(bad))

    def test_missing_local_model_is_rejected(self):
        self.descriptor["model_path"] = str(self.root / "missing.onnx")
        with self.assertRaisesRegex(VoiceRenderError, "existing local"):
            self.render()

    def test_existing_output_is_not_overwritten_by_default(self):
        self.output.write_bytes(b"keep")
        with self.assertRaisesRegex(VoiceRenderError, "already exists"):
            self.render()
        self.assertEqual(self.output.read_bytes(), b"keep")

    def test_nonzero_engine_exit_does_not_create_output(self):
        runner = Mock(return_value=Mock(returncode=2, stdout="", stderr="failure"))
        with self.assertRaisesRegex(VoiceRenderError, "non-zero"):
            self.render(runner=runner)
        self.assertFalse(self.output.exists())

    def test_invalid_text_is_rejected(self):
        with self.assertRaisesRegex(VoiceRenderError, "printable characters"):
            self.render(text="  ")


if __name__ == "__main__":
    unittest.main()
