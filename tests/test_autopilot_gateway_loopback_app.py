"""Offline localhost WSGI runtime verification."""
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from src.autopilot.gateway_loopback_app import make_synthetic_app


class LoopbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app, self.sessions, self.control = make_synthetic_app(
            str(Path(self.temp.name) / "local.sqlite"))

    def call(self, method="GET", path="/api/history", remote="127.0.0.1",
             authorization="", query=""):
        captured = []
        def start(status, headers):
            captured.append(status)
        environ = dict(REQUEST_METHOD=method, PATH_INFO=path,
                       REMOTE_ADDR=remote, HTTP_AUTHORIZATION=authorization,
                       QUERY_STRING=query)
        body = b"".join(self.app(environ, start))
        return captured[0], body

    def test_off_by_default(self):
        self.assertEqual(self.call()[0], "503 Service Unavailable")
        self.assertEqual(self.call(path="/login")[0], "404 Not Found")
        self.assertEqual(self.call(method="POST")[0], "405 Method Not Allowed")

    def test_local_session_and_stop(self):
        token = self.sessions.issue("offline-operator", now=datetime.now(timezone.utc))
        self.control.set_enabled(True)
        status, body = self.call(authorization="Bearer " + token)
        self.assertEqual(status, "200 OK")
        self.assertIn(b'"child_count":2', body)
        self.assertNotIn(b"leg-1", body)
        self.control.set_enabled(False)
        self.assertEqual(self.call(authorization="Bearer " + token)[0],
                         "503 Service Unavailable")

    def test_denials(self):
        self.control.set_enabled(True)
        self.assertEqual(self.call()[0], "401 Unauthorized")
        self.assertEqual(self.call(remote="192.0.2.4")[0], "403 Forbidden")
        self.assertEqual(self.call(query="tenant=wrong")[0], "400 Bad Request")
        self.assertEqual(self.call(method="DELETE")[0], "405 Method Not Allowed")

    def test_health_marks_synthetic(self):
        status, body = self.call(path="/healthz")
        self.assertEqual(status, "200 OK")
        self.assertIn(b"synthetic_loopback_only", body)


if __name__ == "__main__":
    unittest.main()
