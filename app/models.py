"""Database models (tables) for the IIMS.

Entities (from the project report): users, categories, suppliers, products,
sales, inventory entries (stock movements), and an audit log. Forecast and
anomaly tables are added in Phase 4.
"""
from datetime import datetime, date

from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
ROLE_OWNER = "owner"      # Business Owner — views reports & trends
ROLE_MANAGER = "manager"  # Store Manager — full operations + approvals
ROLE_STAFF = "staff"      # Inventory Staff — records stock & sales
ROLES = [ROLE_OWNER, ROLE_MANAGER, ROLE_STAFF]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STAFF)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        return self.role in roles

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Inventory catalogue
# ---------------------------------------------------------------------------
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200))
    products = db.relationship("Product", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact_person = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    email = db.Column(db.String(120))
    lead_time_days = db.Column(db.Integer, default=7)  # days to deliver a restock
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship("Product", backref="supplier", lazy=True)

    def __repr__(self):
        return f"<Supplier {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    sku = db.Column(db.String(64), unique=True, index=True)  # barcode
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"))
    unit_price = db.Column(db.Float, default=0.0)   # selling price
    cost_price = db.Column(db.Float, default=0.0)   # purchase price
    current_stock = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=10)
    unit = db.Column(db.String(16), default="pcs")
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- computed helpers used by the dashboard & lists ---
    @property
    def stock_status(self):
        """'reorder' (red), 'low' (yellow) or 'ok' (green)."""
        if self.current_stock <= self.reorder_point:
            return "reorder"
        if self.current_stock <= self.reorder_point * 1.5:
            return "low"
        return "ok"

    @property
    def status_color(self):
        return {"reorder": "danger", "low": "warning", "ok": "success"}[self.stock_status]

    @property
    def status_label(self):
        return {"reorder": "Reorder now", "low": "Low", "ok": "In stock"}[self.stock_status]

    @property
    def needs_restock(self):
        return self.current_stock <= self.reorder_point

    @property
    def suggested_reorder_qty(self):
        """Simple suggestion: top back up to twice the reorder point."""
        return max(self.reorder_point * 2 - self.current_stock, 0)

    @property
    def stock_value(self):
        return round((self.cost_price or 0) * self.current_stock, 2)

    def __repr__(self):
        return f"<Product {self.name} stock={self.current_stock}>"


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------
class Sale(db.Model):
    """One sale line — this is the history the demand forecast trains on."""
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.Date, default=date.today, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")


class StockMovement(db.Model):
    """The inventory ledger: every change to stock (in / sale / adjustment)."""
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    movement_type = db.Column(db.String(20), nullable=False)  # stock_in | sale | adjustment
    quantity = db.Column(db.Integer, nullable=False)          # signed change to stock
    stock_after = db.Column(db.Integer, nullable=False)       # resulting stock level
    unit_price = db.Column(db.Float)
    note = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    product = db.relationship("Product")
    user = db.relationship("User")


class AuditLog(db.Model):
    """Records every significant action with who did it and when."""
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User")


def log_audit(action, description):
    """Add an audit entry for the current user. Caller is responsible for commit."""
    entry = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        description=description,
    )
    db.session.add(entry)
    return entry


# ---------------------------------------------------------------------------
# AI / Machine Learning outputs (Phase 4)
# ---------------------------------------------------------------------------
class Forecast(db.Model):
    """Predicted daily demand per product, produced by the Prophet model."""
    __tablename__ = "forecasts"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    forecast_date = db.Column(db.Date, nullable=False, index=True)
    predicted_qty = db.Column(db.Float, nullable=False)
    lower = db.Column(db.Float)   # lower bound of the uncertainty interval
    upper = db.Column(db.Float)   # upper bound
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")


class ForecastMetric(db.Model):
    """Accuracy scores per product from back-testing the forecast model."""
    __tablename__ = "forecast_metrics"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    mape = db.Column(db.Float)   # mean absolute percentage error (%)
    mae = db.Column(db.Float)    # mean absolute error (units)
    rmse = db.Column(db.Float)   # root mean squared error
    trained_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")


class AnomalyFlag(db.Model):
    """Unusual sales/inventory events found by the Isolation Forest model."""
    __tablename__ = "anomaly_flags"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    flag_date = db.Column(db.Date, nullable=False, index=True)
    quantity = db.Column(db.Integer)        # what happened
    expected = db.Column(db.Float)          # what was expected (rolling average)
    score = db.Column(db.Float)             # anomaly score (lower = more anomalous)
    reason = db.Column(db.String(40))       # 'spike' or 'drop'
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")
