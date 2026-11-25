# Customer Support Agent

```
customer_support_agent/
├── data/
│   ├── crm/
│   ├── faq/
│   └── policy/
├── report/
│   └── document.md
├── sql/
│   └── create_crm_table.sql
├── src/
│   └── customer_support_agent/
│       ├── agent/
│       ├── api/
│       ├── app/
│       │   └── routes.py
│       ├── db/
│       ├── memory/
│       ├── schema/
│       └── main.py
├── .gitignore
├── pyproject.toml
├── README.md
├── requirements.txt
└── uv.lock
```

| Path | Role |
|------|------|
| `src/customer_support_agent/` | Application package |
| `src/customer_support_agent/main.py` | FastAPI entrypoint |
| `src/customer_support_agent/app/` | HTTP routes |
| `src/customer_support_agent/api/` | API layer |
| `src/customer_support_agent/agent/` | Agent / LangGraph logic |
| `src/customer_support_agent/db/` | Database access |
| `src/customer_support_agent/memory/` | Conversation / support memory |
| `src/customer_support_agent/schema/` | Data models |
| `data/crm/` | CRM source data |
| `data/faq/` | FAQ source data |
| `data/policy/` | Policy source data |
| `sql/` | Database schema scripts |
| `report/` | Project notes |
| `pyproject.toml` | Project metadata and dependencies |
| `requirements.txt` | Pip-style dependency list |
| `uv.lock` | Locked dependency versions |


customer_support_agent/
├── .github/workflows/ci.yml          # lint, type-check, tests, security scan
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── Dockerfile
├── docker-compose.yml                # local Postgres/Qdrant if needed
├── pyproject.toml
├── uv.lock
├── README.md
│
├── src/customer_support_agent/
│   ├── __init__.py
│   ├── __main__.py                   # python -m customer_support_agent
│   ├── main.py                       # app factory only
│   ├── config.py                     # pydantic-settings
│   │
│   ├── api/                          # HTTP layer only (replaces app/ + api/)
│   │   ├── deps.py
│   │   ├── errors.py
│   │   ├── middleware.py
│   │   └── v1/
│   │       ├── router.py
│   │       ├── health.py
│   │       ├── chat.py
│   │       ├── feedback.py
│   │       └── memory.py
│   │
│   ├── schemas/                      # Pydantic request/response models
│   │   ├── chat.py
│   │   ├── order.py
│   │   └── common.py
│   │
│   ├── agent/                        # LangGraph orchestration
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── guardrails.py
│   │   ├── nodes/
│   │   ├── workflows/                # return, refund, delivery
│   │   └── prompts/
│   │
│   ├── tools/                        # functions the LLM can call
│   │   ├── registry.py
│   │   ├── customer_tools.py
│   │   ├── order_tools.py
│   │   ├── shipment_tools.py
│   │   ├── knowledge_tools.py
│   │   └── memory_tools.py
│   │
│   ├── memory/                       # memory system
│   │   ├── short_term.py
│   │   ├── episodic.py               # pgvector
│   │   ├── profile.py
│   │   └── consolidation.py
│   │
│   ├── retrieval/                    # knowledge base (Qdrant)
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── hybrid_search.py
│   │   └── ingest.py
│   │
│   ├── services/                     # business rules, no HTTP or SQL
│   │   ├── order_service.py
│   │   ├── refund_service.py
│   │   └── escalation_service.py
│   │
│   ├── db/
│   │   ├── session.py
│   │   ├── models.py                 # table definitions
│   │   └── repositories/
│   │
│   ├── clients/                      # swappable external adapters
│   │   ├── llm.py
│   │   ├── qdrant.py
│   │   └── supabase.py
│   │
│   ├── observability/                # Langfuse, logging, PII masking
│   │   ├── tracing.py
│   │   ├── logging.py
│   │   └── pii.py
│   │
│   └── core/                         # exceptions, security, constants
│
├── migrations/                       # versioned SQL / Alembic
│   ├── 0001_create_crm_tables.sql
│   └── 0002_enable_pgvector_memories.sql
│
├── data/
│   ├── seed/crm/                     # synthetic customers, orders, shipments
│   └── kb/
│       ├── faq/
│       └── policy/
│
├── scripts/                          # seed_data.py, ingest_kb.py
├── evals/                            # golden dataset, judges, runner
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
├── docs/
│   ├── adr/                          # architecture decision records
│   ├── architecture.md
│   └── runbook.md
└── report/document.md