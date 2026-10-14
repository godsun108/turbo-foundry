"""Synthetic stop-during-read and nonlocal-host regression."""
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.autopilot.gateway_loopback_app import make_synthetic_app


class StopFencingTests(unittest.TestCase):
    def test_stop_during_observation_suppresses_result(self):
        with tempfile.TemporaryDirectory() as folder:
            app, sessions, control = make_synthetic_app(str(Path(folder) / "local.db"))
            token = sessions.issue("offline-operator", now=datetime.now(timezone.utc))
            control.set_enabled(True)
            real_observe = sessions.observe

            def stop_during_read(**kwargs):
                result = real_observe(**kwargs)
                control.set_enabled(False)
                return result

            sessions.observe = stop_during_read
            replies = []
            env = {
                "REMOTE_ADDR": "127.0.0.1",
                "HTTP_HOST": "127.0.0.1:8091",
                "REQUEST_METHOD": "GET",
                "PATH_INFO": "/api/history",
                "HTTP_AUTHORIZATION": "Bearer " + token,
                "QUERY_STRING": "",
            }
            output = b"".join(app(env, lambda status, headers: replies.append(status)))
            self.assertEqual(replies, ["503 Service Unavailable"])
            self.assertNotIn(b"child_count", output)

    def test_dns_rebinding_host_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            app, _, control = make_synthetic_app(str(Path(folder) / "local.db"))
            control.set_enabled(True)
            for host in ("remote.example", "127.0.0.1@remote.example",
                         "remote.example:8091"):
                replies = []
                env = {"REMOTE_ADDR": "127.0.0.1", "HTTP_HOST": host,
                       "REQUEST_METHOD": "GET", "PATH_INFO": "/healthz"}
                b"".join(app(env, lambda status, headers: replies.append(status)))
                self.assertEqual(replies, ["403 Forbidden"])


if __name__ == "__main__":
    unittest.main()
