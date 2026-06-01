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

Prefer stdin through the runtime wrapper so no temporary SQL files are left in the user's project folder and the plugin uses its managed venv automatically:

```bash
printf '%s\n' "<generated SQL>" | python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" validate_sql.py -
printf '%s\n' "<generated SQL>" | python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" execute_oracle_readonly.py - --yes
```

Steps:

1. Use `${CLAUDE_PLUGIN_ROOT}` as the installed plugin root.
2. Prefer the plugin MCP tools when available:
   - `oracle_semantic_health`
   - `oracle_semantic_get_context`
   - `oracle_semantic_validate_sql`
   - `oracle_semantic_execute_sql`
3. If MCP tools are unavailable, fall back to `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py`.
4. Run or reason from MCP health or `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py check_prereqs.py`.
   - If core packages/config are missing, ask the user to run `/oracle-semantic-analytics:setup-analytics`.
   - Missing `SIA_USER_PWD` blocks only live execution, not SQL generation or validation.
5. Load `${CLAUDE_PLUGIN_ROOT}/routing/subject-area-routing.yaml`.
6. Route the question to the best supported subject area.
7. Use the matched subject-area skill and semantic model.
8. Generate relevant semantic context with MCP `oracle_semantic_get_context` or `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py generate_prompt_context.py`.
9. Ask clarifying questions if the term, metric, subject area, or grouping is ambiguous.
10. Generate Oracle 19c SELECT-only SQL.
11. Validate immediately with MCP `oracle_semantic_validate_sql` or `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py validate_sql.py -`; do not ask before running local validation.
12. If `SIA_AUTO_APPROVE=true` is set in user config or environment, and `SIA_USER_PWD` is available, execute the validated SQL without asking again.
13. If auto-approval is not set, ask once before Oracle execution.
14. Execute only with MCP `oracle_semantic_execute_sql` or `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py execute_oracle_readonly.py - --yes`.
15. Summarize result, metric definition, filters, route choice, and caveats.
