# Oracle 19c SQL Rules

- Use `SELECT` only.
- Use fully qualified table names when possible.
- Use explicit `JOIN` syntax.
- Use `FETCH FIRST n ROWS ONLY`, not `LIMIT`.
- Use `SYSDATE` for current date.
- Use `COUNT(DISTINCT ...)` for distinct-count metrics defined by the semantic model.
- Do not use `SELECT *`.
- Do not use DDL or DML.
- Apply required default filters from the semantic YAML.
- If joining `W_XACT_TYPE_D`, include the required `W_XACT_CODE` discriminator.
