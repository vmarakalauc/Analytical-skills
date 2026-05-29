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
  setup_analytics.py
  run_tool.py
  generate_prompt_context.py
  validate_sql.py
  execute_oracle_readonly.py

commands/
  setup-analytics.md
  ask-analytics.md
  check-oracle-config.md
  ask-enrollment.md
```

## First-time setup

After installing the plugin, run the setup command once from Claude Code:

```text
/oracle-semantic-analytics:setup-analytics
```

The setup creates local runtime state outside any project repository:

```text
~/.oracle-semantic-analytics/
  config.json      # non-secret connection/runtime settings
  venv/            # plugin Python dependencies
  reports/         # generated local HTML reports
```

The setup stores non-secret values only:

- `sia_user`
- `sia_dsn`
- `oracle_client_lib`
- `sia_auto_approve`
- `sia_max_rows`
- `reports_dir`

The Oracle password is not stored. Set it in the shell that starts Claude Code before live execution:

```powershell
$env:SIA_USER_PWD = "your_password"
```

For a persistent enterprise setup, set `SIA_USER_PWD` with your approved local password-management process rather than pasting it into Claude chat.

## Local developer setup

For repository development, you can also install dependencies in an in-repo virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r distributed-models/plugins/oracle-semantic-analytics/requirements.txt
```

For SQL generation and validation only, Oracle credentials are not required:

```powershell
python scripts/run_tool.py check_prereqs.py
python scripts/setup_analytics.py --skip-install
python scripts/run_tool.py check_prereqs.py --require-oracle
python scripts/validate_plugin_package.py
python scripts/run_tool.py validate_sql.py examples/sample_generated_sql.sql
Get-Content examples/sample_generated_sql.sql | python scripts/run_tool.py validate_sql.py -
```

The executor defaults to Oracle thick mode because many Oracle environments use Native Network Encryption. Users should not need to choose a mode during normal setup; the setup detects common Oracle Client locations and stores the client library folder when found. Thin mode is an advanced override with `SIA_ORACLE_THIN_MODE=true`.

Never commit real Oracle credentials.

## Generate semantic prompt context

```powershell
python scripts/run_tool.py generate_prompt_context.py \
  --question "How many active students are enrolled by academic program for Fall 2026?"
```

## Validate SQL

```powershell
python scripts/run_tool.py validate_sql.py examples/sample_generated_sql.sql
```

## Execute SQL

Execution is optional and must happen only after SQL validation. Set `sia_auto_approve` in `~/.oracle-semantic-analytics/config.json`, or set `SIA_AUTO_APPROVE=true` in the shell, to skip repeated interactive execution prompts during a controlled demo session:

```powershell
python scripts/run_tool.py execute_oracle_readonly.py examples/sample_generated_sql.sql --yes
Get-Content examples/sample_generated_sql.sql | python scripts/run_tool.py execute_oracle_readonly.py - --yes
```

The executor runs only after the SQL passes local validation, starts an Oracle read-only transaction, and caps returned rows with `SIA_MAX_ROWS` or config `sia_max_rows`. This remains demo-level validation, not production governance.

## Demo workflow

1. Run `/oracle-semantic-analytics:setup-analytics` once after install.
2. Ask with `/oracle-semantic-analytics:ask-analytics`.
3. Route the question using `routing/subject-area-routing.yaml`.
4. Generate or inspect semantic context with `python scripts/run_tool.py generate_prompt_context.py --question "..."`
5. Generate Oracle 19c `SELECT` SQL using only bundled semantic model objects.
6. Validate with `python scripts/run_tool.py validate_sql.py -` using stdin.
7. Execute only with `python scripts/run_tool.py execute_oracle_readonly.py - --yes` using stdin.
8. Use `SIA_AUTO_APPROVE=true` or config `sia_auto_approve: true` to avoid repeated execution prompts during a controlled demo session.

For Claude Code command usage, prefer piping generated SQL to `run_tool.py validate_sql.py -` and `run_tool.py execute_oracle_readonly.py -` so temporary SQL files are not left in the user's project folder.

## Safety boundaries

- Do not paste passwords into Claude chat.
- Do not commit `.env`, Oracle wallet files, DSNs, keys, or student PII.
- Do not create plugin temp files in the user's working directory; use stdin for SQL and `~/.oracle-semantic-analytics/reports` for reports.
- Do not invent tables, joins, metrics, or filters outside `assets/semantic_models/`.
- Do not return row-level student records.
- Use aggregate answers and small-cell/privacy caveats for student analytics.
