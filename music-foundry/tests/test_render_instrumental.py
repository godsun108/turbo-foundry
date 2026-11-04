import importlib.util
import json
import tempfile
import unittest
import wave
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "render_instrumental.py"
spec = importlib.util.spec_from_file_location("instrumental_renderer", SCRIPT)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class InstrumentalRenderTests(unittest.TestCase):
    def test_renders_mix_and_four_wav_stems_without_vocals(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = renderer.render(tmp, 127, 8000)
            expected = ["chords.wav", "bass.wav", "lead.wav", "drums.wav", "instrumental_mix.wav"]
            for name in expected:
                path = out / name
                self.assertTrue(path.is_file())
                with wave.open(str(path), "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 1)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getframerate(), 8000)
                    self.assertGreater(wav.getnframes(), 0)
            manifest = json.loads((out / "audio_manifest.json").read_text())
            self.assertEqual(manifest["render_type"], "procedural_instrumental")
            self.assertFalse(manifest["vocals_rendered"])
            self.assertEqual(len(manifest["stems"]), 4)

    def test_rejects_invalid_sample_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                renderer.render(tmp, 127, 4000)

    def test_rejects_invalid_tempo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                renderer.render(tmp, 0, 8000)


if __name__ == "__main__":
    unittest.main()
