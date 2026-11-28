"""
Test Supabase PostgreSQL connectivity and pgvector.

Usage (from project root)::

    python scripts/test_supabase.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

load_dotenv(ROOT / ".env")

from customer_support_agent.infrastructure.db.supabase_client import (  # noqa: E402
    check_pgvector_installed,
    test_connection,
    validate_schema_dimensions,
)
from customer_support_agent.infrastructure.log import setup_logging  # noqa: E402
from customer_support_agent.utils.config_utils import get_embedding  # noqa: E402


def main() -> int:
    setup_logging()
    embedding_dim = get_embedding().get("dimensions", 1536)

    logger.info("Embedding dimensions (config): {}", embedding_dim)
    logger.info("Testing Supabase connection...")

    ok = test_connection()
    if not ok:
        logger.error(
            "Connection failed. Set SUPABASE_DB_URL in .env and retry."
        )
        return 1

    if not check_pgvector_installed():
        logger.error(
            "pgvector is not installed. "
            "Run in Supabase SQL Editor: CREATE EXTENSION vector;"
        )
        return 1

    validate_schema_dimensions()
    logger.info("Supabase checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
