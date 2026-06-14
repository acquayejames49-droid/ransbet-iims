"""Application configuration.

Reads settings from a .env file so we never hard-code secrets or
database passwords into the source code.
"""
import os
from dotenv import load_dotenv

# Folder this file lives in = the project root.
basedir = os.path.abspath(os.path.dirname(__file__))
# Load variables from the .env file into the environment.
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    # Used by Flask to sign session cookies and CSRF tokens. Keep it secret.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Where the database lives. If DATABASE_URL is not set in .env we fall
    # back to a local SQLite file (zero setup). We switch this to MySQL later
    # by simply setting DATABASE_URL in .env — no code change needed.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + os.path.join(basedir, "iims.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
