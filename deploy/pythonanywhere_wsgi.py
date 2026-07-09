# ============================================================================
# PythonAnywhere WSGI configuration for Ransbet IIMS (free tier, SQLite).
#
# On PythonAnywhere, go to the "Web" tab -> "WSGI configuration file" link,
# DELETE everything in that file, paste THIS in, change USERNAME if needed,
# then click the green "Reload" button.
#
# NOTE: PythonAnywhere's FREE tier no longer includes MySQL, so the live copy
# uses the SQLite database file (iims.db) that ships with the repo. Your LOCAL
# system still runs on real MySQL 8.0. (To use MySQL online instead, upgrade to
# a paid plan and set DATABASE_URL to a mysql+pymysql://... string below.)
# ============================================================================
import sys
import os

USERNAME = "aizen004"   # <-- your PythonAnywhere username (your URL prefix)

project_home = f"/home/{USERNAME}/ransbet-iims"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Use the ready-made SQLite database that comes with the repo.
os.environ["DATABASE_URL"] = f"sqlite:////home/{USERNAME}/ransbet-iims/iims.db"

# SECURITY — replace the placeholder below with your OWN long random string.
# Generate one in a PythonAnywhere Bash console with:
#     python3 -c "import secrets; print(secrets.token_hex(32))"
# Paste the result here (keep the quotes), Save, then Reload. This file lives
# ONLY on PythonAnywhere (it is NOT the copy in the public GitHub repo), so your
# real key stays private. Never commit the real key.
os.environ["SECRET_KEY"] = "CHANGE-ME-to-a-long-random-string-of-characters"

from app import create_app
application = create_app()
