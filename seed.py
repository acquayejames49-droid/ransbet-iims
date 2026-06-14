"""Create tables and load demo data (users + a small sample catalogue).

Run with:  python seed.py
Safe to re-run — it only adds things that are missing.
"""
import random
from datetime import date, timedelta

from app import create_app, db
from app.models import (User, Category, Supplier, Product, Sale, StockMovement,
                        ROLE_OWNER, ROLE_MANAGER, ROLE_STAFF)

app = create_app()

DEMO_USERS = [
    {"name": "Business Owner",  "email": "owner@ransbet.com",   "role": ROLE_OWNER,   "password": "owner123"},
    {"name": "Store Manager",   "email": "manager@ransbet.com", "role": ROLE_MANAGER, "password": "manager123"},
    {"name": "Inventory Staff", "email": "staff@ransbet.com",   "role": ROLE_STAFF,   "password": "staff123"},
]

CATEGORIES = ["Beverages", "Groceries", "Household", "Personal Care", "Snacks"]

SUPPLIERS = [
    {"name": "Accra Distributors Ltd", "contact_person": "Kofi Mensah", "phone": "024 111 2222", "lead_time_days": 5},
    {"name": "Tema Wholesale Co.",     "contact_person": "Ama Boateng", "phone": "020 333 4444", "lead_time_days": 7},
    {"name": "Kumasi Supplies",        "contact_person": "Yaw Osei",    "phone": "027 555 6666", "lead_time_days": 10},
]

# name, category, unit_price, cost_price, current_stock, reorder_point
PRODUCTS = [
    ("Voltic Water 500ml (pack)", "Beverages",     12.00,  8.00,  40, 15),
    ("Coca-Cola 350ml (crate)",   "Beverages",     65.00, 50.00,   8, 10),  # reorder
    ("Milo Tin 400g",             "Beverages",     38.50, 30.00,  22, 12),
    ("Rice 5kg (Royal Aroma)",    "Groceries",     78.00, 65.00,   6, 10),  # reorder
    ("Cooking Oil 1L (Frytol)",   "Groceries",     29.00, 22.00,  18, 15),
    ("Sugar 1kg",                 "Groceries",     16.00, 12.00,  35, 20),
    ("Key Soap (bar)",            "Household",      6.50,  4.00,  50, 25),
    ("Tissue Roll (12 pack)",     "Household",     45.00, 36.00,   9, 10),  # reorder
    ("Colgate Toothpaste 150g",   "Personal Care", 18.00, 13.00,  27, 12),
    ("Pepsodent Soap",            "Personal Care",  7.00,  4.50,  16, 15),
    ("Pringles 110g",             "Snacks",        24.00, 18.00,  14, 10),
    ("Digestive Biscuits",        "Snacks",         9.50,  6.50,  30, 18),
]


def seed_users():
    for u in DEMO_USERS:
        if User.query.filter_by(email=u["email"]).first() is None:
            user = User(name=u["name"], email=u["email"], role=u["role"])
            user.set_password(u["password"])
            db.session.add(user)
            print(f"  user   {u['email']} / {u['password']}")
    db.session.commit()


def seed_catalogue():
    if Product.query.count() > 0:
        print("  catalogue already present — skipping")
        return

    cats = {}
    for name in CATEGORIES:
        c = Category(name=name)
        db.session.add(c)
        cats[name] = c

    sups = []
    for s in SUPPLIERS:
        sup = Supplier(**s)
        db.session.add(sup)
        sups.append(sup)
    db.session.flush()

    products = []
    for i, (name, cat, price, cost, stock, reorder) in enumerate(PRODUCTS):
        p = Product(name=name, sku=f"RB{1000 + i}", category_id=cats[cat].id,
                    supplier_id=sups[i % len(sups)].id, unit_price=price,
                    cost_price=cost, current_stock=stock, reorder_point=reorder)
        db.session.add(p)
        products.append(p)
    db.session.flush()

    # A few recent sales so the Sales page & dashboard aren't empty.
    today = date.today()
    for _ in range(25):
        p = random.choice(products)
        qty = random.randint(1, 4)
        d = today - timedelta(days=random.randint(0, 6))
        db.session.add(Sale(product_id=p.id, quantity=qty, unit_price=p.unit_price,
                            total=round(p.unit_price * qty, 2), sale_date=d))
    db.session.commit()
    print(f"  catalogue: {len(products)} products, {len(SUPPLIERS)} suppliers, "
          f"{len(CATEGORIES)} categories, 25 sample sales")


with app.app_context():
    db.create_all()
    print("Seeding...")
    seed_users()
    seed_catalogue()
    print(f"\nDone. Users={User.query.count()} Products={Product.query.count()} "
          f"Sales={Sale.query.count()}")
