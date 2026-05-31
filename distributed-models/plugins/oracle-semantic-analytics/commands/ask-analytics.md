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
2. Run or reason from `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py check_prereqs.py`.
   - If core packages/config are missing, ask the user to run `/oracle-semantic-analytics:setup-analytics`.
   - Missing `SIA_USER_PWD` blocks only live execution, not SQL generation or validation.
3. Load `${CLAUDE_PLUGIN_ROOT}/routing/subject-area-routing.yaml`.
4. Route the question to the best supported subject area.
5. Use the matched subject-area skill and semantic model.
6. Generate relevant semantic context with `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py generate_prompt_context.py`.
7. Ask clarifying questions if the term, metric, subject area, or grouping is ambiguous.
8. Generate Oracle 19c SELECT-only SQL.
9. Validate immediately with `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py validate_sql.py -` using stdin; do not ask before running local validation.
10. If `SIA_AUTO_APPROVE=true` is set in user config or environment, and `SIA_USER_PWD` is available, execute the validated SQL without asking again.
11. If auto-approval is not set, ask once before Oracle execution.
12. Execute only with `${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py execute_oracle_readonly.py - --yes` using stdin.
13. Summarize result, metric definition, filters, route choice, and caveats.
