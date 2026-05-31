---
description: Run first-time setup for the Oracle semantic analytics plugin.
---

Set up the local Oracle semantic analytics runtime and user config.

Resolve all plugin files relative to the installed plugin root, not the user's current working directory. Do not search or explore the user's project folder for bundled plugin files.

Do not run the setup script in interactive prompt mode from Claude Code. Collect the non-secret values from the user, then run the script with command-line flags.

Ask for these non-secret values:

- SIA Oracle username
- SIA Oracle DSN, such as `host:port/service`
- Oracle Client library folder, or say you will use auto-detection if the user does not know it
- Whether controlled-demo auto-approval should be `true` or `false`
- Maximum rows, default `1000`

Do not ask for the Oracle password.

Run the setup script like this, omitting optional flags only when the user leaves the value blank:

```bash
python <plugin-root>/scripts/setup_analytics.py --sia-user "<user>" --sia-dsn "<host:port/service>" --oracle-client-lib "<client-lib-folder>" --auto-approve false --max-rows 1000
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
