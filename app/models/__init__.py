# ─────────────────────────────────────────────────────────────────
#  app/models/__init__.py
#  Expose models at the package level for easy importing.
# ─────────────────────────────────────────────────────────────────

from app.models.user import User

__all__ = ["User"]
