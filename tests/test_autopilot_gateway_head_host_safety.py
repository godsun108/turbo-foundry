"""Prevent metadata requests or malicious Host values from triggering reads."""
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.autopilot.gateway_loopback_app import (
    make_synthetic_app, _safe_loopback_host,
)


class HistoryHeadSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "gateway.db")
        self.app, self.sessions, self.control = make_synthetic_app(self.db)
        self.token = self.sessions.issue("offline-operator",
                                          now=datetime.now(timezone.utc))
        self.control.set_enabled(True)

    def call(self, method="HEAD", host="127.0.0.1:8091", path="/api/history"):
        reply = []
        env = {
            "REMOTE_ADDR": "127.0.0.1", "HTTP_HOST": host,
            "REQUEST_METHOD": method, "PATH_INFO": path,
            "HTTP_AUTHORIZATION": "Bearer " + self.token, "QUERY_STRING": "",
        }
        data = b"".join(self.app(
            env, lambda status, headers: reply.append(status)))
        return reply[0], data

    def audited_reads(self):
        with sqlite3.connect(self.db) as db:
            return db.execute("SELECT COUNT(*) FROM gateway_read_audit").fetchone()[0]

    def test_head_history_has_no_audit_or_gateway_dispatch(self):
        before = self.audited_reads()
        observed = []
        def forbidden(**kwargs):
            observed.append(kwargs)
            raise AssertionError("HEAD should not request provider history")
        self.sessions.observe = forbidden
        status, body = self.call()
        self.assertEqual(status, "405 Method Not Allowed")
        self.assertEqual(body, b"")
        self.assertFalse(observed)
        self.assertEqual(self.audited_reads(), before)

    def test_get_still_reads_fictional_history(self):
        before = self.audited_reads()
        status, body = self.call(method="GET")
        self.assertEqual(status, "200 OK")
        self.assertIn(b'"child_count":2', body)
        self.assertEqual(self.audited_reads(), before + 1)

    def test_bracket_ipv6_local_host_and_valid_ports(self):
        for host in ("127.0.0.1", "localhost", "[::1]",
                     "localhost:8091", "[::1]:8091", "127.0.0.1:65535"):
            with self.subTest(host=host):
                self.assertTrue(_safe_loopback_host(host))
                self.assertEqual(self.call(path="/healthz", host=host)[0], "200 OK")

    def test_bad_host_must_not_dispatch(self):
        bad = ("127.0.0.1:garbage", "127.0.0.1:", "localhost:65536",
               "localhost:0", "localhost:-1", "[::1", "[::1]:invalid",
               "[::1]:8080:22", "127.0.0.1.evil.test", "localhost.evil.test",
               "127.0.0.1@evil.test", "localhost:1/route", "localhost:１",
               "evil.test", "", None)
        before = self.audited_reads()
        for host in bad:
            with self.subTest(host=host):
                self.assertFalse(_safe_loopback_host(host))
                self.assertEqual(self.call(method="GET", host=host)[0],
                                 "403 Forbidden")
        self.assertEqual(self.audited_reads(), before)


if __name__ == "__main__":
    unittest.main()
