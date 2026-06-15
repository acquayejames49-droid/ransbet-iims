# Demonstration runbook — proving you built it

The strongest proof of authorship in a defense isn't a document — it's being able to
**run it, navigate the code, explain any part, and change it live on request.** This
runbook walks you through a demonstration that shows exactly that, end to end.

> Golden rule: whoever owns a module (see TEAM.md) drives that part of the demo and
> answers its questions. Practise this flow at least once before the real thing.

---

## A. Before the examiners arrive — set the stage (5 min)

Open these and leave them ready:

1. **VS Code** with the project open: *File → Open Folder →* `C:\Users\USER\Desktop\Claude\ransbet-iims`.
2. A **terminal** inside VS Code (`Ctrl+` `` ` ``).
3. **Start the system**: double-click `START_RANSBET.bat` (starts MySQL + the app),
   or in the terminal:
   ```powershell
   .\.venv\Scripts\activate
   python run.py
   ```
4. A **browser** with two tabs:
   - Local: `http://127.0.0.1:5000`
   - Live: `https://aizen004.pythonanywhere.com`
5. **SQLTools** open in VS Code (left sidebar) connected to "Ransbet IIMS (MySQL)".

---

## B. The demonstration flow (≈ 12–15 min)

### 1. "This is our system" — the live product (Acquaye James)
- Show the **live site** in the browser. Emphasise it's on the internet, not your laptop.
- Log in as Manager. Walk the **dashboard**: KPIs, charts, gauge, reminders.
- Open the live site on a **phone** too; record a sale on the phone → the dashboard
  updates within ~5 seconds. *"Multi-user, real-time, from anywhere."*

### 2. "Here is the code that runs it" — VS Code (everyone)
- In VS Code, show the **folder structure** (the `app/`, `frontend/`, the scripts).
- Each member opens **their** files (from TEAM.md) and explains a piece:
  - `app/__init__.py` — how the app is assembled (Acquah).
  - `frontend/src/components/Dashboard.jsx` — the live dashboard (Acquaye).
  - `app/inventory.py` — a route, e.g. `stock_sell` (Abotsi).
  - `train_models.py` — the Prophet + Isolation Forest training (Mensah Sylvia).
  - `app/models.py` + `app/reports.py` — the database tables + PDF reports (Mahama).

### 3. "It runs on our machine too" — local + database
- Show the **local** tab (`127.0.0.1:5000`) running from your terminal.
- In **SQLTools**, expand the `ransbet_iims` database → show the tables
  (`products`, `sales`, `forecasts`, `anomaly_flags`, …). Run a live query:
  ```sql
  SELECT name, current_stock, reorder_point FROM products;
  ```
  *This proves the data lives in a real MySQL database.*

### 4. "We can change it on the spot" — the clincher
Pick ONE quick, visible change to do live (this is the most convincing part):
- **Easiest:** add a product through the UI and show it appear in the list and in the
  SQLTools query. Or record a sale and show stock drop.
- **Code change:** in `app/templates/base.html` or a React component, change a heading,
  save, (rebuild React with `npm run build` if it's the dashboard), refresh — show it
  update. This proves you understand and control the code.

### 5. "Here's how we built it over time" — the trail
- In the terminal: `git log --oneline` — show the commit history.
- Show the **GitHub repo** (`github.com/acquayejames49-droid/ransbet-iims`) with the
  code and the docs (README, ARCHITECTURE, SETUP, TEAM, VIVA).

### 6. "The intelligence" — the AI (Mensah Sylvia)
- On the dashboard, pick a product in **Demand forecast** → explain actual vs predicted
  and the MAPE.
- Show the **Anomaly alerts** and explain a flagged spike.
- Optionally re-run `python train_models.py` to show the models being trained.

---

## C. Likely "prove it" challenges & how to handle them

| Examiner says… | You do… |
|---|---|
| "Explain this function." | Open it, read it line by line in plain English (you own it). |
| "Add a field / change something now." | Do a small UI add, or a small code edit + refresh. |
| "Where is this data stored?" | Switch to SQLTools, show the table + run a SELECT. |
| "Is this really yours or a template?" | Walk the architecture (ARCHITECTURE.md), show git history, change code live. |
| "How does the forecast work?" | Open `train_models.py`, explain Prophet + back-testing + MAPE. |

---

## D. Reset to a clean state (if you experimented before the demo)

If you made test changes to the data and want the tidy sample set back:
```powershell
python seed.py
python generate_sales.py
python train_models.py
```

---

**Bottom line:** if all five of you can each open your files, explain them, and make a
change on request, there is no stronger proof of authorship. The code, the running
app, the MySQL database, the live site, and the git history together tell the whole
story.
