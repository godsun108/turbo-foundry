"""Staging health service never leaks into provider, commerce or customer operations."""
import json
import unittest

from src.autopilot.staging_health_app import application, _allowed_host


class StagingHealthTests(unittest.TestCase):
    def call(self, *, method="GET", path="/healthz", host="127.0.0.1:8094",
             remote="127.0.0.1", query="", extra=None, port="8094"):
        env = {"REQUEST_METHOD": method, "PATH_INFO": path, "HTTP_HOST": host,
               "REMOTE_ADDR": remote, "QUERY_STRING": query, "SERVER_PORT": port}
        env.update(extra or {})
        result = []
        payload = b"".join(application(env, lambda status, headers: result.append(
            (status, dict(headers)))))
        return result[0][0], result[0][1], payload

    def test_health_is_explicitly_not_live(self):
        status, headers, data = self.call()
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Cache-Control"], "no-store")
        report = json.loads(data)
        self.assertEqual(report["mode"], "loopback_health_only")
        self.assertFalse(report["live_provider_connected"])
        self.assertFalse(report["live_service_ready"])
        self.assertFalse(report["customer_checkout_enabled"])
        self.assertFalse(report["communications_enabled"])

    def test_method_routes_and_head(self):
        status, headers, body = self.call(method="HEAD")
        self.assertEqual(status, "200 OK")
        self.assertEqual(body, b"")
        self.assertGreater(int(headers["Content-Length"]), 0)
        for method, path, query in (("POST", "/healthz", ""), ("GET", "/api/history", ""),
                                    ("GET", "/healthz", "token=secret"),
                                    ("GET", "/api/activate", "")):
            with self.subTest(method=method, path=path, query=query):
                self.assertNotEqual(self.call(method=method, path=path, query=query)[0],
                                    "200 OK")

    def test_host_forwarding_and_remote_blocked(self):
        for host in ("foundry.com", "127.0.0.1.evil.com", "127.0.0.1:8443",
                     "127.0.0.1:8094@evil.com", "", "localhost:garbage"):
            with self.subTest(host=host):
                self.assertEqual(self.call(host=host)[0], "403 Forbidden")
        self.assertEqual(self.call(remote="172.20.0.5")[0], "403 Forbidden")
        for header in ("HTTP_X_FORWARDED_FOR", "HTTP_FORWARDED",
                       "HTTP_X_FORWARDED_HOST", "HTTP_X_FORWARDED_PROTO"):
            self.assertEqual(self.call(extra={header:"127.0.0.1"})[0],
                             "403 Forbidden")

    def test_host_validation(self):
        self.assertTrue(_allowed_host({"HTTP_HOST":"localhost:8045",
                                        "SERVER_PORT":"8045"}))
        self.assertTrue(_allowed_host({"HTTP_HOST":"[::1]:8094",
                                        "SERVER_PORT":"8094"}))
        self.assertFalse(_allowed_host({"HTTP_HOST":"localhost",
                                         "SERVER_PORT":"invalid"}))
        self.assertFalse(_allowed_host({"HTTP_HOST":None,
                                         "SERVER_PORT":"8094"}))


if __name__ == "__main__":
    unittest.main()
