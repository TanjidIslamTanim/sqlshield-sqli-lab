# Deploy the static SQLShield case study with GitHub Pages

**Do not publish until university coursework-sharing rules and any applicable ownership requirements are checked.** The repository starts private. GitHub Pages availability for private repositories varies by plan and settings.

The repository includes a **manual-only** GitHub Actions workflow (`.github/workflows/deploy-portfolio.yml`). It uploads `portfolio/` and **never runs or hosts Flask**.

1. After permission is confirmed, open `https://github.com/TanjidIslamTanim/sqlshield-sqli-lab`.
2. Open **Settings → Pages** and set **Build and deployment → Source → GitHub Actions**.
3. Open **Actions → Deploy static SQLShield portfolio → Run workflow** and choose the `main` branch.
4. Wait for the workflow to succeed, then open the Pages link in the deployment details or Settings → Pages.
5. If the repository is named `sqlshield-sqli-lab` and the account is `TanjidIslamTanim`, the expected URL is `https://tanjidislamtanim.github.io/sqlshield-sqli-lab/` (this URL is **not live until deployment succeeds**).
6. Check mobile layout, screenshot links and the repository buttons. Confirm the public site is static and exposes no Flask routes, secrets or database files.

Only the static case study is published. Do not use a public tunnel, web host or cloud service for the intentionally vulnerable backend.
