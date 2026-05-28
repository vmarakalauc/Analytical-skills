#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
import argparse
from pathlib import Path

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
    ROOT / "scripts" / "validate_sql.py",
    ROOT / "scripts" / "execute_oracle_readonly.py",
]

def package_ok(import_name: str) -> bool:
    return importlib.util.find_spec(import_name) is not None

def load_env_files(env_file: str | None) -> None:
    if not load_dotenv:
        return
    load_dotenv()
    for candidate in [
        Path.cwd() / ".env",
        Path.home() / ".oracle-semantic-analytics" / ".env",
    ]:
        if candidate.exists():
            load_dotenv(candidate, override=True)
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
        help="Optional local .env file containing ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, and Oracle client settings.",
    )
    parser.add_argument(
        "--require-oracle",
        action="store_true",
        help="Fail when Oracle execution packages or ORACLE_* settings are missing.",
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

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")

    print(f"ORACLE_USER: {'OK' if user else 'MISSING'}")
    print(f"ORACLE_PASSWORD: {'OK' if password else 'MISSING'}")
    print(f"ORACLE_DSN: {'OK' if dsn else 'MISSING'}")

    if not all([user, password, dsn]):
        oracle_ok = False
        print()
        print("Oracle execution is not configured.")
        print("Set environment variables or use a local .env file that is not committed:")
        print('  export ORACLE_USER="your_user"')
        print('  export ORACLE_PASSWORD="your_password"')
        print('  export ORACLE_DSN="host:1521/service"')
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
