# -----------------------------------------------------------------
#  tests/test_app.py
#  Veltrix - Basic unit tests using pytest + Flask test client.
#
#  Run all tests with:
#      pytest
#  Or with verbose output:
#      pytest -v
# -----------------------------------------------------------------

# pyrefly: ignore [missing-import]
import pytest
from app import create_app, db
# pyrefly: ignore [missing-import]
from app.models.user import User
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash


# -- Fixtures ------------------------------------------------------

@pytest.fixture
def app():
    """
    Create a fresh Flask application configured for testing.
    Uses an in-memory SQLite database so tests never touch disk.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Return a CLI test runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """
    Insert a sample user into the test database and return it.
    Password is 'password123' (hashed).
    """
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password123"),
        )
        db.session.add(user)
        db.session.commit()
        # Re-fetch to ensure we have a live object tied to this session
        return db.session.get(User, user.id)


# -- Tests: Public Routes ------------------------------------------

class TestPublicRoutes:

    def test_landing_page_loads(self, client):
        """Landing page should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_landing_page_contains_branding(self, client):
        """Landing page should display the Veltrix brand name."""
        response = client.get("/")
        assert b"Veltrix" in response.data

    def test_login_page_loads(self, client):
        """Login page should return HTTP 200."""
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_register_page_loads(self, client):
        """Register page should return HTTP 200."""
        response = client.get("/auth/register")
        assert response.status_code == 200


# -- Tests: Authentication -----------------------------------------

class TestAuthentication:

    def test_register_new_user(self, client):
        """Registering with valid data should redirect to login."""
        response = client.post("/auth/register", data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass",
            "confirm_password": "securepass",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"successfully" in response.data.lower() or b"log in" in response.data.lower()

    def test_register_mismatched_passwords(self, client):
        """Registration should fail if passwords do not match."""
        response = client.post("/auth/register", data={
            "username": "baduser",
            "email": "bad@example.com",
            "password": "pass1",
            "confirm_password": "pass2",
        }, follow_redirects=True)
        assert b"do not match" in response.data.lower()

    def test_register_short_password(self, client):
        """Registration should fail if password is fewer than 6 characters."""
        response = client.post("/auth/register", data={
            "username": "baduser",
            "email": "bad@example.com",
            "password": "abc",
            "confirm_password": "abc",
        }, follow_redirects=True)
        assert b"6 characters" in response.data.lower()

    def test_login_valid_credentials(self, client, sample_user):
        """Logging in with correct credentials should redirect to dashboard."""
        response = client.post("/auth/login", data={
            "email": "test@example.com",
            "password": "password123",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"dashboard" in response.data.lower()

    def test_login_invalid_password(self, client, sample_user):
        """Logging in with wrong password should show error."""
        response = client.post("/auth/login", data={
            "email": "test@example.com",
            "password": "wrongpassword",
        }, follow_redirects=True)
        assert b"invalid" in response.data.lower()

    def test_login_unknown_email(self, client):
        """Logging in with unregistered email should show error."""
        response = client.post("/auth/login", data={
            "email": "nobody@example.com",
            "password": "anything",
        }, follow_redirects=True)
        assert b"invalid" in response.data.lower()


# -- Tests: Protected Routes ---------------------------------------

class TestProtectedRoutes:

    def test_dashboard_redirects_when_not_logged_in(self, client):
        """Unauthenticated access to /dashboard should redirect to login."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

    def test_dashboard_accessible_after_login(self, client, sample_user):
        """Dashboard should be accessible after a successful login."""
        # Log in first
        client.post("/auth/login", data={
            "email": "test@example.com",
            "password": "password123",
        }, follow_redirects=True)

        # Now access the dashboard
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"dashboard" in response.data.lower()


# -- Tests: Helper Functions ---------------------------------------

class TestHelpers:

    def test_slugify_basic(self):
        from app.utils.helpers import slugify
        assert slugify("Hello World") == "hello-world"

    def test_slugify_special_chars(self):
        from app.utils.helpers import slugify
        assert slugify("Veltrix! Is #1") == "veltrix-is-1"

    def test_truncate_short_string(self):
        from app.utils.helpers import truncate
        assert truncate("short", 100) == "short"

    def test_truncate_long_string(self):
        from app.utils.helpers import truncate
        result = truncate("A" * 200, 50)
        assert len(result) <= 53  # 50 chars + "..."
        assert result.endswith("...")

    def test_format_datetime_none(self):
        from app.utils.helpers import format_datetime
        assert format_datetime(None) == "N/A"

    def test_format_datetime_valid(self):
        from app.utils.helpers import format_datetime
        from datetime import datetime
        dt = datetime(2024, 1, 15, 9, 30)
        result = format_datetime(dt)
        assert "2024" in result
        assert "January" in result
