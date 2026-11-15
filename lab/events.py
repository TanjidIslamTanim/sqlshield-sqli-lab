"""Minimal, sanitized local test-event history for SQLShield.

Stores only server-generated comparison outcomes, never submitted usernames,
demonstration secrets, SQL strings, IP addresses, or session identifiers.
This is an educational result log, not a real-world SQLi detector.
"""
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

MAX_EVENTS = 5000
FINDINGS = frozenset({
    "injection_effect_observed", "both_authenticated",
    "vulnerable_query_error", "no_bypass_observed",
})
STATUSES = frozenset({"authenticated", "rejected", "query_error"})


def initialize_events(database_path: str | Path) -> None:
    with closing(sqlite3.connect(database_path, timeout=5)) as conn, conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS lab_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            finding TEXT NOT NULL,
            vulnerable_status TEXT NOT NULL,
            protected_status TEXT NOT NULL
        )""")


def record_comparison(database_path: str | Path, finding: str,
                      vulnerable_status: str, protected_status: str) -> int:
    """Persist whitelisted outcome labels; reject arbitrary input values."""
    if finding not in FINDINGS or vulnerable_status not in STATUSES or protected_status not in STATUSES:
        raise ValueError("Unexpected comparison result label")
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(sqlite3.connect(database_path, timeout=5)) as conn, conn:
        cursor = conn.execute(
            """INSERT INTO lab_events
               (created_at, finding, vulnerable_status, protected_status)
               VALUES (?, ?, ?, ?)""",
            (created_at, finding, vulnerable_status, protected_status),
        )
        event_id = cursor.lastrowid
        conn.execute("DELETE FROM lab_events WHERE id <= ?", (event_id - MAX_EVENTS,))
    return event_id


def recent_events(database_path: str | Path, limit: int = 50) -> list[dict]:
    if not isinstance(limit, int) or not 1 <= limit <= 5000:
        raise ValueError("Event limit out of range")
    with closing(sqlite3.connect(database_path, timeout=5)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT id, created_at, finding, vulnerable_status, protected_status
               FROM lab_events ORDER BY id DESC LIMIT ?""", (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def event_statistics(database_path: str | Path) -> dict:
    with closing(sqlite3.connect(database_path, timeout=5)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN finding = 'injection_effect_observed' THEN 1 ELSE 0 END) AS bypass_observed,
            SUM(CASE WHEN finding = 'both_authenticated' THEN 1 ELSE 0 END) AS both_authenticated,
            SUM(CASE WHEN finding = 'no_bypass_observed' THEN 1 ELSE 0 END) AS no_bypass_observed,
            SUM(CASE WHEN finding = 'vulnerable_query_error' THEN 1 ELSE 0 END) AS vulnerable_query_error,
            SUM(CASE WHEN vulnerable_status = 'authenticated' THEN 1 ELSE 0 END) AS vulnerable_matched,
            SUM(CASE WHEN protected_status = 'authenticated' THEN 1 ELSE 0 END) AS protected_matched,
            SUM(CASE WHEN protected_status = 'rejected' THEN 1 ELSE 0 END) AS protected_rejected,
            MAX(created_at) AS last_event_at
            FROM lab_events""").fetchone()
    result = dict(row)
    return {key: (value or 0) if key != "last_event_at" else value
            for key, value in result.items()}
