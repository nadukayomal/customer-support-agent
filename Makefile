.PHONY: help install clean status \
        init-supabase test-supabase \
        seed-crm query-crm \
        ingest-qdrant ingest-qdrant-recreate qdrant-info \
        run test-all \
        demo

# ---------------------------------------------------------------------------
# uv-managed environment (created via: uv sync)
# ---------------------------------------------------------------------------

UV      := uv
PYTHON  := $(UV) run python
UVICORN := $(UV) run uvicorn
PYTEST  := $(UV) run pytest

# ---------------------------------------------------------------------------
# HELP
# ---------------------------------------------------------------------------

help:
	@echo =================================================================
	@echo   Customer Support Agent - Makefile Commands
	@echo =================================================================
	@echo.
	@echo SETUP AND INSTALLATION
	@echo   make install                 Sync deps with uv (uv sync --all-groups)
	@echo   make init-supabase           Initialize Supabase schema (CRM + Memory)
	@echo   make test-supabase           Test Supabase connection and pgvector
	@echo.
	@echo QDRANT (Internal KB - CAG + Parent-Child Chunking)
	@echo   make ingest-qdrant           Ingest internal KB into Qdrant
	@echo   make ingest-qdrant-recreate  Drop, recreate collection, and re-ingest
	@echo   make qdrant-info             Show Qdrant collection stats
	@echo.
	@echo CRM DATA
	@echo   make seed-crm                Load sample CRM rows from sql/insert_data_crm.sql
	@echo   make query-crm               Show CRM table counts (Supabase)
	@echo   make status                  Show system status
	@echo.
	@echo TESTING AND APP
	@echo   make test-all                Run all tests
	@echo   make run                     Start FastAPI (uvicorn)
	@echo   make demo                    Alias for make run
	@echo.
	@echo CLEANUP
	@echo   make clean                   Remove local caches and generated junk
	@echo.

# ---------------------------------------------------------------------------
# SETUP AND INSTALLATION
# ---------------------------------------------------------------------------

install:
	@echo Syncing dependencies with uv...
	$(UV) sync --all-groups
	@echo Installation complete.

# ---------------------------------------------------------------------------
# SUPABASE SETUP
# ---------------------------------------------------------------------------

init-supabase:
	@echo =================================================================
	@echo   Initializing Supabase Schema
	@echo =================================================================
	@echo.
	@echo This will create / verify:
	@echo   CRM:
	@echo     - customers, categories, products
	@echo     - orders, order_items, payments, shipments
	@echo     - support_tickets, ticket_messages, return_requests
	@echo   Memory:
	@echo     - conversations, st_turns
	@echo     - mem_facts, mem_episodes, mem_procedures (pgvector)
	@echo   Knowledge metadata:
	@echo     - kb_documents, kb_chunks
	@echo   Search helpers + IVFFlat indexes
	@echo.
	@echo Initializing schema...
	@$(PYTHON) scripts/init_supabase.py
	@echo.
	@echo Supabase schema initialized successfully.

test-supabase:
	@echo Testing Supabase connection...
	@echo.
	@$(PYTHON) scripts/test_supabase.py

# ---------------------------------------------------------------------------
# QDRANT (RAG Knowledge Base)
# ---------------------------------------------------------------------------

ingest-qdrant:
	@echo =================================================================
	@echo   Ingesting Internal KB -^> Qdrant (Parent-Child Chunking)
	@echo =================================================================
	@echo.
	@echo Configuration:
	@echo   - Source:   data/kb (and data/faq, data/policy)
	@echo   - Strategy: parent_child
	@echo   - RAG type: CAG (Cache-Augmented Generation)
	@echo.
	@$(PYTHON) scripts/ingest_to_qdrant.py --source kb --strategy parent_child

ingest-qdrant-recreate:
	@echo =================================================================
	@echo   Recreating Qdrant Collection + Re-ingesting
	@echo =================================================================
	@$(PYTHON) scripts/ingest_to_qdrant.py --source kb --strategy parent_child --recreate

qdrant-info:
	@echo Qdrant Collection Info:
	@$(PYTHON) -c "from customer_support_agent.infrastructure.db.qdrant_client import collection_info; info = collection_info(); [print('  {}: {}'.format(k, v)) for k, v in info.items()]"

# ---------------------------------------------------------------------------
# CRM DATA
# ---------------------------------------------------------------------------

seed-crm:
	@echo =================================================================
	@echo   Seeding CRM - Supabase (sql/insert_data_crm.sql)
	@echo =================================================================
	@echo.
	@$(PYTHON) scripts/seed_crm_sql.py

query-crm:
	@echo =================================================================
	@echo   CRM Database Statistics (Supabase)
	@echo =================================================================
	@echo.
	@$(PYTHON) -c "from customer_support_agent.infrastructure.db.sql_client import get_session; from sqlalchemy import text; tables = ['customers', 'categories', 'products', 'orders', 'order_items', 'payments', 'shipments', 'support_tickets', 'ticket_messages', 'return_requests']; session = get_session(); print('Table Counts:'); [print('  {:20s} {:>6}'.format(t, session.execute(text('SELECT COUNT(*) FROM {}'.format(t))).scalar())) for t in tables]; session.close(); print(); print('Data is in Supabase PostgreSQL')"

status:
	@echo =================================================================
	@echo   System Status
	@echo =================================================================
	@echo.
	@echo Data Sources:
	@echo   CRM + Memory: Supabase PostgreSQL (cloud)
	@echo   RAG KB:       Qdrant Cloud
	@echo   CAG Cache:    Qdrant Cloud (support_cag_cache)
	@echo.
	@echo Local Data:
	@echo   Knowledge Base: data/kb/
	@echo   FAQ:            data/faq/
	@echo   Policy:         data/policy/
	@echo.
	@echo Configuration:
	@$(PYTHON) --version
	@echo   Env manager: uv
	@echo   Config: config/app.yaml, llm.yaml, models.yaml, rag.yaml
	@echo   ST Memory: Supabase (st_turns table)
	@echo.
	@echo Quick Start:
	@echo   make install ^&^& make init-supabase ^&^& make seed-crm

# ---------------------------------------------------------------------------
# TESTING AND APP
# ---------------------------------------------------------------------------

test-all:
	@echo Running all tests...
	@$(PYTEST) tests/ -v

run:
	@echo Starting FastAPI (uvicorn)...
	@$(UVICORN) customer_support_agent.main:app --host 127.0.0.1 --port 8000 --reload

demo: run

# ---------------------------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------------------------

clean:
	@echo Cleaning local generated data...
	@$(PYTHON) -c "import pathlib, shutil; roots = [pathlib.Path('src'), pathlib.Path('scripts'), pathlib.Path('tests')]; [shutil.rmtree(p, ignore_errors=True) for root in roots if root.exists() for p in root.rglob('__pycache__')]; [p.unlink(missing_ok=True) for root in roots if root.exists() for p in root.rglob('*.pyc')]"
	@echo Cleaned.
	@echo.
	@echo Cloud data (Supabase, Qdrant) is not affected.
	@echo   To reset CRM seed: re-run make seed-crm
	@echo   To reset Qdrant:    run make ingest-qdrant-recreate

# ---------------------------------------------------------------------------
# DEFAULT
# ---------------------------------------------------------------------------

.DEFAULT_GOAL := help
