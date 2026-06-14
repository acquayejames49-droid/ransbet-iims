# Setup — run Ransbet IIMS on a fresh laptop

Two ways to run it:

- **Quick start (SQLite)** — no database to install; running in ~10 minutes. Best
  for a teammate who just wants it working.
- **Full setup (MySQL)** — the database described in the report. A few extra steps.

Both use the same code; only the database differs.

---

## 0. Install the tools (once)

| Tool | Why | Get it |
|------|-----|--------|
| **Python 3.12** | Runs the backend + ML | https://www.python.org/downloads/ (tick **"Add Python to PATH"**) |
| **Node.js (LTS)** | Builds the React dashboard | https://nodejs.org |
| **Git** | Download the code | https://git-scm.com/download/win |
| **VS Code** | Editor (optional) | https://code.visualstudio.com |
| **MySQL 8.0** | Database (Full setup only) | https://dev.mysql.com/downloads/mysql/ → "Windows ZIP Archive" |

---

## 1. Get the code

```bash
git clone https://github.com/acquayejames49-droid/ransbet-iims.git
cd ransbet-iims
```

## 2. Backend (Python) — same for both paths

Create and activate a virtual environment, then install the packages:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
(On macOS/Linux: `python3.12 -m venv .venv` then `source .venv/bin/activate`.)

## 3. Frontend (React) — build the dashboard

In a **second terminal**:
```bash
cd frontend
npm install
npm run build
```
This compiles the dashboard into `app/static/dashboard/`. You only need to re-run
`npm run build` when you change the dashboard code.

---

## 4A. Quick start (SQLite)

1. Create a file named `.env` in the project root with:
   ```
   SECRET_KEY=any-long-random-text
   DATABASE_URL=
   ```
   (Leaving `DATABASE_URL` blank makes the app use a local SQLite file — zero setup.)
2. Load the data:
   ```powershell
   python seed.py            # tables + demo users + sample catalogue
   python generate_sales.py  # ~2 years of sales + realistic stock
   python train_models.py    # train Prophet + Isolation Forest (~2 min)
   ```
3. Run it:
   ```powershell
   python run.py
   ```
4. Open **http://127.0.0.1:5000** and log in (`manager@ransbet.com` / `manager123`).

---

## 4B. Full setup (MySQL — as in the report)

1. **Start MySQL.** If you used the ZIP download, initialise it once and start it
   (see `start_mysql.bat` for the exact paths used in this project), or use the
   MySQL Installer service. You need a running MySQL on `127.0.0.1:3306` with a
   root password.
2. **Create the database** and point the app at it. Put this in `.env`
   (replace `YOURPASSWORD`):
   ```
   SECRET_KEY=any-long-random-text
   DATABASE_URL=mysql+pymysql://root:YOURPASSWORD@127.0.0.1:3306/ransbet_iims
   ```
3. Install the MySQL driver and create the database:
   ```powershell
   pip install pymysql cryptography
   python setup_mysql_db.py   # creates the 'ransbet_iims' database
   ```
4. Load the data (same as Quick start):
   ```powershell
   python seed.py
   python generate_sales.py
   python train_models.py
   ```
5. Run it:
   ```powershell
   python run.py
   ```
6. Open **http://127.0.0.1:5000**.

> On Windows you can also just double-click **`START_RANSBET.bat`**, which starts
> MySQL and the app together.

---

## 5. Inspect the database (optional, for the demo)

Install the **SQLTools** extension in VS Code; a connection named
"Ransbet IIMS (MySQL)" is pre-configured in `.vscode/settings.json`. Click
**Connect** to browse the tables and run SQL.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `node` not recognised after installing Node | Close and reopen the terminal (PATH refresh). |
| `pip install prophet` fails | Make sure you're on Python 3.12, not 3.13/3.14. |
| Dashboard shows old version | Re-run `npm run build` in `frontend/`, then refresh the browser. |
| MySQL "Access denied" | Check the password in `.env` matches your MySQL root password. |
| `func.sum` returns Decimal error | Already handled in code; if you add new sums, cast with `float(...)`. |
