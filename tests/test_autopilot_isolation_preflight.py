"""Offline filesystem-permission preflight tests (no network or SMS)."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.autopilot.isolation_preflight import check_sqlite_isolation


@unittest.skipUnless(os.name == "posix", "POSIX permission inspection only")
class IsolationPreflightTests(unittest.TestCase):
    def test_private_state_store_is_eligible_for_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "private"
            parent.mkdir(mode=0o700)
            parent.chmod(0o700)
            database = parent / "state.db"
            database.touch(mode=0o600)
            database.chmod(0o600)
            result = check_sqlite_isolation(str(database), expected_uid=os.getuid())
            self.assertTrue(result.safe_to_review, result.reasons)

    def test_group_access_blocks_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "private"
            parent.mkdir()
            parent.chmod(0o750)
            database = parent / "state.db"
            database.touch()
            database.chmod(0o640)
            result = check_sqlite_isolation(str(database))
            self.assertFalse(result.safe_to_review)
            self.assertIn("parent_group_or_other_access", result.reasons)
            self.assertIn("state_group_or_other_access", result.reasons)

    def test_symlink_database_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "private"
            parent.mkdir(mode=0o700)
            parent.chmod(0o700)
            real = parent / "real.db"
            real.touch(mode=0o600)
            alias = parent / "alias.db"
            alias.symlink_to(real)
            self.assertIn("state_not_regular_file",
                          check_sqlite_isolation(str(alias)).reasons)

    def test_writable_sidecar_must_be_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "private"
            parent.mkdir(mode=0o700)
            parent.chmod(0o700)
            db = parent / "state.db"
            db.touch(mode=0o600)
            db.chmod(0o600)
            sidecar = Path(str(db) + "-wal")
            sidecar.touch()
            sidecar.chmod(0o644)
            self.assertIn("sidecar_group_or_other_access",
                          check_sqlite_isolation(str(db)).reasons)

    def test_missing_state_and_owner_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "private"
            parent.mkdir(mode=0o700)
            parent.chmod(0o700)
            db = parent / "state.db"
            self.assertFalse(check_sqlite_isolation(str(db)).safe_to_review)
            db.touch(mode=0o600)
            db.chmod(0o600)
            result = check_sqlite_isolation(str(db), expected_uid=os.getuid() + 1)
            self.assertFalse(result.safe_to_review)
            self.assertIn("state_owner_mismatch", result.reasons)


if __name__ == "__main__":
    unittest.main()
