# Plain-English reference — every tool, library, file & command

A complete beginner's glossary of everything used to build Ransbet IIMS, from
start to finish. If you see a word anywhere in the project and wonder "what is
that?", it's explained here in one or two simple sentences.

---

## A. Programs we installed on the laptop

| Tool | What it is / why we used it |
|------|------------------------------|
| **Python** | The main programming language. The whole backend and all the AI/data scripts are written in it. |
| **VS Code** | The "editor" — the program where we actually write and read the code. |
| **Node.js** | A program that runs JavaScript tools on the laptop. We only need it to *build* the React dashboard. |
| **npm** | Comes with Node.js. It downloads JavaScript libraries (like an app store for code). |
| **Git** | A "time machine" that tracks every change to our code on the laptop. |
| **GitHub** | A website that stores an online copy of our Git project (backup + sharing). |
| **MySQL 8.0** | The database — the program that stores all our data (products, sales, etc.). |
| **PythonAnywhere** | The free cloud service that runs our website online 24/7. |
| **SQLTools** (VS Code add-on) | Lets us look inside the MySQL database and run queries from VS Code. |

---

## B. Python libraries (installed with `pip`)

| Library | What it does |
|---------|--------------|
| **Flask** | The web framework — it turns our Python code into a working website/server. |
| **SQLAlchemy** / **Flask-SQLAlchemy** | The **ORM**: lets us define and use the database with Python instead of writing raw SQL. |
| **Flask-Login** | Handles logging users in and out and remembering who's logged in. |
| **Flask-WTF** | Builds forms and protects them from a hacking trick called CSRF. |
| **Flask-Migrate** | Helps change the database structure safely over time. |
| **PyMySQL** + **cryptography** | The "cable" that lets Python talk to the MySQL database. |
| **pandas** | Reads and cleans tables of data (CSV/Excel) — very fast. |
| **NumPy** | Does fast maths on lots of numbers (used by pandas and the AI). |
| **openpyxl** | Lets pandas read Excel files. |
| **Prophet** | The forecasting model (made by Facebook) that predicts future sales. |
| **scikit-learn** | A machine-learning toolkit; we use its **Isolation Forest** for anomaly detection. |
| **reportlab** | Creates PDF files (our exported reports). |
| **pdfplumber** | Reads text out of PDF files (used to read Ransbet's stock-card PDFs). |
| **waitress** | A small web server used when running in production. |
| **python-dotenv** | Loads private settings (like passwords) from the `.env` file. |

## C. Frontend (dashboard) tools

| Tool | What it does |
|------|--------------|
| **React** | Builds the interactive dashboard (the moving charts and cards). |
| **Vite** | The "builder" that turns our React code into files a browser can run (`npm run build`). |
| **Recharts** | A React library that draws the charts (lines, bars, donuts, gauge). |
| **Bootstrap** | Ready-made styling so the pages look neat without writing lots of CSS. |

---

## D. The project's files & folders (what each one does)

### Scripts you run from the terminal
| File | What it does |
|------|--------------|
| **run.py** | Starts the website (then you open `http://127.0.0.1:5000`). |
| **seed.py** | Creates the database tables, the 3 demo logins, and a small sample catalogue. |
| **generate_sales.py** | Generates ~2 years of *practice* sales data + realistic stock levels. |
| **train_models.py** | Trains the two AI models (forecast + anomaly) and saves the results. |
| **import_stock_card.py** | Reads Ransbet's real "stock card" PDF for a product and loads it in (see section F). |
| **setup_mysql_db.py** | Creates the empty `ransbet_iims` database inside MySQL. |
| **config.py** | Settings: which database to use, the secret key. |
| **.env** | Private settings (database password, secret key). **Not** uploaded to GitHub. |
| **requirements.txt** | The shopping list of Python libraries to install. |
| **START_RANSBET.bat** / **start_mysql.bat** | Double-click launchers (start MySQL + the app). |

### The `app/` folder — the website itself
| File | What it does |
|------|--------------|
| **app/__init__.py** | Assembles the whole app (connects the database, login, forms, pages). |
| **app/models.py** | Defines the database tables as Python classes (the "database code"). |
| **app/auth.py** | The login and logout pages. |
| **app/inventory.py** | Products, stock movements, suppliers, categories, the audit log, and barcode scan. |
| **app/api.py** | The **API**: sends data as JSON to the React dashboard. |
| **app/data_admin.py** | Bulk import/export of products and sales (CSV/Excel) + the "danger zone". |
| **app/reports.py** | Builds the downloadable PDF and CSV reports. |
| **app/decorators.py** | The `@role_required` check that enforces who's allowed to do what. |
| **app/templates/** | The HTML pages Flask shows (login, product forms, etc.). |
| **app/static/** | The styling (CSS) and the compiled React dashboard. |

### The `frontend/` folder — the React source
| Item | What it does |
|------|--------------|
| **frontend/src/** | The React code: `App.jsx`, `components/` (Dashboard, Sidebar, KpiRow, SalesForecast, AnomalyFeed, InventoryIntelligence, …). |
| **frontend/package.json** | The React project's library list and build commands. |

---

## E. Commands we ran (and what they mean)

| Command | In plain words |
|---------|----------------|
| `pip install <name>` | Download and install a Python library. |
| `python <file>.py` | Run a Python script. |
| `npm install` | Download the React libraries. |
| `npm run build` | Turn the React source into files the browser can use. |
| `git add .` | Put changed files "in the box" to be saved. |
| `git commit -m "message"` | Save a snapshot of the code with a note. |
| `git push` | Upload the snapshots to GitHub. |
| `mysqld` | Start the MySQL database server. |
| `mysql -u root -p` | Open the MySQL command line to run SQL. |

---

## F. `import_stock_card.py` explained step by step

This script reads one of Ransbet's **stock-card PDFs** (a stock-movement report for
one product) and loads the real data into the system. In plain words it:

1. **Opens the PDF** and reads every line (using the `pdfplumber` library).
2. **Finds the product** name and code at the top (e.g. `22558 : MILO TIN 400G`).
3. **Reads each row** and works out the date, the type of movement, and the quantity:
   - *POS Despatch* = a sale to a customer
   - *Branch Receipt* = stock delivered in
   - *Branch Transfer* = stock sent to another branch
4. **Saves the data** into the database: every "POS Despatch" becomes a real **sale**
   (which the forecast learns from), the product's **current stock** is set to the
   final balance, and deliveries/transfers are recorded as stock movements.
5. After running it, you run **`train_models.py`** so the AI re-learns from the new
   real sales.

It's **reusable** — give it any product's stock-card PDF and it imports that product:
```powershell
python import_stock_card.py "C:\path\to\that product.pdf"
python train_models.py
```

---

## G. Key ideas & processes

| Idea | Simple meaning |
|------|----------------|
| **Virtual environment** (`.venv`) | A private box holding this project's Python libraries, separate from the rest of the laptop. |
| **ORM** | "Object-Relational Mapper" — lets us use the database with Python objects instead of raw SQL. |
| **API** | The messenger that carries data (as JSON) between the dashboard and the server. |
| **JSON** | A simple text format for sending data between programs. |
| **Build** | Turning human-written React code into compact files a browser can run. |
| **Deploy** | Putting the finished system online for everyone to use. |
| **Forecasting** | Predicting future sales by learning patterns from the past. |
| **Anomaly detection** | Automatically spotting unusual events that don't fit the normal pattern. |
| **RBAC** | "Role-Based Access Control" — different users get different permissions. |
| **Real-time (polling)** | The dashboard re-asks for fresh data every few seconds, so it always looks current. |
| **Back-testing** | Checking a forecast's accuracy by hiding recent real data, predicting it, and comparing. |
| **MAPE / MAE** | Two ways to measure forecast error (a percentage vs. an average number of units). |
| **Commit / Push** | Save a snapshot of the code (commit) and upload it to GitHub (push). |
| **LSTM** | "Long Short-Term Memory" — an AI model (neural network) for time-series data that has a built-in *memory* of past values. A powerful but data-hungry alternative to Prophet; we evaluated it but deployed Prophet because it's transparent and works on limited data. |
| **Celery** | A tool that runs jobs automatically on a schedule in the background (e.g. weekly model retraining). It needs an always-on server, so we retrain with a manual command instead. |
| **Tableau / Power BI** | Paid business-intelligence dashboard tools named in the report; we built our dashboard with free, open-source React + Recharts instead. |
