# Viva / defense preparation — practice Q&A

Likely examiner questions with model answers, grouped by module. Practise saying
these in your own words — examiners can tell rehearsed-from-memory from understood.

---

## General / architecture

**Q: Give me a one-sentence description of your project.**
A: An AI-powered web system that tracks Ransbet Supermarket's inventory in real
time and uses machine learning to forecast demand and detect anomalies, so managers
can move from reactive to proactive stock control.

**Q: Why a three-tier architecture?**
A: Separation of concerns. The presentation (React), application (Flask) and data
(MySQL) layers each do one job and communicate through interfaces, so we can change
one — say swap the database — without rewriting the others. The ORM proves this: we
moved from SQLite to MySQL by changing a single line.

**Q: What happens, step by step, when I open the dashboard?**
A: Flask checks the login session and serves the React app; React calls our JSON API
(`/api/summary`, `/api/kpis`, …); Flask queries MySQL and returns JSON; React renders
the charts and repeats every 5 seconds for real-time updates.

**Q: Is it actually real-time? You said you use polling, not WebSockets.**
A: It refreshes every 5 seconds by re-fetching the data (polling). To a user that's
effectively real-time, and it's simpler and works on more hosts than WebSockets. We
could upgrade to WebSockets for instant push if needed.

**Q: Do you use synchronous or asynchronous requests?**
A: Both. The server-rendered pages (login, forms) are synchronous — submit and wait
for a full page reload. The dashboard is asynchronous: it uses JavaScript `async/await`
with `fetch` to pull data in the background and refresh the charts every few seconds
without freezing or reloading the page. To be precise, the *frontend* makes asynchronous
requests while the *Flask backend* handles them synchronously (we didn't use Python's
asyncio). You can see the async code in `frontend/src/lib/api.js` and a synchronous
form route in `app/inventory.py`.

---

## Authentication & security

**Q: How are passwords stored?**
A: Never in plain text — only as salted hashes (Werkzeug's `generate_password_hash`).
At login we hash the input and compare hashes.

**Q: How do you stop a Staff user from deleting products?**
A: The server enforces it. Every protected route has `@role_required(...)`. Even if
someone hid the UI or crafted a request, Flask re-checks the role and returns 403.
Hiding the button in React is just convenience, not the security boundary.

**Q: What is CSRF and how do you prevent it?**
A: Cross-Site Request Forgery — a malicious site tricking your browser into
submitting a form. Flask-WTF adds a secret token to every form that the server
verifies, so forged requests are rejected.

**Q: What exactly hashes the passwords — could you reverse it?**
A: `set_password()` runs the password through Werkzeug's `generate_password_hash`,
which in our version uses **scrypt** — a salted, memory-hard, one-way hash. What's
stored looks like `scrypt:32768:8:1$<salt>$<hash>`. You can't reverse it to the
password; at login we hash the typed password and compare. Each user has a random
salt, so identical passwords still produce different hashes.

**Q: Walk me through what happens when I log in.**
A: The login form (a Flask-WTF form, so its CSRF token is checked) submits email and
password. We look up the user by email, call `check_password`, and if the user is
missing *or* the password is wrong we return the **same** "Invalid email or password"
message — so nobody can discover which emails exist. On success, `login_user()` starts
a signed session cookie and redirects to the requested page (only if it's a safe local
URL). The code is in `app/auth.py`.

**Q: How would a user change their password?**
A: Honestly, this version has no self-service "change password" screen yet — it's a
noted next step. Passwords are set when accounts are created (`seed.py`), and an admin
can reset one by calling `set_password()` (which re-hashes it). Adding a Change Password
page is small because `User` already has `check_password` and `set_password`. (See
`docs/AUTHENTICATION.md`.)

---

## Inventory

**Q: How does the system know when to reorder?**
A: Each product has a reorder point. If `current_stock ≤ reorder_point` it's flagged
red ("reorder") with a suggested quantity (top up to twice the reorder point). These
appear in Reminders and Restock Alerts.

**Q: When a sale is recorded, what changes in the database?**
A: We insert a row in `sales`, decrement the product's `current_stock`, write a
`stock_movements` ledger row with the resulting level, and add an `audit_logs` entry —
all in one transaction.

**Q: Why keep both a `sales` table and a `stock_movements` table?**
A: `sales` is the clean time series the forecast model trains on; `stock_movements`
is the full inventory ledger (receipts, adjustments, sales) for traceability.

---

## Artificial intelligence

**Q: Which algorithm forecasts demand and why?**
A: Facebook **Prophet**. Retail demand has strong weekly and seasonal patterns plus
holiday spikes (Christmas, Eid, etc.); Prophet decomposes a series into trend +
seasonality + holidays, which fits Ghanaian retail well and is robust to gaps.

**Q: What is MAPE and what did you achieve?**
A: Mean Absolute Percentage Error — the average forecast error as a percentage of
actual sales. Lower is better; below 15% is considered accurate in retail. We average
about **13%**, i.e. ~87% accuracy, which meets our ≥85% objective.

**Q: How did you measure accuracy fairly?**
A: Back-testing with a temporal split — train on the older data, hold out the most
recent 30 days, predict them and compare to what actually happened. Using a temporal
(not random) split respects time order and tests true forecasting.

**Q: How does Isolation Forest find anomalies without labels?**
A: It builds random trees that split the data; anomalous points are "different" so
they get isolated in fewer splits (a shorter path). Points with short average paths
get a high anomaly score. We feed it five features per product-day (quantity, rolling
mean/std, deviation, day-of-week) and flag the top ~5% as spikes or drops.

**Q: Does the website train the model on every visit?**
A: No — that would be slow. Training is done offline by `train_models.py`; the
results are saved to the database, and the site only reads them. We retrain when new
sales data arrives.

---

## Database, data tools & deployment

**Q: Why MySQL?**
A: A relational database fits structured, related data (products, sales, suppliers)
with foreign keys and indexing for performance, and it's the industry standard for
this kind of transactional system — as specified in our design.

**Q: Ransbet has thousands of products — surely you didn't type them in?**
A: No. The Import tool reads a CSV/Excel file with pandas and bulk-inserts them,
auto-creating categories and suppliers and matching common column names, so a whole
catalogue loads in seconds.

**Q: How is it deployed, and does it depend on your laptop?**
A: The code is on GitHub and the live site runs on PythonAnywhere's cloud servers, so
it's online 24/7 independent of our laptops. We develop locally (on MySQL) and deploy
a copy to the cloud.

**Q: Can two people use it at the same time and see each other's changes?**
A: Yes. It's a multi-user web app with per-user logins; because the dashboard polls
every 5 seconds, a change one user makes shows up on everyone's screen within seconds.

---

## Report vs. what we built — defending the swaps

Four tools in the report differ from what we delivered. **Every swap went the same way
for the same reason: to keep the system affordable and easy to run for a medium-scale
business with a small budget and no IT staff — exactly the constraints our own Chapter 2
identified.** Lead every answer with that: it turns "why didn't you follow the report?"
into evidence of good engineering judgement.

**Q: Your report mentions LSTM. Why did you deploy only Prophet?**
A: LSTM is a neural network — powerful, but *data-hungry* and a "black box" that's hard
to explain. Ransbet gave us about two years of fairly low per-product sales, and the
owner needs forecasts he can trust. Prophet is built for seasonal retail data, trains in
seconds on limited data, handles Ghanaian holidays directly, and is transparent — it
splits the forecast into trend, weekly, yearly and holiday parts. It already met our ≥85%
target (~13% MAPE), so we deployed Prophet and kept LSTM as documented future work.

**Q: The report proposes Tableau for the dashboard. Why React?**
A: Tableau and Power BI are paid, standalone tools a medium-scale supermarket can't
sustain, and they bolt on separately. React with Recharts is free and open-source,
embedded directly in our web app, works on any browser, uses our existing logins, and
deploys on a free host — the same business-intelligence output within the cost and skills
limits we identified.

**Q: The report says AWS. Where is it actually hosted?**
A: AWS is excellent but carries cost and complexity beyond a medium-scale retailer. We
host the live demo free on PythonAnywhere and run the specified MySQL 8.0 locally. Because
we use an ORM, moving between databases or hosts is a one-line change — so the three-tier
cloud architecture is fully realised; only the provider differs, chosen to keep it free.
(See [DEPLOYMENT_NOTE.md](DEPLOYMENT_NOTE.md).)

**Q: The report mentions Celery for automatic weekly retraining. Did you use it?**
A: No — deliberately. Celery needs an always-on background worker and a message broker
(extra server software), which a free host can't run and which adds cost. Retraining
happens only weekly and isn't time-critical, so we retrain with a single command
(`python train_models.py`) that can be attached to a scheduler on a paid host later. Same
result, far less infrastructure.

---

## Curveballs

**Q: What would you improve with more time?**
A: WebSocket push for instant updates; LSTM as an alternative forecaster to compare
with Prophet; automated weekly retraining (Celery); a paid host for MySQL + a custom
domain; and integrating a real barcode-scanner hardware test.

**Q: What was the hardest part?**
A: (Pick a real one) e.g. getting the React frontend, Flask API and MySQL to work
together with one login session; or tuning the synthetic data so forecast accuracy
was realistic; or the case-sensitive path issue during deployment.

**Q: Show me you understand this — change something live.**
A: (Be ready) e.g. add a product and show it appear; or change a reorder point and
watch the alert update; or open `inventory.py` and explain a route.
