"""Bulk data tools: import a whole catalogue from CSV/Excel, download
templates, export the current catalogue, and clear data.

This is how Ransbet's real catalogue (thousands of products) gets loaded
without typing each item by hand.
"""
import io
from datetime import datetime

import pandas as pd
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, Response)
from flask_login import current_user

from app import db
from app.decorators import role_required
from app.models import (Product, Category, Supplier, Sale, StockMovement,
                        AuditLog, log_audit, ROLE_MANAGER, ROLE_OWNER)

data_bp = Blueprint("data", __name__)
ADMINS = (ROLE_MANAGER, ROLE_OWNER)

# Accept friendly header variations -> our internal field name.
PRODUCT_ALIASES = {
    "name": "name", "product": "name", "product_name": "name", "item": "name",
    "sku": "sku", "barcode": "sku", "code": "sku",
    "category": "category", "category_name": "category",
    "supplier": "supplier", "supplier_name": "supplier", "vendor": "supplier",
    "unit_price": "unit_price", "price": "unit_price", "selling_price": "unit_price",
    "cost_price": "cost_price", "cost": "cost_price", "buying_price": "cost_price",
    "current_stock": "current_stock", "stock": "current_stock", "quantity": "current_stock",
    "qty": "current_stock", "on_hand": "current_stock",
    "reorder_point": "reorder_point", "reorder": "reorder_point",
    "min_stock": "reorder_point", "minimum_stock": "reorder_point",
    "unit": "unit", "uom": "unit",
}

SALES_ALIASES = {
    "date": "date", "sale_date": "date", "day": "date",
    "sku": "sku", "barcode": "sku", "code": "sku",
    "product": "product", "product_name": "product", "name": "product", "item": "product",
    "quantity": "quantity", "qty": "quantity", "units": "quantity", "units_sold": "quantity",
    "unit_price": "unit_price", "price": "unit_price",
}


def _read_upload(file_storage):
    """Read an uploaded CSV or Excel file into a pandas DataFrame."""
    fname = (file_storage.filename or "").lower()
    raw = file_storage.read()
    if fname.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(raw))
    return pd.read_csv(io.BytesIO(raw))


def _normalise_columns(df, aliases):
    """Lower-case headers and rename known aliases to our field names."""
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df.rename(columns={c: aliases[c] for c in df.columns if c in aliases})


def _num(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
@data_bp.route("/data")
@role_required(*ADMINS)
def data_home():
    return render_template("inventory/data.html",
                           counts={
                               "products": Product.query.count(),
                               "suppliers": Supplier.query.count(),
                               "categories": Category.query.count(),
                               "sales": Sale.query.count(),
                           })


# --------------------------- IMPORT PRODUCTS -------------------------------
@data_bp.route("/data/import-products", methods=["POST"])
@role_required(*ADMINS)
def import_products():
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Please choose a CSV or Excel file.", "danger")
        return redirect(url_for("data.data_home"))

    try:
        df = _normalise_columns(_read_upload(file), PRODUCT_ALIASES)
    except Exception as exc:
        flash(f"Could not read the file: {exc}", "danger")
        return redirect(url_for("data.data_home"))

    if "name" not in df.columns:
        flash("The file must have at least a 'name' column.", "danger")
        return redirect(url_for("data.data_home"))

    # Cache categories/suppliers so we only query each once.
    cat_cache = {c.name.lower(): c for c in Category.query.all()}
    sup_cache = {s.name.lower(): s for s in Supplier.query.all()}

    def get_category(name):
        if not name or pd.isna(name):
            return None
        key = str(name).strip().lower()
        if key not in cat_cache:
            c = Category(name=str(name).strip())
            db.session.add(c)
            db.session.flush()
            cat_cache[key] = c
        return cat_cache[key]

    def get_supplier(name):
        if not name or pd.isna(name):
            return None
        key = str(name).strip().lower()
        if key not in sup_cache:
            s = Supplier(name=str(name).strip())
            db.session.add(s)
            db.session.flush()
            sup_cache[key] = s
        return sup_cache[key]

    created = updated = skipped = 0
    for _, row in df.iterrows():
        name = row.get("name")
        if not name or pd.isna(name):
            skipped += 1
            continue
        name = str(name).strip()
        sku = row.get("sku")
        sku = None if (sku is None or pd.isna(sku)) else str(sku).strip()

        # Find existing product by SKU first, then by name.
        product = None
        if sku:
            product = Product.query.filter_by(sku=sku).first()
        if product is None:
            product = Product.query.filter_by(name=name).first()

        if product is None:
            product = Product(name=name, is_active=True)
            db.session.add(product)
            created += 1
        else:
            product.is_active = True
            updated += 1

        product.name = name
        if sku:
            product.sku = sku
        cat = get_category(row.get("category"))
        sup = get_supplier(row.get("supplier"))
        if cat:
            product.category_id = cat.id
        if sup:
            product.supplier_id = sup.id
        if "unit_price" in df.columns:
            product.unit_price = _num(row.get("unit_price"))
        if "cost_price" in df.columns:
            product.cost_price = _num(row.get("cost_price"))
        if "current_stock" in df.columns:
            product.current_stock = int(_num(row.get("current_stock")))
        if "reorder_point" in df.columns:
            product.reorder_point = int(_num(row.get("reorder_point"), 10))
        if "unit" in df.columns and not pd.isna(row.get("unit")):
            product.unit = str(row.get("unit")).strip()

    log_audit("data.import_products",
              f"Imported products ({created} new, {updated} updated)")
    db.session.commit()
    flash(f"Import complete: {created} new, {updated} updated, {skipped} skipped.", "success")
    return redirect(url_for("data.data_home"))


# ----------------------------- IMPORT SALES --------------------------------
@data_bp.route("/data/import-sales", methods=["POST"])
@role_required(*ADMINS)
def import_sales():
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Please choose a CSV or Excel file.", "danger")
        return redirect(url_for("data.data_home"))
    try:
        df = _normalise_columns(_read_upload(file), SALES_ALIASES)
    except Exception as exc:
        flash(f"Could not read the file: {exc}", "danger")
        return redirect(url_for("data.data_home"))

    by_sku = {p.sku: p for p in Product.query.filter(Product.sku.isnot(None))}
    by_name = {p.name.lower(): p for p in Product.query.all()}

    added = skipped = 0
    new_sales = []
    for _, row in df.iterrows():
        product = None
        if "sku" in df.columns and not pd.isna(row.get("sku")):
            product = by_sku.get(str(row.get("sku")).strip())
        if product is None and "product" in df.columns and not pd.isna(row.get("product")):
            product = by_name.get(str(row.get("product")).strip().lower())
        if product is None:
            skipped += 1
            continue
        try:
            qty = int(_num(row.get("quantity")))
            if qty <= 0:
                skipped += 1
                continue
            sale_date = pd.to_datetime(row.get("date")).date()
        except Exception:
            skipped += 1
            continue
        price = _num(row.get("unit_price"), product.unit_price) if "unit_price" in df.columns else product.unit_price
        new_sales.append(Sale(product_id=product.id, quantity=qty, unit_price=price,
                              total=round(price * qty, 2), sale_date=sale_date))
        added += 1

    db.session.bulk_save_objects(new_sales)
    log_audit("data.import_sales", f"Imported {added} historical sales records")
    db.session.commit()
    flash(f"Sales import complete: {added} added, {skipped} skipped.", "success")
    return redirect(url_for("data.data_home"))


# ----------------------------- TEMPLATES / EXPORT --------------------------
def _csv_response(df, filename):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@data_bp.route("/data/template/products")
@role_required(*ADMINS)
def template_products():
    df = pd.DataFrame([{
        "name": "Example Product 1L", "sku": "1234567890123", "category": "Beverages",
        "supplier": "Accra Distributors Ltd", "unit_price": 12.50, "cost_price": 9.00,
        "current_stock": 50, "reorder_point": 15, "unit": "pcs",
    }])
    return _csv_response(df, "products_template.csv")


@data_bp.route("/data/template/sales")
@role_required(*ADMINS)
def template_sales():
    df = pd.DataFrame([
        {"date": "2025-01-15", "sku": "1234567890123", "product": "Example Product 1L",
         "quantity": 3, "unit_price": 12.50},
    ])
    return _csv_response(df, "sales_template.csv")


@data_bp.route("/data/export/products")
@role_required(*ADMINS)
def export_products():
    rows = []
    for p in Product.query.filter_by(is_active=True).order_by(Product.name):
        rows.append({
            "name": p.name, "sku": p.sku, "category": p.category.name if p.category else "",
            "supplier": p.supplier.name if p.supplier else "", "unit_price": p.unit_price,
            "cost_price": p.cost_price, "current_stock": p.current_stock,
            "reorder_point": p.reorder_point, "unit": p.unit,
        })
    df = pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["name", "sku", "category", "supplier", "unit_price", "cost_price",
                 "current_stock", "reorder_point", "unit"])
    stamp = datetime.now().strftime("%Y%m%d")
    return _csv_response(df, f"ransbet_catalogue_{stamp}.csv")


# ------------------------------ DANGER ZONE --------------------------------
@data_bp.route("/data/clear", methods=["POST"])
@role_required(*ADMINS)
def clear_data():
    if request.form.get("confirm") != "DELETE":
        flash('Type DELETE to confirm clearing data.', "warning")
        return redirect(url_for("data.data_home"))

    scope = request.form.get("scope", "all")
    # Always remove things that reference products first (foreign keys).
    Sale.query.delete()
    StockMovement.query.delete()
    if scope == "all":
        Product.query.delete()
        Supplier.query.delete()
        Category.query.delete()
        msg = "All products, suppliers, categories, sales and movements deleted."
    else:  # scope == "transactions" -> keep catalogue, wipe history + reset stock
        for p in Product.query.all():
            p.current_stock = 0
        msg = "All sales and stock movements deleted; stock reset to zero."

    log_audit("data.clear", msg)
    db.session.commit()
    flash(msg + " You can now import Ransbet's real data.", "info")
    return redirect(url_for("data.data_home"))
