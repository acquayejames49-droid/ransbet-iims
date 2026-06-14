"""Generate ~2 years of realistic daily sales for every product.

This gives the AI models something meaningful to learn from. When Ransbet's
real sales arrive, clear this (Import/Data > Danger Zone) and import theirs.

Run with:  python generate_sales.py
"""
import random
from datetime import date, timedelta

import numpy as np
from sqlalchemy import func

from app import create_app, db
from app.models import Product, Sale

app = create_app()

DAYS = 730          # about two years
ANOMALY_RATE = 0.01  # ~1% of days get an injected spike/drop

# Ghanaian holidays / festive periods that lift demand (month, day).
HOLIDAYS = {(1, 1), (3, 6), (5, 1), (7, 1), (12, 24), (12, 25), (12, 26), (12, 31)}


def seasonal_multiplier(d):
    """Combine weekly, yearly and holiday effects into one multiplier."""
    # Weekend uplift (Fri=4, Sat=5 busiest for a supermarket)
    weekday = d.weekday()
    weekly = {0: 0.9, 1: 0.9, 2: 0.95, 3: 1.0, 4: 1.25, 5: 1.4, 6: 1.05}[weekday]

    # Yearly: December festive surge, quieter in the rainy mid-year
    month = d.month
    yearly = 1.0
    if month == 12:
        yearly = 1.5
    elif month in (1, 11):
        yearly = 1.15
    elif month in (6, 7):
        yearly = 0.9

    # Specific holidays
    holiday = 1.6 if (d.month, d.day) in HOLIDAYS else 1.0
    return weekly * yearly * holiday


def generate():
    products = Product.query.filter_by(is_active=True).all()
    if not products:
        print("No products found — run seed.py first.")
        return

    print(f"Clearing old sales and generating {DAYS} days for {len(products)} products...")
    Sale.query.delete()
    db.session.commit()

    start = date.today() - timedelta(days=DAYS - 1)
    rng = np.random.default_rng(42)
    rows = []

    for p in products:
        base = rng.uniform(25, 80)         # this product's typical daily demand
        growth = rng.uniform(0.0, 0.4)     # total growth across the 2 years
        for i in range(DAYS):
            d = start + timedelta(days=i)
            trend = 1 + growth * (i / DAYS)
            mean = base * trend * seasonal_multiplier(d)
            qty = int(rng.poisson(max(mean, 0.1)))

            # Inject the occasional anomaly so the detector has work to do.
            if rng.random() < ANOMALY_RATE:
                if rng.random() < 0.6:
                    qty = int(qty * rng.uniform(3, 6))   # spike
                else:
                    qty = 0                               # sudden drop

            if qty > 0:
                rows.append(Sale(product_id=p.id, quantity=qty, unit_price=p.unit_price,
                                 total=round(p.unit_price * qty, 2), sale_date=d))

    db.session.bulk_save_objects(rows)
    db.session.commit()
    print(f"Done. Inserted {len(rows)} sales records "
          f"from {start} to {date.today()}.")

    # Set realistic stock so the store isn't wildly under/over-stocked:
    # reorder point ~= 1 week of demand, stock ~= 2-3 weeks (a few kept low).
    cut = date.today() - timedelta(days=60)
    low_ids = set(rng.choice([p.id for p in products],
                             size=min(3, len(products)), replace=False).tolist())
    for p in products:
        units = float(db.session.query(func.sum(Sale.quantity))
                      .filter(Sale.product_id == p.id, Sale.sale_date >= cut).scalar() or 0)
        avg_daily = max(units / 60.0, 1)
        p.reorder_point = max(5, round(avg_daily * 7))
        days = rng.uniform(2, 5) if p.id in low_ids else rng.uniform(12, 22)
        p.current_stock = max(0, round(avg_daily * days))
    db.session.commit()
    print("Set realistic stock levels (3 low on purpose, the rest healthy).")


with app.app_context():
    db.create_all()   # make sure the new Phase-4 tables exist too
    generate()
