# Security policy — educational lab

This repository intentionally contains an insecure SQL query for teaching SQL injection.

- **Do not** host or deploy `lab/` publicly, including through cloud platforms, public IPs, tunnels, port forwarding or reverse proxies.
- Run only on your own machine or an isolated VM, bound to `127.0.0.1`.
- Use only the included synthetic data. Never enter real passwords or target external applications.
- The `portfolio/` folder contains static files and original screenshots; it is the only component intended for GitHub Pages.
- Do not commit `.env`, SQLite database files, logs, personal information, tokens, private university submission documents or VM disk images.
- Review all changes before making the repository public. If a genuine security issue is found, contact the maintainer privately instead of posting sensitive details in an issue.
