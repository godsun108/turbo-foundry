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

    def test_applies_vocal_effects_without_modifying_source_take(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "lead.wav"
            write_source(source, [1000, 2000, -1000, -2000] * 200, 16000)
            original = source.read_bytes()
            manifest = {
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1.0,
                "takes": [{
                    "file": "lead.wav", "layer": "dry_lead",
                    "offset_ms": 0, "gain_db": 0, "pan": 0,
                    "effects": {"drive_db": 8, "lowpass_hz": 6000,
                                "delay_ms": 80, "delay_feedback": 35,
                                "delay_wet": 30, "stutter": "1/8"}
                }]
            }
            path = root / "spoken-takes.json"
            path.write_text(json.dumps(manifest))
            out = assembler.assemble(path, root / "out", 8000)
            self.assertEqual(source.read_bytes(), original)
            result = json.loads((out / "spoken_audio_manifest.json").read_text())
            self.assertEqual(result["takes"][0]["effects"]["drive_db"], 8)
            with wave.open(str(out / "dry_lead.wav"), "rb") as wav:
                self.assertEqual(wav.getframerate(), 8000)
                self.assertEqual(wav.getnchannels(), 2)

    def test_phrase_performance_repeats_reverses_and_drop_triggers(self):
        self.assertEqual(assembler._apply_phrase_performance(
            [1, 2, 3, 4, 5, 6], 1000,
            {"start_ms": 1, "end_ms": 4, "repeats": 2,
             "reverse": True, "drop_repeat": False}, 0),
            [1, 4, 3, 2, 4, 5, 6])
        phrase = assembler._apply_phrase_performance(
            [1, 2, 3, 4], 1,
            {"start_ms": 0, "end_ms": 2, "repeats": 1,
             "reverse": False, "drop_repeat": True}, 0)
        self.assertEqual(phrase[:2], [1, 2])
        self.assertEqual(phrase[-2:], [1, 2])
        with self.assertRaises(ValueError):
            assembler._apply_phrase_performance(
                [1, 2], 1000,
                {"start_ms": 0, "end_ms": 3, "repeats": 9,
                 "reverse": False, "drop_repeat": False}, 0)

    def test_automation_keyframes_ramp_and_are_exported(self):
        self.assertEqual(assembler._automation_value(
            [{"time_ms": 1000, "param": "gain_db", "value": -12}],
            "gain_db", 500, 0), -6)
        self.assertEqual(assembler._automation_value(
            [{"time_ms": 0, "param": "gain_db", "value": -12}],
            "gain_db", 0, 0), -12)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_source(root / "lead.wav", [1000] * 800, 8000)
            path = root / "spoken-takes.json"
            path.write_text(json.dumps({
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1,
                "takes": [{
                    "file": "lead.wav", "layer": "dry_lead", "gain_db": 0,
                    "automation": [
                        {"time_ms": 0, "param": "gain_db", "value": -12},
                        {"time_ms": 500, "param": "gain_db", "value": 0}
                    ]
                }]
            }))
            out = assembler.assemble(path, root / "out", 8000)
            result = json.loads((out / "spoken_audio_manifest.json").read_text())
            self.assertEqual(len(result["takes"][0]["automation"]), 2)

    def test_rejects_unsafe_automation_points(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_source(root / "lead.wav", [1000] * 80, 8000)
            path = root / "spoken-takes.json"
            path.write_text(json.dumps({
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1,
                "takes": [{"file": "lead.wav", "layer": "dry_lead",
                           "automation": [{"time_ms": 0, "param": "gain_db",
                                           "value": 40}]}]
            }))
            with self.assertRaises(ValueError):
                assembler.assemble(path, root / "out", 8000)

    def test_delay_effect_preserves_a_bounded_echo_tail(self):
        rendered = assembler._apply_effects(
            [1000.0] * 100, 8000,
            {"delay_ms": 50, "delay_feedback": 40, "delay_wet": 50}
        )
        self.assertGreater(len(rendered), 100)
        self.assertTrue(any(abs(value) > 0 for value in rendered[100:]))
        self.assertLessEqual(len(rendered), 100 + 8 * 400)

    def test_rejects_out_of_range_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_source(root / "lead.wav", [1000, -1000] * 20, 16000)
            path = root / "spoken-takes.json"
            path.write_text(json.dumps({
                "schema": "turbo.music-foundry.spoken-takes.v1",
                "duration_seconds": 1,
                "takes": [{"file": "lead.wav", "layer": "dry_lead",
                           "effects": {"drive_db": 99}}]
            }))
            with self.assertRaises(ValueError):
                assembler.assemble(path, root / "out", 8000)

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
