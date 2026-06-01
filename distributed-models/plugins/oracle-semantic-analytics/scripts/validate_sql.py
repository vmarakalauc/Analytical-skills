#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FORBIDDEN = [
    "INSERT", "UPDATE", "DELETE", "MERGE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK", "EXECUTE"
]
APPROVED_TABLES = {
    "OBIA_DW.W_DOMAIN_MEMBER_LKP_TL",
    "OBIA_DW.W_SIA_ACAD_CAR_D",
    "OBIA_DW.W_SIA_ACAD_ORG_D",
    "OBIA_DW.W_SIA_ACAD_PLAN_D",
    "OBIA_DW.W_SIA_ACAD_PROG_D",
    "OBIA_DW.W_SIA_ACAD_SPLAN_D",
    "OBIA_DW.W_SIA_SCHOLAR_D",
    "OBIA_DW.W_SIA_TERM_D",
    "OBIA_DW.W_SIA_TERM_ENRLMT_F",
    "OBIA_DW.W_STATUS_D",
    "OBIA_DW.W_XACT_TYPE_D",
}
RESTRICTED_COLUMNS = {
    "SCHOLAR_ID",
    "STUDENT_ID",
    "PERSON_ID",
    "EMAIL",
    "PHONE",
    "ADDRESS",
    "SSN",
    "NATIONAL_ID",
}

def normalize(sql: str) -> str:
    cleaned = sql.replace("\x00", "").lstrip("\ufeff\xef\xbb\xbf").strip()
    return re.sub(r"\s+", " ", cleaned, flags=re.MULTILINE).upper()

def referenced_tables(normalized_sql: str) -> set[str]:
    tables = set()
    for match in re.finditer(r"\b(?:FROM|JOIN)\s+([A-Z0-9_$.]+)", normalized_sql):
        table = match.group(1).rstrip(",")
        tables.add(table)
    return tables

def validate(sql: str) -> list[str]:
    errors = []
    normalized = normalize(sql)

    if not (normalized.startswith("SELECT") or normalized.startswith("WITH")):
        errors.append("Only SELECT statements (including CTEs starting with WITH) are allowed.")

    if ";" in normalized[:-1]:
        errors.append("Multiple statements are not allowed.")

    if re.search(r"(--|/\*)", sql):
        errors.append("SQL comments are not allowed in executable demo SQL.")

    for word in FORBIDDEN:
        if re.search(rf"\b{word}\b", normalized):
            errors.append(f"Forbidden SQL keyword found: {word}")

    if re.search(r"\bSELECT\s+\*|\b[A-Z][A-Z0-9_]*\.\*", normalized):
        errors.append("SELECT * is not allowed.")

    if re.search(r"\bLIMIT\b", normalized):
        errors.append("Use Oracle FETCH FIRST n ROWS ONLY instead of LIMIT.")

    for table in referenced_tables(normalized):
        if table.startswith("W_"):
            errors.append(f"Use fully qualified Oracle object names for {table}.")
        elif table.startswith("OBIA_DW.") and table not in APPROVED_TABLES:
            errors.append(f"Table is not approved by the bundled semantic model: {table}")

    for column in RESTRICTED_COLUMNS:
        if re.search(rf"\b{column}\b", normalized):
            errors.append(f"Restricted student-identifying column is not allowed: {column}")

    if "W_SIA_TERM_ENRLMT_F" in normalized:
        if "DELETE_FLG" not in normalized or "'N'" not in normalized:
            errors.append("Term enrollment queries must filter DELETE_FLG = 'N'.")
        if "X_TERM_ENROLLED_FLAG" not in normalized or "'Y'" not in normalized:
            errors.append("Active enrollment queries should filter X_TERM_ENROLLED_FLAG = 'Y'.")

    if "W_XACT_TYPE_D" in normalized and "W_XACT_CODE" not in normalized:
        errors.append("W_XACT_TYPE_D joins require a W_XACT_CODE discriminator.")

    if "FETCH FIRST" not in normalized:
        errors.append("Include an explicit Oracle row limit using FETCH FIRST n ROWS ONLY.")

    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sql_file", help="SQL file to validate, or '-' to read SQL from stdin.")
    args = parser.parse_args()

    if args.sql_file == "-":
        sql = sys.stdin.read()
    else:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    errors = validate(sql)

    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    print("VALIDATION PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
