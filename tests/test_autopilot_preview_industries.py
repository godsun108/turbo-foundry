"""Industry template catalog exposed only by the research-stage preview."""
import json
import unittest
from src.autopilot.portal_app import application


class PreviewIndustriesTests(unittest.TestCase):
    def invoke(self, method="GET", path="/api/industries"):
        captured = {}
        def reply(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)
        body = b"".join(application({"REQUEST_METHOD": method,
                                     "PATH_INFO": path}, reply))
        return captured, body

    def test_industry_templates_are_discovery_only(self):
        meta, data = self.invoke()
        self.assertEqual(meta["status"], "200 OK")
        self.assertEqual(meta["headers"]["Cache-Control"], "no-store")
        parsed = json.loads(data)
        self.assertGreaterEqual(len(parsed), 5)
        self.assertTrue(all(item["status"] == "discovery_only" for item in parsed))
        self.assertTrue(all(item["example_workflows"] for item in parsed))
        self.assertTrue(all("credential" not in str(item).lower() for item in parsed))

    def test_no_provisioning_or_payment_route(self):
        meta, _ = self.invoke(method="POST")
        self.assertEqual(meta["status"], "405 Method Not Allowed")
        meta, _ = self.invoke(path="/api/activate")
        self.assertEqual(meta["status"], "404 Not Found")

    def test_head_has_no_response_body(self):
        meta, body = self.invoke(method="HEAD")
        self.assertEqual(meta["status"], "200 OK")
        self.assertEqual(body, b"")


if __name__ == "__main__":
    unittest.main()
