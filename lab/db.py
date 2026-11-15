"""SQLite setup for SQLShield's local-only, synthetic authentication lab.

The `demo_secret` column deliberately stores *fictional demonstration tokens*
in clear text so that the exercise isolates the SQL injection issue. This is
NOT an acceptable real-world password storage design. See docs/limitations.md.
"""
from pathlib import Path
from contextlib import closing
import sqlite3

DEFAULT_DATABASE = Path(__file__).resolve().parent / "data" / "sqlshield_lab.sqlite3"

# Completely fictional credentials. Never replace with real user data.
DEMO_USERS = (
    ("alice", "DemoPass123!", "Analyst"),
    ("bob", "BlueTeam456!", "Engineer"),
    ("charlie", "SecureLab789!", "Reviewer"),
)


def initialize_database(database_path: str | Path) -> None:
    """Create a fresh schema if missing; seed fictional users only if empty."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(path, timeout=5)) as conn, conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS demo_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                demo_secret TEXT NOT NULL,
                role TEXT NOT NULL
            )"""
        )
        existing = conn.execute("SELECT COUNT(*) FROM demo_users").fetchone()[0]
        if existing == 0:
            conn.executemany(
                "INSERT INTO demo_users (username, demo_secret, role) VALUES (?, ?, ?)",
                DEMO_USERS,
            )
