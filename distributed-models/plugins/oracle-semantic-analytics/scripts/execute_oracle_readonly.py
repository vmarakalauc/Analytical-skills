#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

from validate_sql import validate

def env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y"}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sql_file", help="SQL file to execute, or '-' to read SQL from stdin.")
    parser.add_argument(
        "--env-file",
        help="Optional local .env file containing ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, and Oracle client settings.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm that the user approved executing this validated SQL.",
    )
    args = parser.parse_args()

    if load_dotenv:
        load_dotenv()
        for candidate in [
            Path.cwd() / ".env",
            Path.home() / ".oracle-semantic-analytics" / ".env",
        ]:
            if candidate.exists():
                load_dotenv(candidate, override=True)
        if args.env_file:
            env_path = Path(args.env_file).expanduser()
            if env_path.exists():
                load_dotenv(env_path, override=True)
            else:
                print(f"Env file not found: {env_path}")
                return 1

    if args.sql_file == "-":
        sql = sys.stdin.read()
    else:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    errors = validate(sql)
    if errors:
        print("Refusing execution because validation failed:")
        for e in errors:
            print(f"- {e}")
        return 1

    auto_approve = env_flag("ORACLE_ANALYTICS_AUTO_APPROVE")
    if auto_approve:
        print("ORACLE_ANALYTICS_AUTO_APPROVE=true; executing after validation without interactive prompt.")

    if not args.yes and not auto_approve:
        if not sys.stdin.isatty():
            print("Refusing execution without explicit approval. Re-run with --yes after user confirmation.")
            return 1
        answer = input("Execute this validated SELECT against Oracle? Type 'yes' to continue: ")
        if answer.strip().lower() != "yes":
            print("Execution cancelled.")
            return 1

    try:
        import oracledb
    except ImportError:
        print("Missing package: oracledb. Install with: pip install oracledb")
        return 1

    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    max_rows = int(os.getenv("MAX_ROWS", "1000"))
    thin_mode = env_flag("ORACLE_THIN_MODE", "false")
    oracle_client_lib = os.getenv("ORACLE_CLIENT_LIB_DIR")

    if not all([user, password, dsn]):
        print("Missing ORACLE_USER, ORACLE_PASSWORD, or ORACLE_DSN.")
        print("Run scripts/configure_oracle.py or set environment variables.")
        return 1

    if not thin_mode:
        oracledb.init_oracle_client(lib_dir=oracle_client_lib or None)

    with oracledb.connect(user=user, password=password, dsn=dsn) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(sql)
            cols = [d[0] for d in cur.description]
            print("\t".join(cols))
            count = 0
            for row in cur:
                print("\t".join("" if v is None else str(v) for v in row))
                count += 1
                if count >= max_rows:
                    print(f"Stopped at MAX_ROWS={max_rows}")
                    break
        conn.rollback()

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
