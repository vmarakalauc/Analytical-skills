---
name: oracle-analytics-router
description: Use when the user asks Oracle warehouse analytics questions — enrollment, students, academic programs, terms, or any subject area supported by this plugin
---

# Oracle Analytics Router

## When to Use

Use for any Oracle warehouse analytics question. This skill routes the question to
the right semantic model, loads the model as context, and drives SQL generation,
validation, and execution.

Do not use for:
- Non-Oracle data sources
- Raw schema exploration without a semantic model
- Subject areas not present in `routing/subject-area-routing.yaml`

## Workflow

1. Call `oracle_semantic_health` to confirm prerequisites. If MCP is unavailable,
   fall back to `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" check_prereqs.py`.

2. Read `${CLAUDE_PLUGIN_ROOT}/routing/subject-area-routing.yaml` and match the
   user's question to a route by keywords and intent. If no route matches, explain
   which subject areas are supported.

3. Call `oracle_semantic_get_context` with the user's question. This loads the
   matched semantic model as prompt context. The model is the authority on:
   - Business glossary and term definitions
   - Measures, dimensions, filters, and relationships
   - Physical table/column mappings
   - Behavioral rules (`semantic_rules.behavior`) — clarification requirements,
     SQL generation rules, output rules

4. Follow the `semantic_rules.behavior` section of the loaded model exactly:
   - Apply the clarification rules before generating SQL
   - Apply all sql_generation_rules when writing the query
   - Apply all output_rules when presenting results

5. Generate Oracle 19c SELECT-only SQL using only objects defined in the model's
   `physical_mappings`. Do not invent tables, joins, columns, or metrics.

6. Call `oracle_semantic_validate_sql` immediately. Do not ask the user before
   validating. If MCP unavailable: pipe SQL to
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" validate_sql.py -`

7. If validation fails, fix the SQL and re-validate before proceeding.

8. Always present the validated SQL to the user as a formatted code block before
   calling `oracle_semantic_execute_sql`. This is a required step — `approved: true`
   means the user has seen the SQL. Never pass `approved: true` without showing the
   SQL first.

9. If `sia_auto_approve=true` is configured and `SIA_USER_PWD` is available,
   show the SQL (step 8), then call `oracle_semantic_execute_sql` with `approved: true`.
   Otherwise show the SQL (step 8), ask the user once for confirmation, then call
   `oracle_semantic_execute_sql` with `approved: true`.
   If MCP unavailable: pipe SQL to
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/run_tool.py" execute_oracle_readonly.py - --yes`

10. After execution, decide whether a chart improves understanding. Call
   `oracle_semantic_render_report` only when the result is a small, aggregated
   set of data points where a visualization adds clarity — for example, a trend
   over a few terms or a ranking across a handful of categories. Do not render
   a chart for large result sets, granular row-level data, or when a table is
   already clear. Choose the chart type that best fits the data shape. Always
   include question, validated SQL, result columns, result rows, and a one-sentence
   summary in the report payload.

11. Explain metric definitions, filters applied, assumptions, caveats, and include
   the local report path when a report was rendered.

## Institutional Calendar Convention

All subject areas in this plugin share the same academic term code convention.
Term codes are numeric; the last digit encodes the season:

| Last digit | Season |
|---|---|
| 2 | Winter |
| 4 | Spring |
| 6 | Summer |
| 8 | Autumn |

Examples: `20268` = Autumn 2026, `20264` = Spring 2026.
When filtering by season, use `SUBSTR(term_code_column, -1) = '<digit>'`.
"Current term" always requires clarification — never assume.

## Universal SQL Rules

These apply to every subject area regardless of which model is loaded:

- SELECT-only. No INSERT, UPDATE, DELETE, DROP, or DDL.
- No SELECT *. Name all columns explicitly.
- Fully qualified table names required (e.g. `OBIA_DW.W_SIA_TERM_ENRLMT_F`).
- Use `FETCH FIRST n ROWS ONLY` for row limits. Never use `LIMIT`.
- Validate before execution. Never skip validation.
- Never return row-level records that identify individuals.
- Never read, display, or ask for credential files or passwords.
- Do not create temp SQL files in the user's project folder — pipe SQL via stdin.

## Data Dictionary

When the user asks for a data dictionary, field reference, column mapping, or
business glossary, call `oracle_semantic_data_dictionary`. It generates a
multi-sheet Excel file covering dimensions, measures, glossary, and governance,
opens it automatically, and returns the file path.

## Adding a New Subject Area

Add a new entry to `routing/subject-area-routing.yaml` pointing to a new semantic
YAML under `assets/semantic_models/`. The YAML must include a `semantic_rules.behavior`
block with `clarification_rules`, `sql_generation_rules`, and `output_rules`. No new
SKILL.md is needed — the router uses the YAML as the subject-area skill.

## Safety Rules

- Never ask the user to paste a password into chat.
- Never expose restricted fields (names, emails, IDs, SSNs).
- Never bypass SQL validation.
- Refuse requests for individual records and offer aggregate alternatives.
- If `SIA_AUTO_APPROVE=true` is set, still display SQL before executing.
