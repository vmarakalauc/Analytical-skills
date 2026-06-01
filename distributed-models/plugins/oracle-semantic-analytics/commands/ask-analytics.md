---
description: Route an Oracle analytics question to the right subject-area skill, semantic model, SQL validation flow, and optional execution path.
---

Use `oracle-analytics-router` first for the user's analytics question.

Use `${CLAUDE_PLUGIN_ROOT}` for all bundled plugin files. Do not search, glob, list `~/.claude/plugins`, or explore the user's project folder for `scripts/`, `routing/`, `assets/`, or `skills/`; those directories are bundled inside this plugin.

Use the plugin-owned setup state. Do not create `.env` files or scratch SQL files in the user's project folder. Do not read or print credential files.

Configuration lives outside the repository:

- Non-secret settings: `~/.oracle-semantic-analytics/config.json`
- Password for live execution: `SIA_USER_PWD` in the shell that starts Claude Code
- First-time setup command: `/oracle-semantic-analytics:setup-analytics`

Steps:

1. Use `${CLAUDE_PLUGIN_ROOT}` as the installed plugin root.
2. Call MCP tool `oracle_semantic_health` to confirm prerequisites.
3. Load `${CLAUDE_PLUGIN_ROOT}/routing/subject-area-routing.yaml` and route the question to the best supported subject area.
4. If core packages/config are missing, ask the user to run `/oracle-semantic-analytics:setup-analytics`. Missing `SIA_USER_PWD` blocks only live execution, not SQL generation or validation.
5. Use the matched subject-area skill and semantic model.
6. Call MCP tool `oracle_semantic_get_context` with the user's question to load the semantic context.
7. Ask clarifying questions if the term, metric, subject area, or grouping is ambiguous.
8. Generate Oracle 19c SELECT-only SQL.
9. Call MCP tool `oracle_semantic_validate_sql` immediately — do not ask the user before validating.
10. Always display the validated SQL to the user before executing.
11. If `SIA_AUTO_APPROVE=true` is set in user config or environment, and `SIA_USER_PWD` is available, call MCP tool `oracle_semantic_execute_sql` without asking again.
12. If auto-approval is not set, ask once before Oracle execution, then call MCP tool `oracle_semantic_execute_sql`.
13. Summarize result, metric definition, filters, route choice, and caveats.

If the MCP server is unavailable, fall back to `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py` for each step.
