"""Foundry Mail draft composer never sends messages."""
import os
from pathlib import Path
import tempfile
import unittest

from src.autopilot.foundry_mail_drafts import MailDraft, compose_draft, save_draft


class FoundryMailDraftTests(unittest.TestCase):
    def test_offline_rfc_draft(self):
        draft = MailDraft("buyer@example.org", "sales@example.com",
                          "Hello from Foundry", "Offline only.\n")
        msg = compose_draft(draft)
        self.assertEqual(msg["To"], "buyer@example.org")
        self.assertEqual(msg["X-Foundry-Draft-Status"], "unreviewed")
        self.assertIn("Offline only.", msg.get_content())

    def test_rejects_header_injection_and_invalid_addresses(self):
        good = dict(to_address="buyer@example.org",
                    from_address="sales@example.com", subject="Subject", body="Text")
        for changes in (
            {"to_address": "buyer@example.org\nBcc:other@example.net"},
            {"from_address": "Unknown Person <sales@example.com>"},
            {"subject": "Subject\nBcc:other@example.net"},
            {"to_address": "missing-at-sign"},
            {"body": ""},
            {"reviewed": "true"},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                compose_draft(MailDraft(**(good | changes)))

    def test_no_overwrite_and_private_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draft.eml"
            d = MailDraft("buyer@example.org", "sales@example.com",
                          "Subject", "Body")
            save_draft(d, path)
            self.assertIn(b"X-Foundry-Draft-Status: unreviewed", path.read_bytes())
            with self.assertRaises(FileExistsError):
                save_draft(d, path)
            if os.name == "posix":
                self.assertEqual(path.stat().st_mode & 0o077, 0)


if __name__ == "__main__":
    unittest.main()
