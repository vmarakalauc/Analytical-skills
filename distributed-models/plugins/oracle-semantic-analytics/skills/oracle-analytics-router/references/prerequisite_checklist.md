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
- `~/.oracle-semantic-analytics/config.json`
- `SIA_USER`
- `SIA_DSN`
- `SIA_USER_PWD`
- `ORACLE_CLIENT_LIB` or config `oracle_client_lib`

Optional:

- `SIA_MAX_ROWS`
- `SIA_AUTO_APPROVE`
- `SIA_REPORTS_DIR`
- `SIA_ORACLE_THIN_MODE` for advanced thin-mode override

Validation-only setup should pass with:

```bash
python scripts/run_tool.py check_prereqs.py
```

Execution setup should pass with:

```bash
python scripts/run_tool.py check_prereqs.py --require-oracle
```
