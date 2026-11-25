-- ============================================================================
-- File:        read_crm_data.sql
-- Description: Retrieves records from all CRM, e-commerce, and support tables
--              for data verification and inspection.
-- Tables:      customers, categories, products, orders, order_items,
--              payments, shipments, support_tickets, ticket_messages,
--              return_requests
-- Dialect:     PostgreSQL
-- ============================================================================

-- 1. Customers
SELECT * FROM customers;

-- 2. Categories
SELECT * FROM categories;

-- 3. Products
SELECT * FROM products;

-- 4. Orders
SELECT * FROM orders;

-- 5. Order items
SELECT * FROM order_items;

-- 6. Payments
SELECT * FROM payments;

-- 7. Shipments
SELECT * FROM shipments;

-- 8. Support tickets
SELECT * FROM support_tickets;

-- 9. Ticket messages
SELECT * FROM ticket_messages;

-- 10. Return requests
SELECT * FROM return_requests;

