#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from analytics_config import VENV_DIR

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: run_tool.py <script-name.py> [args...]")
        return 2

    script_name = sys.argv[1]
    script_path = (SCRIPTS / script_name).resolve()
    if script_path.parent != SCRIPTS.resolve() or not script_path.exists():
        print(f"Unknown plugin tool script: {script_name}")
        return 2

    py = venv_python()
    if py.exists() and Path(sys.executable).resolve() != py.resolve():
        result = subprocess.run([str(py), str(script_path), *sys.argv[2:]], check=False)
        return result.returncode

    result = subprocess.run([sys.executable, str(script_path), *sys.argv[2:]], check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
