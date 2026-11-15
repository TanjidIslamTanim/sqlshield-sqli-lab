# Phase 3 — Evidence Dashboard

## Purpose

The dashboard displays **actual outcomes from controlled local comparisons**. It is not a production monitoring system, security information and event management (SIEM) product, or general SQLi detector.

## Routes

- `/dashboard` — visual statistics, finding distribution, comparison chart, timeline and recent history.
- `GET /api/stats` — aggregate counts for completed `/api/compare` requests.
- `GET /api/events?limit=50` — newest events (limit 1–200).
- `GET /api/export.csv` — sanitized retained history as a CSV attachment.
- `GET /api/export.json` — sanitized retained history in JSON.

## Data model

The `lab_events` table contains only:

| Field | Meaning |
|---|---|
| `id` | Auto-incrementing local event number |
| `created_at` | UTC timestamp |
| `finding` | Server-generated comparison finding enum |
| `vulnerable_status` | `authenticated`, `rejected` or `query_error` |
| `protected_status` | `authenticated`, `rejected` or `query_error` |

**Not recorded:** submitted usernames, demo secrets, SQL statements, raw requests, IP addresses, user agents, or personal information. The event table is retained in the local SQLite database, which is excluded from Git via `.gitignore`. At most 5,000 recent events are retained. Only `/api/compare` creates an event; `/api/login/<mode>` does not.

## Interpreting metrics

- **Injection effect observed:** the vulnerable query matched a dummy account and the protected query did not. This is an *outcome-based observation* for a controlled lab test, not a universal attack classifier.
- **Both authenticated:** both queries matched an account. For the supplied valid credentials, this is expected.
- **No bypass observed:** no differential authentication match occurred. Wrong credentials are a common example.
- **Unsafe query error:** the vulnerable SQL statement failed to parse.
- **Protected rejections:** counts all protected query rejections, including wrong passwords; it is **not** a count of attacks blocked.

The charts show recorded comparisons, not all security events or all possible SQLi payloads. The demonstration database intentionally contains public fictional demo secrets; production authentication needs secure password hashing and other protections.

## Demo sequence

1. Start the local Flask app and visit `/dashboard` to show the empty state (if no previous comparisons).
2. Go to `/lab`; run Valid credentials, Wrong password and SQL injection example once each.
3. Return to `/dashboard` and click Refresh. Confirm 3 comparisons, 1 injection effect, 2 vulnerable matches and 2 protected rejections.
4. Export CSV and inspect the rows. Verify no input strings or passwords appear.
5. Restart Flask and confirm the same events remain (SQLite persistence).

## Safety

The lab must remain bound to `127.0.0.1`. Never publish the Flask backend, use public port forwarding or tunnels, or enter real credentials. The public portfolio remains static only.
