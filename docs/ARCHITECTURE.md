# Architecture — Ransbet IIMS

This document explains how the whole system is built and how the pieces fit
together. It mirrors the three-tier design described in Chapter 3 of the report.

---

## 1. Three-tier architecture

The system is divided into three independent layers. Each layer has one job and
talks to the next through a clean interface, so any layer can change without
breaking the others.

```
┌──────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER  (the browser)                         │
│  React single-page dashboard + server-rendered Flask pages │
└───────────────▲───────────────────────┬───────────────────┘
                │  JSON over HTTP        │  HTML pages
                │  (fetch /api/...)      │
┌───────────────┴───────────────────────▼───────────────────┐
│  APPLICATION LAYER  (the server)                           │
│  Flask: authentication, RBAC, business logic, REST API     │
└───────────────▲────────────────────────────────────────────┘
                │  SQL (via SQLAlchemy ORM)
┌───────────────┴────────────────────────────────────────────┐
│  DATA LAYER                                                 │
│  MySQL 8.0 relational database                              │
└────────────────────────────────────────────────────────────┘
```

- **Presentation layer** — what the user sees. The main dashboard is a **React**
  app (built with Vite, charts by Recharts). Operational pages (login, product
  forms, suppliers, reports) are server-rendered with Flask + Jinja2 + Bootstrap.
- **Application layer** — **Flask**. It authenticates users, enforces role-based
  permissions, runs the business logic, exposes a **JSON REST API**, and reads/writes
  the database through the SQLAlchemy ORM. It never lets the browser touch the
  database directly.
- **Data layer** — a **MySQL 8.0** relational database holding every entity
  (products, sales, forecasts, etc.).

> The ML models are trained *offline* by a separate script (`train_models.py`)
> and their results are stored in the database, so the live application only has
> to *read* forecasts — it never trains models while a user waits.

---

## 2. How a request flows (example: opening the dashboard)

1. The browser requests `/dashboard`. Flask checks the session cookie; if not
   logged in, it redirects to `/login`.
2. Flask returns the compiled **React** app (`app/static/dashboard/index.html`).
3. React starts in the browser and calls **`GET /api/me`** to learn who is logged in.
4. React then calls the data endpoints — `/api/summary`, `/api/kpis`,
   `/api/sales-trend`, `/api/reminders`, `/api/forecast/<id>`, `/api/anomalies`, …
5. For each call, Flask runs a SQL query (through SQLAlchemy) against MySQL and
   returns **JSON**.
6. React stores the data in component *state* and draws the cards, charts and tables.
7. A timer re-runs steps 4–6 **every 5 seconds**, which is how the dashboard stays
   "real-time" without reloading the page.

---

## 3. The data model (database tables)

Defined in [`app/models.py`](../app/models.py) using SQLAlchemy. Foreign keys link
the tables; indexes are added on the columns used most for lookups.

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `users` | Login accounts & roles | email, password_hash, role |
| `categories` | Product categories | name |
| `suppliers` | Supplier details | name, contact, lead_time_days |
| `products` | The catalogue | name, sku (barcode), unit_price, current_stock, reorder_point, category_id→, supplier_id→ |
| `sales` | Every sale (the forecasting dataset) | product_id→, quantity, unit_price, total, sale_date |
| `stock_movements` | Inventory ledger (in / adjustment / sale) | product_id→, movement_type, quantity, stock_after, user_id→ |
| `forecasts` | Predicted daily demand (from Prophet) | product_id→, forecast_date, predicted_qty, lower, upper |
| `forecast_metrics` | Model accuracy per product | product_id→, mape, mae, rmse |
| `anomaly_flags` | Unusual events (from Isolation Forest) | product_id→, flag_date, quantity, expected, score, reason |
| `audit_logs` | Who did what, when | user_id→, action, description, created_at |

`→` = foreign key to another table.

**Stock status logic** (a computed property on `Product`):
- `current_stock <= reorder_point` → **reorder** (red)
- `current_stock <= reorder_point × 1.5` → **low** (yellow)
- otherwise → **ok** (green)

---

## 4. Authentication & role-based access control (RBAC)

- Login uses **Flask-Login** with passwords stored only as salted hashes
  (`werkzeug.security`) — never in plain text.
- Sessions are signed cookies; **CSRF protection** (Flask-WTF) guards every form.
- Three roles, enforced on the server by the `@role_required(...)` decorator in
  [`app/decorators.py`](../app/decorators.py):

| Action | Staff | Manager | Owner |
|--------|:----:|:------:|:----:|
| View dashboard, products, sales | ✅ | ✅ | ✅ |
| Add/edit products, receive/sell/adjust stock | ✅ | ✅ | — |
| Delete products, manage suppliers/categories | — | ✅ | ✅ |
| View audit log, import/clear data | — | ✅ | ✅ |

> Security note: hiding a menu item in React is *not* the security boundary — the
> server re-checks the user's role on every protected request, so the rules can't
> be bypassed from the browser. Logged-out API calls get a JSON `401`.

---

## 5. Presentation layer in detail (React)

- The dashboard is a **single-page application**: the page loads once, then React
  updates the content in place.
- Built from **components** (`frontend/src/components/`): `Navbar`, `Reminders`,
  `Tiles`, `Kpis`, `Gauge`, `TopItems`, `MonthlyTrend`, `StockStatus`,
  `RestockAlerts`, `Forecast`, `Anomalies`.
- **State + hooks**: `useState` holds the fetched data; `useEffect` loads it on
  start and sets the 5-second refresh timer.
- **Build-and-serve**: `npm run build` compiles the React source into
  `app/static/dashboard/`, and **Flask serves those static files**. This means one
  server in production (no separate Node server), and the session cookie works
  automatically because everything is same-origin.
- Charts use **Recharts**; the visual theme (Ransbet green) is in
  `frontend/src/index.css`.

---

## 6. The machine-learning pipeline

Two models, both trained by [`train_models.py`](../train_models.py).

### 6.1 Demand forecasting — Facebook Prophet
- For each product, daily sales are aggregated into a time series.
- A **Prophet** model learns the trend, weekly cycle, yearly seasonality and
  Ghanaian public-holiday effects, then predicts the **next 30 days**.
- **Back-testing**: the last 30 days are held out, the model is trained on the rest
  and tested on them to compute accuracy: **MAPE, MAE, RMSE** (stored in
  `forecast_metrics`). The system averages **~13% MAPE (~87% accuracy)**, meeting
  the report's ≥85% target.
- The forward forecast is written to the `forecasts` table; the dashboard simply
  reads it.

### 6.2 Anomaly detection — Isolation Forest
- An **Isolation Forest** (scikit-learn, unsupervised) scores each product-day on
  five features: daily quantity, 7-day rolling mean, 7-day rolling standard
  deviation, deviation from the mean, and day-of-week.
- Points that are "easy to isolate" are flagged as anomalies (a sudden **spike** or
  **drop**) and written to `anomaly_flags`. The trained model is also saved to
  `models/anomaly_model.pkl`.

### 6.3 Retraining
Re-run `python train_models.py` whenever new sales data is added (e.g. after
importing Ransbet's real sales). This refreshes all forecasts and anomalies.

---

## 7. Data tooling

- **Bulk import** ([`app/data_admin.py`](../app/data_admin.py)): upload a CSV/Excel
  catalogue or sales history. Headers are auto-matched (e.g. `barcode`→sku,
  `qty`→stock), and categories/suppliers are created automatically. This is how
  thousands of real products get loaded without manual entry.
- **Reports** ([`app/reports.py`](../app/reports.py)): inventory, sales and
  forecast-accuracy reports exported as CSV or PDF (ReportLab).

---

## 8. Deployment

- Code is version-controlled with **Git** and hosted on **GitHub**.
- The live site runs on **PythonAnywhere** (free tier). The application is identical
  to the local one; only the database connection string differs (set via an
  environment variable in the WSGI file). See [DEPLOY.md](../DEPLOY.md).
- **Database note:** the primary/development system uses **MySQL 8.0** (as specified
  in the report). Because PythonAnywhere's free tier no longer offers MySQL, the
  free public demo uses SQLite — the same code, one configuration line different,
  thanks to the SQLAlchemy ORM abstracting the database.
