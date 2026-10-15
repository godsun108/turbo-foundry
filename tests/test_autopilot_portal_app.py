"""WSGI smoke tests for the integrated, intentionally read-only portal."""
import io
import json
import unittest

from src.autopilot.portal_app import application


def request(path, method="GET"):
    results = {}
    def start(status, headers):
        results["status"] = status
        results["headers"] = dict(headers)
    chunks = application({
        "REQUEST_METHOD": method, "PATH_INFO": path,
        "wsgi.input": io.BytesIO(b""),
    }, start)
    return results, b"".join(chunks)


class PortalAppTests(unittest.TestCase):
    def test_preview_page_is_accessible(self):
        result, body = request("/")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn(b"Checkout", body)
        self.assertIn(b"not yet available", body)
        self.assertIn("no-store", result["headers"]["Cache-Control"])
        self.assertEqual(result["headers"]["X-Frame-Options"], "DENY")

    def test_catalog_labels_all_five_proposals(self):
        result, body = request("/api/offers")
        self.assertEqual(result["status"], "200 OK")
        offers = json.loads(body)
        self.assertEqual(len(offers), 5)
        self.assertEqual(sum(o["status"] == "offline_demo" for o in offers), 1)
        self.assertEqual(sum(o["status"] == "concept" for o in offers), 4)

    def test_readiness_is_truthful_and_all_customer_actions_disabled(self):
        _, body = request("/api/readiness")
        status = json.loads(body)
        self.assertEqual(status["deployment"], "preview_only")
        self.assertTrue(all(value is False for key, value in status.items()
                            if key != "deployment"))

    def test_every_write_endpoint_is_blocked(self):
        for path in ("/api/checkout", "/api/onboard", "/api/accounts", "/"):
            with self.subTest(path=path):
                result, body = request(path, "POST")
                self.assertEqual(result["status"], "405 Method Not Allowed")
                self.assertEqual(json.loads(body)["error"], "read_only_preview")

    def test_health_missing_and_head(self):
        self.assertEqual(json.loads(request("/healthz")[1])["status"], "ok")
        self.assertEqual(request("/nonexistent")[0]["status"], "404 Not Found")
        result, body = request("/api/offers", "HEAD")
        self.assertEqual(result["status"], "200 OK")
        self.assertEqual(body, b"")


if __name__ == "__main__":
    unittest.main()
