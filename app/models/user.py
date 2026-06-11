# ─────────────────────────────────────────────────────────────────
#  app/models/user.py
#  Veltrix – User model
#
#  Inherits from Flask-Login's UserMixin which provides default
#  implementations of is_authenticated, is_active, is_anonymous,
#  and get_id().
# ─────────────────────────────────────────────────────────────────

from flask_login import UserMixin
from datetime import datetime, timezone

from app import db


class User(UserMixin, db.Model):
    """
    Represents a registered user in the application.

    Columns:
        id        – Primary key (auto-increment integer)
        username  – Unique display name
        email     – Unique email address used for login
        password  – Bcrypt-hashed password string
        created_at– Timestamp of registration (UTC)
    """

    __tablename__ = "users"

    # ── Columns ───────────────────────────────────────────────────
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)  # stores the hash
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # ── Representation ────────────────────────────────────────────
    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"
