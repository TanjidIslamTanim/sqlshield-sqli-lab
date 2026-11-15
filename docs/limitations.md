# Phase 3 Scope and Limitations

1. **Deliberate SQL injection vulnerability:** `lab/auth.py` uses string interpolation in vulnerable mode solely for local demonstration. Never reuse it for an actual service.
2. **No real authentication:** A result of `authenticated: true` means a SELECT query matched a synthetic row. The app creates no login session, cookie, or access privileges.
3. **Demo secrets, not user passwords:** The SQLite `demo_secret` values are fictional and intentionally stored in clear text so the exercise isolates SQL query construction. Real systems must use salted, adaptive password hashing (e.g. Argon2id or scrypt) and appropriate credential verification.
4. **What parameterization does:** Binding inputs with `?` placeholders prevents input from altering the SQL statement structure in this example. It does not by itself solve authorization, XSS, CSRF, credential stuffing, rate limiting, session management, or every SQL design risk.
5. **No SQLi detection engine:** The app compares outcomes for a user-supplied test; it does not automatically classify attacks or monitor external traffic.
6. **Local-only controls are not sufficient for public hosting:** Flask binds to `127.0.0.1` and checks client IP, but forwarding/tunnels can expose the service. Do not use them. Keep the lab inside an isolated VM where practical.
7. **Sanitized results, not live detection:** Phase 3 stores server-generated comparison outcome labels and timestamps, with a dashboard and exports. It does not monitor network traffic, classify all SQLi payloads, or store raw submitted input. Up to 5,000 local events are retained.
8. **Input validation:** JSON requests are size-limited and require short strings; this is a stability measure, not a substitute for SQL parameterization.
