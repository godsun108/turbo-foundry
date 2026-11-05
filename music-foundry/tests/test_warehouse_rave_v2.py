import importlib.util
import json
import tempfile
import unittest
import wave
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "warehouse_rave_v2.py"
spec = importlib.util.spec_from_file_location("warehouse_rave_v2", SCRIPT)
rave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rave)


class WarehouseRaveV2Tests(unittest.TestCase):
    def test_arrangement_has_64_bars_and_full_four_on_floor_drop(self):
        events, sections, bars = rave.build_events()
        self.assertEqual(bars, 64)
        self.assertEqual(sections["drop_1"], 16)
        self.assertEqual(sections["final_drop"], 48)
        kick_ticks = [n[1] for n in events["drums"] if n[0] == "kick"]
        first_drop = sections["drop_1"] * rave.BAR
        self.assertTrue(all(first_drop + beat * rave.BEAT in kick_ticks for beat in range(4)))

    def test_renders_mix_and_four_stems(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = rave.render(tmp, 132, 8000)
            for name in ("instrumental_mix.wav", "drums.wav", "bass.wav", "synth.wav", "fx.wav"):
                with wave.open(str(out / name), "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 1)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getframerate(), 8000)
                    self.assertGreater(wav.getnframes(), 0)
            manifest = json.loads((out / "audio_manifest.json").read_text())
            self.assertEqual(manifest["bpm"], 132)
            self.assertEqual(manifest["bars"], 64)
            self.assertFalse(manifest["vocals_rendered"])
            self.assertEqual(manifest["render_type"], "procedural_warehouse_rave_instrumental")

    def test_rejects_out_of_range_tempo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                rave.render(tmp, 200, 8000)


if __name__ == "__main__":
    unittest.main()
