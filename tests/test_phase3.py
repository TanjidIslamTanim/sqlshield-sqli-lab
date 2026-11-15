"""Phase 3: event recording, privacy, analytics, persistence and export."""
import csv
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

from lab.app import create_app


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.db = Path(self.tempdir.name) / "dashboard-test.sqlite3"
        self.client = create_app({"TESTING": True, "LAB_DATABASE": str(self.db)}).test_client()

    def compare(self, username, demo_secret):
        response = self.client.post("/api/compare", json={
            "username": username, "demo_secret": demo_secret,
        })
        self.assertEqual(response.status_code, 200)
        return response.json

    def test_dashboard_and_empty_stats(self):
        self.assertEqual(self.client.get("/dashboard").status_code, 200)
        stats = self.client.get("/api/stats").json
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["bypass_observed"], 0)
        self.assertEqual(self.client.get("/api/events").json["events"], [])

    def test_comparisons_are_logged_and_counted(self):
        self.compare("alice", "DemoPass123!")
        self.compare("alice", "wrong-secret")
        data = self.compare("' OR '1'='1' --", "anything")
        self.assertIsInstance(data["event_id"], int)
        stats = self.client.get("/api/stats").json
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["bypass_observed"], 1)
        self.assertEqual(stats["both_authenticated"], 1)
        self.assertEqual(stats["no_bypass_observed"], 1)
        self.assertEqual(stats["vulnerable_matched"], 2)
        self.assertEqual(stats["protected_matched"], 1)
        self.assertEqual(stats["protected_rejected"], 2)
        events = self.client.get("/api/events?limit=2").json["events"]
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["finding"], "injection_effect_observed")
        self.assertGreater(events[0]["id"], events[1]["id"])

    def test_no_submitted_input_is_persisted_or_exported(self):
        marker = "secret-marker-not-to-log-93f1"
        self.compare("alice", marker)
        with sqlite3.connect(self.db) as conn:
            columns = [row[1] for row in conn.execute("PRAGMA table_info(lab_events)")]
            self.assertEqual(columns, ["id", "created_at", "finding", "vulnerable_status", "protected_status"])
            rows = conn.execute("SELECT * FROM lab_events").fetchall()
            self.assertEqual(len(rows), 1)
            self.assertNotIn(marker, str(rows))
        self.assertNotIn(marker, self.client.get("/api/export.csv").get_data(as_text=True))
        self.assertNotIn(marker, self.client.get("/api/export.json").get_data(as_text=True))
        self.assertNotIn(marker.encode(), self.db.read_bytes())

    def test_invalid_requests_do_not_log_events(self):
        response = self.client.post("/api/compare", json={"username": "alice"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/api/stats").json["total"], 0)
        for limit in ("0", "201", "invalid", "-1"):
            with self.subTest(limit=limit):
                self.assertEqual(self.client.get(f"/api/events?limit={limit}").status_code, 400)

    def test_single_mode_endpoint_not_counted(self):
        self.client.post("/api/login/protected", json={
            "username": "alice", "demo_secret": "DemoPass123!",
        })
        self.assertEqual(self.client.get("/api/stats").json["total"], 0)

    def test_csv_and_json_export(self):
        self.compare("alice", "DemoPass123!")
        response = self.client.get("/api/export.csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response.headers["Content-Disposition"])
        rows = list(csv.DictReader(io.StringIO(response.get_data(as_text=True))))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["finding"], "both_authenticated")
        self.assertNotIn("demo_secret", rows[0])
        self.assertEqual(len(self.client.get("/api/export.json").json["events"]), 1)

    def test_event_history_persists_after_app_recreation(self):
        self.compare("alice", "wrong-secret")
        new_client = create_app({"TESTING": True, "LAB_DATABASE": str(self.db)}).test_client()
        self.assertEqual(new_client.get("/api/stats").json["total"], 1)

    def test_non_loopback_dashboard_and_export_blocked(self):
        for route in ("/dashboard", "/api/events", "/api/stats", "/api/export.csv"):
            with self.subTest(route=route):
                response = self.client.get(route, environ_overrides={"REMOTE_ADDR": "192.0.2.15"})
                self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
