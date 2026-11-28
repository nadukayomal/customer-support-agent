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


-- Delete tables 

-- 1. Ticket messages (usually references support_tickets / customers)
DROP TABLE IF EXISTS ticket_messages;

-- 2. Return requests (usually references orders / order_items / customers)
DROP TABLE IF EXISTS return_requests;

-- 3. Support tickets (usually references customers / orders)
DROP TABLE IF EXISTS support_tickets;

-- 4. Shipments (usually references orders)
DROP TABLE IF EXISTS shipments;

-- 5. Payments (usually references orders)
DROP TABLE IF EXISTS payments;

-- 6. Order items (usually references orders and products)
DROP TABLE IF EXISTS order_items;

-- 7. Orders (usually references customers)
DROP TABLE IF EXISTS orders;

-- 8. Products (usually references categories)
DROP TABLE IF EXISTS products;

-- 9. Categories (parent product category table)
DROP TABLE IF EXISTS categories;

-- 10. Customers (parent customer table)
DROP TABLE IF EXISTS customers;
