"""Two intentionally contrasting SQL query implementations for a local lab.

Do not copy the vulnerable branch into production software.
"""
import sqlite3
from contextlib import closing
from pathlib import Path

VALID_MODES = frozenset({"vulnerable", "protected"})


def authenticate(mode: str, username: str, demo_secret: str, database_path: str | Path) -> dict:
    """Run one lab query and return a sanitized result (no input/secret echoed)."""
    if mode not in VALID_MODES:
        raise ValueError("Unsupported demonstration mode")

    try:
        with closing(sqlite3.connect(database_path, timeout=5)) as conn:
            conn.row_factory = sqlite3.Row
            if mode == "vulnerable":
                # INTENTIONALLY VULNERABLE: user input changes the SQL syntax.
                # Run only against the synthetic database on localhost.
                sql = (
                    "SELECT username, role FROM demo_users "
                    f"WHERE username = '{username}' AND demo_secret = '{demo_secret}' LIMIT 1"
                )
                row = conn.execute(sql).fetchone()
            else:
                # CORRECT DEFENCE: the SQL structure is fixed; inputs are data.
                sql = (
                    "SELECT username, role FROM demo_users "
                    "WHERE username = ? AND demo_secret = ? LIMIT 1"
                )
                row = conn.execute(sql, (username, demo_secret)).fetchone()
    except sqlite3.Error:
        # Don't disclose database internals or raw submitted values to the UI.
        return {
            "mode": mode,
            "status": "query_error",
            "authenticated": False,
            "account": None,
            "role": None,
            "message": "The demonstration query could not be evaluated.",
        }

    if row is None:
        return {
            "mode": mode,
            "status": "rejected",
            "authenticated": False,
            "account": None,
            "role": None,
            "message": "No matching demonstration account.",
        }

    return {
        "mode": mode,
        "status": "authenticated",
        "authenticated": True,
        "account": row["username"],
        "role": row["role"],
        "message": "A demonstration account matched the query.",
    }
