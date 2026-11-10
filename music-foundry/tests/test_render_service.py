import importlib.util
import os
import tempfile
import unittest
import wave
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "service" / "server.py"
SPEC = importlib.util.spec_from_file_location("music_foundry_service", SERVER)
SERVICE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SERVICE)


class RenderServiceContractTests(unittest.TestCase):
    def test_wav_metadata_is_read_from_real_pcm(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "tone.wav"
            with wave.open(str(path), "wb") as output:
                output.setnchannels(1)
                output.setsampwidth(2)
                output.setframerate(22050)
                output.writeframes(b"\\x00\\x00" * 22050)
            metadata = SERVICE.valid_audio(path)
            self.assertEqual(metadata["sample_rate"], 22050)
            self.assertEqual(metadata["channels"], 1)
            self.assertEqual(metadata["duration_seconds"], 1.0)
            self.assertGreater(metadata["bytes"], 4096)

    def test_filename_allowlist_rejects_path_traversal(self):
        self.assertTrue(SERVICE.FILENAME.fullmatch("instrumental_mix.wav"))
        self.assertTrue(SERVICE.FILENAME.fullmatch("audio_manifest.json"))
        self.assertFalse(SERVICE.FILENAME.fullmatch("../secret.wav"))
        self.assertFalse(SERVICE.FILENAME.fullmatch("mix.mp3"))

    def test_project_and_job_limits_are_bounded(self):
        self.assertTrue(SERVICE.SLUG.fullmatch("somebodys-gotta-do-it"))
        self.assertFalse(SERVICE.SLUG.fullmatch("../private"))
        self.assertFalse(SERVICE.SLUG.fullmatch("A" * 100))


if __name__ == "__main__":
    unittest.main()
