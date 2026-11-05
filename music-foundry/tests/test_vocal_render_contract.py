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
            "verification": {
                "status": "passed",
                "verified_modes": ["spoken"],
                "evidence_ref": "tests/fixtures/spoken-renderer-smoke-test.json",
            },
            "formats": ["wav"],
            "credential_handling": "server_or_local_only",
        }
        self.request = contract.make_render_request(
            project_id="somebodys-gotta-do-it",
            source_ref="projects/somebodys-gotta-do-it/cue-sheet.md",
            mode="spoken",
            layers=["dry_lead", "gang_responses", "adlibs_and_chops"],
        )

    def test_verified_spoken_request_is_accepted(self):
        self.assertTrue(contract.validate_renderer_descriptor(self.renderer).ok)
        self.assertTrue(contract.validate_render_request(self.request, self.renderer).ok)

    def test_declaring_sung_is_not_enough_to_claim_singing_capability(self):
        self.request["mode"] = "sung"
        result = contract.validate_render_request(self.request, self.renderer)
        self.assertFalse(result.ok)
        self.assertTrue(any("no verified sung capability" in error for error in result.errors))

    def test_sung_mode_requires_a_passed_evidence_record(self):
        self.renderer["verification"]["verified_modes"].append("sung")
        self.renderer["verification"]["evidence_ref"] = "tests/fixtures/sung-renderer-smoke-test.json"
        self.request["mode"] = "sung"
        self.assertTrue(contract.validate_render_request(self.request, self.renderer).ok)

    def test_verified_mode_without_passed_status_is_rejected(self):
        self.renderer["verification"]["status"] = "pending"
        result = contract.validate_renderer_descriptor(self.renderer)
        self.assertFalse(result.ok)
        self.assertTrue(any("status=passed" in error for error in result.errors))

    def test_verified_mode_without_evidence_reference_is_rejected(self):
        self.renderer["verification"]["evidence_ref"] = ""
        result = contract.validate_renderer_descriptor(self.renderer)
        self.assertFalse(result.ok)
        self.assertTrue(any("evidence_ref" in error for error in result.errors))

    def test_renderer_missing_spoken_capability_is_rejected(self):
        self.renderer["modes"] = ["sung"]
        self.request["mode"] = "spoken"
        result = contract.validate_render_request(self.request, self.renderer)
        self.assertFalse(result.ok)

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
