# Initial Threat Model

## Asset

Integrity of the authentication decision and confidentiality of dummy account records in a local teaching app.

## Trust boundary

Untrusted user-supplied form fields cross from the browser into a server-side SQL query.

## Threat

SQL injection occurs when input is inserted into a SQL statement as executable syntax rather than bound as a data value.

## Demonstration conditions

- Deliberately vulnerable flow exists only in the isolated VM.
- Protected flow uses SQLite parameter binding (`?` placeholders) for untrusted input.
- Identical synthetic test inputs are used for comparison.
- Outcomes are verified by repeatable tests, not inferred from UI alone.

## Out of scope

Real-world target scanning, third-party exploitation, internet-facing vulnerable endpoints, full production authentication hardening, and enterprise intrusion detection.

## Known limitations

Parameterized queries protect the SQL structure when used correctly, but do not independently guarantee secure password storage, authorization, session management or availability. These should be stated as separate concerns in the final report.
