# ─────────────────────────────────────────────────────────────────
#  app/config.py
#  Veltrix – Configuration classes for different environments.
#  Loaded by the application factory in app/__init__.py
# ─────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

# Load .env file variables into the environment (if it exists)
load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    # ── Security ──────────────────────────────────────────────────
    # Pull SECRET_KEY from .env; fall back to a hard-coded default
    # so the app still runs even without a .env file (dev only!).
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-secret-key-change-in-production")

    # ── Database ──────────────────────────────────────────────────
    # Default: SQLite stored inside the auto-created instance/ folder.
    # Override DATABASE_URL in .env to switch to MySQL, PostgreSQL, etc.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///database.db"  # relative to the instance/ folder
    )

    # Disable SQLAlchemy modification tracking (saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── General Flask ─────────────────────────────────────────────
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development-specific config – debug mode on."""
    DEBUG = True


class TestingConfig(Config):
    """Testing config – uses an in-memory SQLite database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disable CSRF protection in tests for simplicity
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production config – debug off, strong secret key required."""
    DEBUG = False


# ── Config selector ───────────────────────────────────────────────
# Map environment name strings to config classes.
config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}


def get_config():
    """Return the correct Config class based on FLASK_ENV env variable."""
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
