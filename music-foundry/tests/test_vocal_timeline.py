"""Static contract checks for the browser-local spoken vocal timeline."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "projects" / "somebodys-gotta-do-it" / "vocal-timeline.html"


class VocalTimelineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = TIMELINE.read_text(encoding="utf-8")

    def test_imports_existing_spoken_take_manifest_schema(self):
        self.assertIn("turbo.music-foundry.spoken-takes.v1", self.source)
        self.assertIn("manifestFile", self.source)
        self.assertIn("audioFiles", self.source)
        self.assertIn("decodeAudioData", self.source)

    def test_only_supported_layers_and_bounded_offsets(self):
        for layer in ("dry_lead", "gang_vocals", "adlibs", "chops", "whisper_double"):
            self.assertIn(layer, self.source)
        self.assertIn("MAX_SECONDS=180", self.source)
        self.assertIn("MAX_TAKES=128", self.source)
        self.assertIn("offset>180000", self.source)

    def test_timeline_edits_offset_gain_pan_and_layer(self):
        self.assertIn("beginDrag", self.source)
        self.assertIn("offset_ms", self.source)
        self.assertIn("gain_db", self.source)
        self.assertIn("pan", self.source)
        self.assertIn("syncManifest", self.source)

    def test_track_sections_are_mapped_to_the_127_bpm_grid(self):
        self.assertIn("BPM=127", self.source)
        self.assertIn("BAR_SECONDS=240/127", self.source)
        self.assertIn("FINAL CHORUS + OUTRO", self.source)
        self.assertIn("PROJECT_DURATION=105.827", self.source)
        self.assertIn('id="sections"', self.source)

    def test_preview_and_wav_mix_stem_export_exist(self):
        self.assertIn("Preview arrangement", self.source)
        self.assertIn("OfflineAudioContext", self.source)
        self.assertIn("spoken_vocal_mix.wav", self.source)
        self.assertIn("audio/wav", self.source)
        self.assertIn("view.setUint16(34,16,true)", self.source)

    def test_per_take_effects_are_validated_and_rendered(self):
        for token in ("drive_db", "lowpass_hz", "delay_ms", "delay_feedback",
                      "delay_wet", "stutter"):
            self.assertIn(token, self.source)
        self.assertIn("connectTakeGraph", self.source)
        self.assertIn("processedBuffer", self.source)
        self.assertIn("effects_rendered:true", self.source)

    def test_phrase_chop_reverse_and_drop_trigger_controls(self):
        for token in ("phraseStart", "phraseEnd", "phraseRepeats", "phraseReverse",
                      "dropRepeat", "applyPhrase", "clearPhrase", "processedBuffer"):
            self.assertIn(token, self.source)
        self.assertIn("DROP_SECONDS=16*4*60/127", self.source)
        self.assertIn("performance:c.performance||null", self.source)

    def test_per_take_automation_lanes_are_editable_and_rendered(self):
        for token in ("autoTime", "autoParam", "autoValue", "addAutomation",
                      "automationList", "scheduleAutomation", "linearRampToValueAtTime"):
            self.assertIn(token, self.source)
        self.assertIn("automation:c.automation||[]", self.source)
        self.assertIn("Maximum 64 automation points per take", self.source)

    def test_exports_keep_spoken_and_sung_modes_separate(self):
        self.assertIn("speech_synthesized:false", self.source)
        self.assertIn("sung_vocals_rendered:false", self.source)
        self.assertIn("does not synthesize speech or singing", self.source)

    def test_no_network_transport_or_remote_dependencies(self):
        self.assertNotIn("fetch(", self.source)
        self.assertNotIn("XMLHttpRequest", self.source)
        self.assertNotIn("WebSocket", self.source)
        self.assertNotIn("<script src=", self.source)


if __name__ == "__main__":
    unittest.main()
