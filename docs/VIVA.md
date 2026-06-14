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
