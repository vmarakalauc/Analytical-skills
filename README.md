# Analytical Skills — Oracle Semantic Analytics Plugin

A Claude Code plugin for Oracle 19c text-to-SQL analytics. It ships Claude Code skills, a bundled semantic YAML model, local SQL validation, and optional read-only Oracle execution.

## Install

```powershell
claude plugin marketplace add vmarakalauc/Analytical-skills
claude plugin install oracle-semantic-analytics@analytical-skills
```

Claude resolves the plugin through `.claude-plugin/marketplace.json`, which points to `distributed-models/plugins/oracle-semantic-analytics`.

## Quickstart

See the [plugin README](distributed-models/plugins/oracle-semantic-analytics/README.md) for step-by-step setup and usage.

## Validate

```powershell
claude plugin validate .
claude plugin validate ./distributed-models/plugins/oracle-semantic-analytics
python distributed-models/plugins/oracle-semantic-analytics/scripts/validate_plugin_package.py
python distributed-models/plugins/oracle-semantic-analytics/scripts/validate_sql.py distributed-models/plugins/oracle-semantic-analytics/examples/sample_generated_sql.sql
```

## Credential policy

Never commit Oracle credentials, wallet files, `.env` files, production DSNs, API keys, or real student PII. The plugin reads the Oracle password from the `SIA_USER_PWD` environment variable only.
