---
description: Route Oracle 19c warehouse analytics questions to the correct subject-area skill, semantic model, validation flow, and optional read-only execution path.
disable-model-invocation: true
---

# Oracle Analytics Router

Use this skill when the user asks a warehouse analytics question that may be answered from Oracle using this plugin.

## Routing workflow

1. Check core prerequisites with `scripts/check_prereqs.py`.
2. Load `routing/subject-area-routing.yaml`.
3. Match the user question to a route by keywords, subject-area intent, and available semantic models.
4. If no route matches, say that this demo only supports the listed subject areas and ask the user to rephrase within those domains.
5. For the matched route, use the route's subject-area skill and semantic model.
6. Generate Oracle 19c `SELECT` SQL only from bundled semantic context.
7. Validate SQL with `scripts/validate_sql.py` before offering execution.
8. Ask the user before running SQL against Oracle.
9. Execute SQL only through `scripts/execute_oracle_readonly.py <sql-file> --yes` after explicit user approval.
10. Explain the metric definition, filters, assumptions, and caveats.

## Current routes

The demo currently supports:

- `student_enrollment` through `student-enrollment-analytics`

Do not invent additional routes. Future subject areas should be added to `routing/subject-area-routing.yaml` and receive their own subject-area skill.

## Prerequisite handling

For prompt-context generation and SQL validation:

```bash
python -m pip install -r requirements.txt
python scripts/check_prereqs.py
```

For live Oracle execution:

```bash
python scripts/check_prereqs.py --require-oracle
```

If Oracle configuration is missing, say:

```text
Oracle execution is not configured yet. You can still generate and validate SQL. For live execution, run the configuration helper or set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN in your shell environment. Do not paste passwords into chat.
```

Then suggest:

```bash
python plugins/oracle-semantic-analytics/scripts/configure_oracle.py
```

## Safety rules

- Never ask the user to paste a password directly into Claude chat.
- Never store credentials in this repository.
- Never return row-level sensitive records.
- Never bypass validation.
- Never run `execute_oracle_readonly.py` without explicit user approval.
- If the user asks for unsafe SQL or individual student records, refuse and offer aggregate alternatives.

## Production caveat

This local skill/plugin model is for demo and power-user scenarios. Production usage should use a central governed MCP/API gateway.
