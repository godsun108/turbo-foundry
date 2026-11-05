import hashlib, json, tempfile, unittest, wave
from pathlib import Path
from import_singing_render import import_render

class SingingRenderImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.render_dir = self.root / "render"
        self.render_dir.mkdir()
        self.audio = self.render_dir / "generated.wav"
        with wave.open(str(self.audio), "wb") as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(24000)
            wav.writeframes(b"\x01\x00" * 24000)
        digest = hashlib.sha256(self.audio.read_bytes()).hexdigest()
        self.render_manifest = self.render_dir / "singing_render_manifest.json"
        self.render_manifest.write_text(json.dumps({
            "schema": "turbo.music-foundry.singing-render.v1",
            "project_id": "somebodys-gotta-do-it", "engine": "Soul-AILab/SoulX-Singer",
            "audio_file": str(self.audio), "audio_sha256": digest,
            "source_score_sha256": "a" * 64, "status": "rendered"
        }), encoding="utf-8")
        self.output = self.root / "import" / "spoken-takes.json"

    def tearDown(self): self.temp.cleanup()

    def test_import_creates_existing_timeline_manifest_and_preserves_audio(self):
        original = self.audio.read_bytes()
        result = import_render(render_manifest_path=self.render_manifest, output_manifest_path=self.output,
            offset_ms=30000, project_duration_seconds=105.827, layer="gang_vocals", gain_db=-2, pan=0.1)
        take = result["takes"][0]; copied = self.output.parent / take["file"]
        self.assertEqual(result["schema"], "turbo.music-foundry.spoken-takes.v1")
        self.assertEqual(take["offset_ms"], 30000)
        self.assertEqual(take["layer"], "gang_vocals")
        self.assertTrue(take["source"]["imported_unchanged"])
        self.assertEqual(copied.read_bytes(), original)
        self.assertEqual(self.audio.read_bytes(), original)

    def test_rejects_tampered_audio_hash(self):
        self.audio.write_bytes(self.audio.read_bytes() + b"x")
        with self.assertRaisesRegex(ValueError, "checksum"):
            import_render(render_manifest_path=self.render_manifest, output_manifest_path=self.output,
                offset_ms=0, project_duration_seconds=105.827)

    def test_rejects_wrong_wav_format(self):
        with wave.open(str(self.audio), "wb") as wav:
            wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(24000); wav.writeframes(b"\0\0\0\0" * 100)
        manifest = json.loads(self.render_manifest.read_text())
        manifest["audio_sha256"] = hashlib.sha256(self.audio.read_bytes()).hexdigest()
        self.render_manifest.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "mono 24 kHz 16-bit"):
            import_render(render_manifest_path=self.render_manifest, output_manifest_path=self.output,
                offset_ms=0, project_duration_seconds=105.827)

    def test_refuses_overwrite(self):
        self.output.parent.mkdir(); self.output.write_text("{}")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            import_render(render_manifest_path=self.render_manifest, output_manifest_path=self.output,
                offset_ms=0, project_duration_seconds=105.827)

    def test_rejects_take_outside_song_duration(self):
        with self.assertRaisesRegex(ValueError, "extend beyond"):
            import_render(render_manifest_path=self.render_manifest, output_manifest_path=self.output,
                offset_ms=105000, project_duration_seconds=105.827)

    def test_rejects_unexpected_project(self):
        manifest = json.loads(self.render_manifest.read_text()); manifest["project_id"] = "another-song"
        self.render_manifest.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "targets Somebody"):
            import_render(render_manifest_path=self.render_manifest, output_manifest_path=self.output,
                offset_ms=0, project_duration_seconds=105.827)

if __name__ == "__main__": unittest.main()
