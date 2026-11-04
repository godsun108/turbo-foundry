"""Static safety-contract checks for the local browser recording booth.

These checks do not replace real iPhone/Safari microphone and audio-decoding tests.
"""
from pathlib import Path
import unittest


BOOTH = (
    Path(__file__).resolve().parents[1]
    / "projects"
    / "somebodys-gotta-do-it"
    / "recording-booth.html"
)


class RecordingBoothContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = BOOTH.read_text(encoding="utf-8")

    def test_explicit_microphone_permission_flow(self):
        self.assertIn("navigator.mediaDevices?.getUserMedia", self.source)
        self.assertIn("recordButton.addEventListener('click'", self.source)
        self.assertIn("stream?.getTracks().forEach(t=>t.stop())", self.source)

    def test_local_wav_export_contract(self):
        self.assertIn("function wavFromMono", self.source)
        self.assertIn("sampleRate = 48000", self.source)
        self.assertIn("view.setUint16(34,16,true)", self.source)
        self.assertIn("type:'audio/wav'", self.source)

    def test_session_safety_limits(self):
        self.assertIn("MAX_SESSION_SECONDS = 180", self.source)
        self.assertIn("MAX_TAKES = 128", self.source)
        self.assertIn("decoded.duration > MAX_SESSION_SECONDS", self.source)

    def test_manifest_duration_is_derived_from_takes(self):
        self.assertIn("takes.map(t=>t.offset_ms/1000+t.duration)", self.source)
        self.assertIn("schema:'turbo.music-foundry.spoken-takes.v1'", self.source)

    def test_no_network_transport_or_upload_code(self):
        self.assertNotIn("fetch(", self.source)
        self.assertNotIn("XMLHttpRequest", self.source)
        self.assertNotIn("WebSocket", self.source)

    def test_source_is_not_persisted_as_hidden_recording_storage(self):
        self.assertIn("Download each WAV before leaving", self.source)
        self.assertIn("page memory", self.source)


if __name__ == "__main__":
    unittest.main()
