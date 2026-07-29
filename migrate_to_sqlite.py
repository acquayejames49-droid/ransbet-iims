"""Copy the local MySQL database into a fresh SQLite file for deployment.

PythonAnywhere's free tier runs SQLite and cannot spare the CPU to retrain.
This copies every table from MySQL into a new .db file that can be uploaded
directly, so the live site is an exact match of the local system.

Usage:
    python migrate_to_sqlite.py                  -> writes live_copy.db
    python migrate_to_sqlite.py my_name.db       -> writes my_name.db

Run from the project root with the virtual environment active, in a terminal
where DATABASE_URL is NOT overridden to sqlite (the script checks this).
"""
import os
import sys

from sqlalchemy import create_engine, select

# Import the app so config.py loads .env and every model registers its table.
from app import create_app, db
from app import models  # noqa: F401  - registers tables on db.metadata

OUT_NAME = sys.argv[1] if len(sys.argv) > 1 else "live_copy.db"
OUT_PATH = os.path.abspath(OUT_NAME)
CHUNK = 5000


def main():
    app = create_app()
    source_url = app.config["SQLALCHEMY_DATABASE_URI"]

    if not source_url.startswith("mysql"):
        print("Source is not MySQL — it is:")
        print(f"  {source_url}")
        print()
        print("This usually means DATABASE_URL is set to SQLite in this terminal.")
        print("Open a fresh terminal, activate the venv, and run again without")
        print("setting DATABASE_URL, so config.py reads .env as normal.")
        sys.exit(1)

    if os.path.exists(OUT_PATH):
        print(f"{OUT_PATH} already exists. Delete or rename it first.")
        sys.exit(1)

    print(f"Source: {source_url.split('@')[-1]}")
    print(f"Target: {OUT_PATH}")
    print()

    src = create_engine(source_url)
    dst = create_engine("sqlite:///" + OUT_PATH.replace("\\", "/"))

    with app.app_context():
        meta = db.metadata

    # Build the empty schema in SQLite from the same model definitions.
    meta.create_all(dst)

    total = 0
    with src.connect() as sconn, dst.begin() as dconn:
        for table in meta.sorted_tables:
            rows = sconn.execute(select(table)).mappings().all()
            if not rows:
                print(f"  {table.name}: 0")
                continue
            for i in range(0, len(rows), CHUNK):
                batch = [dict(r) for r in rows[i:i + CHUNK]]
                dconn.execute(table.insert(), batch)
            print(f"  {table.name}: {len(rows):,}")
            total += len(rows)

    size_mb = os.path.getsize(OUT_PATH) / (1024 * 1024)
    print()
    print(f"Copied {total:,} rows into {OUT_NAME} ({size_mb:.1f} MB)")

    # Read the copy back through a clean connection as a sanity check.
    check = create_engine("sqlite:///" + OUT_PATH.replace("\\", "/"))
    with check.connect() as conn:
        for name in ("products", "sales", "forecasts", "anomaly_flags"):
            if name in meta.tables:
                n = conn.execute(
                    select(db.func.count()).select_from(meta.tables[name])
                ).scalar()
                print(f"  verified {name}: {n:,}")


if __name__ == "__main__":
    main()
