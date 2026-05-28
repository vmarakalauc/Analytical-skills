---
description: Route an Oracle analytics question to the right subject-area skill, semantic model, SQL validation flow, and optional execution path.
---

Use `oracle-analytics-router` first for the user's analytics question.

Resolve all plugin files relative to the installed plugin root, not the user's current working directory. Do not search or explore the user's project folder for `scripts/`, `routing/`, `assets/`, or `skills/`; those directories are bundled inside this plugin. If you need the plugin root, read the loaded plugin metadata or `~/.claude/plugins/installed_plugins.json` once, then use absolute paths from that root.

Do not read or print `.env` file contents. If the user keeps credentials in a local ignored `.env`, pass its path with `--env-file <path>` instead of opening it.

Prefer stdin for generated SQL so no temporary SQL files are left in the user's project folder:

```bash
printf '%s\n' "<generated SQL>" | python <plugin-root>/scripts/validate_sql.py -
printf '%s\n' "<generated SQL>" | python <plugin-root>/scripts/execute_oracle_readonly.py - --env-file <path> --yes
```

Steps:

1. Resolve the installed plugin root.
2. Run or reason from `<plugin-root>/scripts/check_prereqs.py`.
3. Load `<plugin-root>/routing/subject-area-routing.yaml`.
4. Route the question to the best supported subject area.
5. Use the matched subject-area skill and semantic model.
6. Generate relevant semantic context with `<plugin-root>/scripts/generate_prompt_context.py`.
7. Ask clarifying questions if the term, metric, subject area, or grouping is ambiguous.
8. Generate Oracle 19c SELECT-only SQL.
9. Validate with `<plugin-root>/scripts/validate_sql.py -` using stdin, or with a file only if the user asks to keep the SQL.
10. Ask the user before executing unless `ORACLE_ANALYTICS_AUTO_APPROVE=true` is set by the user.
11. Execute only with `<plugin-root>/scripts/execute_oracle_readonly.py - --yes` using stdin after explicit approval, or pass `--env-file <path>` when the user keeps credentials in a local ignored `.env`.
12. Summarize result, metric definition, filters, route choice, and caveats.
