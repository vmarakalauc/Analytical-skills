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
        payload = {
            "plugin_root": str(ROOT),
            "semantic_model_exists": MODEL.exists(),
            "config_exists": CONFIG.exists(),
            "runtime_python": runtime_python(),
            "sia_user_set": bool(os.getenv("SIA_USER")),
            "sia_dsn_set": bool(os.getenv("SIA_DSN")),
            "sia_password_set": bool(os.getenv("SIA_USER_PWD")),
            "oracle_client_lib_set": bool(os.getenv("ORACLE_CLIENT_LIB")),
            "note": "No credential values are read or returned.",
        }
        return text_result(json.dumps(payload, indent=2))

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
                "serverInfo": {"name": "oracle-semantic-analytics", "version": "0.1.2"},
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
