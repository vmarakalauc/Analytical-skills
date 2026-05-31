---
description: Check local Oracle analytics plugin prerequisites and configuration.
---

Run the local Oracle semantic analytics prerequisite check.

Resolve all plugin files relative to the installed plugin root, not the user's current working directory. Do not search or explore the user's project folder for bundled plugin files.

Use the plugin-owned setup state. Do not create `.env` files in the user's project folder. Do not read or print credential files.

Configuration lives outside the repository:

- Non-secret settings: `~/.oracle-semantic-analytics/config.json`
- Password for live execution: `SIA_USER_PWD` in the shell that starts Claude Code
- First-time setup command: `/oracle-semantic-analytics:setup-analytics`

Steps:

1. Run `python <plugin-root>/scripts/run_tool.py check_prereqs.py`, or `python <plugin-root>/scripts/run_tool.py check_prereqs.py --require-oracle` for live execution readiness.
2. If configuration is missing, explain the missing items.
3. Do not ask the user to paste passwords into chat.
4. Recommend `/oracle-semantic-analytics:setup-analytics` for first-time setup and `SIA_USER_PWD` for the password.
