#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(os.getenv("ORACLE_SEMANTIC_PLUGIN_ROOT", Path(__file__).resolve().parents[1])).resolve()
SCRIPTS = ROOT / "scripts"
MODEL = ROOT / "assets" / "semantic_models" / "sia_term_enrollments.yaml"
CONFIG = Path.home() / ".oracle-semantic-analytics" / "config.json"
VENV_DIR = Path.home() / ".oracle-semantic-analytics" / "venv"


def runtime_python() -> str:
    windows_python = VENV_DIR / "Scripts" / "python.exe"
    posix_python = VENV_DIR / "bin" / "python"
    if windows_python.exists():
        return str(windows_python)
    if posix_python.exists():
        return str(posix_python)
    return sys.executable


def json_dumps(data: dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def respond(message_id: Any, result: dict[str, Any] | None = None, error: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": message_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result or {}
    sys.stdout.write(json_dumps(payload) + "\n")
    sys.stdout.flush()


def text_result(text: str, is_error: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return result


def tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "name": "oracle_semantic_health",
            "description": "Check Oracle semantic analytics plugin runtime and local configuration status without reading secrets.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "oracle_semantic_get_context",
            "description": "Return semantic context for an analytics question from the bundled SIA semantic model.",
            "inputSchema": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"],
                "additionalProperties": False,
            },
        },
        {
            "name": "oracle_semantic_validate_sql",
            "description": "Validate generated Oracle SQL against the bundled semantic model safety rules.",
            "inputSchema": {
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"],
                "additionalProperties": False,
            },
        },
        {
            "name": "oracle_semantic_execute_sql",
            "description": "Execute validated read-only Oracle SQL using local SIA configuration and SIA_USER_PWD.",
            "inputSchema": {
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"],
                "additionalProperties": False,
            },
        },
        {
            "name": "oracle_semantic_save_report",
            "description": (
                "Save a complete self-contained HTML report to the reports directory and open it in the browser. "
                "Use this when you want full control over the visualization — generate the HTML including "
                "Chart.js charts, tables, and layout, then pass it here to save and open. "
                "The HTML must be a complete document (<!doctype html>...)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "html": {"type": "string", "description": "Complete self-contained HTML document."},
                    "title": {"type": "string", "description": "Short title used for the filename slug."},
                },
                "required": ["html", "title"],
                "additionalProperties": False,
            },
        },
        {
            "name": "oracle_semantic_data_dictionary",
            "description": (
                "Generate an Excel data dictionary for the bundled semantic model. "
                "Produces a multi-sheet .xlsx file covering dimensions, measures, "
                "business glossary, and governance rules. Opens the file automatically."
            ),
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "oracle_semantic_render_report",
            "description": (
                "Render query results as a local HTML analytics report with an optional chart. "
                "Use after SQL execution when a visualization improves understanding; for trends "
                "prefer line charts, for categorical breakdowns prefer bar charts, and for small "
                "or single-value results prefer no chart."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array", "items": {"type": "array"}},
                    "sql": {"type": "string"},
                    "summary": {"type": "string"},
                    "chart_type": {"type": "string", "enum": ["auto", "none", "line", "bar"]},
                },
                "required": ["question", "columns", "rows"],
                "additionalProperties": False,
            },
        },
    ]


def run_script(script: str, args: list[str], stdin: str | None = None) -> tuple[int, str]:
    command = [runtime_python(), str(SCRIPTS / script), *args]
    proc = subprocess.run(
        command,
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode, proc.stdout


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "oracle_semantic_health":
        code, output = run_script("check_prereqs.py", ["--require-oracle"])
        return text_result(output, is_error=code != 0)

    if name == "oracle_semantic_get_context":
        question = str(arguments.get("question", "")).strip()
        if not question:
            return text_result("Missing required argument: question", is_error=True)
        code, output = run_script("generate_prompt_context.py", ["--question", question])
        return text_result(output, is_error=code != 0)

    if name == "oracle_semantic_validate_sql":
        sql = str(arguments.get("sql", "")).strip()
        if not sql:
            return text_result("Missing required argument: sql", is_error=True)
        code, output = run_script("validate_sql.py", ["-"], stdin=sql)
        return text_result(output, is_error=code != 0)

    if name == "oracle_semantic_execute_sql":
        sql = str(arguments.get("sql", "")).strip()
        if not sql:
            return text_result("Missing required argument: sql", is_error=True)
        code, output = run_script("execute_oracle_readonly.py", ["-", "--yes"], stdin=sql)
        return text_result(output, is_error=code != 0)

    if name == "oracle_semantic_save_report":
        html = str(arguments.get("html", "")).strip()
        title = str(arguments.get("title", "report")).strip()
        if not html:
            return text_result("Missing required argument: html", is_error=True)
        import re as _re
        from datetime import datetime as _dt
        from pathlib import Path as _Path
        slug = _re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")[:60] or "report"
        reports_dir = _Path.home() / ".oracle-semantic-analytics" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{_dt.now().strftime('%Y%m%d-%H%M%S')}-{slug}.html"
        path = reports_dir / filename
        path.write_text(html, encoding="utf-8")
        try:
            import webbrowser
            webbrowser.open(path.as_uri())
        except Exception:
            pass
        return text_result(f"Report saved: {path}")

    if name == "oracle_semantic_data_dictionary":
        code, output = run_script("render_data_dictionary.py", [])
        if code != 0:
            return text_result(output, is_error=True)
        return text_result(f"Data dictionary written: {output.strip()}")

    if name == "oracle_semantic_render_report":
        payload = {
            "question": arguments.get("question"),
            "columns": arguments.get("columns"),
            "rows": arguments.get("rows"),
            "sql": arguments.get("sql", ""),
            "summary": arguments.get("summary", ""),
            "chart_type": arguments.get("chart_type", "auto"),
        }
        code, output = run_script("render_report.py", ["-"], stdin=json.dumps(payload))
        if code != 0:
            return text_result(output, is_error=True)
        return text_result(f"Report written: {output.strip()}")

    return text_result(f"Unknown tool: {name}", is_error=True)


def handle(message: dict[str, Any]) -> None:
    message_id = message.get("id")
    method = message.get("method")
    if message_id is None:
        return

    if method == "initialize":
        respond(
            message_id,
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "oracle-semantic-analytics", "version": "0.1.4"},
            },
        )
        return

    if method == "ping":
        respond(message_id, {})
        return

    if method == "tools/list":
        respond(message_id, {"tools": tool_schema()})
        return

    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        respond(message_id, call_tool(str(name), arguments))
        return

    respond(message_id, error={"code": -32601, "message": f"Method not found: {method}"})


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            handle(message)
        except Exception as exc:
            message_id = message.get("id")
            if message_id is not None:
                respond(message_id, error={"code": -32000, "message": str(exc)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
