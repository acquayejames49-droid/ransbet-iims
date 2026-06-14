"""Create the MySQL database named in DATABASE_URL.

Run this ONCE after MySQL is running and after you've set DATABASE_URL in .env
to a mysql URL, e.g.:
    DATABASE_URL=mysql+pymysql://root:YOURPASS@127.0.0.1:3306/ransbet_iims

Then run:  python setup_mysql_db.py
After that, run seed.py, generate_sales.py and train_models.py as usual.
"""
import os
from urllib.parse import urlparse

import pymysql
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("DATABASE_URL", "")
if not url.startswith("mysql"):
    raise SystemExit("DATABASE_URL in .env is not a mysql:// URL — set it first.")

# mysql+pymysql://user:pass@host:port/dbname  ->  pull the pieces out
p = urlparse(url.replace("mysql+pymysql", "mysql"))
dbname = p.path.lstrip("/")

conn = pymysql.connect(host=p.hostname or "127.0.0.1", port=p.port or 3306,
                       user=p.username or "root", password=p.password or "")
with conn.cursor() as cur:
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
conn.commit()
conn.close()
print(f"Database '{dbname}' is ready on {p.hostname}:{p.port or 3306}.")
