# Ransbet IIMS — Intelligent Inventory Management System

An AI-powered, web-based inventory management and **sales-forecasting** system built
as a final-year project for **Ransbet Supermarket, Tarkwa**. It replaces manual,
spreadsheet-based stock-keeping with a real-time dashboard, machine-learning demand
forecasting, and automatic anomaly detection.

> **Live demo:** https://aizen004.pythonanywhere.com
> **Sign in:** `manager@ransbet.com` / `manager123` (other demo logins below)

---

## 👥 Team

University of Mines and Technology (UMaT), Tarkwa — BSc Information Systems & Technology
Supervisor: **Dr Hamidu Abdel-Fatao**

| Name | Index number |
|------|--------------|
| Acquah Joshua Mensah | FOE.41.020.006.22 |
| Acquaye James | FOE.41.020.008.22 |
| Abotsi Kafui Kosi | FOE.41.020.003.22 |
| Mensah Alima Sylvia | FOE.41.020.078.22 |
| Mahama Lukeman | FOE.41.020.076.22 |

See **[docs/TEAM.md](docs/TEAM.md)** for the module-ownership split (who built/presents what).

---

## ✨ Features (the 10 functional requirements)

1. **Product catalogue** — add / edit / remove products (name, category, price, supplier, reorder point).
2. **Real-time stock tracking** — live levels with colour-coded status (🟢 ok / 🟡 low / 🔴 reorder).
3. **AI demand forecasting** — Facebook **Prophet** predicts each product's next 30 days (~87% accuracy).
4. **Anomaly detection** — **Isolation Forest** flags unusual sales spikes/drops.
5. **Restock alerts** — automatic alerts with a suggested reorder quantity.
6. **Business-intelligence dashboard** — KPIs, charts and a gauge meter, refreshing live.
7. **Barcode scanning** — USB scanner or on-screen webcam lookup.
8. **Report export** — inventory, sales and forecast-accuracy reports as **CSV and PDF**.
9. **Role-based access control** — Store Manager, Inventory Staff, Business Owner.
10. **Audit log** — every action recorded with the user and timestamp.

---

## 🧱 Tech stack

| Layer | Technology |
|-------|------------|
| Presentation (frontend) | **React** + Vite + Recharts (single-page dashboard) + Bootstrap |
| Application (backend) | **Python 3.12** + **Flask** (REST/JSON API) + Flask-Login (auth) + SQLAlchemy (ORM) |
| Data | **MySQL 8.0** (relational database; SQLite used only for the free public demo — see [deployment note](docs/DEPLOYMENT_NOTE.md)) |
| Machine learning | **Prophet** (forecasting), **scikit-learn** Isolation Forest (anomalies), pandas / NumPy |
| Reporting | ReportLab (PDF), pandas (CSV/Excel) |
| Deployment | PythonAnywhere (free cloud hosting), Git / GitHub |

Architecture follows the report's **three-tier design**. Full explanation in
**[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## 🚀 Run it yourself

- **Quick start (any laptop, zero database setup):** see **[docs/SETUP.md](docs/SETUP.md)** → "Quick start (SQLite)".
- **Full setup (MySQL, as in the report):** see **[docs/SETUP.md](docs/SETUP.md)** → "Full setup (MySQL)".

On Windows you can simply double-click **`START_RANSBET.bat`** once everything is installed.

---

## 🔑 Demo logins

| Role | Email | Password | Can do |
|------|-------|----------|--------|
| Store Manager | manager@ransbet.com | manager123 | Everything: forecasts, approvals, deletes, suppliers |
| Inventory Staff | staff@ransbet.com | staff123 | Add products, record sales, receive/adjust stock |
| Business Owner | owner@ransbet.com | owner123 | View reports, trends, manage catalogue |

---

## 📂 Project structure (high level)

```
ransbet-iims/
├── app/                  # Flask application (backend)
│   ├── __init__.py       # app factory: db, login, CSRF, blueprints
│   ├── models.py         # database tables (SQLAlchemy)
│   ├── auth.py           # login / logout
│   ├── inventory.py      # products, stock, suppliers, categories, audit
│   ├── api.py            # JSON endpoints that feed the React dashboard
│   ├── data_admin.py     # bulk CSV/Excel import + export
│   ├── reports.py        # PDF / CSV report exports
│   ├── decorators.py     # @role_required (RBAC)
│   ├── templates/        # server-rendered pages (login, products, etc.)
│   └── static/dashboard/ # the compiled React dashboard
├── frontend/             # React source (Vite) for the dashboard
├── seed.py               # create tables + demo users + sample catalogue
├── generate_sales.py     # generate ~2 years of sales + realistic stock
├── train_models.py       # train Prophet + Isolation Forest
├── run.py                # start the web app
└── docs/                 # architecture, setup, team split, viva prep
```

---

## 📖 Documentation

- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** — a complete beginner's tour of the website: what you see, every function, and the roles.
- **[docs/GLOSSARY.md](docs/GLOSSARY.md)** — plain-English reference: every tool, library, file & command explained for beginners.
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the whole system works, the data model, the ML pipeline.
- **[docs/DATABASE.md](docs/DATABASE.md)** — database design: ER diagram, all tables, relationships, sample queries.
- **[docs/SETUP.md](docs/SETUP.md)** — install and run on a fresh laptop.
- **[docs/TEAM.md](docs/TEAM.md)** — module ownership across the five members.
- **[docs/VIVA.md](docs/VIVA.md)** — practice questions & answers for the defense.
- **[docs/DEMO.md](docs/DEMO.md)** — step-by-step demonstration runbook.
- **[docs/schema.sql](docs/schema.sql)** — the raw MySQL `CREATE TABLE` statements.
- **[docs/DEMO_QUERIES.md](docs/DEMO_QUERIES.md)** — practice SQL queries for the defense (easy → impressive).
- **[DEPLOY.md](DEPLOY.md)** — how the live deployment was done.
- **[docs/DEPLOYMENT_NOTE.md](docs/DEPLOYMENT_NOTE.md)** — which database runs where (MySQL vs SQLite) and why.

---

*Academic project — University of Mines and Technology, 2026.*
