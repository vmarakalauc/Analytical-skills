# Prerequisite Checklist

Required for routing, prompt context, and SQL validation:

- Python 3.10+
- `PyYAML`
- `python-dotenv`
- `sqlparse`
- Routing file exists:
  - `routing/subject-area-routing.yaml`
- Semantic YAML file exists:
  - `assets/semantic_models/sia_term_enrollments.yaml`

Required for live Oracle execution:

- `oracledb`
- `ORACLE_USER`
- `ORACLE_PASSWORD`
- `ORACLE_DSN`

Optional:

- `ORACLE_THIN_MODE`
- `MAX_ROWS`

Validation-only setup should pass with:

```bash
python scripts/check_prereqs.py
```

Execution setup should pass with:

```bash
python scripts/check_prereqs.py --require-oracle
```
