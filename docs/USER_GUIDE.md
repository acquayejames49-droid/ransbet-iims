# User guide — a complete beginner's tour of the site

This explains, in plain everyday language, exactly what someone sees when they open
the Ransbet IIMS website, what every part of the screen does, and what the different
users are allowed to do. No technical knowledge needed.

> **Live site:** https://aizen004.pythonanywhere.com
> **Demo logins:** manager@ransbet.com / manager123 · staff@ransbet.com / staff123 ·
> owner@ransbet.com / owner123

---

## The 10‑second version

> "This is a smart website that keeps track of everything Ransbet Supermarket sells
> and has in stock. It warns staff when something is running low, and it even
> **predicts** how much will sell next month. Different staff log in and see what
> they're allowed to."

---

## Step 1 — Opening the site (the Login page)

The first thing you see is a **login box** — a white card that says **"Ransbet IIMS"**
with two boxes, **Email** and **Password**, and a green **Sign in** button.

*Why?* Like a phone passcode, only people with an account can get in — so customers or
strangers can't see or change the shop's private data. You type a staff login and
click **Sign in**.

---

## Step 2 — The Home page (the Dashboard)

After logging in you land on the **Overview dashboard** — the colourful green screen. It's
the "control room." Everything on it refreshes **by itself every few seconds**, so the
numbers are always current. Here's each part, in plain words:

**The left sidebar** (down the left edge, always visible) — the main menu:
- Top: the **"Ransbet IIMS · Tarkwa · Ghana"** name (click it any time to return to Overview).
- The sections: **Overview, Inventory, Scan, Sales, Movements, Suppliers, Reports**.
- A **"Manage"** group (only **managers/owners** see this): **Categories, Audit log,
  Import / Data**.
- At the very bottom: a small green **"AI Insight"** card that says, in one sentence, how
  many items are predicted to run out soon.

**The top bar** (across the top of the main area) — the page title **"Overview"**, a
**"Welcome back, [your name] · [today's date]"** greeting, a **search box**, a
**notifications bell**, and on the far right your **name with your initials** — click that
to **log out**.

**The green banner** (the "hero") — the headline AI message, e.g. *"Your inventory is
projected to stay 96% optimal this month,"* with two buttons: **Run new forecast** and
**Export report**.

**Four KPI cards** (the headline numbers, each with an up/down arrow versus last month):
- **Forecasted Revenue** — predicted sales value for the period ahead.
- **Units in Stock** — how many items are on the shelves right now.
- **Stockout Risk** — how many products are in danger of running out.
- **Forecast Accuracy** — how closely the AI's past predictions matched what really sold.

**Sales Forecast** (the big card on the left) — the clever part. Pick any product from the
dropdown and a time range (**7 / 14 / 30 days**). The green chart shows **two lines**: the
**solid green line = what actually sold** (recorded history) and the **dashed green line =
what the AI predicts**, split by a faint **"Today"** marker so you can see past versus
future on one chart. Underneath: **Predicted units**, a **Confidence** score, and how it
compares with the last period.

**Anomaly Feed** (the card on the right) — a **live** list of unusual events the AI noticed
(a sudden spike or drop in a product's sales), so the manager can investigate.

**Inventory Intelligence** (table) — every key product with its **current stock** (and a
little progress bar), its **predicted 7‑day demand**, and a **status pill**: 🟢 Healthy,
🟡 Low, 🔴 Critical.

Scroll down to the **"More insights"** heading for the familiar extra panels:
- **Reminders** — a to‑do list with big coloured numbers: how many products are **out of
  stock**, need **reordering**, are **predicted to run out** soon, and how many **unusual
  events** to review.
- **Monthly sales trend** — revenue bars plus a units line, month by month.
- **Inventory KPI meter** — a speedometer‑style dial of the **total value of all stock**.
- **Top items by qty sold** — a ring/donut chart of the best sellers.
- **Stock status** — a traffic‑light ring: how many products are 🟢 fine, 🟡 low,
  🔴 need reordering.
- **Restock alerts** — the list of products to reorder, with a suggested quantity and a
  green **Receive** button.

---

## Step 3 — The menu sections (what each page does)

Everything below is reached from the **left sidebar**.

| Menu item | What it's for (plain English) |
|---|---|
| **Overview** | The dashboard overview — the Home screen described above. |
| **Inventory** | The full product list: name, stock, price, status. Here you **Sell, Receive, Adjust, Edit** or **Delete** items. |
| **Scan** | Point a barcode scanner at a product to find it instantly. |
| **Sales** | A history of every recorded sale. |
| **Movements** | A logbook of every stock change (received, sold, adjusted). |
| **Suppliers** | The companies that supply the shop's products. |
| **Reports** | Download neat **PDF or Excel** reports (inventory, sales, forecast accuracy). |
| **Categories** *(managers only)* | Groupings like "Beverages," "Groceries." |
| **Audit log** *(managers only)* | A record of **who did what, and when**. |
| **Import / Data** *(managers only)* | Bulk‑load a product list from a file, export data, or clear data. |

---

## Step 4 — The roles (who's allowed to do what)

The word beside your name is your **role** — think of it as a different key:

| Role | Login | What they can do |
|---|---|---|
| 🟢 **Store Manager** | manager@ransbet.com | **Everything** — the master key. Forecasts, approvals, delete, manage. |
| 🟡 **Inventory Staff** | staff@ransbet.com | Day‑to‑day work: **add products, record sales, receive/adjust stock**. Cannot delete or see the audit log. |
| 🔵 **Business Owner** | owner@ransbet.com | Mostly **views** — reports, trends, the big picture. |

> Easy way to show this off: log in as the **Manager** (the sidebar shows *all* items,
> including the **Manage** group), then log out and log in as **Staff** — the **Manage**
> items (Categories, Audit log, Import / Data) **disappear** from the sidebar. That visibly
> proves the system gives different people different access.

---

## A ready demonstration script (what to actually say)

1. *"When you open the site, it asks you to log in — only staff can get in."* → log in as Manager.
2. *"This is the control room. These green numbers are live and update by themselves."* → point at the KPI cards + Reminders.
3. *"It tells us what to reorder…"* → scroll to Restock alerts.
4. *"…and this is the clever part — it predicts the future."* → pick a product in **Sales Forecast** (solid green line = what actually sold, dashed green line = the AI's prediction).
5. *"…and it flags anything unusual."* → show the **Anomaly Feed**.
6. *"Different staff see different things."* → log out, log in as Staff, and show that the **Manage** items have disappeared from the sidebar.

The whole tour takes about **3 minutes**, and a complete beginner will follow every word.
