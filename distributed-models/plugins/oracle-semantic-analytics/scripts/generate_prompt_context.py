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
        "name": model.get("name"),
        "description": model.get("description"),
        "tables": model.get("tables", []),
        "relationships": model.get("relationships", []),
        "verified_queries": model.get("verified_queries", []),
        "module_custom_instructions": model.get("module_custom_instructions", "")
    }

    print(f'''
USER QUESTION:
{args.question}

ORACLE ANALYTICS ROUTER SKILL:
{oracle_skill}

SUBJECT-AREA ROUTING:
{routing}

STUDENT ENROLLMENT ANALYTICS SKILL:
{enrollment_skill}

SQL RULES:
{sql_rules}

LOCAL SEMANTIC YAML CONTEXT:
{compact(yaml.safe_dump(relevant, sort_keys=False), 16000)}

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
