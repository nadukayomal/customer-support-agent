"""
This file make connection with supabase.
    - get_supabase_client()
    - get_supabase_engine()
    - get_supabase_session()
"""

import os
from typing import Optional
from loguru import logger
from sqlalchemy import text
from supabase import Client, create_client
from customer_support_agent.utils.config_utils import get_embedding
from .sql_client import get_session, get_sql_engine

_supabase_client: Optional[Client] = None


def get_supabase_client():
    """ 
    Get or Create supabase REST client for, 
        - auth
        - realtime
        - storage
    Return :
        supabase client instance
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
    try:
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info(f"Supabase client created: {supabase_url}")

        return _supabase_client

    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise RuntimeError(
            "Could not create Supabase client. "
            "Please check SUPABASE_URL and SUPABASE_ANON_KEY."
        ) from e 


def get_supabase_engine():
    """
    Return the shared database engine and connection pool for raw SQL or pool access.

    Created as a backward-compatible wrapper around ``get_sql_engine()`` so older
    Supabase-named imports keep working while routing to the canonical ``sql_client``.
    """
    return get_sql_engine()


def get_supabase_session():
    """
    Return a new per-request session for customer, conversation, and memory data.

    Created as a backward-compatible wrapper around ``get_session()`` so older
    Supabase-named imports keep working while routing to the canonical ``sql_client``.
    """
    return get_session()


def test_connection():
    """Test Supabase PostgreSQL connection."""
    try:
        engine = get_sql_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

        logger.info("Supabase connection test: SUCCESS")
        return True

    except Exception as e:
        logger.error(f"Supabase connection test: FAILED - {e}")
        return False


def check_pgvector_installed() -> bool:
    """Check if pgvector extension is installed in Supabase."""
    try:
        engine = get_sql_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            installed = result.scalar() == "vector"

        if installed:
            logger.info("pgvector extension: INSTALLED")
        else:
            logger.warning("pgvector extension: NOT INSTALLED")
            logger.warning("Run in Supabase SQL Editor: CREATE EXTENSION vector;")

        return installed

    except Exception as e:
        logger.error(f"Failed to check pgvector: {e}")
        return False


def init_supabase_schema():
    """
    Initialize Supabase schema dynamically from config.
    """
    from .supabase_schema import generate_supabase_schema

    embedding_dim = get_embedding().get("dimensions", 1536)
    sql_content = generate_supabase_schema()
    engine = get_sql_engine()

    try:
        with engine.begin() as conn:
            conn.execute(text(sql_content))

        logger.info("Supabase schema initialised (vector dim={})", embedding_dim)

    except Exception as e:
        logger.error("Failed to initialise schema: {}", e)
        raise


def set_user_context(user_id: str):
    """
    Set user context for Row Level Security (RLS).

    Args:
        user_id: User identifier
    """
    engine = get_sql_engine()

    with engine.connect() as conn:
        conn.execute(text(f"SET app.user_id = '{user_id}'"))


def validate_schema_dimensions():
    """
    Validate that Supabase schema vector dimensions match config embedding.dimensions.
    """
    embedding_dim = get_embedding().get("dimensions", 1536)

    try:
        engine = get_sql_engine()

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT atttypmod
                    FROM pg_attribute
                    WHERE attrelid = 'mem_facts'::regclass
                    AND attname = 'embedding'
                """)
            ).scalar()

            if result:
                db_dim = result
                if db_dim != embedding_dim:
                    raise ValueError(
                        f"   Schema dimension mismatch!\n"
                        f"   Database: vector({db_dim})\n"
                        f"   Config:   embedding.dimensions={embedding_dim}\n"
                        f"   Fix: Run 'make clean-supabase && make init-supabase'"
                    )

                logger.info("Schema validation passed: vector({})", embedding_dim)
            else:
                logger.warning(
                    "Could not validate schema dimensions (table may not exist)"
                )

    except Exception as e:
        logger.warning("Schema validation skipped: {}", e)


try:
    if test_connection():
        check_pgvector_installed()
        validate_schema_dimensions()
except Exception as e:
    logger.warning(f"Supabase not fully configured: {e}")
    logger.info("Set SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_DB_URL in .env")