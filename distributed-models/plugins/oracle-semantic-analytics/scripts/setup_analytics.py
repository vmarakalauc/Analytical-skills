#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path

from analytics_config import CONFIG_DIR, CONFIG_FILE, REPORTS_DIR, VENV_DIR, find_oracle_client, write_config

ROOT = Path(__file__).resolve().parents[1]


def prompt_value(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def install_runtime(skip_install: bool = False) -> bool:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if skip_install:
        print("Skipped Python runtime and package install.")
        return True

    if not VENV_DIR.exists():
        print(f"Creating Python runtime: {VENV_DIR}")
        try:
            venv.EnvBuilder(with_pip=True, clear=False).create(VENV_DIR)
        except Exception as exc:
            print(f"Could not create Python runtime: {exc}")
            print("Install or repair Python venv/ensurepip support, then rerun setup.")
            return False
    else:
        print(f"Python runtime already exists: {VENV_DIR}")

    requirements = ROOT / "requirements.txt"
    print(f"Installing Python packages from {requirements}")
    result = subprocess.run(
        [str(venv_python()), "-m", "pip", "install", "-r", str(requirements)],
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-install", action="store_true", help="Create config only; do not install Python packages.")
    parser.add_argument("--yes", action="store_true", help="Accept defaults for prompts where possible.")
    parser.add_argument("--sia-user", help="SIA Oracle username to store in local non-secret config.")
    parser.add_argument("--sia-dsn", help="SIA Oracle DSN, for example host:port/service.")
    parser.add_argument("--oracle-client-lib", help="Oracle Client library folder for thick mode.")
    parser.add_argument("--auto-approve", choices=["true", "false"], help="Whether validated SQL may execute without an extra prompt.")
    parser.add_argument("--max-rows", type=int, help="Maximum rows to return from live execution.")
    args = parser.parse_args()

    print("Oracle Semantic Analytics setup")
    print("=" * 40)
    print("This creates local runtime/config outside the repository.")
    print("The password is not stored. Set SIA_USER_PWD in your shell before live execution.")
    print()

    install_ok = install_runtime(skip_install=args.skip_install)
    if not install_ok:
        print()
        print("Package installation failed. Fix pip/network access and rerun setup.")
        return 1

    detected_client = find_oracle_client()
    has_cli_config = any(
        value is not None
        for value in [
            args.sia_user,
            args.sia_dsn,
            args.oracle_client_lib,
            args.auto_approve,
            args.max_rows,
        ]
    )
    if args.yes or has_cli_config:
        sia_user = args.sia_user or ""
        sia_dsn = args.sia_dsn or ""
        oracle_client_lib = args.oracle_client_lib if args.oracle_client_lib is not None else detected_client
        auto_approve = args.auto_approve == "true" if args.auto_approve is not None else False
        max_rows = args.max_rows or 1000
    else:
        sia_user = prompt_value("SIA Oracle username")
        sia_dsn = prompt_value("SIA Oracle DSN (host:port/service)")
        oracle_client_lib = prompt_value("Oracle Client library folder", detected_client)
        auto_raw = prompt_value("Auto-execute validated SQL in controlled sessions? true/false", "false")
        rows_raw = prompt_value("Maximum rows to return", "1000")
        auto_approve = auto_raw.strip().lower() in {"1", "true", "yes", "y"}
        try:
            max_rows = int(rows_raw)
        except ValueError:
            max_rows = 1000

    config = {
        "sia_user": sia_user,
        "sia_dsn": sia_dsn,
        "oracle_client_lib": oracle_client_lib,
        "sia_auto_approve": auto_approve,
        "sia_max_rows": max_rows,
        "reports_dir": str(REPORTS_DIR),
        "venv_python": str(venv_python()),
    }
    config_path = write_config(config)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print(f"Wrote config: {config_path}")
    print(f"Reports directory: {REPORTS_DIR}")
    print()
    print("Before live Oracle execution, set the password in the shell that starts Claude Code:")
    print('  PowerShell: $env:SIA_USER_PWD = "your_password"')
    print('  CMD: set SIA_USER_PWD=your_password')
    print("For a persistent user variable, set it outside chat with your normal password-management process.")
    print()
    print("Next check:")
    print(f"  python {ROOT / 'scripts' / 'run_tool.py'} check_prereqs.py --require-oracle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
