import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "vocal_render_contract.py"
spec = importlib.util.spec_from_file_location("vocal_render_contract", SCRIPT)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class GenesisKokoroDescriptorTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / "renderers" / "genesis-kokoro-psola-v1.json"
        self.renderer = json.loads(path.read_text(encoding="utf-8"))

    def test_candidate_descriptor_is_valid_but_not_yet_verified(self):
        result = contract.validate_renderer_descriptor(self.renderer)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(self.renderer["verification"]["verified_modes"], [])
        self.assertEqual(self.renderer["verification"]["status"], "pending")

    def test_sung_dispatch_remains_blocked_until_independent_evidence(self):
        request = contract.make_render_request(
            project_id="fine-china",
            source_ref="projects/fine-china/vocal_score_draft.json",
            mode="sung",
            layers=["dry_lead"],
            sample_rate=48000,
            bit_depth=16,
            channels=1,
        )
        result = contract.validate_render_request(request, self.renderer)
        self.assertFalse(result.ok)
        self.assertTrue(any("no verified sung capability" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
