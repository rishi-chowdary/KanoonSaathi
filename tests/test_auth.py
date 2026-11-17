from app.models.user import User


def test_register_success(client, app):
    """Test standard user registration via web form."""
    response = client.post(
        "/register",
        data={
            "full_name": "Counsel Alexander",
            "email": "alexander@firm.com",
            "password": "StrongPassword2026",
            "confirm_password": "StrongPassword2026",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data or b"Sign In" in response.data

    with app.app_context():
        user = User.query.filter_by(email="alexander@firm.com").first()
        assert user is not None
        assert user.full_name == "Counsel Alexander"
        assert user.check_password("StrongPassword2026")
        assert not user.check_password("WrongPassword")
        # Ensure password is not stored in plaintext
        assert user.password_hash != "StrongPassword2026"
        assert "scrypt:" in user.password_hash


def test_register_duplicate_email_rejected(client, test_user):
    """Registration with an already-used email must fail."""
    response = client.post(
        "/register",
        data={
            "full_name": "Imposter Lawyer",
            "email": test_user.email,
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_register_password_mismatch(client):
    """Registration fails when confirmation password does not match."""
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "mismatch@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Passwords must match" in response.data


def test_register_password_too_short(client):
    """Password below 8 characters must be rejected."""
    response = client.post(
        "/register",
        data={
            "full_name": "Test User",
            "email": "short@example.com",
            "password": "short",
            "confirm_password": "short",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"at least 8 characters" in response.data


def test_login_success(client, test_user):
    """Successful authentication establishes session and redirects to dashboard."""
    response = client.post(
        "/login",
        data={
            "email": test_user.email,
            "password": "SecurePassword123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Contract Dashboard" in response.data
    assert b"Sarah Jenkins" in response.data


def test_login_invalid_password(client, test_user):
    """Wrong password attempt must fail with clear feedback."""
    response = client.post(
        "/login",
        data={
            "email": test_user.email,
            "password": "IncorrectPassword999",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_nonexistent_email(client):
    """Non-existent email attempt must fail gracefully."""
    response = client.post(
        "/login",
        data={
            "email": "does_not_exist@firm.com",
            "password": "AnyPassword123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_protected_routes_require_login(client):
    """Unauthenticated access to dashboard and profile redirects to /login."""
    response_dash = client.get("/dashboard")
    assert response_dash.status_code == 302
    assert "/login" in response_dash.headers["Location"]

    response_prof = client.get("/profile")
    assert response_prof.status_code == 302
    assert "/login" in response_prof.headers["Location"]


def test_logout(client, test_user):
    """Logging out clears session and prevents access to protected routes."""
    # 1. Login
    client.post(
        "/login",
        data={"email": test_user.email, "password": "SecurePassword123!"},
    )

    # 2. Confirm authenticated
    resp_dash = client.get("/dashboard")
    assert resp_dash.status_code == 200

    # 3. Logout
    resp_logout = client.post("/logout", follow_redirects=True)
    assert resp_logout.status_code == 200
    assert b"signed out" in resp_logout.data or b"Sign In" in resp_logout.data

    # 4. Confirm dashboard is blocked again
    resp_blocked = client.get("/dashboard")
    assert resp_blocked.status_code == 302


def test_profile_update(client, test_user, app):
    """Authenticated user can update their full name."""
    client.post(
        "/login",
        data={"email": test_user.email, "password": "SecurePassword123!"},
    )

    response = client.post(
        "/profile",
        data={
            "full_name": "Sarah Jenkins, Esq.",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Profile updated successfully" in response.data

    with app.app_context():
        from app.extensions import db

        updated = db.session.get(User, test_user.id)
        assert updated.full_name == "Sarah Jenkins, Esq."


def test_api_register_and_login_flow(client):
    """JSON API endpoints for programmatic authentication."""
    # 1. Register API
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "email": "apilawyer@example.com",
            "password": "StrongApiPassword123",
            "fullName": "API Attorney",
        },
    )
    assert reg_resp.status_code == 201
    assert reg_resp.json["user"]["email"] == "apilawyer@example.com"

    # 2. Duplicate API check
    dup_resp = client.post(
        "/api/auth/register",
        json={
            "email": "apilawyer@example.com",
            "password": "StrongApiPassword123",
            "fullName": "API Attorney",
        },
    )
    assert dup_resp.status_code == 409

    # 3. Logout
    client.post("/api/auth/logout")

    # 4. Login API
    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "apilawyer@example.com",
            "password": "StrongApiPassword123",
        },
    )
    assert login_resp.status_code == 200
    assert login_resp.json["user"]["full_name"] == "API Attorney"

    # 5. Profile API
    prof_resp = client.get("/api/auth/profile")
    assert prof_resp.status_code == 200
    assert prof_resp.json["email"] == "apilawyer@example.com"
