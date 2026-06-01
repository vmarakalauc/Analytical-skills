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

def validate_mcp_config() -> None:
    mcp_path = ROOT / ".mcp.json"
    mcp = load_json(mcp_path)
    servers = mcp.get("mcpServers", {})
    server = servers.get("oracle-semantic-analytics")
    if not server:
        fail(".mcp.json missing oracle-semantic-analytics server")
    args = server.get("args", [])
    if not any("${CLAUDE_PLUGIN_ROOT}" in str(arg) for arg in args):
        fail(".mcp.json server args must use ${CLAUDE_PLUGIN_ROOT}")
    if not (ROOT / "mcp_server" / "oracle_semantic_mcp.py").exists():
        fail("MCP server script is missing")

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
        for field in ["id", "semantic_model", "keywords"]:
            if not route.get(field):
                fail(f"route missing required field {field}: {route}")
        if not (ROOT / route["semantic_model"]).exists():
            fail(f"route references missing semantic model: {route['semantic_model']}")

def validate_no_committed_secrets() -> None:
    ignored_parts = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".oracle-semantic-analytics",
    }
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or ignored_parts.intersection(path.parts):
            continue
        if any(part.startswith(".tmp-") for part in path.parts):
            continue
        rel = path.relative_to(REPO_ROOT)
        if rel in ALLOWED_SECRET_FILES:
            continue
        if path.suffix.lower() in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".exe", ".dll"}:
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
    contract_fields = [
        "semantic_model",
        "domain",
        "business_glossary",
        "logical_model",
        "semantic_rules",
        "physical_mappings",
        "governance",
        "validation",
        "interoperability",
        "lineage",
        "freshness",
        "presentation",
        "verified_queries",
    ]
    for field in contract_fields:
        if field not in model:
            fail(f"semantic model missing required contract field: {field}")
    semantic_model = model["semantic_model"]
    for field in ["id", "name", "version", "model_type", "description"]:
        if not semantic_model.get(field):
            fail(f"semantic_model missing required field: {field}")
    logical = model["logical_model"]
    for field in ["entities", "dimensions", "measures", "filters", "relationships"]:
        if not logical.get(field):
            fail(f"logical_model missing required field: {field}")
    entities = {entity.get("id"): entity for entity in logical["entities"]}
    fact = entities.get("entity.term_enrollment")
    if not fact:
        fail("logical_model missing entity.term_enrollment")
    if not fact.get("grain", {}).get("keys"):
        fail("entity.term_enrollment grain must declare keys")
    measures = {measure.get("name"): measure for measure in logical["measures"]}
    for metric_name in ["student_count", "enrollment_count"]:
        metric = measures.get(metric_name)
        if not metric:
            fail(f"logical_model missing measure: {metric_name}")
        for field in ["id", "type", "entity", "default_filters", "allowed_dimensions", "format"]:
            if field not in metric:
                fail(f"measure {metric_name} missing required field: {field}")
    for rel in logical["relationships"]:
        for field in ["id", "cardinality", "join_type_default", "trusted", "role"]:
            if field not in rel:
                fail(f"relationship {rel.get('id')} missing required field: {field}")
    physical = model["physical_mappings"][0]
    for field in ["platform", "objects", "joins", "measure_expressions", "filter_expressions"]:
        if field not in physical:
            fail(f"physical mapping missing required field: {field}")
    if physical["platform"].get("type") != "oracle":
        fail("expected an oracle physical mapping for this demo")
    governance = model["governance"]
    if not governance.get("security") or not governance.get("privacy_controls"):
        fail("governance must include security and privacy_controls")
    if not model["validation"].get("sql_generation") or not model["validation"].get("evaluation_tests"):
        fail("validation must include sql_generation and evaluation_tests")

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
    validate_mcp_config()
    validate_skills()
    validate_routing()
    validate_no_committed_secrets()
    validate_yaml()
    validate_sample_sql()
    print("Plugin package validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
