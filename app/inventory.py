"""Inventory module: products, stock movements, suppliers, categories,
sales history and the audit log."""
from datetime import date

from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, DecimalField, SelectField,
                     SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Optional, Email, Length, NumberRange

from app import db
from app.decorators import role_required
from app.models import (Product, Category, Supplier, Sale, StockMovement,
                        log_audit, ROLE_OWNER, ROLE_MANAGER, ROLE_STAFF)

inventory_bp = Blueprint("inventory", __name__)

# Who can do what (matches the report's role descriptions).
CAN_EDIT_PRODUCTS = (ROLE_STAFF, ROLE_MANAGER)        # add/edit products + record stock
CAN_MANAGE = (ROLE_MANAGER, ROLE_OWNER)               # delete, suppliers, categories, audit


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------
class ProductForm(FlaskForm):
    name = StringField("Product name", validators=[DataRequired(), Length(max=120)])
    sku = StringField("Barcode / SKU", validators=[Optional(), Length(max=64)])
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    supplier_id = SelectField("Supplier", coerce=int, validators=[Optional()])
    unit_price = DecimalField("Selling price (GHS)", places=2,
                              validators=[DataRequired(), NumberRange(min=0)])
    cost_price = DecimalField("Cost price (GHS)", places=2, default=0,
                              validators=[Optional(), NumberRange(min=0)])
    reorder_point = IntegerField("Reorder point", default=10,
                                 validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField("Unit (e.g. pcs, kg)", default="pcs",
                       validators=[Optional(), Length(max=16)])
    submit = SubmitField("Save product")


class SupplierForm(FlaskForm):
    name = StringField("Supplier name", validators=[DataRequired(), Length(max=120)])
    contact_person = StringField("Contact person", validators=[Optional(), Length(max=120)])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    lead_time_days = IntegerField("Lead time (days)", default=7,
                                  validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("Save supplier")


class CategoryForm(FlaskForm):
    name = StringField("Category name", validators=[DataRequired(), Length(max=80)])
    description = StringField("Description", validators=[Optional(), Length(max=200)])
    submit = SubmitField("Add category")


def _populate_choices(form):
    form.category_id.choices = [(0, "— none —")] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name)]
    form.supplier_id.choices = [(0, "— none —")] + [
        (s.id, s.name) for s in Supplier.query.order_by(Supplier.name)]


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
@inventory_bp.route("/products")
@login_required
def products():
    q = request.args.get("q", "").strip()
    query = Product.query.filter_by(is_active=True)
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Product.name.ilike(like), Product.sku.ilike(like)))
    items = query.order_by(Product.name).all()
    return render_template("inventory/products.html", products=items, q=q,
                           can_edit=current_user.role in CAN_EDIT_PRODUCTS,
                           can_manage=current_user.role in CAN_MANAGE)


@inventory_bp.route("/scan")
@login_required
def scan():
    """Barcode scan: a USB scanner types the code + Enter, or use the webcam.
    Looks the product up by barcode (or name) and shows its actions."""
    code = request.args.get("code", "").strip()
    product = None
    if code:
        product = Product.query.filter_by(sku=code, is_active=True).first()
        if product is None:
            product = Product.query.filter(Product.is_active.is_(True),
                                           Product.name.ilike(f"%{code}%")).first()
    return render_template("inventory/scan.html", code=code, product=product,
                           searched=bool(code),
                           can_edit=current_user.role in CAN_EDIT_PRODUCTS)


@inventory_bp.route("/products/new", methods=["GET", "POST"])
@role_required(*CAN_EDIT_PRODUCTS)
def product_new():
    form = ProductForm()
    _populate_choices(form)
    if form.validate_on_submit():
        sku = (form.sku.data or "").strip() or None
        if sku and Product.query.filter_by(sku=sku).first():
            flash("A product with that barcode already exists.", "danger")
        else:
            p = Product(
                name=form.name.data.strip(),
                sku=sku,
                category_id=form.category_id.data or None,
                supplier_id=form.supplier_id.data or None,
                unit_price=float(form.unit_price.data),
                cost_price=float(form.cost_price.data or 0),
                reorder_point=form.reorder_point.data,
                unit=(form.unit.data or "pcs").strip(),
            )
            db.session.add(p)
            db.session.flush()
            log_audit("product.create", f"Created product '{p.name}' (#{p.id})")
            db.session.commit()
            flash("Product added.", "success")
            return redirect(url_for("inventory.products"))
    return render_template("inventory/product_form.html", form=form, title="New product")


@inventory_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@role_required(*CAN_EDIT_PRODUCTS)
def product_edit(pid):
    p = Product.query.get_or_404(pid)
    form = ProductForm(obj=p)
    _populate_choices(form)
    if request.method == "GET":
        form.category_id.data = p.category_id or 0
        form.supplier_id.data = p.supplier_id or 0
    if form.validate_on_submit():
        sku = (form.sku.data or "").strip() or None
        clash = Product.query.filter(Product.sku == sku, Product.id != p.id).first()
        if sku and clash:
            flash("Another product already uses that barcode.", "danger")
        else:
            p.name = form.name.data.strip()
            p.sku = sku
            p.category_id = form.category_id.data or None
            p.supplier_id = form.supplier_id.data or None
            p.unit_price = float(form.unit_price.data)
            p.cost_price = float(form.cost_price.data or 0)
            p.reorder_point = form.reorder_point.data
            p.unit = (form.unit.data or "pcs").strip()
            log_audit("product.edit", f"Edited product '{p.name}' (#{p.id})")
            db.session.commit()
            flash("Product updated.", "success")
            return redirect(url_for("inventory.products"))
    return render_template("inventory/product_form.html", form=form,
                           title=f"Edit — {p.name}", product=p)


@inventory_bp.route("/products/<int:pid>/delete", methods=["POST"])
@role_required(*CAN_MANAGE)
def product_delete(pid):
    p = Product.query.get_or_404(pid)
    p.is_active = False
    log_audit("product.delete", f"Removed product '{p.name}' (#{p.id})")
    db.session.commit()
    flash(f"'{p.name}' removed from the catalogue.", "info")
    return redirect(url_for("inventory.products"))


# ---------------------------------------------------------------------------
# Stock movements: receive / sell / adjust
# ---------------------------------------------------------------------------
@inventory_bp.route("/products/<int:pid>/receive", methods=["GET", "POST"])
@role_required(*CAN_EDIT_PRODUCTS)
def stock_receive(pid):
    p = Product.query.get_or_404(pid)
    if request.method == "POST":
        qty = request.form.get("quantity", type=int)
        note = request.form.get("note", "").strip()
        if not qty or qty <= 0:
            flash("Enter a quantity greater than zero.", "danger")
        else:
            p.current_stock += qty
            db.session.add(StockMovement(product_id=p.id, movement_type="stock_in",
                                         quantity=qty, stock_after=p.current_stock,
                                         note=note, user_id=current_user.id))
            log_audit("stock.receive", f"Received {qty} {p.unit} of '{p.name}' (now {p.current_stock})")
            db.session.commit()
            flash(f"Received {qty} units. New stock: {p.current_stock}.", "success")
            return redirect(url_for("inventory.products"))
    return render_template("inventory/movement_form.html", product=p, action="receive",
                           title=f"Receive stock — {p.name}")


@inventory_bp.route("/products/<int:pid>/sell", methods=["GET", "POST"])
@role_required(*CAN_EDIT_PRODUCTS)
def stock_sell(pid):
    p = Product.query.get_or_404(pid)
    if request.method == "POST":
        qty = request.form.get("quantity", type=int)
        price = request.form.get("unit_price", type=float)
        if price is None:
            price = p.unit_price
        if not qty or qty <= 0:
            flash("Enter a quantity greater than zero.", "danger")
        elif qty > p.current_stock:
            flash(f"Not enough stock — only {p.current_stock} {p.unit} available.", "danger")
        else:
            p.current_stock -= qty
            db.session.add(Sale(product_id=p.id, quantity=qty, unit_price=price,
                                total=round(price * qty, 2), sale_date=date.today(),
                                user_id=current_user.id))
            db.session.add(StockMovement(product_id=p.id, movement_type="sale",
                                         quantity=-qty, stock_after=p.current_stock,
                                         unit_price=price, user_id=current_user.id))
            log_audit("sale.record", f"Sold {qty} {p.unit} of '{p.name}' @ GHS {price:.2f}")
            db.session.commit()
            flash(f"Sale recorded. {p.name} stock is now {p.current_stock}.", "success")
            return redirect(url_for("inventory.products"))
    return render_template("inventory/movement_form.html", product=p, action="sell",
                           title=f"Record sale — {p.name}")


@inventory_bp.route("/products/<int:pid>/adjust", methods=["GET", "POST"])
@role_required(*CAN_EDIT_PRODUCTS)
def stock_adjust(pid):
    p = Product.query.get_or_404(pid)
    if request.method == "POST":
        new_count = request.form.get("new_count", type=int)
        note = request.form.get("note", "").strip()
        if new_count is None or new_count < 0:
            flash("Enter the new counted stock (zero or more).", "danger")
        else:
            old = p.current_stock
            delta = new_count - old
            p.current_stock = new_count
            db.session.add(StockMovement(product_id=p.id, movement_type="adjustment",
                                         quantity=delta, stock_after=new_count,
                                         note=note, user_id=current_user.id))
            log_audit("stock.adjust", f"Adjusted '{p.name}' from {old} to {new_count} (delta {delta:+d})")
            db.session.commit()
            flash(f"Stock for {p.name} set to {new_count}.", "success")
            return redirect(url_for("inventory.products"))
    return render_template("inventory/movement_form.html", product=p, action="adjust",
                           title=f"Adjust stock — {p.name}")


@inventory_bp.route("/movements")
@login_required
def movements():
    items = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(300).all()
    return render_template("inventory/movements.html", movements=items)


@inventory_bp.route("/sales")
@login_required
def sales():
    items = Sale.query.order_by(Sale.created_at.desc()).limit(300).all()
    revenue = round(sum(s.total for s in items), 2)
    return render_template("inventory/sales.html", sales=items, revenue=revenue)


# ---------------------------------------------------------------------------
# Suppliers
# ---------------------------------------------------------------------------
@inventory_bp.route("/suppliers")
@login_required
def suppliers():
    items = Supplier.query.order_by(Supplier.name).all()
    return render_template("inventory/suppliers.html", suppliers=items,
                           can_manage=current_user.role in CAN_MANAGE)


@inventory_bp.route("/suppliers/new", methods=["GET", "POST"])
@role_required(*CAN_MANAGE)
def supplier_new():
    form = SupplierForm()
    if form.validate_on_submit():
        s = Supplier(name=form.name.data.strip(), contact_person=form.contact_person.data,
                     phone=form.phone.data, email=form.email.data,
                     lead_time_days=form.lead_time_days.data or 7)
        db.session.add(s)
        db.session.flush()
        log_audit("supplier.create", f"Added supplier '{s.name}'")
        db.session.commit()
        flash("Supplier added.", "success")
        return redirect(url_for("inventory.suppliers"))
    return render_template("inventory/supplier_form.html", form=form, title="New supplier")


@inventory_bp.route("/suppliers/<int:sid>/edit", methods=["GET", "POST"])
@role_required(*CAN_MANAGE)
def supplier_edit(sid):
    s = Supplier.query.get_or_404(sid)
    form = SupplierForm(obj=s)
    if form.validate_on_submit():
        s.name = form.name.data.strip()
        s.contact_person = form.contact_person.data
        s.phone = form.phone.data
        s.email = form.email.data
        s.lead_time_days = form.lead_time_days.data or 7
        log_audit("supplier.edit", f"Edited supplier '{s.name}'")
        db.session.commit()
        flash("Supplier updated.", "success")
        return redirect(url_for("inventory.suppliers"))
    return render_template("inventory/supplier_form.html", form=form, title=f"Edit — {s.name}")


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
@inventory_bp.route("/categories", methods=["GET", "POST"])
@role_required(*CAN_MANAGE)
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data.strip()).first():
            flash("That category already exists.", "warning")
        else:
            c = Category(name=form.name.data.strip(), description=form.description.data)
            db.session.add(c)
            db.session.flush()
            log_audit("category.create", f"Added category '{c.name}'")
            db.session.commit()
            flash("Category added.", "success")
        return redirect(url_for("inventory.categories"))
    items = Category.query.order_by(Category.name).all()
    return render_template("inventory/categories.html", form=form, categories=items)


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------
@inventory_bp.route("/audit")
@role_required(*CAN_MANAGE)
def audit():
    from app.models import AuditLog
    items = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(300).all()
    return render_template("inventory/audit.html", logs=items)
