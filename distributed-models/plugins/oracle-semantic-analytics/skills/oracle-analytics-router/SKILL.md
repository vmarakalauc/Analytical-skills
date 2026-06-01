---
name: oracle-analytics-router
description: Use when the user asks Oracle warehouse analytics questions that may match a supported subject area in this plugin
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

- MCP server: `oracle-semantic-analytics` (started automatically by Claude Code after `/reload-plugins`)
- MCP tools: `oracle_semantic_health`, `oracle_semantic_get_context`, `oracle_semantic_validate_sql`, `oracle_semantic_execute_sql`
- Bash fallback (only if MCP unavailable): `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" <script> ...`
- Routes file: `${CLAUDE_PLUGIN_ROOT}/routing/subject-area-routing.yaml`
- User config: `~/.oracle-semantic-analytics/config.json`
- Live execution password: `SIA_USER_PWD` in the shell that starts Claude Code
- Auto-approval: `sia_auto_approve=true` in config or `SIA_AUTO_APPROVE=true` in environment

## Workflow

1. Call `oracle_semantic_health` to confirm prerequisites. If MCP is unavailable, fall back to `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" check_prereqs.py`.
2. Read `${CLAUDE_PLUGIN_ROOT}/routing/subject-area-routing.yaml` to select the subject area.
3. Match the user question to a route by keywords and subject-area intent.
4. If no route matches, explain which subject areas are supported and ask the user to rephrase.
5. For the matched route, use the subject-area skill and semantic model.
6. Call `oracle_semantic_get_context` with the user's question to load the semantic context needed for SQL generation. Fallback: `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" generate_prompt_context.py --question "..."`.
7. Generate Oracle 19c `SELECT`-only SQL from the semantic context.
8. Immediately call `oracle_semantic_validate_sql` with the generated SQL — do not ask the user before validating. Fallback: pipe SQL to `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" validate_sql.py -`.
9. If validation fails, fix the SQL and re-validate before proceeding.
10. If `sia_auto_approve=true` is configured and `SIA_USER_PWD` is available, call `oracle_semantic_execute_sql` directly.
11. Otherwise ask the user once for approval, then call `oracle_semantic_execute_sql`. Fallback: pipe SQL to `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" execute_oracle_readonly.py - --yes`.
12. Explain the metric definition, filters, assumptions, and caveats.

All `${CLAUDE_PLUGIN_ROOT}` paths resolve to the installed plugin root. Do not search the user's project folder for plugin files. Do not read or print credential files.

## Supported Routes

The demo currently supports:

- `student_enrollment` through `student-enrollment-analytics`

Do not invent additional routes. Additional subject areas should be added to `routing/subject-area-routing.yaml` and receive their own subject-area skill.

## Prerequisite Handling

Call `oracle_semantic_health` first. If the MCP server is not available, fall back to:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" check_prereqs.py
python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" check_prereqs.py --require-oracle
```

If Oracle configuration is missing, say:

```text
Oracle execution is not configured yet. You can still generate and validate SQL. For live execution, run /oracle-semantic-analytics:setup-analytics once, then set SIA_USER_PWD in the shell that starts Claude Code. Do not paste passwords into chat.
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
- Assuming thin mode works in all Oracle environments. Thick mode is the default for Native Network Encryption compatibility.
