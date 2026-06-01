# AGENTS.md — Distributed Models Plugin

## Goal

Build a Claude Code plugin marketplace demo where users install skills, semantic YAML, helper scripts, and local Oracle execution tools.

## Architecture

This demo intentionally distributes:

- Semantic YAML
- Claude skills
- Local prerequisite scripts
- Local SQL validation
- Optional local Oracle read-only execution

## Rules

- Never edit files under `~/.claude/plugins/cache/`. That directory is the
  installed plugin cache and is overwritten on every plugin update. Any edits
  made there are silently lost. If a bug is found in a plugin script, fix it
  in the source repository and bump the plugin version to distribute the fix.
- Do not implement a central server here.
- Do not add MCP gateway code here.
- Do not commit real Oracle credentials.
- Do not ask users to paste passwords into Claude chat.
- Store local credential examples only as templates.
- Use environment variables or local ignored config for credentials.
- Generate Oracle 19c SELECT-only SQL.
- Validate SQL before execution.
- Ask user confirmation before execution.
- Treat this as demo/prototype, not production governance.