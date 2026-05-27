#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_ROOT = ROOT.parents[1]
REPO_ROOT = MARKETPLACE_ROOT.parent

SECRET_PATTERNS = [
    re.compile(r"(?i)oracle_password\s*=\s*['\"](?!your_password|\.{3})[^'\"]+['\"]"),
    re.compile(r"(?i)password\s*[:=]\s*['\"](?!your_password|\.{3})[^'\"]+['\"]"),
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"][^'\"]+['\"]"),
]

ALLOWED_SECRET_FILES = {
    Path("distributed-models/plugins/oracle-semantic-analytics/scripts/configure_oracle.py"),
}

def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)

def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path} is not valid JSON: {exc}")

def validate_marketplace() -> None:
    marketplace = load_json(MARKETPLACE_ROOT / ".claude-plugin" / "marketplace.json")
    for field in ["name", "owner", "plugins"]:
        if field not in marketplace:
            fail(f"marketplace.json missing required field: {field}")
    for plugin in marketplace["plugins"]:
        source = plugin.get("source")
        if not source:
            fail("marketplace plugin entry missing source")
        plugin_root = marketplace.get("metadata", {}).get("pluginRoot", ".")
        resolved = (MARKETPLACE_ROOT / plugin_root / source).resolve()
        if not resolved.exists():
            fail(f"marketplace source does not exist: {source}")

def validate_plugin_manifest() -> None:
    manifest = load_json(ROOT / ".claude-plugin" / "plugin.json")
    for field in ["name", "description", "version"]:
        if not manifest.get(field):
            fail(f"plugin.json missing required field: {field}")
    forbidden_component_dirs = ["skills", "commands", "agents", "hooks"]
    for name in forbidden_component_dirs:
        if (ROOT / ".claude-plugin" / name).exists():
            fail(f"{name}/ must be at plugin root, not under .claude-plugin/")

def validate_skills() -> None:
    skills_dir = ROOT / "skills"
    if not skills_dir.exists():
        fail("skills/ directory is missing")
    for skill in skills_dir.glob("*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---"):
            fail(f"{skill.relative_to(ROOT)} missing YAML frontmatter")
        frontmatter = text.split("---", 2)[1]
        if "description:" not in frontmatter:
            fail(f"{skill.relative_to(ROOT)} missing description frontmatter")

def validate_routing() -> None:
    try:
        import yaml
    except ImportError:
        fail("PyYAML is required for routing validation")
    routing_path = ROOT / "routing" / "subject-area-routing.yaml"
    routing = yaml.safe_load(routing_path.read_text(encoding="utf-8"))
    routes = routing.get("routes", [])
    if not routes:
        fail("routing/subject-area-routing.yaml must define at least one route")
    for route in routes:
        for field in ["id", "skill", "semantic_model", "keywords"]:
            if not route.get(field):
                fail(f"route missing required field {field}: {route}")
        if not (ROOT / "skills" / route["skill"] / "SKILL.md").exists():
            fail(f"route references missing skill: {route['skill']}")
        if not (ROOT / route["semantic_model"]).exists():
            fail(f"route references missing semantic model: {route['semantic_model']}")

def validate_no_committed_secrets() -> None:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(REPO_ROOT)
        if rel in ALLOWED_SECRET_FILES:
            continue
        if path.suffix.lower() in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"possible committed secret in {rel}")

def validate_yaml() -> None:
    try:
        import yaml
    except ImportError:
        fail("PyYAML is required for package validation")
    model_path = ROOT / "assets" / "semantic_models" / "sia_term_enrollments.yaml"
    model = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    for field in ["name", "description", "tables", "relationships", "verified_queries"]:
        if field not in model:
            fail(f"semantic model missing required field: {field}")

def validate_sample_sql() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from validate_sql import validate

    sql = (ROOT / "examples" / "sample_generated_sql.sql").read_text(encoding="utf-8")
    errors = validate(sql)
    if errors:
        fail("sample SQL failed validation: " + "; ".join(errors))

def main() -> int:
    validate_marketplace()
    validate_plugin_manifest()
    validate_skills()
    validate_routing()
    validate_no_committed_secrets()
    validate_yaml()
    validate_sample_sql()
    print("Plugin package validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
