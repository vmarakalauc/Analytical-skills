#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def compact(text: str, limit: int = 12000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [truncated] ..."

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--model", default=str(ROOT / "assets" / "semantic_models" / "sia_term_enrollments.yaml"))
    args = parser.parse_args()

    model_path = Path(args.model)
    model = yaml.safe_load(model_path.read_text(encoding="utf-8"))

    oracle_skill = read(ROOT / "skills" / "oracle-analytics-router" / "SKILL.md")
    enrollment_skill = read(ROOT / "skills" / "student-enrollment-analytics" / "SKILL.md")
    routing = read(ROOT / "routing" / "subject-area-routing.yaml")
    sql_rules = read(ROOT / "skills" / "oracle-analytics-router" / "references" / "sql_rules.md")

    relevant = {
        "semantic_model": model.get("semantic_model", {}),
        "domain": model.get("domain", {}),
        "business_glossary": model.get("business_glossary", []),
        "logical_model": model.get("logical_model", {}),
        "semantic_rules": model.get("semantic_rules", {}),
        "physical_mappings": model.get("physical_mappings", []),
        "governance": model.get("governance", {}),
        "validation": model.get("validation", {}),
        "presentation": model.get("presentation", {}),
        "verified_queries": model.get("verified_queries", []),
    }

    print(f'''
USER QUESTION:
{args.question}

CANONICAL SEMANTIC SHORTCUTS:
- Full-time students: join OBIA_DW.W_XACT_TYPE_D as load_d on f.ACAD_LOAD_WID = load_d.ROW_WID and load_d.W_XACT_CODE = 'SIA_ACADEMIC_LOAD_CODE'; filter load_d.XACT_TYPE_CODE = 'F'.
- Fall/Autumn terms: filter SUBSTR(t.TERM_CODE, -1) = '8'. Winter uses suffix '2', Spring uses suffix '4', Summer uses suffix '6'.
- Do not run discovery queries for these mappings unless the user explicitly asks to audit the semantic model.

ORACLE ANALYTICS ROUTER SKILL:
{oracle_skill}

SUBJECT-AREA ROUTING:
{routing}

STUDENT ENROLLMENT ANALYTICS SKILL:
{enrollment_skill}

SQL RULES:
{sql_rules}

LOCAL SEMANTIC YAML CONTEXT:
{compact(yaml.safe_dump(relevant, sort_keys=False), 30000)}

TASK:
- Interpret the question.
- Ask clarifying questions if required.
- Generate Oracle 19c SELECT-only SQL.
- Apply required semantic filters.
- Validate before execution.
- Explain metric definitions and assumptions.
'''.strip())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
