---
description: Ask a student enrollment analytics question using the bundled semantic model.
---

Use the student enrollment semantic model to answer the user's analytics question.

Use `${CLAUDE_PLUGIN_ROOT}` for all bundled plugin files. Do not search, glob, list `~/.claude/plugins`, or explore the user's project folder for bundled plugin files.

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
5. Use `oracle-analytics-router` to confirm the route is `student_enrollment`.
6. Load `${CLAUDE_PLUGIN_ROOT}/assets/semantic_models/sia_term_enrollments.yaml`.
7. Generate relevant semantic context with MCP `oracle_semantic_get_context` or `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py generate_prompt_context.py`.
8. Ask clarifying questions if the term, metric, or grouping is ambiguous.
9. Generate Oracle 19c SELECT-only SQL.
10. Validate immediately with MCP `oracle_semantic_validate_sql` or `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py validate_sql.py -`; do not ask before running local validation.
11. If `SIA_AUTO_APPROVE=true` is set in user config or environment, and `SIA_USER_PWD` is available, execute the validated SQL without asking again.
12. If auto-approval is not set, ask once before Oracle execution.
13. Execute only with MCP `oracle_semantic_execute_sql` or `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py execute_oracle_readonly.py - --yes`.
14. Summarize result, metric definition, filters, and caveats.
