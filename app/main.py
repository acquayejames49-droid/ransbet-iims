"""Main pages.

The dashboard is now a React app. Flask serves the compiled React files
(built into app/static/dashboard). If that build doesn't exist yet, it falls
back to the original server-rendered dashboard so the app never breaks.
"""
import os
from datetime import date

from flask import Blueprint, render_template, send_from_directory, current_app
from flask_login import login_required

from app.models import Product, Sale

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    build_dir = os.path.join(current_app.static_folder, "dashboard")
    index_file = os.path.join(build_dir, "index.html")
    if os.path.exists(index_file):
        return send_from_directory(build_dir, "index.html")

    # Fallback: server-rendered dashboard (used before the React build exists).
    products = Product.query.filter_by(is_active=True).all()
    low_stock = [p for p in products if p.needs_restock]
    today_sales = Sale.query.filter_by(sale_date=date.today()).all()
    return render_template(
        "dashboard.html",
        total_products=len(products),
        low_stock=low_stock,
        low_stock_count=len(low_stock),
        stock_value=round(sum(p.stock_value for p in products), 2),
        today_revenue=round(sum(s.total for s in today_sales), 2),
        today_units=sum(s.quantity for s in today_sales),
    )
