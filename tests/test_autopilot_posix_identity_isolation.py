"""POSIX two-identity SQLite isolation rehearsal; offline, privileged opt-in only.

This test is skipped unless explicitly opted in by a privileged CI/VM operator.
It never contacts Twilio or enables SMS. It cannot validate a deployment
unless it actually runs using distinct real OS user IDs.
"""
import os
from pathlib import Path
import pwd
import sqlite3
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(
    os.name == "posix" and hasattr(os, "geteuid")
    and os.geteuid() == 0
    and os.environ.get("AUTOPILOT_RUN_PRIVILEGED_ISOLATION") == "1",
    "requires root on disposable POSIX host and explicit opt-in",
)
class SeparateIdentityIsolationTests(unittest.TestCase):
    def test_distinct_unprivileged_identity_cannot_open_writer_database(self):
        # Restrict the full parent directory, not just the database.
        # Do not run this test as part of a deployed worker.
        candidate = pwd.getpwnam("nobody")
        if candidate.pw_uid == 0:
            self.skipTest("no non-root nobody user")
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "restricted"
            parent.mkdir(mode=0o700)
            parent.chmod(0o700)
            db_path = parent / "state.db"
            with sqlite3.connect(db_path) as db:
                db.execute("CREATE TABLE worker_control (enabled INTEGER)")
                db.execute("INSERT INTO worker_control VALUES (0)")
            db_path.chmod(0o600)

            code = (
                "import sqlite3,sys\n"
                "try:\n"
                " sqlite3.connect(sys.argv[1]).execute('UPDATE worker_control SET enabled=1')\n"
                "except (sqlite3.OperationalError, PermissionError):\n"
                " sys.exit(0)\n"
                "sys.exit(2)\n"
            )

            def drop_privileges():
                os.setgroups([])
                os.setgid(candidate.pw_gid)
                os.setuid(candidate.pw_uid)

            result = subprocess.run(
                [sys.executable, "-c", code, str(db_path)],
                preexec_fn=drop_privileges, timeout=5, check=False,
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with sqlite3.connect(db_path) as db:
                self.assertEqual(
                    db.execute("SELECT enabled FROM worker_control").fetchone()[0], 0
                )


if __name__ == "__main__":
    unittest.main()
