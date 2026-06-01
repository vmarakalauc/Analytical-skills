# Oracle Semantic Analytics — Plugin Quickstart

A Claude Code plugin for Oracle 19c student enrollment analytics. It generates and validates SQL from natural language using a bundled semantic model, with optional live Oracle execution.

---

## Step 1 — Install the plugin

Open a terminal (PowerShell or CMD) and run:

```powershell
claude plugin marketplace add vmarakalauc/Analytical-skills
claude plugin install oracle-semantic-analytics@analytical-skills
```

Then open Claude Code and reload plugins by typing this in the chat input:

```text
/reload-plugins
```

> **New to Claude Code?** Download and install it from [claude.ai/code](https://claude.ai/code), then open it. All `/commands` are typed directly in the chat input box.

---

## Step 2 — Set your Oracle password

Do this **before** running setup, so the setup wizard can verify your connection.

Open a terminal, set the password, then start Claude Code from that same terminal:

**PowerShell:**

```powershell
$env:SIA_USER_PWD = "your_password"
claude
```

**CMD:**

```cmd
set SIA_USER_PWD=your_password
claude
```

Do not paste the password into the Claude chat. If Claude Code is already running, close it, set the variable, and restart from the same shell.

---

## Step 3 — Run first-time setup

In the Claude Code chat input, run:

```text
/oracle-semantic-analytics:setup-analytics
```

The wizard will ask for a few connection settings — have these ready (ask your DBA if unsure):

| Prompt | What to enter |
|---|---|
| Oracle username | Your DB username, e.g. `SIA_USER` |
| Oracle DSN | Easy Connect string, e.g. `myhost:1521/MYDB` |
| Oracle Client folder | Path to Oracle Instant Client, e.g. `C:\oracle\instantclient_21` — leave blank for thin mode |
| Row limit | Max rows to return per query, e.g. `100` |
| Auto-approve | `y` for demos (skips execution prompt), `n` for normal use |

Setup creates a local config outside your project folder:

```text
~/.oracle-semantic-analytics/
  config.json      # non-secret settings
  venv/            # isolated Python runtime
  reports/         # generated HTML reports
```

**The Oracle password is never stored** — it stays in your shell environment only.

---

## Step 4 — Check readiness

```text
/oracle-semantic-analytics:check-oracle-config
```

This confirms prerequisites and connection settings are correct. A missing `SIA_USER_PWD` only blocks live execution — SQL generation and validation work without it.

---

## Step 5 — Ask analytics questions

```text
/oracle-semantic-analytics:ask-analytics
```

Example questions:

```text
How many active students are enrolled by academic program for Fall 2026?
Show full-time student count for each fall term over the last three years.
Break down enrollment by academic career for the current academic year.
```

Claude will:
1. Route the question to the right skill via `routing/subject-area-routing.yaml`
2. Load the bundled semantic model (`assets/semantic_models/sia_term_enrollments.yaml`)
3. Clarify ambiguous terms (e.g. "current term") before generating SQL
4. Generate an Oracle 19c `SELECT`-only query
5. Validate the SQL locally before presenting it
6. Ask for your approval before executing against Oracle (unless `sia_auto_approve` is set)
7. Return an aggregated result table with metric definitions and caveats

---

## Demo mode

For controlled demos, set `sia_auto_approve: true` during setup or in the shell:

```powershell
$env:SIA_AUTO_APPROVE = "true"
```

Validated read-only SQL will execute without an extra prompt.

---

## Available commands

| Command | Purpose |
|---|---|
| `/oracle-semantic-analytics:setup-analytics` | First-time setup wizard |
| `/oracle-semantic-analytics:check-oracle-config` | Check prerequisites and connection readiness |
| `/oracle-semantic-analytics:ask-analytics` | Ask any Oracle warehouse analytics question |
| `/oracle-semantic-analytics:ask-enrollment` | Ask a student enrollment analytics question directly |

---

## Plugin contents

```text
skills/
  oracle-analytics-router/        # Routes questions to the right subject-area skill
  student-enrollment-analytics/   # Student enrollment analytics skill

assets/
  semantic_models/
    sia_term_enrollments.yaml     # Semantic contract + Oracle 19c physical mapping

routing/
  subject-area-routing.yaml       # Keyword-based subject-area routing config

scripts/
  run_tool.py                     # Venv-aware script runner
  check_prereqs.py                # Prerequisite checker
  setup_analytics.py              # First-time setup wizard
  configure_oracle.py             # Manual terminal config fallback
  analytics_config.py             # Config file I/O
  generate_prompt_context.py      # Generate semantic context from question
  validate_sql.py                 # Local SQL validation (no Oracle required)
  execute_oracle_readonly.py      # Read-only Oracle execution
  validate_plugin_package.py      # Plugin package structure validator

commands/
  setup-analytics.md
  check-oracle-config.md
  ask-analytics.md
  ask-enrollment.md

examples/
  sample_generated_sql.sql        # Reference SQL example
```

---

## Manual terminal fallback

If the Claude Code command flow doesn't work, run setup from a terminal:

```powershell
python "${CLAUDE_PLUGIN_ROOT}/scripts/configure_oracle.py"
```

---

## Local developer setup

For repository development only:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r distributed-models/plugins/oracle-semantic-analytics/requirements.txt
```

Run individual tools directly (from the plugin scripts folder):

```powershell
python scripts/run_tool.py check_prereqs.py
python scripts/run_tool.py validate_sql.py examples/sample_generated_sql.sql
python scripts/run_tool.py generate_prompt_context.py --question "active student count by program for Fall 2026"
```

---

## Safety rules

- Never paste the Oracle password into Claude chat
- Never commit `.env`, wallet files, DSNs, API keys, or student PII
- SQL generation and validation never require a live Oracle connection
- Only `SELECT` statements are permitted — no DML or DDL
- Execution is always read-only and row-capped
- Results are aggregate only — no row-level student records are returned
