---
description: Ask a student enrollment analytics question using the bundled semantic model.
---

Use the student enrollment semantic model to answer the user's analytics question.

Resolve all plugin files relative to the installed plugin root, not the user's current working directory. Do not search or explore the user's project folder for bundled plugin files.

Do not read or print `.env` file contents. If the user keeps credentials in a local ignored `.env`, pass its path with `--env-file <path>` instead of opening it.

Prefer stdin for generated SQL so no temporary SQL files are left in the user's project folder:

```bash
printf '%s\n' "<generated SQL>" | python <plugin-root>/scripts/validate_sql.py -
printf '%s\n' "<generated SQL>" | python <plugin-root>/scripts/execute_oracle_readonly.py - --env-file <path> --yes
```

Steps:

1. Resolve the installed plugin root.
2. Run or reason from `<plugin-root>/scripts/check_prereqs.py`.
3. Use `oracle-analytics-router` to confirm the route is `student_enrollment`.
4. Load `<plugin-root>/assets/semantic_models/sia_term_enrollments.yaml`.
5. Generate relevant semantic context with `<plugin-root>/scripts/generate_prompt_context.py`.
6. Ask clarifying questions if the term, metric, or grouping is ambiguous.
7. Generate Oracle 19c SELECT-only SQL.
8. Validate with `<plugin-root>/scripts/validate_sql.py -` using stdin, or with a file only if the user asks to keep the SQL.
9. Ask the user before executing unless `ORACLE_ANALYTICS_AUTO_APPROVE=true` is set by the user.
10. Execute only with `<plugin-root>/scripts/execute_oracle_readonly.py - --yes` using stdin after explicit approval, or pass `--env-file <path>` when the user keeps credentials in a local ignored `.env`.
11. Summarize result, metric definition, filters, and caveats.
