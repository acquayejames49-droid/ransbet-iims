"""Import a Ransbet stock-card PDF (stock valuation / movement report).

Ransbet's POS system exports one PDF per product listing every stock movement
with a running balance. This script reads it and loads it into the system:
  - POS Despatch    -> a customer sale (goes to the sales table -> feeds forecast)
  - Branch Receipt  -> stock received  (a stock-in movement)
  - Branch Transfer -> stock sent to another branch (a stock-out movement)
The product's current stock is set to the final balance in the report.

Usage:
    python import_stock_card.py "C:\\path\\to\\stock card.pdf"
(With no path, it uses the Milo file on the Desktop.)

After importing, run:  python train_models.py   (to refresh the forecast).
"""
import re
import sys
from datetime import datetime

import pdfplumber

from app import create_app, db
from app.models import Product, Sale, StockMovement

app = create_app()
DEFAULT_PDF = r"C:\Users\USER\Desktop\stock valuation on milo.pdf"
NUM = r"-?\d+(?:\.\d+)?"


def parse(pdf_path):
    code = name = opening = None
    movements = []  # (date, type, qty, balance)
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or "").splitlines():
                line = line.strip()
                m = re.match(r"^(\d+)\s*:\s*(.+)$", line)          # "22558 : MILO TIN 400G"
                if m and code is None:
                    code, name = m.group(1), m.group(2).strip()
                    continue
                m = re.match(rf"^\d{{2}}-\d{{2}}-\d{{4}}\s+Opening Balance\s+({NUM})", line)
                if m:
                    opening = float(m.group(1))
                    continue
                m = re.match(rf"^(\d{{2}}-\d{{2}}-\d{{4}})\s+\S+\s+"
                             rf"(POS Despatch|Branch Transfer|Branch Receipt)\s+({NUM})\s+({NUM})", line)
                if m:
                    d = datetime.strptime(m.group(1), "%d-%m-%Y").date()
                    movements.append((d, m.group(2), float(m.group(3)), float(m.group(4))))
    return code, name, opening, movements


def run(pdf_path):
    code, name, opening, movements = parse(pdf_path)
    if not movements:
        print("No movements parsed — please check the PDF.")
        return

    sales = [(d, q) for (d, t, q, b) in movements if t == "POS Despatch"]
    receipts = [(d, q, b) for (d, t, q, b) in movements if t == "Branch Receipt"]
    transfers = [(d, q, b) for (d, t, q, b) in movements if t == "Branch Transfer"]
    final_balance = int(movements[-1][3])

    print(f"Product       : {code} - {name}")
    print(f"Opening stock : {opening}")
    print(f"Date range    : {movements[0][0]} -> {movements[-1][0]}")
    print(f"Sales (POS)   : {len(sales)} days, {int(sum(q for _, q in sales))} units total")
    print(f"Receipts      : {len(receipts)}   Transfers: {len(transfers)}")
    print(f"Final stock   : {final_balance}")

    with app.app_context():
        product = (Product.query.filter_by(sku=code).first()
                   or Product.query.filter(Product.name.ilike(f"%{name}%")).first()
                   or Product.query.filter(Product.name.ilike("%milo%")).first())
        if product is None:
            product = Product(name=name.title(), unit_price=0, cost_price=0, reorder_point=20)
            db.session.add(product)
            db.session.flush()
            print("  (created a new product)")

        product.sku = code
        product.is_active = True
        product.current_stock = final_balance
        price = product.unit_price or 0

        # Replace this product's data with the REAL data from Ransbet.
        Sale.query.filter_by(product_id=product.id).delete()
        StockMovement.query.filter_by(product_id=product.id).delete()

        for d, q in sales:
            db.session.add(Sale(product_id=product.id, quantity=int(q), unit_price=price,
                                total=round(price * q, 2), sale_date=d))
        for d, q, bal in receipts:
            db.session.add(StockMovement(product_id=product.id, movement_type="stock_in",
                                         quantity=int(q), stock_after=int(bal),
                                         note="Branch Receipt (Ransbet)",
                                         created_at=datetime.combine(d, datetime.min.time())))
        for d, q, bal in transfers:
            db.session.add(StockMovement(product_id=product.id, movement_type="adjustment",
                                         quantity=-int(q), stock_after=int(bal),
                                         note="Branch Transfer to RS2",
                                         created_at=datetime.combine(d, datetime.min.time())))
        db.session.commit()
        print(f"\nDONE. Real data loaded into product #{product.id} '{product.name}'.")
        print("Now run:  python train_models.py   to refresh the forecast.")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF)
