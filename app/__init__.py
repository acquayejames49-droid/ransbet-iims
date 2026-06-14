"""Application factory.

This file wires the whole app together: it creates the Flask object,
connects the database, sets up login + CSRF protection, and registers the
"blueprints" (groups of pages).
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from config import Config

# Create the extension objects here (not yet attached to an app).
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access that page."
login_manager.login_message_category = "warning"


@login_manager.unauthorized_handler
def _handle_unauthorized():
    """API calls get a clean JSON 401; normal pages redirect to the login page."""
    from flask import request, jsonify, redirect, url_for
    if request.path.startswith("/api/"):
        return jsonify(error="unauthorized"), 401
    return redirect(url_for("auth.login", next=request.path))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Attach the extensions to this app.
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)  # protects every form POST against forgery

    # Register the page groups.
    from app.auth import auth_bp
    from app.main import main_bp
    from app.inventory import inventory_bp
    from app.api import api_bp
    from app.data_admin import data_bp
    from app.reports import reports_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(reports_bp)

    # Friendly error pages.
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    return app


# Import the models so SQLAlchemy knows about the tables and the login
# user-loader gets registered.
from app import models  # noqa: E402,F401
