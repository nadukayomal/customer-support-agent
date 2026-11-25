# Customer Support Agent

![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-1C3C3C.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-DC244C.svg)
![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)

An end-to-end AI-powered e-commerce customer support agent built with FastAPI, LangGraph, Supabase PostgreSQL (pgvector), and Qdrant, combining CRM order and ticket retrieval, hybrid RAG with semantic caching (CAG) and corrective RAG (CRAG), structured conversation memory, and multi-step support workflows.

---



## Overview

The Customer Support Agent is designed to automate and assist e-commerce customer service operations by grounding LLM responses in live CRM records, knowledge-base policies, and persistent customer interaction memory.

### Core Objectives

1. Understand and triage incoming customer inquiries.
2. Persist and recall previous customer interactions through structured memory.
3. Retrieve customer profiles, orders, payments, and product catalog records from the CRM database.
4. Track order fulfillment and shipment delivery status.
5. Answer questions on products, warranties, returns, and refunds using knowledge-base retrieval.
6. Execute multi-step support workflows (returns, refunds, payment issues, escalations).
7. Continuously improve support quality through Langfuse tracing and structured memory consolidation.

---



## Technology Stack


| Layer                  | Technology                                                          | Purpose                                                              |
| ---------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------- |
| API Framework          | FastAPI, Uvicorn, Pydantic v2                                       | HTTP endpoints, request/response validation, SSE streaming           |
| Agent Orchestration    | LangGraph                                                           | Stateful multi-step support workflows and tool execution             |
| LLM Providers          | OpenRouter, OpenAI, Anthropic, Google, Groq, DeepSeek               | Tiered chat (`general`, `strong`, `reason`) and embeddings           |
| Relational & Memory DB | Supabase PostgreSQL, SQLAlchemy (async), asyncpg, pgvector, Alembic | 10-table CRM schema and vector-backed episodic memory                |
| Vector Knowledge Base  | Qdrant, rank-bm25, tiktoken                                         | Hybrid retrieval, semantic caching (CAG), and Corrective RAG (CRAG)  |
| Auth & Rate Limiting   | PyJWT, slowapi                                                      | Token-based customer identity and API rate limiting                  |
| Observability          | Langfuse, structlog                                                 | LLM tracing, token/latency logging, and PII redaction                |
| Tooling & Quality      | uv, ruff, mypy, pytest                                              | Dependency locking, linting, strict type checking, and async testing |


---



## Current Implementation Status

The project is in active **Alpha (**`0.1.0`**)** development. Below is the status of each component based on the current codebase:


| Component                         | Status      | Details                                                                                                                                                                |
| --------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dependency & Tooling Setup        | Implemented | `pyproject.toml`, `requirements.txt`, `uv.lock`, `ruff`, `mypy`, and `pytest` configured                                                                               |
| YAML Configuration                | Implemented | `config/app.yaml`, `config/llm.yaml`, `config/models.yaml`, and `config/rag.yaml` defined                                                                              |
| CRM Database Schema               | Implemented | 10 PostgreSQL tables, indexes, constraints, and `updated_at` triggers in `sql/create_crm_table.sql`                                                                    |
| CRM Sample Data & Queries         | Implemented | Seed data (`sql/insert_data_crm.sql`) and inspection queries (`sql/read_crm_table.sql`)                                                                                |
| Architecture Documentation        | Implemented | CRM schema and system objectives documented in `report/document.md`                                                                                                    |
| FastAPI Application & Schemas     | Partial     | `main.py`, `api/routes.py` (`POST /user_query`), and `schema/chat.py` (`ChatRequest`, `ChatResponse`) implemented; `utils/api_utils.py` currently returns an echo stub |
| Config Loader                     | Scaffolded  | `src/customer_support_agent/utils/config_utils.py` created (empty)                                                                                                     |
| Agent, Tools, DB, Memory, Prompts | Scaffolded  | Directories created under `src/customer_support_agent/` and `data/` awaiting implementation                                                                            |
| Tests, Migrations & Evals         | Planned     | Configured in `pyproject.toml` (`testpaths = ["tests"]`); directories not yet created                                                                                  |


---



## Project Structure

```text
customer_support_agent/
├── config/
│   ├── app.yaml                  # Data/KB/log paths, PII-redacted logging, Langfuse toggle
│   ├── llm.yaml                  # Default provider, tier, LLM and embedding defaults
│   ├── models.yaml               # Provider-to-model catalog (general/strong/reason) and vector dims
│   └── rag.yaml                  # Chunking strategies, retrieval, CAG cache, and CRAG thresholds
├── data/                         # Local data root (gitignored)
│   ├── crm/                      # CRM source data (scaffolded)
│   ├── faq/                      # FAQ documents (scaffolded)
│   └── policy/                   # Policy documents (scaffolded)
├── report/
│   └── document.md               # Objectives, tech stack, and CRM database documentation
├── scripts/                      # Utility and ingestion scripts (scaffolded)
├── sql/
│   ├── create_crm_table.sql      # PostgreSQL DDL for 10 CRM tables, indexes, and triggers
│   ├── insert_data_crm.sql       # Sample seed dataset across all 10 tables
│   └── read_crm_table.sql        # Verification SELECT queries for all CRM tables
├── src/
│   └── customer_support_agent/
│       ├── agent/                # LangGraph orchestration (scaffolded)
│       │   └── tools/            # Agent tool definitions (scaffolded)
│       ├── api/
│       │   └── routes.py         # FastAPI router exposing POST /user_query
│       ├── db/                   # Database access and repositories (scaffolded)
│       ├── memory/               # Conversation and episodic memory (scaffolded)
│       ├── prompts/              # System and workflow prompts (scaffolded)
│       ├── schema/
│       │   └── chat.py           # ChatRequest and ChatResponse Pydantic models
│       ├── utils/
│       │   ├── api_utils.py      # Query handler (currently echo stub)
│       │   └── config_utils.py   # Configuration loader (scaffolded)
│       └── main.py               # FastAPI app entrypoint and Uvicorn runner
├── .env                          # Environment secrets and service URLs (gitignored)
├── .gitignore
├── pyproject.toml                # Package metadata, dependencies, ruff/mypy/pytest config
├── README.md
├── requirements.txt              # Pip-style requirements and editable install
└── uv.lock                       # Locked dependency graph
```

---



## CRM Database Schema

Defined in `sql/create_crm_table.sql` for PostgreSQL / Supabase with UUID primary keys, referential integrity, `CHECK` constraints, 11 foreign-key performance indexes, and automatic `updated_at` triggers:


| Table             | Purpose                                                            | Key Relationships                                                                           |
| ----------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| `customers`       | Customer profile and contact details                               | One-to-many with `orders`, `support_tickets`                                                |
| `categories`      | Hierarchical product categories                                    | Self-referential parent category; one-to-many with `products`                               |
| `products`        | Product catalog, SKU, pricing, stock                               | Belongs to `categories`; referenced by `order_items`                                        |
| `orders`          | Purchase orders, status, totals, shipping address                  | Belongs to `customers`; parent of `order_items`, `payments`, `shipments`, `support_tickets` |
| `order_items`     | Line items with generated `subtotal` (`quantity * unit_price`)     | Belongs to `orders` and `products`; parent of `return_requests`                             |
| `payments`        | Payment methods, transaction refs, payment status                  | Belongs to `orders`                                                                         |
| `shipments`       | Tracking numbers, carriers, delivery milestones                    | Belongs to `orders`                                                                         |
| `support_tickets` | Customer complaints, category, priority, status                    | Belongs to `customers`; optionally linked to `orders`                                       |
| `ticket_messages` | Conversation log (`customer`, `ai_agent`, `human_agent`, `system`) | Belongs to `support_tickets`                                                                |
| `return_requests` | Return reasons, approval status, quantity, refund amount           | Belongs to `order_items`                                                                    |


---



## Configuration

Runtime behavior is split across four YAML files in `config/` and environment variables in `.env`:

- `config/app.yaml`: Configures `data`, `data/kb`, and `logs` paths, `INFO`-level logging with token/latency tracking and `redact_pii: true`, and the Langfuse observability switch.
- `config/llm.yaml`: Sets `openrouter` as the default provider gateway, `general` tier, deterministic `temperature: 0.0`, `max_tokens: 2000`, and `1536`-dimensional `small` embeddings (`batch_size: 100`).
- `config/models.yaml`: Maps `general`, `strong`, and `reason` tiers to concrete model IDs for `openrouter`, `openai`, `anthropic`, `google`, `groq`, and `deepseek`, along with embedding dimensions (`1536` / `3072`).
- `config/rag.yaml`: Defines five chunking presets (`fixed`, `semantic`, `sliding`, `parent_child`, `late`), retrieval defaults (`top_k: 4`, `similarity_threshold: 0.7`), CAG semantic cache (`support_cag_cache`, threshold `0.90`, 24h TTL, `cache_personalized: false`), and CRAG fallback (`confidence_threshold: 0.6`, `expanded_k: 8`).



### Environment Variables

Create a `.env` file in the project root with the required service credentials:

```env
# Supabase / PostgreSQL
SUPABASE_DB_URL=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=

# Qdrant
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=

# LLM Providers
OPENROUTER_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=

# Optional Services & Flags
REDIS_URL=
TAVILY_API_KEY=
USE_SB_ST=

# Langfuse Observability (when observability.enabled is true)
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=
```

---



## Getting Started



### Prerequisites

- Python 3.11 or higher
- `uv` (recommended) or `pip`
- PostgreSQL / Supabase instance
- Qdrant instance



### Installation

Using `uv`:

```bash
uv sync
```

Using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .
```

To include optional local embedding dependencies (`sentence-transformers`):

```bash
uv sync --extra local-embeddings
```



### Database Setup

Execute the SQL scripts against your PostgreSQL / Supabase database in order:

1. Create tables, constraints, indexes, and triggers: `sql/create_crm_table.sql`
2. Load sample CRM records (optional, for local testing): `sql/insert_data_crm.sql`
3. Verify loaded records: `sql/read_crm_table.sql`



### Running the API Server

Start the FastAPI development server on `http://127.0.0.1:8000`:

```bash
uvicorn customer_support_agent.main:app --host 127.0.0.1 --port 8000 --reload
```

Or run the module directly:

```bash
python -m customer_support_agent.main
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

---



## API Reference



### `POST /user_query`

Accepts a customer message and optional conversation identifier. In the current milestone, `get_user_query` in `src/customer_support_agent/utils/api_utils.py` acts as a stub that echoes the incoming message and assigns a UUID `conversation_id` if omitted.

**Request (**`ChatRequest`**)**

```json
{
  "message": "Where is my laptop delivery?",
  "conversation_id": null
}
```

**Response (**`ChatResponse`**)**

```json
{
  "reply": "Where is my laptop delivery?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "sources": [],
  "escalated": false
}
```

---



## Development

Quality checks configured in `pyproject.toml`:

```bash
# Lint and format check
ruff check src/

# Static type checking (strict mode)
mypy src/

# Run test suite
pytest
```

