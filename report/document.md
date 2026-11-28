# The project is building customer support AI agent.
## Objectives
- 1. Understand customer questions.
- 2. Remember previous customer interactions.
- 3. Retrieve customer and order information.
- 4. Check order and delivery status.
- 5. Answer questions about products, returns and refunds.
- 6. Handle multi-step support workflows.
- 7. Learn from previous support interactions through a structured memory system.

## Tech stack
- Supabase
- pgvector
- qdrant
- Langfuse

## Data base creation 

# E-Commerce CRM Database Documentation

## 1. Project Overview

This database is designed for an AI-powered E-commerce
Customer Support Agent.

The CRM database stores customer information, products,
orders, payments, deliveries, support requests, and returns.

**Database:** PostgreSQL
**Platform:** Supabase
**Backend:** FastAPI
**AI Framework:** LangGraph

---

## 2. CRM Tables

The database contains 10 main tables.

### 2.1 customers

**Purpose:**
Stores customer profile information.

**Attributes:**
- customer_id (UUID, PK)
- full_name (VARCHAR)
- email (VARCHAR, UNIQUE)
- phone (VARCHAR)
- address (TEXT)
- city (VARCHAR)
- country (VARCHAR)
- created_at (TIMESTAMPTZ)
- updated_at (TIMESTAMPTZ)

**Relationships:**
- One customer can have many orders.
- One customer can create many support tickets.

---

### 2.2 categories

**Purpose:**
Organizes products into different categories.

**Attributes:**
- category_id (UUID, PK)
- category_name (VARCHAR)
- description (TEXT)
- parent_category_id (UUID, FK)
- created_at (TIMESTAMPTZ)

**Relationships:**
- One category can contain many products.
- One category can have multiple subcategories.

---

### 2.3 products

**Purpose:**
Stores product details, prices, and stock information.

**Attributes:**
- product_id (UUID, PK)
- category_id (UUID, FK)
- product_name (VARCHAR)
- description (TEXT)
- sku (VARCHAR, UNIQUE)
- price (NUMERIC)
- stock_quantity (INTEGER)
- is_active (BOOLEAN)
- created_at (TIMESTAMPTZ)
- updated_at (TIMESTAMPTZ)

**Relationships:**
- Many products belong to one category.
- One product can appear in many order items.

---

### 2.4 orders

**Purpose:**
Stores customer purchase orders and order information.

**Attributes:**
- order_id (UUID, PK)
- customer_id (UUID, FK)
- order_number (VARCHAR, UNIQUE)
- order_status (VARCHAR)
- total_amount (NUMERIC)
- shipping_address (TEXT)
- order_date (TIMESTAMPTZ)
- updated_at (TIMESTAMPTZ)

**Relationships:**
- Many orders belong to one customer.
- One order can contain many order items.
- One order can have multiple payments.
- One order can have multiple shipments.
- One order can be linked to multiple support tickets.

---

### 2.5 order_items

**Purpose:**
Stores individual products included in each order.

**Attributes:**
- order_item_id (UUID, PK)
- order_id (UUID, FK)
- product_id (UUID, FK)
- quantity (INTEGER)
- unit_price (NUMERIC)
- subtotal (NUMERIC, GENERATED)

**Relationships:**
- Many order items belong to one order.
- Many order items can reference one product.
- One order item can have multiple return requests.

---

### 2.6 payments

**Purpose:**
Stores payment transactions and payment statuses.

**Attributes:**
- payment_id (UUID, PK)
- order_id (UUID, FK)
- payment_method (VARCHAR)
- transaction_reference (VARCHAR, UNIQUE)
- amount (NUMERIC)
- payment_status (VARCHAR)
- paid_at (TIMESTAMPTZ)
- created_at (TIMESTAMPTZ)

**Relationships:**
- Many payment transactions can belong to one order.

---

### 2.7 shipments

**Purpose:**
Stores delivery information and shipment tracking details.

**Attributes:**
- shipment_id (UUID, PK)
- order_id (UUID, FK)
- tracking_number (VARCHAR, UNIQUE)
- carrier_name (VARCHAR)
- shipment_status (VARCHAR)
- shipped_at (TIMESTAMPTZ)
- estimated_delivery (TIMESTAMPTZ)
- delivered_at (TIMESTAMPTZ)
- created_at (TIMESTAMPTZ)

**Relationships:**
- Multiple shipments can belong to one order.

---

### 2.8 support_tickets

**Purpose:**
Stores customer complaints, questions, and support requests.

**Attributes:**
- ticket_id (UUID, PK)
- customer_id (UUID, FK)
- order_id (UUID, FK, NULLABLE)
- subject (VARCHAR)
- description (TEXT)
- ticket_category (VARCHAR)
- priority (VARCHAR)
- ticket_status (VARCHAR)
- assigned_to (UUID, NULLABLE)
- created_at (TIMESTAMPTZ)
- updated_at (TIMESTAMPTZ)

**Relationships:**
- Many support tickets can belong to one customer.
- One support ticket can contain many messages.
- A support ticket can optionally relate to an order.

---

### 2.9 ticket_messages

**Purpose:**
Stores messages exchanged between customers,
AI agents, human agents, and the support system.

**Attributes:**
- message_id (UUID, PK)
- ticket_id (UUID, FK)
- sender_type (VARCHAR)
- sender_id (UUID, NULLABLE)
- message_content (TEXT)
- created_at (TIMESTAMPTZ)

**Relationships:**
- Many messages belong to one support ticket.

---

### 2.10 return_requests

**Purpose:**
Stores product return requests and refund information.

**Attributes:**
- return_id (UUID, PK)
- order_item_id (UUID, FK)
- return_reason (TEXT)
- return_status (VARCHAR)
- quantity (INTEGER)
- refund_amount (NUMERIC)
- requested_at (TIMESTAMPTZ)
- resolved_at (TIMESTAMPTZ)

**Relationships:**
- Many return requests can reference one order item.

---

## 3. Database Relationships Summary

| Parent Table | Child Table | Relationship |
|---|---|---|
| customers | orders | One-to-Many |
| customers | support_tickets | One-to-Many |
| categories | products | One-to-Many |
| categories | categories | One-to-Many |
| orders | order_items | One-to-Many |
| products | order_items | One-to-Many |
| orders | payments | One-to-Many |
| orders | shipments | One-to-Many |
| orders | support_tickets | One-to-Many |
| support_tickets | ticket_messages | One-to-Many |
| order_items | return_requests | One-to-Many |

---

## 4. Database Design Concepts

### Primary Keys (PK)
Uniquely identify each record in a table.

Example: customer_id.

### Foreign Keys (FK)
Connect one table to another table.

Example: customer_id in the orders table references
customer_id in the customers table.

### UUID
Universally Unique Identifier used as the primary key
for database records.

### TIMESTAMPTZ
Stores date and time information with timezone awareness.

### NUMERIC
Stores accurate decimal values, especially prices and
financial transactions.

### Indexes
Improve query performance when searching and joining tables.

---

## 5. How the CRM Supports the AI Agent

The AI Customer Support Agent uses CRM information
to answer customer questions.

Examples:

1. Customer identification:
   Retrieve customer information from customers.

2. Order tracking:
   Retrieve orders, order_items, and shipments.

3. Payment assistance:
   Check payment information from payments.

4. Product inquiries:
   Retrieve product details from products.

5. Customer complaints:
   Create and manage support_tickets.

6. Conversation history:
   Retrieve messages from ticket_messages.

7. Return assistance:
   Check return_requests and related order_items.

---

## 6. Technology Stack

- Database: PostgreSQL
- Database Platform: Supabase
- Vector Search: pgvector
- Backend API: FastAPI
- Agent Orchestration: LangGraph
- AI Memory: PostgreSQL + pgvector

---

## 7. Conclusion

The CRM database provides structured storage for
e-commerce business information.

It allows the AI Customer Support Agent to retrieve
customer details, understand order history, check
payments, track deliveries, and manage customer issues.

The CRM database works alongside the AI Memory database
to provide context-aware and personalized customer support.

