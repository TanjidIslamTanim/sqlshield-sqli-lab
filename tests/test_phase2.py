"""Reproducible local-only SQL injection comparison tests."""
import tempfile
import unittest
from pathlib import Path

from lab.app import create_app
from lab.db import DEMO_USERS


class AuthenticationComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        db = Path(self.tempdir.name) / "isolated-test.sqlite3"
        self.client = create_app({"TESTING": True, "LAB_DATABASE": str(db)}).test_client()

    def compare(self, username: str, demo_secret: str):
        response = self.client.post("/api/compare", json={"username": username, "demo_secret": demo_secret})
        self.assertEqual(response.status_code, 200)
        return response.json

    def test_valid_credentials_work_in_both_modes(self):
        username, demo_secret, role = DEMO_USERS[0]
        data = self.compare(username, demo_secret)
        self.assertTrue(data["vulnerable"]["authenticated"])
        self.assertTrue(data["protected"]["authenticated"])
        self.assertEqual(data["protected"]["account"], username)
        self.assertEqual(data["protected"]["role"], role)
        self.assertEqual(data["finding"], "both_authenticated")

    def test_wrong_password_is_rejected_by_both(self):
        data = self.compare("alice", "wrong-secret")
        self.assertFalse(data["vulnerable"]["authenticated"])
        self.assertFalse(data["protected"]["authenticated"])
        self.assertEqual(data["finding"], "no_bypass_observed")

    def test_injection_bypasses_vulnerable_but_not_protected(self):
        data = self.compare("' OR '1'='1' --", "anything")
        self.assertTrue(data["vulnerable"]["authenticated"])
        self.assertFalse(data["protected"]["authenticated"])
        self.assertEqual(data["finding"], "injection_effect_observed")

    def test_password_field_injection_is_blocked_in_protected(self):
        data = self.compare("alice", "' OR '1'='1' --")
        self.assertTrue(data["vulnerable"]["authenticated"])
        self.assertFalse(data["protected"]["authenticated"])

    def test_malformed_query_returns_sanitized_error(self):
        data = self.compare("alice'", "anything")
        self.assertEqual(data["vulnerable"]["status"], "query_error")
        self.assertFalse(data["protected"]["authenticated"])
        self.assertNotIn("SELECT username", str(data))

    def test_response_does_not_echo_submitted_secret(self):
        secret = "dummy-not-for-logging"
        data = self.compare("alice", secret)
        self.assertNotIn(secret, str(data))

    def test_json_required(self):
        response = self.client.post("/api/compare", data="hello", content_type="text/plain")
        self.assertEqual(response.status_code, 415)

    def test_input_validation(self):
        for payload in (
            {},
            {"username": "alice", "demo_secret": 123},
            {"username": "", "demo_secret": "x"},
            {"username": "a" * 161, "demo_secret": "x"},
        ):
            with self.subTest(payload=payload):
                response = self.client.post("/api/compare", json=payload)
                self.assertEqual(response.status_code, 400)

    def test_single_mode_endpoint(self):
        response = self.client.post(
            "/api/login/protected", json={"username": "alice", "demo_secret": "DemoPass123!"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["authenticated"])
        self.assertEqual(self.client.post("/api/login/unknown", json={}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
