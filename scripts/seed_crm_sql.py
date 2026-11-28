"""
Load sample CRM rows from sql/insert_data_crm.sql into Supabase.

Usage (from project root)::

    python scripts/seed_crm_sql.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

load_dotenv(ROOT / ".env")

from customer_support_agent.infrastructure.db.sql_client import (  # noqa: E402
    get_sql_engine,
    test_connection,
)
from customer_support_agent.infrastructure.log import setup_logging  # noqa: E402

SQL_FILE = ROOT / "sql" / "insert_data_crm.sql"


def main() -> int:
    setup_logging()

    if not SQL_FILE.is_file():
        logger.error("Seed SQL not found: {}", SQL_FILE)
        return 1

    if not test_connection():
        logger.error(
            "Cannot connect to Supabase. Set SUPABASE_DB_URL in .env and retry."
        )
        return 1

    sql_content = SQL_FILE.read_text(encoding="utf-8")
    engine = get_sql_engine()

    try:
        with engine.begin() as conn:
            conn.execute(text(sql_content))
        logger.info("CRM seed applied from {}", SQL_FILE)
        return 0
    except Exception as e:
        logger.error("Failed to seed CRM: {}", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
