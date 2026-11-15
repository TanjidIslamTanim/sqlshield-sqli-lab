# SQLShield — Phase 4 VM Demonstration Runbook

**Status:** Draft; VM demonstration has not yet been confirmed. Only use the synthetic local lab.

## Before starting
- Confirm your course's approved VM and current semester deadline.
- Copy SQLShield into the VM. Do not use a public tunnel or bind Flask to `0.0.0.0`.
- Use a guest-OS browser; `127.0.0.1` refers to the VM itself.
- Do not use real accounts, personal passwords, or third-party sites.

## Ubuntu / Debian VM commands
```bash
cd /path/to/SQLShield
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python -m lab.app
```
If venv is missing, install `python3-venv` using the course-approved method. Keep the lab loopback-only.

## Live demonstration (approximately 5 minutes)
1. In the VM browser open `http://127.0.0.1:5000/lab`.
2. Click **Valid credentials** → **Run comparison**. Both should match the fictional account.
3. Click **Wrong password** → **Run comparison**. Both should reject.
4. Click **SQL injection example** → **Run comparison**. Unsafe query should match; protected query should reject.
5. Open `http://127.0.0.1:5000/dashboard`; refresh. Review metrics, chart, timeline, and test history.
6. Click **Export CSV** and **Export JSON**. Open each downloaded file and verify that outcome labels match the displayed events. Do not claim this step passed until verified.
7. Explain the mechanism: unsafe string interpolation vs `?` parameter binding in `lab/auth.py`.
8. Stop the server with Ctrl+C. Never deploy this Flask lab to the public internet.

## Evidence capture checklist
- [ ] VM guest desktop visible, showing local Flask server and browser
- [ ] Automated test command and `OK` output visible
- [ ] Three comparison outcomes shown in VM
- [ ] Dashboard after three comparisons
- [ ] Exported CSV and JSON opened and checked
- [ ] Record VM OS/version, Python version, date, team member, and test notes

## Fallback if the live demo fails
Use the screenshots from the verified Windows local run **and explicitly label them as Windows local evidence**. Do not represent them as VM screenshots. Explain the failure and provide a plan to rerun the VM test.
