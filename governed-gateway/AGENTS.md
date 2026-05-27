# AGENTS.md — Governed Gateway

## Goal

Build a central governed MCP/API gateway demo for Oracle 19c semantic analytics.

## Architecture

This demo does not distribute full semantic models to users. It centralizes:

- Semantic registry
- Semantic retrieval
- SQL validation
- Oracle execution
- Policy enforcement
- Audit logging

## Rules

- Do not put Oracle credentials in client plugins.
- Do not expose raw `oracle.execute_sql` to business users.
- Execute only validated query IDs.
- Prefer user/proxy identity for Oracle access.
- Enforce security and privacy server-side.
- Keep skills thin; they should call the gateway.
- Treat this as the production-oriented architecture.