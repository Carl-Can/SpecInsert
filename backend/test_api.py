"""API checks that do not call an LLM provider."""

import os
import unittest

os.environ["CORS_ORIGINS"] = "https://demo.example"
os.environ["LLM_API_KEY"] = "your_api_key_here"

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


class ApiTests(unittest.TestCase):
    def test_health_reports_unconfigured_placeholder_key(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["llm_configured"])
        self.assertFalse(body["diagnostic_device"])
        self.assertEqual(body["knowledge_base"], "curated_chunks")
        self.assertNotIn("your_api_key_here", response.text)

    def test_root_is_explicitly_educational(self):
        body = client.get("/").json()
        self.assertEqual(body["name"], "Bio-House")
        self.assertTrue(body["educational_use_only"])
        self.assertFalse(body["diagnostic_device"])

    def test_scenarios_list_has_four_presets(self):
        body = client.get("/api/scenarios").json()
        ids = {item["id"] for item in body["scenarios"]}
        self.assertEqual(ids, {"biohacker", "grapefruit", "methanol", "thalidomide"})

    def test_diagnose_refuses_placeholder_key(self):
        response = client.post(
            "/api/diagnose/stream",
            json={"case_input": "metformin and grapefruit", "scenario_id": "custom"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("placeholder", response.json()["detail"])

    def test_cors_allows_configured_public_origin(self):
        response = client.get("/api/health", headers={"Origin": "https://demo.example"})
        self.assertEqual(response.headers.get("access-control-allow-origin"), "https://demo.example")

    def test_cors_does_not_reflect_an_unlisted_origin(self):
        response = client.get("/api/health", headers={"Origin": "https://evil.example"})
        self.assertNotEqual(response.headers.get("access-control-allow-origin"), "https://evil.example")


if __name__ == "__main__":
    unittest.main()
