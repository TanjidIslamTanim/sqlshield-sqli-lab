"""Standalone SQLite tests that do not depend on Flask being installed."""
import tempfile
import unittest
from pathlib import Path

from lab.events import initialize_events, record_comparison, recent_events, event_statistics


class EventStorageTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.db = Path(self.tempdir.name) / "events.sqlite3"
        initialize_events(self.db)

    def test_record_and_summary(self):
        record_comparison(self.db, "both_authenticated", "authenticated", "authenticated")
        record_comparison(self.db, "injection_effect_observed", "authenticated", "rejected")
        self.assertEqual(event_statistics(self.db)["total"], 2)
        self.assertEqual(event_statistics(self.db)["bypass_observed"], 1)
        self.assertEqual(recent_events(self.db, 1)[0]["finding"], "injection_effect_observed")

    def test_rejects_unexpected_values(self):
        with self.assertRaises(ValueError):
            record_comparison(self.db, "untrusted input", "authenticated", "rejected")
        self.assertEqual(event_statistics(self.db)["total"], 0)


if __name__ == "__main__":
    unittest.main()
