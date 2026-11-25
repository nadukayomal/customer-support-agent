-- ============================================================================
-- File:        create_crm_table.sql
-- Description: Defines the PostgreSQL relational schema, foreign-key
--              constraints, check constraints, performance indexes, and
--              automatic updated_at triggers for an e-commerce CRM system.
-- Tables:      customers, categories, products, orders, order_items,
--              payments, shipments, support_tickets, ticket_messages,
--              return_requests
-- Dialect:     PostgreSQL
-- ============================================================================

-- 1. CUSTOMERS

CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. CATEGORIES
CREATE TABLE IF NOT EXISTS categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id UUID REFERENCES categories(category_id)
        ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- 3. PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES categories(category_id)
        ON DELETE SET NULL,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0
        CHECK (stock_quantity >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- 4. ORDERS
CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id)
        ON DELETE RESTRICT,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    order_status VARCHAR(30) NOT NULL DEFAULT 'pending'
        CHECK (order_status IN (
            'pending',
            'confirmed',
            'processing',
            'shipped',
            'delivered',
            'cancelled'
        )),
    total_amount NUMERIC(12,2) NOT NULL DEFAULT 0
        CHECK (total_amount >= 0),
    shipping_address TEXT NOT NULL,
    order_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- 5. ORDER ITEMS
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(order_id)
        ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id)
        ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    subtotal NUMERIC(12,2)
        GENERATED ALWAYS AS (quantity * unit_price) STORED
);


-- 6. PAYMENTS
CREATE TABLE IF NOT EXISTS payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(order_id)
        ON DELETE RESTRICT,
    payment_method VARCHAR(50) NOT NULL,
    transaction_reference VARCHAR(150) UNIQUE,
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    payment_status VARCHAR(30) NOT NULL DEFAULT 'pending'
        CHECK (payment_status IN (
            'pending',
            'successful',
            'failed',
            'refunded'
        )),
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- 7. SHIPMENTS
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(order_id)
        ON DELETE RESTRICT,
    tracking_number VARCHAR(100) UNIQUE,
    carrier_name VARCHAR(100),
    shipment_status VARCHAR(30) NOT NULL DEFAULT 'preparing'
        CHECK (shipment_status IN (
            'preparing',
            'shipped',
            'in_transit',
            'out_for_delivery',
            'delivered',
            'failed'
        )),
    shipped_at TIMESTAMPTZ,
    estimated_delivery TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- 8. SUPPORT TICKETS
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id)
        ON DELETE RESTRICT,
    order_id UUID REFERENCES orders(order_id)
        ON DELETE SET NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT,
    ticket_category VARCHAR(100),
    priority VARCHAR(20) NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    ticket_status VARCHAR(30) NOT NULL DEFAULT 'open'
        CHECK (ticket_status IN (
            'open',
            'in_progress',
            'waiting_for_customer',
            'resolved',
            'closed'
        )),
    assigned_to UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- 9. TICKET MESSAGES
CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES support_tickets(ticket_id)
        ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL
        CHECK (sender_type IN (
            'customer',
            'ai_agent',
            'human_agent',
            'system'
        )),
    sender_id UUID,
    message_content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- 10. RETURN REQUESTS
CREATE TABLE IF NOT EXISTS return_requests (
    return_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_item_id UUID NOT NULL REFERENCES order_items(order_item_id)
        ON DELETE RESTRICT,
    return_reason TEXT NOT NULL,
    return_status VARCHAR(30) NOT NULL DEFAULT 'requested'
        CHECK (return_status IN (
            'requested',
            'approved',
            'rejected',
            'received',
            'refunded',
            'completed'
        )),
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    refund_amount NUMERIC(12,2) NOT NULL DEFAULT 0
        CHECK (refund_amount >= 0),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);


-- =====================================================
-- INDEXES FOR BETTER QUERY PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_orders_customer
    ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product
    ON order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_products_category
    ON products(category_id);

CREATE INDEX IF NOT EXISTS idx_categories_parent
    ON categories(parent_category_id);

CREATE INDEX IF NOT EXISTS idx_payments_order
    ON payments(order_id);

CREATE INDEX IF NOT EXISTS idx_shipments_order
    ON shipments(order_id);

CREATE INDEX IF NOT EXISTS idx_tickets_customer
    ON support_tickets(customer_id);

CREATE INDEX IF NOT EXISTS idx_tickets_order
    ON support_tickets(order_id);

CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket
    ON ticket_messages(ticket_id);

CREATE INDEX IF NOT EXISTS idx_returns_order_item
    ON return_requests(order_item_id);


-- =====================================================
-- AUTOMATIC UPDATED_AT TRIGGER
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_customers_updated_at ON customers;
CREATE TRIGGER trg_customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_products_updated_at ON products;
CREATE TRIGGER trg_products_updated_at
BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_orders_updated_at ON orders;
CREATE TRIGGER trg_orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_tickets_updated_at ON support_tickets;
CREATE TRIGGER trg_tickets_updated_at
BEFORE UPDATE ON support_tickets
FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- =====================================================
-- CRM TABLE CREATION COMPLETED
-- =====================================================