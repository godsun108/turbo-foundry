import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "projects" / "somebodys-gotta-do-it" / "build_lyric_events.py"
spec = importlib.util.spec_from_file_location("build_lyric_events", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class LyricEventBuilderTests(unittest.TestCase):
    def setUp(self):
        self.project = SCRIPT.parent
        self.cue_text = (self.project / "cue-sheet.md").read_text(encoding="utf-8")
        self.timing = json.loads((self.project / "vocal_timing.json").read_text(encoding="utf-8"))

    def test_every_event_points_to_exact_source_line(self):
        events = builder.extract_lyric_lines(self.cue_text)
        source_lines = self.cue_text.splitlines()
        self.assertGreater(len(events), 30)
        for event in events:
            self.assertEqual(event["text"], source_lines[event["source_line"] - 1])
            self.assertTrue(event["event_id"].endswith(f"L{event['source_line']:03d}"))

    def test_original_phrasing_and_parentheticals_are_preserved(self):
        events = builder.extract_lyric_lines(self.cue_text)
        texts = [event["text"] for event in events]
        self.assertIn("(Fuck it, I'll do it)", texts)
        self.assertIn("(And I'm not done yet)", texts)
        self.assertIn("Drop a track that makes the whole club lose their fucking minds", texts)

    def test_adlib_suggestions_are_not_misclassified_as_canonical_lyrics(self):
        events = builder.extract_lyric_lines(self.cue_text)
        texts = [event["text"] for event in events]
        self.assertNotIn('After “Fold the laundry?” — “Eventually.”', texts)
        self.assertNotIn('After “Text my mom?” — “You better.”', texts)

    def test_timing_is_not_falsely_locked_to_section_start(self):
        manifest = builder.build_manifest(self.cue_text, self.timing, "cue-sheet.md")
        self.assertTrue(manifest["events"])
        for event in manifest["events"]:
            self.assertEqual(event["timing"]["status"], "unplaced")
            self.assertIsNone(event["timing"]["bar"])
            self.assertIsNone(event["timing"]["beat"])

    def test_manifest_tracks_canonical_source_hash_and_section_landmarks(self):
        manifest = builder.build_manifest(self.cue_text, self.timing, "cue-sheet.md")
        self.assertEqual(manifest["source_ref"], "cue-sheet.md")
        self.assertEqual(manifest["source_sha256"], __import__("hashlib").sha256(
            self.cue_text.encode("utf-8")
        ).hexdigest())
        self.assertEqual(manifest["events"][0]["section_start_bar"], 0)
        self.assertEqual(manifest["events"][-1]["section_id"], "final_chorus_outro")


if __name__ == "__main__":
    unittest.main()
