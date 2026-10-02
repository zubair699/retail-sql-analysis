-- =========================================================
-- Retail Sales Analysis - SQL Queries
-- Database: retail.db (SQLite)
-- Tables: customers, products, orders, order_items, returns
-- =========================================================


-- ---------------------------------------------------------
-- 1. Top 10 products by quantity sold
-- Business question: which products move the most units?
-- ---------------------------------------------------------
SELECT p.description, SUM(oi.quantity) AS total_units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_units_sold DESC
LIMIT 10;


-- ---------------------------------------------------------
-- 2. Top 10 products by revenue
-- Business question: which products actually make the most money?
-- (Not always the same answer as query 1 - high volume doesn't
-- always mean high revenue if the item is cheap.)
-- ---------------------------------------------------------
SELECT p.description, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;


-- ---------------------------------------------------------
-- 3. Top 10 customers by total spend
-- Business question: who are our most valuable customers?
-- ---------------------------------------------------------
SELECT o.customer_id, c.country, SUM(oi.quantity * oi.unit_price) AS total_spent
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id
ORDER BY total_spent DESC
LIMIT 10;


-- ---------------------------------------------------------
-- 4. Monthly revenue trend
-- Business question: is revenue growing, shrinking, or seasonal?
-- ---------------------------------------------------------
SELECT strftime('%Y-%m', o.order_date) AS month, SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;


-- ---------------------------------------------------------
-- 5. Revenue by country
-- Business question: which markets drive the most revenue?
-- ---------------------------------------------------------
SELECT c.country, SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.country
ORDER BY revenue DESC;


-- ---------------------------------------------------------
-- 6. Average order value
-- Business question: how much does a customer spend per order, on average?
-- ---------------------------------------------------------
SELECT AVG(order_total) AS avg_order_value
FROM (
  SELECT o.order_id, SUM(oi.quantity * oi.unit_price) AS order_total
  FROM orders o
  JOIN order_items oi ON o.order_id = oi.order_id
  GROUP BY o.order_id
);


-- ---------------------------------------------------------
-- 7. Repeat customers (placed more than 1 order)
-- Business question: how loyal is our customer base?
-- ---------------------------------------------------------
SELECT customer_id, COUNT(*) AS num_orders
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY num_orders DESC
LIMIT 10;


-- ---------------------------------------------------------
-- 8. Return rate per product
-- Business question: which products get returned most often
-- relative to how much they sell? (uses the separate returns table)
-- ---------------------------------------------------------
SELECT p.description,
       SUM(r.quantity) AS total_returned,
       SUM(oi.quantity) AS total_sold,
       ROUND(100.0 * SUM(r.quantity) / SUM(oi.quantity), 2) AS return_rate_pct
FROM products p
LEFT JOIN returns r ON p.product_id = r.product_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id
HAVING total_sold > 0
ORDER BY return_rate_pct DESC
LIMIT 10;