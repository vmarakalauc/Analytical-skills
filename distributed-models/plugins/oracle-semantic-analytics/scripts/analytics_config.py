#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".oracle-semantic-analytics"
CONFIG_FILE = CONFIG_DIR / "config.json"
REPORTS_DIR = CONFIG_DIR / "reports"
VENV_DIR = CONFIG_DIR / "venv"


def env_flag(value: str | None, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def read_config(config_file: str | Path | None = None) -> dict[str, Any]:
    path = Path(config_file).expanduser() if config_file else CONFIG_FILE
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_config_error": f"Invalid JSON in {path}"}
    if not isinstance(data, dict):
        return {"_config_error": f"Config file must contain a JSON object: {path}"}
    return data


def write_config(config: dict[str, Any], config_file: str | Path | None = None) -> Path:
    path = Path(config_file).expanduser() if config_file else CONFIG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def runtime_settings(config_file: str | Path | None = None) -> dict[str, Any]:
    config = read_config(config_file)
    reports_dir = os.getenv("SIA_REPORTS_DIR") or config.get("reports_dir") or str(REPORTS_DIR)
    max_rows_raw = os.getenv("SIA_MAX_ROWS") or str(config.get("sia_max_rows") or config.get("max_rows") or "1000")
    try:
        max_rows = int(max_rows_raw)
    except ValueError:
        max_rows = 1000

    return {
        "config": config,
        "config_error": config.get("_config_error"),
        "user": os.getenv("SIA_USER") or config.get("sia_user"),
        "password": os.getenv("SIA_USER_PWD"),
        "dsn": os.getenv("SIA_DSN") or config.get("sia_dsn"),
        "oracle_client_lib": (
            os.getenv("ORACLE_CLIENT_LIB")
            or config.get("oracle_client_lib")
        ),
        "auto_approve": env_flag(
            os.getenv("SIA_AUTO_APPROVE"),
            default=env_flag(str(config.get("sia_auto_approve", "")), default=False),
        ),
        "max_rows": max_rows,
        "reports_dir": str(Path(reports_dir).expanduser()),
        "thin_mode": env_flag(os.getenv("SIA_ORACLE_THIN_MODE"), default=False),
    }


def find_oracle_client() -> str:
    candidates = [
        Path("C:/Oracle/Middleware/OAS_Home/bin"),
        Path("C:/oracle/instantclient"),
        Path("C:/instantclient"),
    ]
    for candidate in candidates:
        if (candidate / "oci.dll").exists():
            return str(candidate)

    for root in [Path("C:/Oracle"), Path("C:/oracle")]:
        if not root.exists():
            continue
        try:
            for oci in root.rglob("oci.dll"):
                return str(oci.parent)
        except OSError:
            continue
    return ""
