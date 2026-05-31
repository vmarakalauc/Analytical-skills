---
name: setup-oracle-semantic-analytics
description: Use when the user needs first-time local setup for the Oracle semantic analytics plugin runtime, config, Oracle Client path, or password guidance
disable-model-invocation: true
---

# Setup Oracle Semantic Analytics

## Overview

Prepares the local runtime and non-secret configuration for the Oracle semantic analytics plugin. Setup is a one-time action per workstation unless the user changes Oracle connection settings or reinstalls Python.

## When to Use

Use for:

- First run after installing the plugin
- Missing Python dependencies
- Missing `~/.oracle-semantic-analytics/config.json`
- Oracle Client path configuration
- Explaining how `SIA_USER_PWD` should be set

Do not use for:

- Storing passwords
- Reading credential files into chat
- Creating `.env` files in the user's project directory
- Generating analytics SQL

## Quick Reference

- Setup script: `scripts/setup_analytics.py`
- Config file: `~/.oracle-semantic-analytics/config.json`
- Runtime venv: `~/.oracle-semantic-analytics/venv`
- Reports directory: `~/.oracle-semantic-analytics/reports`
- Password variable: `SIA_USER_PWD`

## Workflow

1. Resolve the installed plugin root.
2. Run `python <plugin-root>/scripts/setup_analytics.py`.
3. Let the setup script create the venv, install dependencies, detect Oracle Client, and write non-secret config.
4. Tell the user to set `SIA_USER_PWD` in the shell that starts Claude Code before live execution.
5. Run `python <plugin-root>/scripts/run_tool.py check_prereqs.py --require-oracle` to verify execution readiness.

## Safety Rules

- Never ask the user to paste a password into chat.
- Never write the password to config.
- Never create `.env` in the user's current project folder.
- Never display values from credential files.
