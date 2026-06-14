# Team & module ownership

The system divides cleanly into **five modules** — one per team member. Each owner
should be able to **explain, run, and modify** their module, and answer questions on
it during the defense. (These are suggestions — feel free to swap to match each
person's strengths.)

> Tip: everyone should still understand the *overall* three-tier architecture
> ([ARCHITECTURE.md](ARCHITECTURE.md)) so the presentation flows as one system.

---

## 1. System Architecture, Authentication & Security
**Owner: Acquah Joshua Mensah**

- The Flask **application factory** and how the app is wired together.
- **Login / logout**, password hashing, sessions, CSRF protection.
- **Role-based access control** (the three roles and the `@role_required` decorator).
- The three-tier design and the JSON-401 handling for the API.

**Files:** `app/__init__.py`, `app/auth.py`, `app/decorators.py`, `config.py`,
`app/templates/login.html`

**Be ready to:** add a new user/role, explain why server-side checks (not the UI)
enforce security, show a logged-out API call returning 401.

---

## 2. Frontend & Real-time Dashboard (React)
**Owner: Acquaye James**

- The **React** single-page dashboard (components, state, hooks).
- **Recharts** visualisations, the KPI gauge, the Ransbet green theme.
- The **5-second polling** that makes it "real-time", and the build-and-serve model.

**Files:** `frontend/src/**`, `app/static/css/style.css`, `app/api.py` (the JSON
endpoints the dashboard consumes)

**Be ready to:** explain how data flows from API → state → chart, change a chart or
colour and rebuild (`npm run build`), demo two devices updating live.

---

## 3. Inventory Management
**Owner: Abotsi Kafui Kosi**

- **Product catalogue** CRUD, categories, suppliers.
- **Stock movements**: receive, sell, adjust — and how each updates stock + the ledger.
- **Restock alerts** and the colour-coded stock status.
- The **audit log**.

**Files:** `app/inventory.py`, `app/templates/inventory/*` (except scan/data),
the `Product`/`Supplier`/`Category`/`StockMovement`/`AuditLog` models

**Be ready to:** add a product, record a sale and show stock dropping, explain the
reorder-point logic, show the audit trail.

---

## 4. Artificial Intelligence (Forecasting & Anomaly Detection)
**Owner: Mensah Alima Sylvia**

- **Prophet** demand forecasting and how seasonality/holidays are modelled.
- **Back-testing** and the accuracy metrics (MAPE / MAE / RMSE).
- **Isolation Forest** anomaly detection (the five features, contamination).
- The training/retraining pipeline.

**Files:** `train_models.py`, `generate_sales.py`, the `Forecast`/`ForecastMetric`/
`AnomalyFlag` models, the `Forecast`/`Anomalies` React components

**Be ready to:** explain what MAPE means and why ~13% is good, re-run training,
explain how an anomaly is "isolated", point to a flagged spike.

---

## 5. Database, Data Tools, Reporting & Deployment
**Owner: Mahama Lukeman**

- **MySQL** schema, the SQLAlchemy ORM, switching DB via `.env`.
- **Bulk import/export** (CSV/Excel) and the danger-zone data wipe.
- **Report exports** (inventory/sales/forecast as CSV & PDF).
- **Barcode** scanning and the **deployment** to PythonAnywhere.

**Files:** `app/models.py`, `app/data_admin.py`, `app/reports.py`,
`app/inventory.py` (`/scan`), `setup_mysql_db.py`, `DEPLOY.md`

**Be ready to:** import a CSV of products, export a PDF report, show the MySQL
tables in SQLTools, explain how the live site was deployed.

---

## Suggested presentation order (≈ 12–15 min)

1. **Acquaye James** — intro + live demo of the dashboard (the "wow").
2. **Abotsi Kafui Kosi** — add a product / record a sale (core workflow).
3. **Mensah Alima Sylvia** — the AI: forecast + anomaly.
4. **Mahama Lukeman** — reports, import, and the live deployment.
5. **Acquah Joshua Mensah** — architecture & security wrap-up + Q&A lead.
