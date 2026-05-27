---
description: Answer student enrollment analytics questions using the bundled SIA term enrollment semantic model and Oracle 19c SQL rules.
disable-model-invocation: true
---

# Student Enrollment Analytics

Use this skill when the user asks about student enrollment, active students, terms, academic programs, academic careers, majors, minors, academic load, new/returning students, or related institutional enrollment metrics.

## Semantic model

Use:

```text
assets/semantic_models/sia_term_enrollments.yaml
```

Before using the model, confirm the package is available:

```bash
python scripts/check_prereqs.py
```

Do not require Oracle credentials unless the user asks to execute the generated SQL.

## Business interpretation

- "Students" usually means distinct active students.
- "Student count" means `COUNT(DISTINCT SCHOLAR_WID)` when supported by the semantic model.
- "Active enrollment" requires:
  - `DELETE_FLG = 'N'`
  - `X_TERM_ENROLLED_FLAG = 'Y'`
- "Enrollment count" may mean enrollment rows; clarify if the user means distinct students or records.
- "Current term" or "this term" may require clarification.
- For Fall 2026 in this demo, assume term code `20263` only if the local model or user confirms the convention.

## Required SQL behavior

- Use the term enrollment semantic model.
- Apply active enrollment filters by default.
- Group only by dimensions defined or mapped in the semantic model.
- Include an Oracle row limit with `FETCH FIRST n ROWS ONLY` for demo queries.
- Validate generated SQL with `scripts/validate_sql.py` before offering execution.
- Do not expose individual student records.
- Do not include student names, emails, IDs, GPA, or identifiable records unless explicitly allowed by policy. For this demo, treat those as disallowed.

## Demo question

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
