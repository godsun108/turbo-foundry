import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "warehouse_rave_v3.py"
SPEC = importlib.util.spec_from_file_location("warehouse_rave_v3", SCRIPT)
v3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v3)


class WarehouseRaveV3Tests(unittest.TestCase):
    def test_composition_has_56_bars_and_distinct_sections(self):
        tracks, arrangement = v3.build_notes()
        self.assertEqual(sum(section["bars"] for section in arrangement), 56)
        self.assertEqual([s["name"] for s in arrangement], [
            "intro", "verse_1", "pre_drop", "drop_1",
            "verse_2", "bridge", "final_drop", "outro"
        ])
        self.assertEqual(arrangement[-1]["start_bar"], 52)

    def test_hook_and_section_dynamics_are_written(self):
        tracks, arrangement = v3.build_notes()
        self.assertGreater(len(tracks["lead"]), 40)
        self.assertGreater(len(tracks["bass"]), 100)
        self.assertGreater(len(tracks["drums"]), 300)
        # The final drop deliberately lifts the hook an octave in its closing phrase.
        self.assertTrue(any(note[0] == 93 for note in tracks["lead"]))

    def test_midi_export_is_valid_and_manifest_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = v3.make(tmp, 127)
            expected = {"chords.mid", "bass.mid", "lead.mid", "drums.mid", "texture.mid", "manifest.json"}
            self.assertEqual({p.name for p in out.iterdir()}, expected)
            for filename in expected - {"manifest.json"}:
                data = (out / filename).read_bytes()
                self.assertTrue(data.startswith(b"MThd"))
                self.assertIn(b"MTrk", data)
            manifest = json.loads((out / "manifest.json").read_text())
            self.assertEqual(manifest["bars"], 56)
            self.assertEqual(manifest["bpm"], 127)
            self.assertEqual(manifest["schema"], "turbo.music-foundry.composition.v3")

    def test_rejects_invalid_tempo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                v3.make(tmp, 300)


if __name__ == "__main__":
    unittest.main()
