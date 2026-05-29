#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import argparse
from pathlib import Path

from analytics_config import CONFIG_FILE, runtime_settings

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PACKAGES = ["yaml", "dotenv", "sqlparse"]
EXECUTION_PACKAGES = ["oracledb"]
REQUIRED_FILES = [
    ROOT / "routing" / "subject-area-routing.yaml",
    ROOT / "assets" / "semantic_models" / "sia_term_enrollments.yaml",
    ROOT / "scripts" / "setup_analytics.py",
    ROOT / "scripts" / "run_tool.py",
    ROOT / "scripts" / "validate_sql.py",
    ROOT / "scripts" / "execute_oracle_readonly.py",
]

def package_ok(import_name: str) -> bool:
    return importlib.util.find_spec(import_name) is not None

def load_env_files(env_file: str | None) -> None:
    if not load_dotenv:
        return
    if env_file:
        env_path = Path(env_file).expanduser()
        if env_path.exists():
            load_dotenv(env_path, override=True)
        else:
            print(f"Env file not found: {env_path}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env-file",
        help="Optional legacy local .env file. Prefer ~/.oracle-semantic-analytics/config.json plus SIA_USER_PWD.",
    )
    parser.add_argument(
        "--require-oracle",
        action="store_true",
        help="Fail when Oracle execution packages or SIA settings are missing.",
    )
    args = parser.parse_args()
    load_env_files(args.env_file)

    print("Oracle Semantic Analytics prerequisite check")
    print("=" * 52)

    ok = True
    oracle_ok = True
    print(f"Python: {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        print("Python version: MISSING (requires 3.10+)")
        ok = False

    for pkg in REQUIRED_PACKAGES:
        status = "OK" if package_ok(pkg) else "MISSING"
        print(f"Package {pkg}: {status}")
        if status == "MISSING":
            ok = False

    for pkg in EXECUTION_PACKAGES:
        status = "OK" if package_ok(pkg) else "MISSING"
        print(f"Execution package {pkg}: {status}")
        if status == "MISSING":
            oracle_ok = False

    for file in REQUIRED_FILES:
        status = "OK" if file.exists() else "MISSING"
        print(f"File {file.relative_to(ROOT)}: {status}")
        if status == "MISSING":
            ok = False

    settings = runtime_settings()
    if settings["config_error"]:
        print(f"Config: ERROR ({settings['config_error']})")
        oracle_ok = False
    else:
        print(f"Config {CONFIG_FILE}: {'OK' if CONFIG_FILE.exists() else 'MISSING'}")

    user = settings["user"]
    password = settings["password"]
    dsn = settings["dsn"]
    oracle_client_lib = settings["oracle_client_lib"]

    print(f"SIA_USER: {'OK' if user else 'MISSING'}")
    print(f"SIA_USER_PWD: {'OK' if password else 'MISSING'}")
    print(f"SIA_DSN: {'OK' if dsn else 'MISSING'}")
    print(f"ORACLE_CLIENT_LIB: {'OK' if oracle_client_lib else 'MISSING'}")
    print(f"SIA_AUTO_APPROVE: {'OK' if settings['auto_approve'] else 'false'}")
    print(f"SIA_MAX_ROWS: {settings['max_rows']}")

    if not all([user, password, dsn]):
        oracle_ok = False
        print()
        print("Oracle execution is not configured.")
        print("Run the first-time setup helper, then set the password in the shell that starts Claude Code:")
        print("  python scripts/setup_analytics.py")
        print('  PowerShell: $env:SIA_USER_PWD = "your_password"')
        print('  CMD: set SIA_USER_PWD=your_password')
        print()
        print("Do not paste passwords into Claude chat.")

    if args.require_oracle and not oracle_ok:
        ok = False

    if ok:
        print()
        if oracle_ok:
            print("All prerequisites look ready, including Oracle execution settings.")
        else:
            print("Core validation prerequisites look ready. Oracle execution is not configured.")
        return 0

    print()
    print("Prerequisites are incomplete. Complete the missing items and retry.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
