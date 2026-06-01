---
description: Check local Oracle analytics plugin prerequisites and configuration.
---

Run the local Oracle semantic analytics prerequisite check.

Use `${CLAUDE_PLUGIN_ROOT}` for all bundled plugin files. Do not search, glob, list `~/.claude/plugins`, or explore the user's project folder for bundled plugin files.

Use the plugin-owned setup state. Do not create `.env` files in the user's project folder. Do not read or print credential files.

Configuration lives outside the repository:

- Non-secret settings: `~/.oracle-semantic-analytics/config.json`
- Password for live execution: `SIA_USER_PWD` in the shell that starts Claude Code
- First-time setup command: `/oracle-semantic-analytics:setup-analytics`

Steps:

1. Prefer MCP `oracle_semantic_health` when available.
2. If MCP is unavailable, run `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" check_prereqs.py`, or `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" check_prereqs.py --require-oracle` for live execution readiness.
3. If configuration is missing, explain the missing items.
4. Do not ask the user to paste passwords into chat.
5. Recommend `/oracle-semantic-analytics:setup-analytics` for first-time setup and `SIA_USER_PWD` for the password.
