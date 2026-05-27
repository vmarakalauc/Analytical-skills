---
description: Route an Oracle analytics question to the right subject-area skill, semantic model, SQL validation flow, and optional execution path.
---

Use `oracle-analytics-router` first for the user's analytics question.

Steps:

1. Run or reason from `scripts/check_prereqs.py`.
2. Load `routing/subject-area-routing.yaml`.
3. Route the question to the best supported subject area.
4. Use the matched subject-area skill and semantic model.
5. Generate relevant semantic context with `scripts/generate_prompt_context.py`.
6. Ask clarifying questions if the term, metric, subject area, or grouping is ambiguous.
7. Generate Oracle 19c SELECT-only SQL.
8. Validate with `scripts/validate_sql.py`.
9. Ask the user before executing.
10. Execute only with `scripts/execute_oracle_readonly.py <sql-file> --yes` after explicit approval.
11. Summarize result, metric definition, filters, route choice, and caveats.
