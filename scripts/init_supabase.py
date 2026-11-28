"""
Initialize supabase schema to create memory and crm tables.

Usage (from project root)::

    python scripts/init_supabase.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Allow `python scripts/init_supabase.py` without an editable install.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

load_dotenv(ROOT / ".env")

from customer_support_agent.infrastructure.db.supabase_client import (  # noqa: E402
    check_pgvector_installed,
    init_supabase_schema,
    test_connection,
)
from customer_support_agent.infrastructure.log import setup_logging  # noqa: E402



def main() -> int:
    setup_logging()

    try:
        if not test_connection():
            logger.error(
                "Cannot connect to Supabase. "
                "Set SUPABASE_DB_URL in .env and retry."
            )
            return 1

        if not check_pgvector_installed():
            logger.error(
                "pgvector is required. "
                "Run in Supabase SQL Editor: CREATE EXTENSION vector;"
            )
            return 1

        init_supabase_schema()
        logger.info("Supabase schema initialized successfully.")
        return 0
    except Exception as e:
        logger.error("Failed to initialize schema: {}", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
