# Oracle Semantic Analytics Plugin

This Claude Code plugin demonstrates local/distributed Oracle semantic analytics for an Oracle 19c warehouse demo. It ships Claude Code skills, a bundled semantic YAML model, helper scripts, and local SQL validation.

The plugin follows Claude Code plugin conventions:

- `.claude-plugin/plugin.json` contains plugin metadata only.
- `skills/` contains skill directories with `SKILL.md`.
- `commands/` contains optional slash-command markdown files.
- Runtime assets and scripts stay inside the plugin root so installed marketplace copies remain self-contained.

## Contents

```text
skills/
  oracle-analytics-router/
  student-enrollment-analytics/

assets/
  semantic_models/
    sia_term_enrollments.yaml

routing/
  subject-area-routing.yaml

scripts/
  check_prereqs.py
  configure_oracle.py
  generate_prompt_context.py
  validate_sql.py
  execute_oracle_readonly.py

commands/
  ask-analytics.md
  check-oracle-config.md
  ask-enrollment.md
```

## Local configuration

Install Python dependencies in a local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For SQL generation and validation only, Oracle credentials are not required:

```powershell
python scripts/check_prereqs.py
python scripts/check_prereqs.py --env-file C:\sql\.env --require-oracle
python scripts/validate_plugin_package.py
python scripts/validate_sql.py examples/sample_generated_sql.sql
Get-Content examples/sample_generated_sql.sql | python scripts/validate_sql.py -
```

For optional Oracle execution, use environment variables:

```bash
export ORACLE_USER="your_user"
export ORACLE_PASSWORD="your_password"
export ORACLE_DSN="host.example.edu:1521/service_name"
```

Optional:

```bash
export ORACLE_THIN_MODE=false
export ORACLE_CLIENT_LIB_DIR="/path/to/instantclient"
export MAX_ROWS=1000
export ORACLE_ANALYTICS_AUTO_APPROVE=false
```

The executor defaults to Oracle thick mode because many Oracle environments use Native Network Encryption. Set `ORACLE_THIN_MODE=true` only when your Oracle service supports thin mode. Set `ORACLE_ANALYTICS_AUTO_APPROVE=true` only for a controlled demo session where you want validated SQL to execute without an interactive prompt.

Never commit real Oracle credentials.

You can also write local settings outside the repository:

```powershell
python scripts/configure_oracle.py
python scripts/check_prereqs.py --require-oracle
```

## Generate semantic prompt context

```powershell
python scripts/generate_prompt_context.py \
  --question "How many active students are enrolled by academic program for Fall 2026?"
```

## Validate SQL

```powershell
python scripts/validate_sql.py examples/sample_generated_sql.sql
```

## Execute SQL

Execution is optional and must happen only after SQL validation and explicit user approval, unless `ORACLE_ANALYTICS_AUTO_APPROVE=true` is set in the local shell or ignored user config:

```powershell
python scripts/execute_oracle_readonly.py examples/sample_generated_sql.sql --yes
python scripts/execute_oracle_readonly.py examples/sample_generated_sql.sql --env-file C:\sql\.env --yes
Get-Content examples/sample_generated_sql.sql | python scripts/execute_oracle_readonly.py - --env-file C:\sql\.env --yes
```

The executor runs only after the SQL passes local validation, starts an Oracle read-only transaction, and caps returned rows with `MAX_ROWS`. This remains demo-level validation, not production governance.

## Demo workflow

1. Check prerequisites with `python scripts/check_prereqs.py`.
2. Route the question using `routing/subject-area-routing.yaml`.
3. Generate or inspect semantic context with `python scripts/generate_prompt_context.py --question "..."`
4. Generate Oracle 19c `SELECT` SQL using only bundled semantic model objects.
5. Validate with `python scripts/validate_sql.py <sql-file>`.
6. Ask for user approval before Oracle execution.
7. Execute only with `python scripts/execute_oracle_readonly.py <sql-file> --yes`.

For Claude Code command usage, prefer piping generated SQL to `validate_sql.py -` and `execute_oracle_readonly.py -` so temporary SQL files are not left in the user's project folder.

## Safety boundaries

- Do not paste passwords into Claude chat.
- Do not commit `.env`, Oracle wallet files, DSNs, keys, or student PII.
- Do not invent tables, joins, metrics, or filters outside `assets/semantic_models/`.
- Do not return row-level student records.
- Use aggregate answers and small-cell/privacy caveats for student analytics.
