#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from analytics_config import VENV_DIR

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ALLOWED_DIRS = {SCRIPTS.resolve(), (ROOT / "mcp_server").resolve()}


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: run_tool.py <script-name.py> [args...]")
        return 2

    script_name = sys.argv[1]
    # Allow scripts/foo.py or mcp_server/foo.py passed as relative paths
    candidate = (ROOT / script_name).resolve()
    if candidate.parent not in ALLOWED_DIRS or not candidate.exists():
        # Fallback: bare name looked up in scripts/
        candidate = (SCRIPTS / script_name).resolve()
        if candidate.parent != SCRIPTS.resolve() or not candidate.exists():
            print(f"Unknown plugin tool script: {script_name}")
            return 2
    script_path = candidate

    py = venv_python()
    if py.exists() and Path(sys.executable).resolve() != py.resolve():
        result = subprocess.run([str(py), str(script_path), *sys.argv[2:]], check=False)
        return result.returncode

    result = subprocess.run([sys.executable, str(script_path), *sys.argv[2:]], check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
