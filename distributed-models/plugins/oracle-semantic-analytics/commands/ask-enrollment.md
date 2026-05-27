---
description: Ask a student enrollment analytics question using the bundled semantic model.
---

Use the student enrollment semantic model to answer the user's analytics question.

Steps:

1. Run or reason from `scripts/check_prereqs.py`.
2. Use `oracle-analytics-router` to confirm the route is `student_enrollment`.
3. Load `assets/semantic_models/sia_term_enrollments.yaml`.
4. Generate relevant semantic context with `scripts/generate_prompt_context.py`.
5. Ask clarifying questions if the term, metric, or grouping is ambiguous.
6. Generate Oracle 19c SELECT-only SQL.
7. Validate with `scripts/validate_sql.py`.
8. Ask the user before executing.
9. Execute only with `scripts/execute_oracle_readonly.py <sql-file> --yes` after explicit approval.
10. Summarize result, metric definition, filters, and caveats.
