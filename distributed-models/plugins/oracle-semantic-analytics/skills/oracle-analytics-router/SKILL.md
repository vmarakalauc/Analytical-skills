---
name: oracle-analytics-router
description: Use when the user asks Oracle warehouse analytics questions that may match a supported subject area in this plugin
disable-model-invocation: true
---

# Oracle Analytics Router

## Overview

Routes warehouse analytics requests to the right subject-area skill and semantic contract. This is the generic entry point for the plugin; subject-specific interpretation belongs in the routed skill. Physical SQL generation is selected from the semantic contract's physical mappings.

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
- Core prerequisite check: `python scripts/run_tool.py check_prereqs.py`
- Live execution readiness: `python scripts/run_tool.py check_prereqs.py --require-oracle`
- First-time setup: `python scripts/setup_analytics.py`
- User config: `~/.oracle-semantic-analytics/config.json`
- Live execution password: `SIA_USER_PWD` in the shell that starts Claude Code
- Runtime wrapper: `python scripts/run_tool.py <script-name.py> ...`
- Context generator: `python scripts/run_tool.py generate_prompt_context.py --question "..."`
- SQL validator: `python scripts/run_tool.py validate_sql.py -` reads generated SQL from stdin
- SQL executor: `python scripts/run_tool.py execute_oracle_readonly.py - --yes` reads generated SQL from stdin
- Demo auto-approval: `SIA_AUTO_APPROVE=true` in user config or environment
- Oracle mode default: thick mode; thin mode is advanced-only with `SIA_ORACLE_THIN_MODE=true`

## Workflow

1. Check core prerequisites with `scripts/run_tool.py check_prereqs.py`.
2. Load `routing/subject-area-routing.yaml`.
3. Match the user question to a route by keywords, subject-area intent, and available semantic models.
4. If no route matches, say that this demo only supports the listed subject areas and ask the user to rephrase within those domains.
5. For the matched route, use the route's subject-area skill and semantic model.
6. Generate Oracle 19c `SELECT` SQL only from bundled semantic context.
7. Validate SQL immediately with `scripts/run_tool.py validate_sql.py -`; do not ask before local validation.
8. If `SIA_AUTO_APPROVE=true` is configured and `SIA_USER_PWD` is available, execute validated SQL without asking again.
9. If auto-approval is not set, ask once before Oracle execution.
10. Execute SQL only through `scripts/run_tool.py execute_oracle_readonly.py - --yes` using stdin.
11. Explain the metric definition, filters, assumptions, and caveats.

All relative paths above are relative to the installed plugin root. Do not search or explore the user's current working directory for bundled plugin files. Do not read or print credential files.

## Supported Routes

The demo currently supports:

- `student_enrollment` through `student-enrollment-analytics`

Do not invent additional routes. Future subject areas should be added to `routing/subject-area-routing.yaml` and receive their own subject-area skill.

## Prerequisite Handling

For prompt-context generation and SQL validation:

```bash
python scripts/setup_analytics.py
python scripts/run_tool.py check_prereqs.py
```

For live Oracle execution:

```bash
python scripts/run_tool.py check_prereqs.py --require-oracle
```

If Oracle configuration is missing, say:

```text
Oracle execution is not configured yet. You can still generate and validate SQL. For live execution, run /oracle-semantic-analytics:setup-analytics once, then set SIA_USER_PWD in the shell that starts Claude Code. Do not paste passwords into chat.
```

Then suggest:

```bash
python plugins/oracle-semantic-analytics/scripts/setup_analytics.py
```

## Safety Rules

- Never ask the user to paste a password directly into Claude chat.
- Never store credentials in this repository.
- Never return row-level sensitive records.
- Never bypass validation.
- Never run `execute_oracle_readonly.py` before validation. User approval is satisfied by `SIA_AUTO_APPROVE=true`; otherwise ask once before live execution.
- If the user asks for unsafe SQL or individual student records, refuse and offer aggregate alternatives.

## Common Mistakes

- Treating missing Oracle credentials as blocking for SQL generation. Credentials are required only for live execution.
- Looking for bundled plugin files in the user's working directory. Resolve `scripts/`, `routing/`, `assets/`, and `skills/` from the installed plugin root.
- Leaving generated SQL scratch files in the user's project. Prefer piping generated SQL to `validate_sql.py -` and `execute_oracle_readonly.py -`.
- Reading `.env`, config, or credential values into the conversation. Never display credential files or passwords.
- Routing unsupported subject areas by inventing tables or metrics. Instead, explain the supported routes.
- Executing SQL before validation, or asking repeatedly after `SIA_AUTO_APPROVE=true` is already set.
- Assuming thin mode works in all Oracle environments. This demo defaults to thick mode for Native Network Encryption compatibility.
- Putting production governance in the local plugin. The production model is a central gateway.

## Production Caveat

This local skill/plugin model is for demo and power-user scenarios. Production usage should use a central governed MCP/API gateway.
