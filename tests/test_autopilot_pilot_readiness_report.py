"""Fail-closed commercial readiness regression tests; synthetic only."""
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from src.autopilot.commercial_release_gate import (
    REQUIRED_FOR_DISCOVERY, REQUIRED_FOR_LIVE_PILOT,
)
from src.autopilot.pilot_readiness_report import (
    evaluate_evidence, render_report, main,
)


def item():
    return {"passed": True, "reference": "synthetic-proof", "verified_by": "test-reviewer"}


class PilotReadinessTests(unittest.TestCase):
    def test_empty_evidence_is_no_go(self):
        result = evaluate_evidence({})
        self.assertFalse(result["discovery_ready"])
        self.assertFalse(result["live_pilot_ready"])
        self.assertEqual(set(result["missing_live_pilot"]), set(REQUIRED_FOR_LIVE_PILOT))
        self.assertIn("NO-GO", render_report(result))
        self.assertEqual(result["verified_live_pilot_count"], 0)

    def test_discovery_proofs_do_not_approve_customer_service(self):
        result = evaluate_evidence({k: item() for k in REQUIRED_FOR_DISCOVERY})
        self.assertTrue(result["discovery_ready"])
        self.assertFalse(result["live_pilot_ready"])
        self.assertEqual(result["verified_discovery_count"], len(REQUIRED_FOR_DISCOVERY))

    def test_missing_one_live_proof_blocks(self):
        raw = {k: item() for k in REQUIRED_FOR_DISCOVERY + REQUIRED_FOR_LIVE_PILOT}
        raw.pop("delivery_reconciliation_test")
        result = evaluate_evidence(raw)
        self.assertFalse(result["live_pilot_ready"])
        self.assertIn("delivery_reconciliation_test", result["missing_live_pilot"])

    def test_full_claimed_proofs_require_independent_review(self):
        raw = {k: item() for k in REQUIRED_FOR_DISCOVERY + REQUIRED_FOR_LIVE_PILOT}
        result = evaluate_evidence(raw)
        self.assertTrue(result["live_pilot_ready"])
        self.assertIn("INDEPENDENT APPROVAL REVIEW", render_report(result))
        self.assertIn("NOT independently authenticated", render_report(result))

    def test_rejects_unrecognized_untrusted_and_malformed_items(self):
        for raw in (
            {"invented_gate": item()},
            {REQUIRED_FOR_DISCOVERY[0]: True},
            {REQUIRED_FOR_DISCOVERY[0]: {"passed": 1, "reference": "r", "verified_by": "a"}},
            {REQUIRED_FOR_DISCOVERY[0]: {"passed": True, "reference": "r"}},
            [],
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                evaluate_evidence(raw)

    def test_blank_reference_and_actor_do_not_count(self):
        raw = {REQUIRED_FOR_DISCOVERY[0]: {"passed": True, "reference": " ", "verified_by": " "}}
        result = evaluate_evidence(raw)
        self.assertFalse(result["discovery_ready"])

    def test_cli_generates_no_go_artifacts_and_exit_two(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            markdown, json_path = out / "readiness.md", out / "readiness.json"
            rc = main(["--markdown", str(markdown), "--json", str(json_path)])
            self.assertEqual(rc, 2)
            self.assertIn("NO-GO", markdown.read_text())
            self.assertIs(json.loads(json_path.read_text())["live_pilot_ready"], False)


if __name__ == "__main__":
    unittest.main()
