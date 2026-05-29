---
description: Run first-time setup for the Oracle semantic analytics plugin.
---

Set up the local Oracle semantic analytics runtime and user config.

Resolve all plugin files relative to the installed plugin root, not the user's current working directory. Do not search or explore the user's project folder for bundled plugin files.

Run:

```bash
python <plugin-root>/scripts/setup_analytics.py
```

This setup creates:

- `~/.oracle-semantic-analytics/venv` for plugin Python dependencies.
- `~/.oracle-semantic-analytics/config.json` for non-secret settings.
- `~/.oracle-semantic-analytics/reports` for generated local reports.

It must not store the Oracle password. After setup, tell the user to set the password in the shell that starts Claude Code:

```powershell
$env:SIA_USER_PWD = "your_password"
```

Do not ask the user to paste the password into chat. Do not read or print credential files.
