import importlib.util
import json
import tempfile
import unittest
import wave
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "warehouse_rave_v3.py"
SPEC = importlib.util.spec_from_file_location("warehouse_rave_v3", SCRIPT)
v3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v3)


class WarehouseRaveV3Tests(unittest.TestCase):
    def test_arrangement_has_distinct_sections_and_full_song_form(self):
        events, starts, bars = v3.build_events()
        self.assertEqual(bars, 68)
        self.assertEqual(starts["drop_a"], 16)
        self.assertEqual(starts["breakdown"], 40)
        self.assertEqual(starts["final_drop"], 52)
        self.assertEqual(starts["outro_tag"], 68 - 4)
        self.assertGreater(len(events["lead"]), 0)
        self.assertGreater(len(events["fx"]), 0)

    def test_harmony_and_motif_are_not_flat_single_loop(self):
        self.assertEqual([item[0] for item in v3.HARMONY], [45, 41, 48, 43])
        self.assertEqual(len(set(v3.MOTIF)), 6)
        events, _, _ = v3.build_events()
        bass_pitches = {note[4] for note in events["bass"]}
        lead_pitches = {note[4] for note in events["lead"]}
        self.assertGreaterEqual(len(bass_pitches), 5)
        self.assertGreaterEqual(len(lead_pitches), 7)

    def test_renders_mix_and_five_stems_with_v3_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = v3.render(tmp, 127, 8000)
            expected = ("instrumental_mix.wav", "drums.wav", "bass.wav",
                        "synth.wav", "lead.wav", "fx.wav")
            for name in expected:
                with wave.open(str(out / name), "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 1)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getframerate(), 8000)
                    self.assertGreater(wav.getnframes(), 0)
            manifest = json.loads((out / "audio_manifest.json").read_text())
            self.assertEqual(manifest["version"], 3)
            self.assertEqual(manifest["bars"], 68)
            self.assertEqual(manifest["harmony"], ["Am", "F", "C", "G"])
            self.assertFalse(manifest["vocals_rendered"])

    def test_rejects_invalid_tempo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                v3.render(tmp, 190, 8000)


if __name__ == "__main__":
    unittest.main()
