-- ============================================================================
-- File:        insert_data_crm.sql
-- Description: Populates relational sample data across all 10 e-commerce
--              CRM, catalog, order fulfillment, payment, and support tables.
-- Tables:      customers, categories, products, orders, order_items,
--              payments, shipments, support_tickets, ticket_messages,
--              return_requests
-- Dialect:     PostgreSQL
-- ============================================================================


-- 1. CUSTOMERS
INSERT INTO customers
(customer_id, full_name, email, phone, address, city, country)
VALUES
('10000000-0000-0000-0000-000000000001', 'John Silva', 'john@gmail.com', '0771234567', '12 Main Street', 'Colombo', 'Sri Lanka'),
('10000000-0000-0000-0000-000000000002', 'Sarah Perera', 'sarah@gmail.com', '0711234567', '25 Lake Road', 'Kandy', 'Sri Lanka'),
('10000000-0000-0000-0000-000000000003', 'David Fernando', 'david@gmail.com', '0751234567', '45 Temple Road', 'Galle', 'Sri Lanka'),
('10000000-0000-0000-0000-000000000004', 'Emma Jayasuriya', 'emma@gmail.com', '0761234567', '18 Park Road', 'Kurunegala', 'Sri Lanka'),
('10000000-0000-0000-0000-000000000005', 'Michael Silva', 'michael@gmail.com', '0721234567', '90 Beach Road', 'Negombo', 'Sri Lanka');

-- 2. CATEGORIES
INSERT INTO categories
(category_id, category_name, description)
VALUES
('20000000-0000-0000-0000-000000000001', 'Electronics', 'Electronic devices'),
('20000000-0000-0000-0000-000000000002', 'Mobile Phones', 'Smartphones and mobile devices'),
('20000000-0000-0000-0000-000000000003', 'Accessories', 'Computer and mobile accessories'),
('20000000-0000-0000-0000-000000000004', 'Laptops', 'Laptop computers'),
('20000000-0000-0000-0000-000000000005', 'Home Appliances', 'Household electronic appliances');

-- 3. PRODUCTS
INSERT INTO products
(product_id, category_id, product_name, description, sku, price, stock_quantity)
VALUES
('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002', 'Samsung Galaxy S24', 'Samsung smartphone 256GB', 'SAM-S24-001', 250000.00, 15),
('30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004', 'Dell Inspiron 15', 'Dell laptop 16GB RAM', 'DEL-IN15-001', 320000.00, 8),
('30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000003', 'Logitech Wireless Mouse', 'Wireless computer mouse', 'LOG-MOU-001', 8500.00, 50),
('30000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000003', 'Mechanical Keyboard', 'RGB mechanical keyboard', 'KEY-RGB-001', 15000.00, 25),
('30000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000005', 'Samsung Microwave', 'Digital microwave oven', 'SAM-MIC-001', 45000.00, 12);

-- 4. ORDERS
INSERT INTO orders
(order_id, customer_id, order_number, order_status, total_amount, shipping_address)
VALUES
('40000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'ORD-1001', 'delivered', 258500.00, '12 Main Street, Colombo'),
('40000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', 'ORD-1002', 'shipped', 320000.00, '25 Lake Road, Kandy'),
('40000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', 'ORD-1003', 'processing', 23500.00, '45 Temple Road, Galle'),
('40000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000004', 'ORD-1004', 'confirmed', 45000.00, '18 Park Road, Kurunegala'),
('40000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000005', 'ORD-1005', 'pending', 335000.00, '90 Beach Road, Negombo');

-- 5. ORDER ITEMS
INSERT INTO order_items
(order_item_id, order_id, product_id, quantity, unit_price)
VALUES
('50000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 1, 250000.00),
('50000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000003', 1, 8500.00),
('50000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000002', 1, 320000.00),
('50000000-0000-0000-0000-000000000004', '40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000003', 1, 8500.00),
('50000000-0000-0000-0000-000000000005', '40000000-0000-0000-0000-000000000003', '30000000-0000-0000-0000-000000000004', 1, 15000.00),
('50000000-0000-0000-0000-000000000006', '40000000-0000-0000-0000-000000000004', '30000000-0000-0000-0000-000000000005', 1, 45000.00),
('50000000-0000-0000-0000-000000000007', '40000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000002', 1, 320000.00),
('50000000-0000-0000-0000-000000000008', '40000000-0000-0000-0000-000000000005', '30000000-0000-0000-0000-000000000004', 1, 15000.00);


-- 6. PAYMENTS
INSERT INTO payments
(payment_id, order_id, payment_method, transaction_reference, amount, payment_status, paid_at)
VALUES
('60000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'card', 'TXN-1001', 258500.00, 'successful', NOW() - INTERVAL '10 days'),
('60000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000002', 'bank_transfer', 'TXN-1002', 320000.00, 'successful', NOW() - INTERVAL '5 days'),
('60000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000003', 'cash_on_delivery', 'TXN-1003', 23500.00, 'pending', NULL),
('60000000-0000-0000-0000-000000000004', '40000000-0000-0000-0000-000000000004', 'card', 'TXN-1004', 45000.00, 'successful', NOW() - INTERVAL '2 days'),
('60000000-0000-0000-0000-000000000005', '40000000-0000-0000-0000-000000000005', 'card', 'TXN-1005', 335000.00, 'failed', NULL);


-- 7. SHIPMENTS
INSERT INTO shipments
(shipment_id, order_id, tracking_number, carrier_name, shipment_status, shipped_at, estimated_delivery)
VALUES
('70000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'TRK-1001', 'DHL', 'delivered', NOW() - INTERVAL '8 days', NOW() - INTERVAL '7 days'),
('70000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000002', 'TRK-1002', 'FedEx', 'in_transit', NOW() - INTERVAL '2 days', NOW() + INTERVAL '2 days'),
('70000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000003', 'TRK-1003', 'DHL', 'preparing', NULL, NOW() + INTERVAL '5 days'),
('70000000-0000-0000-0000-000000000004', '40000000-0000-0000-0000-000000000004', 'TRK-1004', 'Domex', 'preparing', NULL, NOW() + INTERVAL '4 days');


-- 8. SUPPORT TICKETS
INSERT INTO support_tickets
(ticket_id, customer_id, order_id, subject, description, ticket_category, priority, ticket_status)
VALUES
('80000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001', 'Product damaged', 'The laptop mouse arrived damaged.', 'Product complaint', 'high', 'open'),
('80000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000002', 'Delivery tracking', 'Where is my laptop delivery?', 'Order tracking', 'medium', 'in_progress'),
('80000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000003', 'Payment question', 'I want to know whether my payment was received.', 'Payment issue', 'medium', 'open'),
('80000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000004', '40000000-0000-0000-0000-000000000004', 'Product information', 'Can you explain the microwave warranty?', 'Product inquiry', 'low', 'resolved'),
('80000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000005', '40000000-0000-0000-0000-000000000005', 'Payment failed', 'My card was declined during checkout.', 'Payment issue', 'urgent', 'open');


-- 9. TICKET MESSAGES
INSERT INTO ticket_messages
(message_id, ticket_id, sender_type, message_content)
VALUES
('90000000-0000-0000-0000-000000000001', '80000000-0000-0000-0000-000000000001', 'customer', 'My mouse arrived damaged.'),
('90000000-0000-0000-0000-000000000002', '80000000-0000-0000-0000-000000000001', 'ai_agent', 'Sorry about that. We can help you with a replacement.'),
('90000000-0000-0000-0000-000000000003', '80000000-0000-0000-0000-000000000002', 'customer', 'Where is my laptop?'),
('90000000-0000-0000-0000-000000000004', '80000000-0000-0000-0000-000000000002', 'ai_agent', 'Your laptop is currently in transit.'),
('90000000-0000-0000-0000-000000000005', '80000000-0000-0000-0000-000000000003', 'customer', 'Has my payment been received?'),
('90000000-0000-0000-0000-000000000006', '80000000-0000-0000-0000-000000000003', 'ai_agent', 'Your payment is still pending.'),
('90000000-0000-0000-0000-000000000007', '80000000-0000-0000-0000-000000000004', 'customer', 'What is the microwave warranty period?'),
('90000000-0000-0000-0000-000000000008', '80000000-0000-0000-0000-000000000004', 'human_agent', 'The product has a one-year warranty.'),
('90000000-0000-0000-0000-000000000009', '80000000-0000-0000-0000-000000000005', 'customer', 'My card payment failed.'),
('90000000-0000-0000-0000-000000000010', '80000000-0000-0000-0000-000000000005', 'ai_agent', 'Please contact your bank or try another payment method.');


-- 10. RETURN REQUESTS
INSERT INTO return_requests
(return_id, order_item_id, return_reason, return_status, quantity, refund_amount)
VALUES
('A0000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002', 'Mouse arrived damaged.', 'requested', 1, 8500.00),
('A0000000-0000-0000-0000-000000000002', '50000000-0000-0000-0000-000000000006', 'Customer changed their mind.', 'approved', 1, 45000.00);


-- =====================================================
-- SAMPLE DATA INSERTION COMPLETED
-- =====================================================