"""JSON endpoints that feed the live dashboard (stat cards + charts).

The dashboard page calls these every few seconds, which is how the numbers
update in "real time" without reloading the page.
"""
from datetime import date, timedelta

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import (Product, Category, Sale, Forecast, ForecastMetric,
                        AnomalyFlag)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/summary")
@login_required
def summary():
    products = Product.query.filter_by(is_active=True).all()
    low = [p for p in products if p.needs_restock]
    today = Sale.query.filter_by(sale_date=date.today()).all()
    return jsonify(
        total_products=len(products),
        low_stock=len(low),
        stock_value=round(sum(p.stock_value for p in products), 2),
        today_revenue=round(sum(s.total for s in today), 2),
        today_units=sum(s.quantity for s in today),
    )


@api_bp.route("/sales-trend")
@login_required
def sales_trend():
    """Total sales value per day for the last 14 days."""
    start = date.today() - timedelta(days=13)
    rows = (db.session.query(Sale.sale_date, func.sum(Sale.total))
            .filter(Sale.sale_date >= start)
            .group_by(Sale.sale_date).all())
    totals = {d: float(t or 0) for d, t in rows}
    labels, data = [], []
    for i in range(14):
        d = start + timedelta(days=i)
        labels.append(d.strftime("%b %d"))
        data.append(round(totals.get(d, 0), 2))
    return jsonify(labels=labels, data=data)


@api_bp.route("/stock-status")
@login_required
def stock_status():
    """How many products are OK / Low / need Reorder."""
    counts = {"ok": 0, "low": 0, "reorder": 0}
    for p in Product.query.filter_by(is_active=True):
        counts[p.stock_status] += 1
    return jsonify(**counts)


@api_bp.route("/stock-by-category")
@login_required
def stock_by_category():
    """Total units in stock grouped by category."""
    cats = Category.query.order_by(Category.name).all()
    labels = [c.name for c in cats]
    data = [sum(p.current_stock for p in c.products if p.is_active) for c in cats]
    return jsonify(labels=labels, data=data)


@api_bp.route("/me")
@login_required
def me():
    """Who is logged in — the React app calls this on startup."""
    return jsonify(name=current_user.name, role=current_user.role,
                   email=current_user.email)


@api_bp.route("/restock-alerts")
@login_required
def restock_alerts():
    """Products at or below their reorder point, with a suggested order qty."""
    items = [p for p in Product.query.filter_by(is_active=True) if p.needs_restock]
    return jsonify([{
        "id": p.id, "name": p.name, "current_stock": p.current_stock,
        "unit": p.unit, "reorder_point": p.reorder_point,
        "suggested": p.suggested_reorder_qty,
    } for p in items])


# --------------------------- AI: forecasting & anomalies -------------------
@api_bp.route("/products")
@login_required
def products_list():
    """Lightweight product list for the forecast dropdown."""
    items = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    return jsonify([{"id": p.id, "name": p.name} for p in items])


@api_bp.route("/forecast/<int:pid>")
@login_required
def forecast(pid):
    """Recent actual sales + the predicted next 30 days for one product."""
    p = Product.query.get_or_404(pid)
    cutoff = date.today() - timedelta(days=60)
    rows = (db.session.query(Sale.sale_date, func.sum(Sale.quantity))
            .filter(Sale.product_id == pid, Sale.sale_date >= cutoff)
            .group_by(Sale.sale_date).all())
    history = [{"date": d.strftime("%Y-%m-%d"), "qty": int(q)} for d, q in sorted(rows)]

    fc = Forecast.query.filter_by(product_id=pid).order_by(Forecast.forecast_date).all()
    forecast_rows = [{"date": f.forecast_date.strftime("%Y-%m-%d"),
                      "yhat": f.predicted_qty, "lower": f.lower, "upper": f.upper}
                     for f in fc]

    m = (ForecastMetric.query.filter_by(product_id=pid)
         .order_by(ForecastMetric.trained_at.desc()).first())
    metric = None
    if m:
        metric = {"mape": round(m.mape, 1) if m.mape is not None else None,
                  "mae": round(m.mae, 2) if m.mae is not None else None,
                  "rmse": round(m.rmse, 2) if m.rmse is not None else None}
    return jsonify(product=p.name, history=history, forecast=forecast_rows, metric=metric)


@api_bp.route("/anomalies")
@login_required
def anomalies():
    """Most recent unusual sales events flagged by the model."""
    items = AnomalyFlag.query.order_by(AnomalyFlag.flag_date.desc()).limit(50).all()
    return jsonify([{
        "id": a.id, "product": a.product.name if a.product else "—",
        "date": a.flag_date.strftime("%Y-%m-%d"), "quantity": a.quantity,
        "expected": a.expected, "reason": a.reason, "score": a.score,
    } for a in items])


@api_bp.route("/ai-summary")
@login_required
def ai_summary():
    """Headline AI numbers for the dashboard."""
    metrics = ForecastMetric.query.all()
    mapes = [m.mape for m in metrics if m.mape is not None]
    return jsonify(
        avg_mape=round(sum(mapes) / len(mapes), 1) if mapes else None,
        products_modelled=len(metrics),
        anomaly_count=AnomalyFlag.query.filter_by(resolved=False).count(),
    )


# ---------------------------------------------------------------------------
# Rich dashboard data (NetSuite-style home)
# ---------------------------------------------------------------------------
MONTH_ABBR = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _month_start(d):
    return date(d.year, d.month, 1)


def _add_months(d, n):
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, 1)


def _mkey(d):
    return f"{d.year:04d}-{d.month:02d}"


def _monthly_sales(months_back=12):
    """Aggregate sales into the last N calendar months (DB-agnostic)."""
    today = date.today()
    this_start = _month_start(today)
    range_start = _add_months(this_start, -(months_back - 1))
    rows = (db.session.query(Sale.sale_date, Sale.quantity, Sale.total)
            .filter(Sale.sale_date >= range_start).all())
    monthly = {}
    for d, qty, total in rows:
        m = monthly.setdefault(_mkey(d), {"orders": 0, "units": 0, "revenue": 0.0})
        m["orders"] += 1
        m["units"] += qty
        m["revenue"] += total
    keys = [_mkey(_add_months(this_start, -i)) for i in range(months_back - 1, -1, -1)]
    return this_start, keys, monthly


@api_bp.route("/kpis")
@login_required
def kpis():
    # Fair comparison: this month-to-date vs the SAME day range last month
    # (otherwise a partial current month always looks lower than a full one).
    today = date.today()
    this_start = _month_start(today)
    last_start = _add_months(this_start, -1)
    elapsed = (today - this_start).days
    prev_end = last_start + timedelta(days=elapsed)

    def totals(start, end):
        row = (db.session.query(func.count(Sale.id), func.sum(Sale.quantity),
                                func.sum(Sale.total))
               .filter(Sale.sale_date >= start, Sale.sale_date <= end).first())
        return {"orders": row[0] or 0, "units": int(row[1] or 0),
                "revenue": float(row[2] or 0)}

    cur_t, prev_t = totals(this_start, today), totals(last_start, prev_end)
    _, keys, monthly = _monthly_sales(12)

    def spark(metric):
        return [round(monthly.get(k, {}).get(metric, 0), 2) for k in keys[-6:]]

    def make(metric, label, money=False):
        c, p = cur_t[metric], prev_t[metric]
        change = round((c - p) / p * 100, 1) if p else None
        return {"label": label, "period": "Month-to-date vs last month",
                "current": round(c, 2), "previous": round(p, 2),
                "change": change, "spark": spark(metric), "money": money}

    fc_total = db.session.query(func.sum(Forecast.predicted_qty)).scalar() or 0
    kpi_list = [
        make("orders", "Orders"),
        make("revenue", "Revenue (GHS)", money=True),
        make("units", "Units sold"),
        {"label": "Forecast demand (next 30d)", "period": "AI prediction",
         "current": round(fc_total), "previous": None, "change": None,
         "spark": [], "money": False},
    ]

    products = Product.query.filter_by(is_active=True).all()
    stock_value = round(sum(p.stock_value for p in products), 2)
    gauge = {"value": stock_value, "max": max(round(stock_value * 1.4, -2), 1000),
             "label": "Inventory value (GHS)"}
    return jsonify(kpis=kpi_list, gauge=gauge)


@api_bp.route("/monthly-trend")
@login_required
def monthly_trend():
    this_start, keys, monthly = _monthly_sales(12)
    out = []
    for i, k in enumerate(keys):
        ms = _add_months(this_start, -(len(keys) - 1 - i))
        v = monthly.get(k, {})
        out.append({"month": MONTH_ABBR[ms.month],
                    "revenue": round(v.get("revenue", 0), 2),
                    "units": int(v.get("units", 0))})
    return jsonify(out)


@api_bp.route("/top-items")
@login_required
def top_items():
    cut = date.today() - timedelta(days=90)
    rows = (db.session.query(Product.name, func.sum(Sale.quantity))
            .join(Sale, Sale.product_id == Product.id)
            .filter(Sale.sale_date >= cut)
            .group_by(Product.name)
            .order_by(func.sum(Sale.quantity).desc()).limit(10).all())
    return jsonify([{"name": n, "qty": int(q)} for n, q in rows])


@api_bp.route("/reminders")
@login_required
def reminders():
    today = date.today()
    products = Product.query.filter_by(is_active=True).all()

    out_of_stock = sum(1 for p in products if p.current_stock <= 0)
    reorder = sum(1 for p in products if p.needs_restock)
    approaching = sum(1 for p in products if p.stock_status == "low")
    no_supplier = sum(1 for p in products if p.supplier_id is None)
    no_barcode = sum(1 for p in products if not p.sku)

    # AI reminder: items whose forecast demand over the next 7 days exceeds stock.
    next7 = today + timedelta(days=7)
    fc = (db.session.query(Forecast.product_id, func.sum(Forecast.predicted_qty))
          .filter(Forecast.forecast_date <= next7).group_by(Forecast.product_id).all())
    fc_map = {pid: float(t or 0) for pid, t in fc}
    predicted_out = sum(1 for p in products if fc_map.get(p.id, 0) > p.current_stock)

    cut30 = today - timedelta(days=30)
    sold_ids = {pid for (pid,) in db.session.query(Sale.product_id)
                .filter(Sale.sale_date >= cut30).distinct()}
    slow_movers = sum(1 for p in products if p.id not in sold_ids)

    sales_today = Sale.query.filter_by(sale_date=today).count()
    cut7 = today - timedelta(days=7)
    spikes = AnomalyFlag.query.filter(AnomalyFlag.flag_date >= cut7,
                                      AnomalyFlag.reason == "spike").count()
    drops = AnomalyFlag.query.filter(AnomalyFlag.flag_date >= cut7,
                                     AnomalyFlag.reason == "drop").count()
    anomalies = AnomalyFlag.query.filter_by(resolved=False).count()

    featured = [
        {"label": "Products out of stock", "count": out_of_stock, "color": "danger", "href": "/products"},
        {"label": "Items to reorder", "count": reorder, "color": "warning", "href": "/products"},
        {"label": "Predicted to run out (7 days)", "count": predicted_out, "color": "danger", "href": "/dashboard"},
        {"label": "Anomaly alerts to review", "count": anomalies, "color": "info", "href": "/dashboard"},
    ]
    listed = [
        {"label": "Approaching reorder point", "count": approaching, "color": "warning", "href": "/products"},
        {"label": "Sales recorded today", "count": sales_today, "color": "info", "href": "/sales"},
        {"label": "Demand spikes (last 7 days)", "count": spikes, "color": "warning", "href": "/dashboard"},
        {"label": "Demand drops (last 7 days)", "count": drops, "color": "secondary", "href": "/dashboard"},
        {"label": "Slow movers (no sale in 30 days)", "count": slow_movers, "color": "secondary", "href": "/products"},
        {"label": "Products without a supplier", "count": no_supplier, "color": "secondary", "href": "/products"},
        {"label": "Products without a barcode", "count": no_barcode, "color": "secondary", "href": "/products"},
    ]
    return jsonify(featured=featured, list=listed)


# ---------------------------------------------------------------------------
# Redesigned "Overview" dashboard data
# ---------------------------------------------------------------------------
@api_bp.route("/overview")
@login_required
def overview():
    today = date.today()
    products = Product.query.filter_by(is_active=True).all()
    total = len(products) or 1
    ok = sum(1 for p in products if p.stock_status == "ok")
    units_in_stock = sum(p.current_stock for p in products)
    stockout_risk = sum(1 for p in products if p.needs_restock)

    # Forecasted revenue (next 30 days) = sum(predicted_qty * selling price)
    price_by_pid = {p.id: (p.unit_price or 0) for p in products}
    fc_rows = (db.session.query(Forecast.product_id, func.sum(Forecast.predicted_qty))
               .group_by(Forecast.product_id).all())
    forecasted_revenue = round(sum(float(t or 0) * price_by_pid.get(pid, 0)
                                   for pid, t in fc_rows), 2)

    # Forecast accuracy from the back-tested metrics
    mapes = [m.mape for m in ForecastMetric.query.all() if m.mape is not None]
    avg_mape = round(sum(mapes) / len(mapes), 1) if mapes else None
    accuracy = round(100 - avg_mape, 1) if avg_mape is not None else None

    # Revenue change: this month-to-date vs the same days last month
    this_start = _month_start(today)
    last_start = _add_months(this_start, -1)
    prev_end = last_start + timedelta(days=(today - this_start).days)

    def rev(a, b):
        return float(db.session.query(func.sum(Sale.total))
                     .filter(Sale.sale_date >= a, Sale.sale_date <= b).scalar() or 0)
    cur_rev, prev_rev = rev(this_start, today), rev(last_start, prev_end)
    rev_change = round((cur_rev - prev_rev) / prev_rev * 100, 1) if prev_rev else None

    first_name = (current_user.name or "there").split()[0]
    return jsonify(
        user_first=first_name,
        date=today.strftime("%A, %B ") + str(today.day),
        optimal_pct=round(ok / total * 100),
        kpis={
            "forecasted_revenue": {"value": forecasted_revenue, "change": rev_change, "sub": "Next 30 days"},
            "units_in_stock": {"value": units_in_stock, "change": None, "sub": f"Across {total} SKUs"},
            "stockout_risk": {"value": stockout_risk, "change": None, "sub": "Reorder suggested"},
            "forecast_accuracy": {"value": accuracy, "change": None,
                                  "sub": f"MAPE: {avg_mape}%" if avg_mape is not None else "—"},
        },
    )


@api_bp.route("/inventory-intelligence")
@login_required
def inventory_intelligence():
    next7 = date.today() + timedelta(days=7)
    fc = (db.session.query(Forecast.product_id, func.sum(Forecast.predicted_qty))
          .filter(Forecast.forecast_date <= next7).group_by(Forecast.product_id).all())
    demand = {pid: float(t or 0) for pid, t in fc}
    labels = {"ok": "Healthy", "low": "Low", "reorder": "Critical"}
    rows = []
    for p in Product.query.filter_by(is_active=True).order_by(Product.name):
        target = max(p.reorder_point * 2.5, 1)
        rows.append({
            "id": p.id, "name": p.name, "sku": p.sku or "—",
            "stock": p.current_stock,
            "stock_pct": min(100, round(p.current_stock / target * 100)),
            "status": labels[p.stock_status],
            "predicted": round(demand.get(p.id, 0)),
        })
    return jsonify(rows)
