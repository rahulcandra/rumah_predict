# -----------------------------------------------------------------
#  app/routes/auth.py
#  Veltrix - Authentication Blueprint
#
#  All routes are prefixed with /auth (set in app/__init__.py):
#    GET  /auth/login    -> login form
#    POST /auth/login    -> process login
#    GET  /auth/register -> registration form
#    POST /auth/register -> process registration
#    GET  /auth/logout   -> log out and redirect to landing
# -----------------------------------------------------------------

# pyrefly: ignore [missing-import]
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request
)
# pyrefly: ignore [missing-import]
from flask_login import login_user, logout_user, login_required, current_user
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.user import User

# Create the blueprint; "auth" is its internal name
auth_bp = Blueprint("auth", __name__)


# -- Register ------------------------------------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    GET  - Render the registration form.
    POST - Validate input, hash password, create user, redirect to login.
    """
    # If already logged in, send straight to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # -- Basic validation --------------------------------------
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters long.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        # -- Check for duplicates ----------------------------------
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "danger")
            return render_template("register.html")

        # -- Create user with hashed password ----------------------
        hashed_pw = generate_password_hash(password)
        new_user  = User(username=username, email=email, password=hashed_pw)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    # GET request - just render the form
    return render_template("register.html")


# -- Login ---------------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  - Render the login form.
    POST - Validate credentials and log the user in.
    """
    # If already logged in, send to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = True if request.form.get("remember") else False

        # -- Look up user by email ---------------------------------
        user = User.query.filter_by(email=email).first()

        # -- Verify password ---------------------------------------
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html")

        # -- Log the user in ---------------------------------------
        login_user(user, remember=remember)
        flash(f"Welcome back, {user.username}!", "success")

        # Redirect to the page the user originally tried to visit
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    # GET request - just render the form
    return render_template("login.html")


# -- Logout --------------------------------------------------------

@auth_bp.route("/logout")
@login_required  # only logged-in users can log out
def logout():
    """Log the current user out and redirect to the landing page."""
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.landing"))
