"""Smoke checks for the Phase 3 application."""
import tempfile
import unittest
from pathlib import Path

from lab.app import create_app


class SQLShieldSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        db = Path(self.tempdir.name) / "test.sqlite3"
        self.client = create_app({"TESTING": True, "LAB_DATABASE": str(db)}).test_client()

    def test_home_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SQLShield", response.data)

    def test_comparison_page_loads(self):
        response = self.client.get("/lab")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Same input", response.data)

    def test_dashboard_loads(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Security", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok", "phase": 3})

    def test_security_headers(self):
        response = self.client.get("/")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_non_loopback_client_is_blocked(self):
        response = self.client.get("/", environ_overrides={"REMOTE_ADDR": "192.0.2.10"})
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
