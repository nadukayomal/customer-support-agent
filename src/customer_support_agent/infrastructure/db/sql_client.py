"""
SQLAlchemy Database Client for Supabase PostgreSQL.

Manages the database engine, session factory, and SQLAlchemy table
definitions for the application's long-term memory system.

Responsibilities:
    - Initialize and manage the SQLAlchemy database connection.
    - Provide database sessions for executing queries.
    - Define semantic (mem_facts) and episodic (mem_episodes) memory tables.
    - Support pgvector embeddings for semantic search.
    - Create database tables and test database connectivity.

Configuration:
    Requires SUPABASE_DB_URL and embedding.dimensions from config/llm.yaml.
"""

import os
from typing import Optional

from loguru import logger
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UUID,
    create_engine,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from customer_support_agent.utils.config_utils import get_embedding

# Singleton engine
_engine: Optional[object] = None
_SessionLocal: Optional[object] = None

# Metadata
metadata = MetaData()

# Vector size from config/llm.yaml → embedding.dimensions
EMBEDDING_DIM = get_embedding().get("dimensions", 1536)

# ============================================================
# 1. Semantic Memory: mem_facts
# ============================================================
# Stores long-term customer facts, preferences, and useful
# information extracted from e-commerce conversations.
#
# Examples:
# - Customer prefers email delivery notifications.
# - Customer is interested in gaming laptops.
# - Customer prefers products under $1,000.
# - Customer prefers cash on delivery.
#
# These facts can be retrieved using vector similarity search.


mem_facts_table = Table(
    "mem_facts",
    metadata,

    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),

    # Authenticated application user who owns this memory.
    Column(
        "user_id",
        Text,
        nullable=False,
        index=True,
    ),

    # Actual customer fact or preference.
    Column(
        "text",
        Text,
        nullable=False,
    ),

    # Vector representation of the customer fact.
    Column(
        "embedding",
        Vector(EMBEDDING_DIM),
        nullable=True,
    ),

    # Application-assigned importance or confidence score.
    Column(
        "score",
        Float,
        nullable=False,
    ),

    # Categories such as preferences, products, delivery, payments.
    Column(
        "tags",
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    ),

    # When the memory was created.
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    ),

    # Last time this memory was retrieved or used.
    Column(
        "last_used_at",
        DateTime(timezone=True),
        nullable=True,
        server_default=text("NOW()"),
    ),

    # Optional memory expiration timestamp.
    Column(
        "ttl_at",
        DateTime(timezone=True),
        nullable=True,
    ),

    # Pinned memories should be protected from normal cleanup.
    Column(
        "pin",
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
    ),

    # Soft deletion instead of immediately removing a record.
    Column(
        "deleted",
        Boolean,
        nullable=False,
        server_default=text("FALSE"),
        index=True,
    ),
)


# ============================================================
# 2. Episodic Memory: mem_episodes
# ============================================================
# Stores summaries of meaningful previous customer
# support conversations and experiences.
#
# Examples:
# - Customer reported a damaged laptop.
# - Customer requested a refund for an order.
# - Customer experienced a delayed delivery.
# - Customer contacted support about a failed payment.
#
# These summaries can be retrieved using vector similarity search.


mem_episodes_table = Table(
    "mem_episodes",
    metadata,

    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),

    # Authenticated application user who owns this episode.
    Column(
        "user_id",
        Text,
        nullable=False,
        index=True,
    ),

    # Conversation session associated with this episode.
    Column(
        "session_id",
        Text,
        nullable=False,
        index=True,
    ),

    # Summarized customer-support experience.
    Column(
        "summary",
        Text,
        nullable=False,
    ),

    # Vector representation of the episode summary.
    Column(
        "summary_embedding",
        Vector(EMBEDDING_DIM),
        nullable=True,
    ),

    # Topics such as orders, returns, refunds, delivery, products.
    Column(
        "topic_tags",
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    ),

    # Beginning of the conversation.
    Column(
        "start_at",
        DateTime(timezone=True),
        nullable=False,
    ),

    # Ending of the conversation.
    Column(
        "end_at",
        DateTime(timezone=True),
        nullable=False,
    ),

    # Number of messages/turns included in the episode.
    Column(
        "turn_count",
        Integer,
        nullable=False,
    ),

    # Original conversation messages stored as structured JSON.
    Column(
        "turns",
        JSONB,
        nullable=False,
    ),

    # When the episode summary was created.
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    ),
)

def get_sql_engine():
    """
    Get SQLAlchemy engine for Supabase PostgreSQL.
    
    Returns:
        SQLAlchemy engine
    """
    global _engine

    if _engine is None:
        db_url = os.getenv("SUPABASE_DB_URL")
        
        if not db_url:
            raise ValueError(
                "SUPABASE_DB_URL must be set in .env file. "
                "Format: postgresql://postgres:[password]@db.xxxxx.supabase.co:5432/postgres"
            )
        
        _engine = create_engine(
                                db_url,
                                pool_size=5,
                                max_overflow=10,
                                pool_pre_ping=True,
                                pool_recycle=3600,
                                echo=False,  # Set to True for SQL debugging
                                )
        logger.info(f"Supabase SQL engine created")
    return _engine


def get_session():
    """
    Get SQLAlchemy session for Supabase.
    
    Returns:
        SQLAlchemy session
    """
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_sql_engine()
        _SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return _SessionLocal()


def create_tables():
    """
    Create database tables if they don't exist.
    
    Note: In production with Supabase, tables should be created via SQL Editor
    using sql/supabase_schema.sql for full pgvector support and RLS policies.
    """
    engine = get_sql_engine()
    metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")


def test_connection():
    """
    Test Supabase database connection.
    
    Returns:
        True if connection successful, False otherwise
    """
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


