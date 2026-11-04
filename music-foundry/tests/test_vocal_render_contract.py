import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "vocal_render_contract.py"
spec = importlib.util.spec_from_file_location("vocal_render_contract", SCRIPT)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class VocalRenderContractTests(unittest.TestCase):
    def setUp(self):
        self.renderer = {
            "schema": contract.RENDERER_SCHEMA,
            "id": "local-test-renderer",
            "execution": "local",
            "modes": ["spoken", "sung"],
            "formats": ["wav"],
            "credential_handling": "server_or_local_only",
        }
        self.request = contract.make_render_request(
            project_id="somebodys-gotta-do-it",
            source_ref="cue-sheet.md",
            mode="spoken",
            layers=["dry_lead", "gang_responses", "adlibs_and_chops"],
        )

    def test_valid_spoken_request_and_dual_mode_renderer(self):
        self.assertTrue(contract.validate_renderer_descriptor(self.renderer).ok)
        self.assertTrue(contract.validate_render_request(self.request, self.renderer).ok)

    def test_sung_mode_is_a_first_class_supported_mode(self):
        self.request["mode"] = "sung"
        self.assertTrue(contract.validate_render_request(self.request, self.renderer).ok)

    def test_renderer_missing_sung_capability_is_rejected(self):
        self.renderer["modes"] = ["spoken"]
        self.request["mode"] = "sung"
        result = contract.validate_render_request(self.request, self.renderer)
        self.assertFalse(result.ok)
        self.assertTrue(any("does not support sung" in error for error in result.errors))

    def test_bad_audio_spec_is_rejected(self):
        self.request["sample_rate"] = 22050
        self.request["bit_depth"] = 32
        self.request["format"] = "mp3"
        self.assertFalse(contract.validate_render_request(self.request).ok)

    def test_credentials_are_rejected_from_browser_facing_contract(self):
        self.renderer["api_key"] = "must-never-be-here"
        result = contract.validate_renderer_descriptor(self.renderer)
        self.assertFalse(result.ok)
        self.assertTrue(any("credential" in error for error in result.errors))

    def test_empty_layers_and_missing_source_are_rejected(self):
        self.request["layers"] = []
        self.request["source_ref"] = ""
        self.assertFalse(contract.validate_render_request(self.request).ok)


if __name__ == "__main__":
    unittest.main()
