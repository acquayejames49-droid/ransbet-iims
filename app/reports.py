"""Report exports: inventory, sales, and forecast-accuracy as CSV or PDF."""
import io
from datetime import datetime, date, timedelta

import pandas as pd
from flask import Blueprint, render_template, request, send_file, Response
from flask_login import login_required
from sqlalchemy import func

from app import db
from app.models import Product, Sale, ForecastMetric

reports_bp = Blueprint("reports", __name__)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _csv(df, filename):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


def _pdf(title, headers, rows, filename, summary=None):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer)
    from reportlab.lib.styles import getSampleStyleSheet

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            topMargin=1.4 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"Ransbet IIMS &mdash; {title}", styles["Title"]),
        Paragraph(datetime.now().strftime("Generated %d %b %Y, %H:%M"), styles["Normal"]),
        Spacer(1, 10),
    ]
    if summary:
        story.append(Paragraph(summary, styles["Heading4"]))
        story.append(Spacer(1, 8))

    data = [headers] + [[str(c) for c in r] for r in rows]
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#15803d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdf4")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(table)
    doc.build(story)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True,
                     download_name=filename)


def _date_range():
    today = date.today()
    try:
        start = datetime.strptime(request.args.get("start"), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        start = today - timedelta(days=30)
    try:
        end = datetime.strptime(request.args.get("end"), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        end = today
    return start, end


# ---------------------------------------------------------------------------
# pages & data builders
# ---------------------------------------------------------------------------
@reports_bp.route("/reports")
@login_required
def reports_home():
    today = date.today()
    return render_template("reports.html",
                           default_start=(today - timedelta(days=30)).isoformat(),
                           default_end=today.isoformat())


def _inventory_rows():
    rows = []
    for p in Product.query.filter_by(is_active=True).order_by(Product.name):
        rows.append([p.name, p.category.name if p.category else "",
                     p.current_stock, p.reorder_point, f"{p.unit_price:.2f}",
                     f"{p.cost_price:.2f}", f"{p.stock_value:.2f}", p.status_label])
    return rows


INV_HEADERS = ["Product", "Category", "Stock", "Reorder pt", "Price",
               "Cost", "Stock value", "Status"]


@reports_bp.route("/reports/inventory.csv")
@login_required
def inventory_csv():
    df = pd.DataFrame(_inventory_rows(), columns=INV_HEADERS)
    return _csv(df, "inventory_report.csv")


@reports_bp.route("/reports/inventory.pdf")
@login_required
def inventory_pdf():
    rows = _inventory_rows()
    total_value = sum(float(r[6]) for r in rows)
    summary = f"{len(rows)} active products &nbsp;|&nbsp; Total stock value: GHS {total_value:,.2f}"
    return _pdf("Inventory Report", INV_HEADERS, rows, "inventory_report.pdf", summary)


SALES_HEADERS = ["Date", "Product", "Qty", "Unit price", "Total"]


def _sales_rows(start, end):
    q = (db.session.query(Sale.sale_date, Product.name, Sale.quantity,
                          Sale.unit_price, Sale.total)
         .join(Product, Product.id == Sale.product_id)
         .filter(Sale.sale_date >= start, Sale.sale_date <= end)
         .order_by(Sale.sale_date.desc()))
    return [[d.isoformat(), n, q_, f"{up:.2f}", f"{t:.2f}"]
            for d, n, q_, up, t in q.all()]


@reports_bp.route("/reports/sales.csv")
@login_required
def sales_csv():
    start, end = _date_range()
    df = pd.DataFrame(_sales_rows(start, end), columns=SALES_HEADERS)
    return _csv(df, f"sales_{start}_{end}.csv")


@reports_bp.route("/reports/sales.pdf")
@login_required
def sales_pdf():
    start, end = _date_range()
    rows = _sales_rows(start, end)
    revenue = sum(float(r[4]) for r in rows)
    units = sum(int(r[2]) for r in rows)
    summary = (f"Period: {start} to {end} &nbsp;|&nbsp; {len(rows)} sales &nbsp;|&nbsp; "
               f"{units} units &nbsp;|&nbsp; Revenue: GHS {revenue:,.2f}")
    # Cap PDF rows so a 2-year export doesn't make a giant file.
    return _pdf("Sales Report", SALES_HEADERS, rows[:600],
                f"sales_{start}_{end}.pdf", summary)


FC_HEADERS = ["Product", "MAPE (%)", "MAE (units)", "RMSE", "Accuracy"]


def _forecast_rows():
    rows = []
    for m in ForecastMetric.query.join(Product).order_by(Product.name):
        acc = f"{max(0, 100 - m.mape):.1f}%" if m.mape is not None else "n/a"
        rows.append([m.product.name,
                     f"{m.mape:.1f}" if m.mape is not None else "n/a",
                     f"{m.mae:.2f}" if m.mae is not None else "n/a",
                     f"{m.rmse:.2f}" if m.rmse is not None else "n/a", acc])
    return rows


@reports_bp.route("/reports/forecast.csv")
@login_required
def forecast_csv():
    df = pd.DataFrame(_forecast_rows(), columns=FC_HEADERS)
    return _csv(df, "forecast_accuracy.csv")


@reports_bp.route("/reports/forecast.pdf")
@login_required
def forecast_pdf():
    rows = _forecast_rows()
    mapes = [float(r[1]) for r in rows if r[1] != "n/a"]
    avg = sum(mapes) / len(mapes) if mapes else 0
    summary = f"{len(rows)} products modelled &nbsp;|&nbsp; Average MAPE: {avg:.1f}% (accuracy {100 - avg:.1f}%)"
    return _pdf("Forecast Accuracy Report", FC_HEADERS, rows,
                "forecast_accuracy.pdf", summary)
