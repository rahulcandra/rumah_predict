# ─────────────────────────────────────────────────────────────────
#  app/__init__.py
#  Veltrix – Application Factory
#
#  Using the factory pattern means we can create multiple instances
#  of the app (e.g. for testing) without conflicts.
# ─────────────────────────────────────────────────────────────────

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime, timezone

from app.config import get_config

# ── Extension instances (not yet bound to any app) ────────────────
db            = SQLAlchemy()
migrate       = Migrate()
login_manager = LoginManager()


def create_app():
    """
    Application factory function.
    Call this to create and configure a Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # ── Load configuration ────────────────────────────────────────
    app.config.from_object(get_config())

    # ── Initialise extensions with the app ────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    # ── Flask-Login setup ─────────────────────────────────────────
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"          # redirect here if not logged in
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # ── User loader callback (required by Flask-Login) ────────────
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        """Tell Flask-Login how to reload a user from the session."""
        return db.session.get(User, int(user_id))

    # ── Jinja2 context processor ──────────────────────────────────
    # Makes `now()` available in every template so the footer can
    # render the current year with {{ now().year }}.
    @app.context_processor
    def inject_globals():
        return {"now": lambda: datetime.now(timezone.utc)}

    # ── Register Blueprints ───────────────────────────────────────
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # ── Create DB tables if they don't exist (dev convenience) ────
    with app.app_context():
        db.create_all()

    return app
