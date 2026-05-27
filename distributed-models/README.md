# Analytical Skills

Claude Code plugin marketplace for analytical/data skills.

This repository contains one plugin:

```text
oracle-semantic-analytics
```

The plugin demonstrates the distributed semantic YAML + skills pattern:

- The semantic model YAML is bundled with the plugin.
- Claude Code skills tell Claude when and how to use the semantic model.
- Helper scripts check prerequisites, generate semantic prompt context, validate SQL, and optionally execute read-only Oracle SQL.
- Users configure their own local Oracle credentials outside the repository.

## Install in Claude Code

If publishing `distributed-models` as its own GitHub repository, users can add the marketplace:

```text
/plugin marketplace add vmarakalauc/Analytical-skills
```

Then install the plugin:

```text
/plugin install oracle-semantic-analytics@analytical-skills
```

CLI equivalents:

```bash
claude plugin marketplace add vmarakalauc/Analytical-skills
claude plugin install oracle-semantic-analytics@analytical-skills
```

If publishing from the parent `Analytical-skills` repository, use the root marketplace instead. The root marketplace points to `./distributed-models/plugins/oracle-semantic-analytics`.

For local development before publishing, load the plugin directly:

```bash
claude --plugin-dir ./plugins/oracle-semantic-analytics
```

Then run `/reload-plugins` inside Claude Code if you edit skill files.

## Validate before publishing

From this `distributed-models` marketplace directory:

```bash
python plugins/oracle-semantic-analytics/scripts/validate_plugin_package.py
python plugins/oracle-semantic-analytics/scripts/validate_sql.py plugins/oracle-semantic-analytics/examples/sample_generated_sql.sql
claude plugin validate .
claude plugin validate ./plugins/oracle-semantic-analytics
```

The Python validation is intentionally local and does not require Oracle credentials. The Claude validation requires a current Claude Code install with plugin support.

## Demo prompt

After install, ask Claude Code:

```text
How many active students are enrolled by academic program for Fall 2026?
```

Expected behavior:

1. Claude detects an Oracle/student-enrollment analytics question.
2. Claude uses the installed skill.
3. Claude routes the question through `oracle-analytics-router`.
4. Claude runs or asks to run prerequisite checks.
5. If Oracle config is missing, Claude asks the user to set environment variables or local config.
6. Claude loads the bundled YAML semantic model.
7. Claude asks clarifying questions if required.
8. Claude generates Oracle 19c SQL.
9. Claude validates SQL.
10. Claude asks before executing.
11. Claude executes read-only SQL only if configured and approved.

## Important demo warning

This plugin is intentionally a Demo 1 distributed model. It is useful for portability and proof of concept, but production should use a central governed MCP/API gateway for semantic version control, SQL validation, Oracle execution, audit, and privacy enforcement.
