# Analytical Skills

This repository contains Claude Code plugin and semantic analytics demos for Oracle 19c analytical AI workflows.

## Repository layout

```text
distributed-models/
  Claude Code plugin marketplace demo that ships skills, local helper scripts,
  and a bundled semantic YAML model.

governed-gateway/
  Placeholder for the production-oriented central MCP/API gateway model.
```

## Current demo

The production-quality demo artifact in this branch is:

```text
distributed-models/plugins/oracle-semantic-analytics
```

It demonstrates a distributed Claude Code plugin for student enrollment analytics over Oracle 19c. It is suitable for a controlled demo or power-user proof of concept. Production deployment should use the governed gateway model so semantic retrieval, SQL validation, Oracle execution, policy enforcement, and audit logging are centralized.

## Credential policy

Do not commit Oracle credentials, wallet files, `.env` files, production DSNs, API keys, or real student PII. The plugin uses environment variables or a local file under the user's home directory for Oracle connection settings.

## Validate

From the repository root:

```powershell
python distributed-models/plugins/oracle-semantic-analytics/scripts/validate_plugin_package.py
python distributed-models/plugins/oracle-semantic-analytics/scripts/validate_sql.py distributed-models/plugins/oracle-semantic-analytics/examples/sample_generated_sql.sql
```

If Claude Code with plugin support is installed, also run:

```powershell
cd distributed-models
claude plugin validate .
claude plugin validate ./plugins/oracle-semantic-analytics
```
