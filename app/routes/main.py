# ─────────────────────────────────────────────────────────────────
#  app/routes/main.py
#  Veltrix – Main Blueprint
#
#  Handles public-facing pages:
#    GET  /           → landing page
#    GET  /dashboard  → protected dashboard (login required)
#    POST /dashboard  → salary prediction form submission
# ─────────────────────────────────────────────────────────────────

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime, timezone

from app.utils.helpers import format_datetime
from app.services.model_service import (
    predict_salary,
    get_field_options,
    get_model_info,
    PredictionInputError,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    """
    Public landing page.
    Accessible to everyone – logged-in users see a personalised
    greeting, guests see the default welcome message.
    """
    return render_template("landing.html")


@main_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Protected dashboard page – model overview, metrics & analytics.
    """
    joined       = format_datetime(current_user.created_at)
    current_date = format_datetime(datetime.now(timezone.utc), fmt="%A, %B %d %Y")

    options = get_field_options()
    info    = get_model_info()

    return render_template(
        "dashboard.html",
        joined=joined,
        current_date=current_date,
        options=options,
        info=info,
    )


@main_bp.route("/test-model", methods=["GET", "POST"])
@login_required
def test_model():
    """
    Live inference page.
    GET  → render empty prediction form.
    POST → process form input, return prediction result.
    """
    options = get_field_options()
    info    = get_model_info()
    result  = None

    if request.method == "POST":
        result = predict_salary(request.form)

    return render_template(
        "test_model.html",
        options=options,
        info=info,
        result=result,
    )