---
name: oracle-analytics-router
description: Use when the user asks Oracle warehouse analytics questions that may match a supported subject area in this plugin
disable-model-invocation: true
---

# Oracle Analytics Router

## Overview

Routes Oracle 19c warehouse analytics requests to the right subject-area skill and semantic model. This is the generic entry point for the plugin; subject-specific interpretation belongs in the routed skill.

## When to Use

Use for:

- Oracle warehouse analytics questions
- Natural-language text-to-SQL requests over supported semantic models
- General `/ask-analytics` requests that need subject-area selection

Do not use for:

- Non-Oracle data sources
- Raw schema exploration
- Direct SQL execution without validation
- Subject areas absent from `routing/subject-area-routing.yaml`

## Quick Reference

- Routes file: `routing/subject-area-routing.yaml`
- Core prerequisite check: `python scripts/check_prereqs.py`
- Live execution readiness: `python scripts/check_prereqs.py --require-oracle`
- Local env file support: `--env-file <path-to-local-.env>`
- Context generator: `python scripts/generate_prompt_context.py --question "..."`
- SQL validator: `python scripts/validate_sql.py -` reads generated SQL from stdin
- SQL executor: `python scripts/execute_oracle_readonly.py - --yes` reads generated SQL from stdin
- Demo auto-approval: `ORACLE_ANALYTICS_AUTO_APPROVE=true`
- Oracle mode default: thick mode unless `ORACLE_THIN_MODE=true`

## Workflow

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

All relative paths above are relative to the installed plugin root. Do not search or explore the user's current working directory for bundled plugin files. Do not read or print `.env` file contents; pass `.env` paths with `--env-file`.

## Supported Routes

The demo currently supports:

- `student_enrollment` through `student-enrollment-analytics`

Do not invent additional routes. Future subject areas should be added to `routing/subject-area-routing.yaml` and receive their own subject-area skill.

## Prerequisite Handling

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

## Safety Rules

- Never ask the user to paste a password directly into Claude chat.
- Never store credentials in this repository.
- Never return row-level sensitive records.
- Never bypass validation.
- Never run `execute_oracle_readonly.py` without explicit user approval unless `ORACLE_ANALYTICS_AUTO_APPROVE=true` is already set by the user in the local environment.
- If the user asks for unsafe SQL or individual student records, refuse and offer aggregate alternatives.

## Common Mistakes

- Treating missing Oracle credentials as blocking for SQL generation. Credentials are required only for live execution.
- Looking for bundled plugin files in the user's working directory. Resolve `scripts/`, `routing/`, `assets/`, and `skills/` from the installed plugin root.
- Leaving generated SQL scratch files in the user's project. Prefer piping generated SQL to `validate_sql.py -` and `execute_oracle_readonly.py -`.
- Reading `.env` into the conversation. Never display credential files.
- Routing unsupported subject areas by inventing tables or metrics. Instead, explain the supported routes.
- Executing SQL before validation or without explicit user approval.
- Assuming thin mode works in all Oracle environments. This demo defaults to thick mode for Native Network Encryption compatibility.
- Putting production governance in the local plugin. The production model is a central gateway.

## Production Caveat

This local skill/plugin model is for demo and power-user scenarios. Production usage should use a central governed MCP/API gateway.
