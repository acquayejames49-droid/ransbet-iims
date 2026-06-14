# ============================================================================
# PythonAnywhere WSGI configuration for Ransbet IIMS.
#
# On PythonAnywhere, go to the "Web" tab -> "WSGI configuration file" link,
# DELETE everything in that file, and paste THIS in. Then change the three
# CAPITALISED placeholders to match your account, and click "Reload".
# ============================================================================
import sys
import os

# 1) Your PythonAnywhere username (the one in your URL):
USERNAME = "ransbetiims"          # <-- CHANGE to your PythonAnywhere username

# 2) The MySQL password you set on the "Databases" tab:
DB_PASSWORD = "YOUR_DB_PASSWORD"  # <-- CHANGE this

# --- usually no need to edit below this line ---
project_home = f"/home/{USERNAME}/ransbet-iims"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Database: PythonAnywhere names it  <username>$ransbet_iims
os.environ["DATABASE_URL"] = (
    f"mysql+pymysql://{USERNAME}:{DB_PASSWORD}"
    f"@{USERNAME}.mysql.pythonanywhere-services.com/{USERNAME}$ransbet_iims"
)
os.environ["SECRET_KEY"] = "CHANGE-ME-to-a-long-random-string-of-characters"

from app import create_app
application = create_app()
