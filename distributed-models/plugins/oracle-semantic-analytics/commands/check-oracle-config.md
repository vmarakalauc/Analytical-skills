---
description: Check local Oracle analytics plugin prerequisites and configuration.
---

Run the local Oracle semantic analytics prerequisite check.

Resolve all plugin files relative to the installed plugin root, not the user's current working directory. Do not search or explore the user's project folder for bundled plugin files.

Do not read or print `.env` file contents. If the user keeps credentials in a local ignored `.env`, pass its path with `--env-file <path>` instead of opening it.

Steps:

1. Run `python <plugin-root>/scripts/check_prereqs.py`, or `python <plugin-root>/scripts/check_prereqs.py --env-file <path> --require-oracle` for live execution readiness.
2. If configuration is missing, explain the missing items.
3. Do not ask the user to paste passwords into chat.
4. Recommend using environment variables, `<plugin-root>/scripts/configure_oracle.py`, or a local ignored `.env` file passed as `--env-file <path>`.
