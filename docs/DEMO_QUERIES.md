# Practice SQL queries for the demo

A graded set of SQL queries to run in **SQLTools** during the defense — grouped from
easy to impressive, all matched to this project's tables. For each: the plain
question an examiner might ask → the query → what it returns.

> **How to run:** paste a query into the SQLTools SQL editor, then click
> **"Run on active connection"** (or press `Ctrl+E` `Ctrl+E`). Results appear in a grid
> on the right; use **EXPORT** to save them to a file.
> **Reminder:** start MySQL first (double-click `start_mysql.bat`), or SQLTools can't connect.

---

## 🟢 Basic — viewing & filtering

**"Show me all your products."**
```sql
SELECT * FROM products;
```

**"List products from most to least stock."**
```sql
SELECT name, current_stock FROM products ORDER BY current_stock DESC;
```

**"Which products need reordering?"**
```sql
SELECT name, current_stock, reorder_point
FROM products WHERE current_stock <= reorder_point;
```

**"Find a specific product (e.g. Milo)."**
```sql
SELECT * FROM products WHERE name LIKE '%Milo%';
```

**"How many products do you have?"**
```sql
SELECT COUNT(*) AS total_products FROM products;
```

---

## 🟡 Aggregations — totals & summaries

**"What's your total sales revenue?"**
```sql
SELECT SUM(total) AS total_revenue FROM sales;
```

**"What's the total value of stock on hand?"**
```sql
SELECT SUM(current_stock * cost_price) AS stock_value FROM products;
```

**"How many units were sold each day recently?"**
```sql
SELECT sale_date, SUM(quantity) AS units_sold
FROM sales GROUP BY sale_date ORDER BY sale_date DESC LIMIT 10;
```

**"How many products are in each category?"**
```sql
SELECT c.name AS category, COUNT(p.id) AS products
FROM categories c LEFT JOIN products p ON p.category_id = c.id
GROUP BY c.name;
```

---

## 🔵 Joins — combining tables (this impresses examiners)

**"What are your top 5 best-selling products?"** *(joins sales + products)*
```sql
SELECT p.name, SUM(s.quantity) AS units_sold
FROM sales s JOIN products p ON p.id = s.product_id
GROUP BY p.name ORDER BY units_sold DESC LIMIT 5;
```

**"Show each product with its supplier."** *(joins products + suppliers)*
```sql
SELECT p.name AS product, s.name AS supplier
FROM products p LEFT JOIN suppliers s ON s.id = p.supplier_id;
```

**"Show each product with its category."**
```sql
SELECT p.name AS product, c.name AS category
FROM products p LEFT JOIN categories c ON c.id = p.category_id;
```

---

## 🟣 The intelligent side — your AI data

**"Show your forecast accuracy per product."** *(the MAPE/MAE from the report)*
```sql
SELECT p.name, m.mape, m.mae, m.rmse
FROM forecast_metrics m JOIN products p ON p.id = m.product_id
ORDER BY m.mape;
```

**"Show the anomalies the system detected."**
```sql
SELECT p.name, a.flag_date, a.reason, a.quantity, a.expected
FROM anomaly_flags a JOIN products p ON p.id = a.product_id
ORDER BY a.flag_date DESC LIMIT 10;
```

**"Show the audit trail — who did what."**
```sql
SELECT u.name, a.action, a.description, a.created_at
FROM audit_logs a JOIN users u ON u.id = a.user_id
ORDER BY a.created_at DESC LIMIT 10;
```

---

## ⚠️ Queries that CHANGE data (know them, use carefully)

Examiners sometimes ask "can you add or update a record with SQL?" These **modify**
the database, so only run them if asked (they alter your demo data). To undo test
changes afterwards, you can re-load the sample data with
`python seed.py` → `generate_sales.py` → `train_models.py`.

```sql
-- add a category
INSERT INTO categories (name) VALUES ('Test Category');

-- update a product's stock
UPDATE products SET current_stock = 500 WHERE name = 'Milo Tin 400g';

-- delete the test category again
DELETE FROM categories WHERE name = 'Test Category';
```

---

## Quick cheatsheet

| Keyword | Plain meaning |
|---------|---------------|
| `SELECT … FROM …` | "Show me these columns from this table" |
| `WHERE` | Filter to matching rows |
| `ORDER BY … DESC` | Sort (DESC = high to low) |
| `LIMIT n` | Only the first n rows |
| `COUNT / SUM / AVG` | Count / total / average |
| `GROUP BY` | Summarise per group (e.g. per product) |
| `JOIN … ON …` | Combine two tables by a shared id |
| `INSERT / UPDATE / DELETE` | Add / change / remove rows (**changes data**) |
