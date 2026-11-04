import array
import importlib.util
import json
import tempfile
import unittest
import wave
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "assemble_spoken_takes.py"
spec = importlib.util.spec_from_file_location("spoken_take_assembler", SCRIPT)
assembler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembler)


def write_source(path, samples, rate=16000, channels=1):
    values = array.array("h")
    for sample in samples:
        values.append(sample)
        if channels == 2:
            values.append(sample)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(values.tobytes())


class SpokenTakeAssemblyTests(unittest.TestCase):
    def test_places_recorded_take_and_exports_layer_and_mix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_source(root / "lead.wav", [1000, 2000, -1000, -2000], 16000)
            manifest = {
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1.0,
                "takes": [{"file": "lead.wav", "layer": "dry_lead",
                           "offset_ms": 100, "gain_db": 0, "pan": 0}]
            }
            path = root / "spoken-takes.json"
            path.write_text(json.dumps(manifest))
            out = assembler.assemble(path, root / "out", 8000)
            self.assertTrue((out / "dry_lead.wav").is_file())
            self.assertTrue((out / "spoken_vocal_mix.wav").is_file())
            with wave.open(str(out / "spoken_vocal_mix.wav"), "rb") as wav:
                self.assertEqual(wav.getnchannels(), 2)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertEqual(wav.getframerate(), 8000)
                self.assertEqual(wav.getnframes(), 8000)
                frames = array.array("h")
                frames.frombytes(wav.readframes(wav.getnframes()))
                self.assertEqual(frames[0], 0)
                self.assertGreater(max(abs(v) for v in frames), 0)
            result = json.loads((out / "spoken_audio_manifest.json").read_text())
            self.assertEqual(result["render_type"], "recorded_spoken_take_assembly")
            self.assertFalse(result["speech_synthesized"])
            self.assertFalse(result["source_takes_modified"])
            self.assertEqual(result["take_count"], 1)

    def test_output_must_not_overwrite_source_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "spoken-takes.json"
            path.write_text(json.dumps({
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1, "takes": []
            }))
            with self.assertRaises(ValueError):
                assembler.assemble(path, root, 8000)

    def test_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "spoken-takes.json"
            path.write_text(json.dumps({
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1,
                "takes": [{"file": "../outside.wav", "layer": "dry_lead"}]
            }))
            with self.assertRaises(ValueError):
                assembler.assemble(path, root / "out", 8000)

    def test_rejects_unknown_layer_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "spoken-takes.json"
            path.write_text(json.dumps({
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1,
                "takes": [{"file": "missing.wav", "layer": "sung_lead"}]
            }))
            with self.assertRaises(ValueError):
                assembler.assemble(path, root / "out", 8000)

    def test_rejects_invalid_sample_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "spoken-takes.json"
            path.write_text(json.dumps({
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1, "takes": []
            }))
            with self.assertRaises(ValueError):
                assembler.assemble(path, root / "out", 4000)


if __name__ == "__main__":
    unittest.main()
