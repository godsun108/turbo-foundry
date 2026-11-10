import json
import unittest
from pathlib import Path

from music_foundry.vocal_render_contract import make_render_request, validate_render_request, validate_renderer_descriptor


class GenesisKokoroDescriptorTests(unittest.TestCase):
    def setUp(self):
        path = Path("music-foundry/renderers/genesis-kokoro-psola-v1.json")
        self.renderer = json.loads(path.read_text(encoding="utf-8"))

    def test_candidate_descriptor_is_valid_but_not_yet_verified(self):
        result = validate_renderer_descriptor(self.renderer)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(self.renderer["verification"]["verified_modes"], [])
        self.assertEqual(self.renderer["verification"]["status"], "pending")

    def test_sung_dispatch_remains_blocked_until_independent_evidence(self):
        request = make_render_request(
            project_id="fine-china",
            source_ref="projects/fine-china/vocal_score_draft.json",
            mode="sung",
            layers=["dry_lead"],
            sample_rate=48000,
            bit_depth=16,
            channels=1,
        )
        result = validate_render_request(request, self.renderer)
        self.assertFalse(result.ok)
        self.assertIn("renderer has no verified sung capability", result.errors)


if __name__ == "__main__":
    unittest.main()
