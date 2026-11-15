# Security Boundaries

1. **Only owned systems:** SQL injection testing is limited to the team's own local lab with synthetic accounts.
2. **Never publish the vulnerable backend:** The Flask lab binds to `127.0.0.1` inside the VM. Do not enable public IP binding, port forwarding, reverse proxies, or tunnels.
3. **Static-only public deployment:** GitHub Pages publishes `portfolio/` and nothing under `lab/`.
4. **No secrets or personal data:** Use synthetic usernames and test credentials only. Keep local databases, logs, `.env` files, and VM images out of the repository.
5. **Log sparingly:** If test-event logging is implemented, log test IDs, timestamps, mode and result, not raw passwords, access tokens or personal data.
6. **No inflated claims:** Parameterization protects query structure from SQL injection; it does not by itself solve all authentication, authorization, CSRF, XSS, rate-limiting or credential-storage issues.
7. **Assessment compliance:** Follow university AI-use, attribution and group-contribution rules. Only claim development, testing, and other work that can be explained and supported.
