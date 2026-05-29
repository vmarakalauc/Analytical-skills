---
name: student-enrollment-analytics
description: Use when the user asks about student enrollment, active students, academic terms, programs, careers, majors, minors, or academic load
disable-model-invocation: true
---

# Student Enrollment Analytics

## Overview

Interprets student enrollment analytics questions using the bundled platform-agnostic SIA term enrollment semantic contract. This skill handles enrollment-specific business terms, default filters, privacy boundaries, and the selected physical mapping for Oracle 19c SQL generation.

## When to Use

Use for questions about:

- Student enrollment and active students
- Academic terms, academic years, and term comparisons
- Academic programs, careers, majors, minors, and academic load
- New versus returning students
- Aggregate institutional enrollment metrics

Do not use for:

- Individual student records
- Student names, IDs, emails, addresses, GPA details, or other identifying records
- Finance, billing, procurement, or non-enrollment subject areas
- Live Oracle execution before router/prerequisite and validation checks

## Quick Reference

- Semantic contract: `assets/semantic_models/sia_term_enrollments.yaml`
- Core prerequisite check: `python scripts/run_tool.py check_prereqs.py`
- SQL validator: `python scripts/run_tool.py validate_sql.py -`
- First-time setup for live execution: `python scripts/setup_analytics.py`
- Live execution password: `SIA_USER_PWD` in the shell that starts Claude Code
- Default metric for "students": `COUNT(DISTINCT SCHOLAR_WID)`
- Default active enrollment filters: `DELETE_FLG = 'N'` and `X_TERM_ENROLLED_FLAG = 'Y'`

## Workflow

1. Confirm the package is available with `scripts/run_tool.py check_prereqs.py`.
2. Load `assets/semantic_models/sia_term_enrollments.yaml`.
3. Clarify ambiguous terms, especially "current term", "this term", "students", and "enrollments".
4. Resolve logical measures, dimensions, filters, and relationships first; then use the Oracle 19c physical mapping to generate `SELECT` SQL.
5. Apply active enrollment filters by default.
6. Add `FETCH FIRST n ROWS ONLY` for demo queries.
7. Validate generated SQL with `scripts/run_tool.py validate_sql.py -` without asking first; local validation is safe and does not connect to Oracle.
8. Do not require Oracle credentials unless the user asks to execute the generated SQL.
9. For live execution, use the plugin setup state and `SIA_USER_PWD`; do not ask for or display passwords.

## Semantic Contract

```text
assets/semantic_models/sia_term_enrollments.yaml
```

## Business Interpretation

- "Students" usually means distinct active students.
- "Student count" means `COUNT(DISTINCT SCHOLAR_WID)` when supported by the semantic model.
- "Active enrollment" requires:
  - `DELETE_FLG = 'N'`
  - `X_TERM_ENROLLED_FLAG = 'Y'`
- "Enrollment count" may mean enrollment rows; clarify if the user means distinct students or records.
- "Current term" or "this term" may require clarification.
- For Fall 2026 in this demo, assume term code `20263` only if the local model or user confirms the convention.

## Required SQL Behavior

- Use the term enrollment semantic model.
- Apply active enrollment filters by default.
- Group only by dimensions defined or mapped in the semantic model.
- Include an Oracle row limit with `FETCH FIRST n ROWS ONLY` for demo queries.
- Validate generated SQL with `scripts/run_tool.py validate_sql.py -` before execution; no user approval is needed for validation.
- Do not expose individual student records.
- Do not include student names, emails, IDs, GPA, or identifiable records unless explicitly allowed by policy. For this demo, treat those as disallowed.

## Common Mistakes

- Counting enrollment rows when the user asked for students. Use distinct students unless the user asks for records.
- Answering "current term" without clarification.
- Omitting `DELETE_FLG = 'N'` or `X_TERM_ENROLLED_FLAG = 'Y'`.
- Returning row-level student detail instead of aggregate enrollment metrics.
- Using dimensions or joins that are not defined or mapped in the semantic model.

## Demo Question

For:

```text
How many active students are enrolled by academic program for Fall 2026?
```

Expected interpretation:

- Subject area: Student Information Analytics / Term Enrollments
- Metric: student count
- Expression: `COUNT(DISTINCT SCHOLAR_WID)`
- Group by: academic program
- Filters:
  - `DELETE_FLG = 'N'`
  - `X_TERM_ENROLLED_FLAG = 'Y'`
  - Fall 2026 term
- SQL dialect: Oracle 19c
- Output: aggregate table and explanation
