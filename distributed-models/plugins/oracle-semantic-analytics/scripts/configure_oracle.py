#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import getpass
import os

CONFIG_DIR = Path.home() / ".oracle-semantic-analytics"
ENV_FILE = CONFIG_DIR / ".env"

def dotenv_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'

def main() -> int:
    print("Local Oracle configuration helper")
    print("This writes a local .env file outside the plugin repository.")
    print("Do not commit this file.")
    print()

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    user = input("Oracle user: ").strip()
    dsn = input("Oracle DSN (host:1521/service): ").strip()
    password = getpass.getpass("Oracle password: ")

    ENV_FILE.write_text(
        f"ORACLE_USER={dotenv_quote(user)}\n"
        f"ORACLE_PASSWORD={dotenv_quote(password)}\n"
        f"ORACLE_DSN={dotenv_quote(dsn)}\n"
        f'ORACLE_THIN_MODE="true"\n'
        f'MAX_ROWS="1000"\n',
        encoding="utf-8"
    )
    if os.name == "posix":
        ENV_FILE.chmod(0o600)

    print()
    print(f"Wrote {ENV_FILE}")
    print("Before running tools, load it with:")
    print(f"  PowerShell: Get-Content {ENV_FILE} | ForEach-Object {{ if ($_ -match '^(.*?)=(.*)$') {{ [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim('\\\"'), 'Process') }} }}")
    print(f"  Bash: set -a && source {ENV_FILE} && set +a")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
