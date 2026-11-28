"""
Dynamic Supabase schema generator for the e-commerce AI customer support system.

Generates PostgreSQL DDL using the shared embedding configuration. The schema
contains e-commerce CRM data, AI conversation memory, and knowledge-base
metadata. Knowledge-base embeddings are stored and searched in Qdrant Cloud.
"""

from customer_support_agent.utils.config_utils import (
    get_embedding,
    get_provider,
    get_provider_models,
)


def generate_supabase_schema() -> str:
    """
    Generate the complete Supabase PostgreSQL schema.

    Returns:
        SQL DDL string with vector dimensions taken from config/llm.yaml.
    """
    embedding_dim = get_embedding().get("dimensions", 1536)
    embedding_tier = get_embedding().get("tier", "small")
    provider = get_provider().get("default", "openrouter")
    embedding_model = (
        get_provider_models(provider).get("embedding", {}).get(embedding_tier, "")
    )

    return f"""-- ============================================================================
    -- E-commerce AI Customer Support Schema
    -- PostgreSQL + pgvector
    -- Generated from config_utils (llm.yaml / models.yaml)
    -- Embedding model: {embedding_model}
    -- Embedding dimensions: {embedding_dim}
    -- ============================================================================

    CREATE EXTENSION IF NOT EXISTS vector;

    -- ============================================================================
    -- 1. E-COMMERCE CRM (10 TABLES)
    -- ============================================================================

    -- Customers: customer profiles and contact details

    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        external_user_id TEXT UNIQUE,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE'
            CHECK (status IN ('ACTIVE', 'INACTIVE', 'BLOCKED')),
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_customers_external_user_id
        ON customers(external_user_id);
    CREATE INDEX IF NOT EXISTS idx_customers_email
        ON customers(email);


    -- Categories: product classification and optional hierarchy

    CREATE TABLE IF NOT EXISTS categories (
        category_id TEXT PRIMARY KEY,
        parent_category_id TEXT REFERENCES categories(category_id) ON DELETE SET NULL,
        name TEXT NOT NULL,
        description TEXT,
        active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_categories_parent
        ON categories(parent_category_id);
    CREATE INDEX IF NOT EXISTS idx_categories_active
        ON categories(active);


    -- Products: product catalogue

    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        category_id TEXT REFERENCES categories(category_id) ON DELETE SET NULL,
        sku TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
        currency CHAR(3) NOT NULL DEFAULT 'USD',
        stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
        status TEXT NOT NULL DEFAULT 'ACTIVE'
            CHECK (status IN ('ACTIVE', 'INACTIVE', 'OUT_OF_STOCK', 'ARCHIVED')),
        attributes JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_products_category
        ON products(category_id);
    CREATE INDEX IF NOT EXISTS idx_products_status
        ON products(status);
    CREATE INDEX IF NOT EXISTS idx_products_name
        ON products(name);

    -- Orders: customer order headers

    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
        order_number TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'PENDING'
            CHECK (status IN (
                'PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED',
                'DELIVERED', 'CANCELLED', 'RETURNED', 'REFUNDED'
            )),
        subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (subtotal >= 0),
        shipping_fee NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (shipping_fee >= 0),
        discount NUMERIC(12, 2) NOT NULL DEFAULT 0 CHECK (discount >= 0),
        total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
        currency CHAR(3) NOT NULL DEFAULT 'USD',
        shipping_address JSONB,
        billing_address JSONB,
        notes TEXT,
        ordered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_orders_customer
        ON orders(customer_id);
    CREATE INDEX IF NOT EXISTS idx_orders_status
        ON orders(status);
    CREATE INDEX IF NOT EXISTS idx_orders_ordered_at
        ON orders(ordered_at DESC);


    -- Order items: individual products within an order

    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
        product_id TEXT REFERENCES products(product_id) ON DELETE SET NULL,
        product_name TEXT NOT NULL,
        sku TEXT,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
        line_total NUMERIC(12, 2) NOT NULL CHECK (line_total >= 0),
        product_snapshot JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_order_items_order
        ON order_items(order_id);
    CREATE INDEX IF NOT EXISTS idx_order_items_product
        ON order_items(product_id);
    

    -- Payments: payment attempts and transaction records

    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE RESTRICT,
        provider TEXT,
        provider_transaction_id TEXT UNIQUE,
        method TEXT NOT NULL
            CHECK (method IN ('CARD', 'BANK_TRANSFER', 'CASH_ON_DELIVERY', 'WALLET', 'OTHER')),
        status TEXT NOT NULL DEFAULT 'PENDING'
            CHECK (status IN ('PENDING', 'AUTHORIZED', 'CAPTURED', 'FAILED', 'REFUNDED', 'PARTIALLY_REFUNDED')),
        amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
        currency CHAR(3) NOT NULL DEFAULT 'USD',
        paid_at TIMESTAMPTZ,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_payments_order
        ON payments(order_id);
    CREATE INDEX IF NOT EXISTS idx_payments_status
        ON payments(status);

    -- Shipments: fulfilment and delivery tracking

    CREATE TABLE IF NOT EXISTS shipments (
        shipment_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
        carrier TEXT,
        tracking_number TEXT UNIQUE,
        status TEXT NOT NULL DEFAULT 'PENDING'
            CHECK (status IN (
                'PENDING', 'PACKED', 'SHIPPED', 'IN_TRANSIT',
                'OUT_FOR_DELIVERY', 'DELIVERED', 'FAILED', 'RETURNED'
            )),
        shipped_at TIMESTAMPTZ,
        estimated_delivery_at TIMESTAMPTZ,
        delivered_at TIMESTAMPTZ,
        tracking_url TEXT,
        delivery_address JSONB,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_shipments_order
        ON shipments(order_id);
    CREATE INDEX IF NOT EXISTS idx_shipments_status
        ON shipments(status);
    CREATE INDEX IF NOT EXISTS idx_shipments_tracking
        ON shipments(tracking_number);


    -- Support tickets: customer support cases


    CREATE TABLE IF NOT EXISTS support_tickets (
        ticket_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
        order_id TEXT REFERENCES orders(order_id) ON DELETE SET NULL,
        subject TEXT NOT NULL,
        description TEXT,
        category TEXT,
        priority TEXT NOT NULL DEFAULT 'NORMAL'
            CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')),
        status TEXT NOT NULL DEFAULT 'OPEN'
            CHECK (status IN ('OPEN', 'IN_PROGRESS', 'WAITING_FOR_CUSTOMER', 'RESOLVED', 'CLOSED')),
        assigned_to TEXT,
        source TEXT NOT NULL DEFAULT 'AI_AGENT'
            CHECK (source IN ('AI_AGENT', 'HUMAN_AGENT', 'EMAIL', 'WEB', 'PHONE', 'OTHER')),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        resolved_at TIMESTAMPTZ
    );

    CREATE INDEX IF NOT EXISTS idx_support_tickets_customer
        ON support_tickets(customer_id);
    CREATE INDEX IF NOT EXISTS idx_support_tickets_order
        ON support_tickets(order_id);
    CREATE INDEX IF NOT EXISTS idx_support_tickets_status
        ON support_tickets(status);
    CREATE INDEX IF NOT EXISTS idx_support_tickets_priority
        ON support_tickets(priority);


    -- Ticket messages: messages exchanged within a support ticket


    CREATE TABLE IF NOT EXISTS ticket_messages (
        message_id TEXT PRIMARY KEY,
        ticket_id TEXT NOT NULL REFERENCES support_tickets(ticket_id) ON DELETE CASCADE,
        sender_type TEXT NOT NULL
            CHECK (sender_type IN ('CUSTOMER', 'AI_AGENT', 'HUMAN_AGENT', 'SYSTEM')),
        sender_id TEXT,
        content TEXT NOT NULL,
        attachments JSONB NOT NULL DEFAULT '[]'::jsonb,
        is_internal BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket
        ON ticket_messages(ticket_id, created_at);
    

    -- Return requests: product return and refund requests


    CREATE TABLE IF NOT EXISTS return_requests (
        return_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
        order_id TEXT NOT NULL REFERENCES orders(order_id) ON DELETE RESTRICT,
        order_item_id TEXT REFERENCES order_items(order_item_id) ON DELETE SET NULL,
        reason TEXT NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
        status TEXT NOT NULL DEFAULT 'REQUESTED'
            CHECK (status IN (
                'REQUESTED', 'APPROVED', 'REJECTED', 'ITEM_RECEIVED',
                'REFUND_PENDING', 'REFUNDED', 'EXCHANGED', 'CANCELLED'
            )),
        resolution TEXT,
        refund_amount NUMERIC(12, 2) CHECK (refund_amount >= 0),
        requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        resolved_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_return_requests_customer
        ON return_requests(customer_id);
    CREATE INDEX IF NOT EXISTS idx_return_requests_order
        ON return_requests(order_id);
    CREATE INDEX IF NOT EXISTS idx_return_requests_status
        ON return_requests(status);


    -- ============================================================================
    -- 2. AI CONVERSATION MEMORY (5 TABLES)
    -- ============================================================================

    -- Conversations: one record for each customer support conversation/session

    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id TEXT NOT NULL,
        customer_id TEXT REFERENCES customers(customer_id) ON DELETE SET NULL,
        session_id TEXT NOT NULL UNIQUE,
        channel TEXT NOT NULL DEFAULT 'WEB'
            CHECK (channel IN ('WEB', 'MOBILE', 'EMAIL', 'WHATSAPP', 'OTHER')),
        status TEXT NOT NULL DEFAULT 'ACTIVE'
            CHECK (status IN ('ACTIVE', 'COMPLETED', 'ESCALATED', 'ARCHIVED')),
        started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        ended_at TIMESTAMPTZ,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_conversations_user
        ON conversations(user_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_customer
        ON conversations(customer_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_started_at
        ON conversations(started_at DESC);    

    -- Short-term memory: individual conversation turns/messages

    CREATE TABLE IF NOT EXISTS st_turns (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id TEXT NOT NULL,
        session_id TEXT NOT NULL REFERENCES conversations(session_id) ON DELETE CASCADE,
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
        content TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        ttl_at TIMESTAMPTZ
    );

    CREATE INDEX IF NOT EXISTS idx_st_turns_user_session
        ON st_turns(user_id, session_id, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_st_turns_ttl
        ON st_turns(ttl_at) WHERE ttl_at IS NOT NULL;

    -- Semantic memory: durable facts and customer preferences

    CREATE TABLE IF NOT EXISTS mem_facts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id TEXT NOT NULL,
        text TEXT NOT NULL,
        embedding vector({embedding_dim}),
        score REAL NOT NULL CHECK (score >= 0 AND score <= 1),
        tags JSONB NOT NULL DEFAULT '[]'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        last_used_at TIMESTAMPTZ DEFAULT NOW(),
        ttl_at TIMESTAMPTZ,
        pin BOOLEAN NOT NULL DEFAULT FALSE,
        deleted BOOLEAN NOT NULL DEFAULT FALSE
    );

    CREATE INDEX IF NOT EXISTS idx_mem_facts_user_id
        ON mem_facts(user_id);
    CREATE INDEX IF NOT EXISTS idx_mem_facts_score
        ON mem_facts(score DESC);
    CREATE INDEX IF NOT EXISTS idx_mem_facts_deleted
        ON mem_facts(deleted) WHERE deleted = FALSE;
    CREATE INDEX IF NOT EXISTS idx_mem_facts_ttl
        ON mem_facts(ttl_at) WHERE ttl_at IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_mem_facts_embedding
        ON mem_facts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

    -- Episodic memory: summaries and transcripts of previous conversations

    CREATE TABLE IF NOT EXISTS mem_episodes (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        summary TEXT NOT NULL,
        summary_embedding vector({embedding_dim}),
        topic_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
        start_at TIMESTAMPTZ NOT NULL,
        end_at TIMESTAMPTZ NOT NULL,
        turn_count INTEGER NOT NULL CHECK (turn_count > 0),
        turns JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_mem_episodes_user_id
        ON mem_episodes(user_id);
    CREATE INDEX IF NOT EXISTS idx_mem_episodes_session_id
        ON mem_episodes(session_id);
    CREATE INDEX IF NOT EXISTS idx_mem_episodes_start_at
        ON mem_episodes(start_at DESC);
    CREATE INDEX IF NOT EXISTS idx_mem_episodes_created_at
        ON mem_episodes(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_mem_episodes_embedding
        ON mem_episodes USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);

    -- Procedural memory: reusable agent workflows and task instructions

    CREATE TABLE IF NOT EXISTS mem_procedures (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL,
        context_when TEXT,
        steps JSONB NOT NULL,
        conditions JSONB,
        examples JSONB,
        embedding vector({embedding_dim}),
        category TEXT,
        active BOOLEAN NOT NULL DEFAULT TRUE,
        version INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_mem_procedures_name
        ON mem_procedures(name);
    CREATE INDEX IF NOT EXISTS idx_mem_procedures_category
        ON mem_procedures(category);
    CREATE INDEX IF NOT EXISTS idx_mem_procedures_active
        ON mem_procedures(active) WHERE active = TRUE;
    CREATE INDEX IF NOT EXISTS idx_mem_procedures_embedding
        ON mem_procedures USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);


    -- ============================================================================
    -- 3. KNOWLEDGE BASE METADATA (2 TABLES)
    -- Knowledge document embeddings are stored/retrieved in Qdrant Cloud.
    -- Supabase stores document/chunk metadata and Qdrant point references.
    -- ============================================================================

    CREATE TABLE IF NOT EXISTS kb_documents (
        document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        source TEXT,
        source_type TEXT NOT NULL DEFAULT 'OTHER'
            CHECK (source_type IN ('PDF', 'HTML', 'DOCX', 'MARKDOWN', 'CSV', 'OTHER')),
        description TEXT,
        status TEXT NOT NULL DEFAULT 'ACTIVE'
            CHECK (status IN ('PROCESSING', 'ACTIVE', 'FAILED', 'ARCHIVED')),
        version INTEGER NOT NULL DEFAULT 1,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_kb_documents_status
        ON kb_documents(status);
    CREATE INDEX IF NOT EXISTS idx_kb_documents_source_type
        ON kb_documents(source_type);


    CREATE TABLE IF NOT EXISTS kb_chunks (
        chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        document_id UUID NOT NULL REFERENCES kb_documents(document_id) ON DELETE CASCADE,
        chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
        content TEXT NOT NULL,
        qdrant_point_id TEXT UNIQUE,
        token_count INTEGER,
        metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (document_id, chunk_index)
    );

    CREATE INDEX IF NOT EXISTS idx_kb_chunks_document
        ON kb_chunks(document_id);

    -- ============================================================================
    -- 4. SEMANTIC SEARCH FUNCTIONS
    -- ============================================================================

    CREATE OR REPLACE FUNCTION search_mem_facts(
    query_embedding vector({embedding_dim}),
    query_user_id TEXT,
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 10
    )
    RETURNS TABLE (
        id UUID,
        user_id TEXT,
        text TEXT,
        score REAL,
        tags JSONB,
        similarity FLOAT
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            f.id,
            f.user_id,
            f.text,
            f.score,
            f.tags,
            1 - (f.embedding <=> query_embedding) AS similarity
        FROM mem_facts AS f
        WHERE f.user_id = query_user_id
          AND f.deleted = FALSE
          AND (f.ttl_at IS NULL OR f.ttl_at > NOW())
          AND f.embedding IS NOT NULL
          AND 1 - (f.embedding <=> query_embedding) >= match_threshold
        ORDER BY f.embedding <=> query_embedding
        LIMIT match_count;
    END;
    $$;

    CREATE OR REPLACE FUNCTION search_mem_episodes(
    query_embedding vector({embedding_dim}),
    query_user_id TEXT,
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 10
    )
    RETURNS TABLE (
        id UUID,
        user_id TEXT,
        session_id TEXT,
        summary TEXT,
        topic_tags JSONB,
        start_at TIMESTAMPTZ,
        end_at TIMESTAMPTZ,
        turn_count INTEGER,
        similarity FLOAT
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            e.id,
            e.user_id,
            e.session_id,
            e.summary,
            e.topic_tags,
            e.start_at,
            e.end_at,
            e.turn_count,
            1 - (e.summary_embedding <=> query_embedding) AS similarity
        FROM mem_episodes AS e
        WHERE e.user_id = query_user_id
          AND e.summary_embedding IS NOT NULL
          AND 1 - (e.summary_embedding <=> query_embedding) >= match_threshold
        ORDER BY e.summary_embedding <=> query_embedding
        LIMIT match_count;
    END;
    $$;

    -- ============================================================================
    -- 5. ROW LEVEL SECURITY
    -- The application must set app.user_id from a verified authenticated identity
    -- on the SAME database connection/transaction as each protected query.
    -- This custom setting is not authentication by itself.
    -- ============================================================================

    ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
    ALTER TABLE st_turns ENABLE ROW LEVEL SECURITY;
    ALTER TABLE mem_facts ENABLE ROW LEVEL SECURITY;
    ALTER TABLE mem_episodes ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "Users can access their conversations" ON conversations;
    CREATE POLICY "Users can access their conversations"
    ON conversations FOR ALL
    USING (user_id = current_setting('app.user_id', TRUE))
    WITH CHECK (user_id = current_setting('app.user_id', TRUE));

    DROP POLICY IF EXISTS "Users can access their short-term turns" ON st_turns;
    CREATE POLICY "Users can access their short-term turns"
    ON st_turns FOR ALL
    USING (user_id = current_setting('app.user_id', TRUE))
    WITH CHECK (user_id = current_setting('app.user_id', TRUE));

    DROP POLICY IF EXISTS "Users can access their own facts" ON mem_facts;
    CREATE POLICY "Users can access their own facts"
    ON mem_facts FOR ALL
    USING (user_id = current_setting('app.user_id', TRUE))
    WITH CHECK (user_id = current_setting('app.user_id', TRUE));

    DROP POLICY IF EXISTS "Users can access their own episodes" ON mem_episodes;
    CREATE POLICY "Users can access their own episodes"
    ON mem_episodes FOR ALL
    USING (user_id = current_setting('app.user_id', TRUE))
    WITH CHECK (user_id = current_setting('app.user_id', TRUE));


    -- CRM and knowledge-base RLS policies must be added according to the final
    -- authentication model and whether records are customer-owned or public.
    -- Do not expose service-role credentials to a browser or mobile application.

    -- ============================================================================
    -- 6. ANALYTICS VIEWS
    -- ============================================================================


    CREATE OR REPLACE VIEW v_active_facts AS
    SELECT
        user_id,
        COUNT(*) AS total_facts,
        AVG(score) AS avg_score,
        COUNT(*) FILTER (WHERE pin = TRUE) AS pinned_facts
    FROM mem_facts
    WHERE deleted = FALSE
      AND (ttl_at IS NULL OR ttl_at > NOW())
    GROUP BY user_id;

    CREATE OR REPLACE VIEW v_episode_stats AS
    SELECT
        user_id,
        COUNT(*) AS total_episodes,
        SUM(turn_count) AS total_turns,
        AVG(turn_count) AS avg_turns_per_episode,
        MAX(created_at) AS last_episode_at
    FROM mem_episodes
    GROUP BY user_id;

    CREATE OR REPLACE VIEW v_customer_order_summary AS
    SELECT
        c.customer_id,
        c.full_name,
        COUNT(o.order_id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS lifetime_order_value,
        MAX(o.ordered_at) AS last_order_at
    FROM customers AS c
    LEFT JOIN orders AS o ON o.customer_id = c.customer_id
    GROUP BY c.customer_id, c.full_name;

    -- ============================================================================
    -- 7. DATABASE OBJECT DOCUMENTATION
    -- ============================================================================

    COMMENT ON TABLE customers IS 'Customer profiles for the e-commerce platform';
    COMMENT ON TABLE categories IS 'Product category hierarchy';
    COMMENT ON TABLE products IS 'E-commerce product catalogue';
    COMMENT ON TABLE orders IS 'Customer order headers and totals';
    COMMENT ON TABLE order_items IS 'Products and quantities belonging to orders';
    COMMENT ON TABLE payments IS 'Payment transactions and payment status';
    COMMENT ON TABLE shipments IS 'Shipment tracking and delivery information';
    COMMENT ON TABLE support_tickets IS 'Customer support cases';
    COMMENT ON TABLE ticket_messages IS 'Messages exchanged within support tickets';
    COMMENT ON TABLE return_requests IS 'Product return and refund requests';

    COMMENT ON TABLE conversations IS 'Customer support conversation/session records';
    COMMENT ON TABLE st_turns IS 'Short-term conversation messages with optional TTL';
    COMMENT ON TABLE mem_facts IS 'Long-term semantic customer facts and preferences';
    COMMENT ON TABLE mem_episodes IS 'Long-term episodic memory and conversation summaries';
    COMMENT ON TABLE mem_procedures IS 'Procedural memory containing reusable agent workflows';
    COMMENT ON TABLE kb_documents IS 'Knowledge-base document metadata';
    COMMENT ON TABLE kb_chunks IS 'Knowledge-base chunk metadata and Qdrant point references';

    COMMENT ON FUNCTION search_mem_facts IS 'Semantic search over customer memory facts';
    COMMENT ON FUNCTION search_mem_episodes IS 'Semantic search over previous conversation summaries';
    COMMENT ON FUNCTION search_mem_procedures IS 'Semantic search over active agent procedures';

    -- ============================================================================
    -- 8. COMPLETION NOTICE
    -- ============================================================================

    DO $$
    BEGIN
        RAISE NOTICE 'E-commerce AI customer support schema created/verified.';
        RAISE NOTICE 'CRM tables: customers, categories, products, orders, order_items, payments, shipments, support_tickets, ticket_messages, return_requests.';
        RAISE NOTICE 'Memory tables: conversations, st_turns, mem_facts, mem_episodes, mem_procedures.';
        RAISE NOTICE 'Knowledge tables: kb_documents, kb_chunks.';
        RAISE NOTICE 'Embedding model: {embedding_model} ({embedding_dim} dimensions).';
        RAISE NOTICE 'Knowledge-base vectors are managed in Qdrant Cloud.';
    END;
    $$;
    """

if __name__ == "__main__":
    schema_sql = generate_supabase_schema()
    print(schema_sql)