import array
import hashlib
import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import process_instrument_stems as processor
import assemble_spoken_takes as assembler


def write_wav(path, samples, rate=8000):
    values = array.array("h", samples)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(values.tobytes())


class InstrumentStemProcessingTests(unittest.TestCase):
    def _project(self, root):
        source = root / "source"
        source.mkdir()
        samples = [int(5000 * ((i % 80) / 80 - .5)) for i in range(2400)]
        write_wav(source / "bass.wav", samples)
        write_wav(source / "synth.wav", [int(v * .6) for v in samples])
        manifest = {
            "title": "DSP test",
            "bpm": 132,
            "sample_rate": 8000,
            "channels": 1,
            "bit_depth": 16,
            "stems": ["bass.wav", "synth.wav"],
        }
        (source / "audio_manifest.json").write_text(json.dumps(manifest))
        config = {
            "schema": processor.SCHEMA,
            "source_manifest": "source/audio_manifest.json",
            "stems": {
                "bass.wav": {
                    "effects": {
                        "drive_db": 3,
                        "lowpass_hz": 5000,
                        "delay_ms": 50,
                        "delay_feedback": 20,
                        "delay_wet": 15,
                    },
                    "automation": [
                        {"param": "gain_db", "time_ms": 0, "value": -3},
                        {"param": "gain_db", "time_ms": 150, "value": 0},
                    ],
                    "gain_db": -2,
                    "pan": -0.35,
                },
                "synth.wav": {
                    "effects": {"lowpass_hz": 9000},
                    "gain_db": -4,
                    "pan": 0.35,
                },
            },
        }
        config_path = root / "instrument-stem-processing.json"
        config_path.write_text(json.dumps(config))
        return source, config_path, samples

    def test_processes_stems_to_separate_stereo_mix_without_mutating_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, config, _ = self._project(root)
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.glob("*.wav")}
            output = processor.process(config, root / "processed")
            self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.glob("*.wav")})
            manifest = json.loads((output / "instrument_stem_manifest.json").read_text())
            self.assertFalse(manifest["source_stems_modified"])
            self.assertEqual(manifest["bpm"], 132)
            self.assertEqual(set(manifest["stems"]), {"bass.wav", "synth.wav"})
            for name in manifest["stems"] + [manifest["mix"]]:
                with wave.open(str(output / name), "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 2)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getframerate(), 8000)
                    values = array.array("h")
                    values.frombytes(wav.readframes(wav.getnframes()))
                    self.assertLessEqual(max((abs(v) for v in values), default=0), 32768)

    def test_rejects_output_inside_source_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, config, _ = self._project(root)
            with self.assertRaisesRegex(ValueError, "outside the source"):
                processor.process(config, source / "processed")

    def test_rejects_path_traversal_stem(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, config, _ = self._project(root)
            manifest = json.loads((source / "audio_manifest.json").read_text())
            manifest["stems"][0] = "../outside.wav"
            (source / "audio_manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "plain WAV filenames"):
                processor.process(config, root / "processed")

    def test_stutter_uses_project_tempo(self):
        samples = list(range(2000))
        at_132 = assembler._apply_effects(samples, 8000, {"stutter": "1/4"}, tempo_bpm=132)
        at_127 = assembler._apply_effects(samples, 8000, {"stutter": "1/4"}, tempo_bpm=127)
        slice_132 = round((60 / 132 / 4) * 8000)
        slice_127 = round((60 / 127 / 4) * 8000)
        self.assertEqual(at_132[slice_132], float(samples[0]))
        self.assertEqual(at_127[slice_127], float(samples[0]))
        self.assertNotEqual(slice_132, slice_127)


if __name__ == "__main__":
    unittest.main()
