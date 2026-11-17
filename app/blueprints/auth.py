from urllib.parse import urlparse

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import csrf, db
from app.forms.auth import LoginForm, ProfileForm, RegisterForm
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


def is_safe_redirect_url(target: str) -> bool:
    """Ensure the redirect URL stays within the same host to prevent open redirects."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
        or not test_url.netloc
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Web login view."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.full_name}.", "success")
            next_page = request.args.get("next")
            if next_page and is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password. Please check your credentials.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Web registration view."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("An account with this email address already exists.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            email=email,
            full_name=form.full_name.data.strip(),
            role="USER",
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. Please sign in with your credentials.", "success"
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Sign the user out of the current session."""
    if current_user.is_authenticated:
        logout_user()
        flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View and update profile information."""
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()

        # Handle password change if requested
        if form.new_password.data:
            if not form.current_password.data or not current_user.check_password(
                form.current_password.data
            ):
                flash(
                    "Current password must be provided and correct to change password.",
                    "danger",
                )
                return render_template("auth/profile.html", form=form)
            if len(form.new_password.data) < 8:
                flash("New password must be at least 8 characters long.", "danger")
                return render_template("auth/profile.html", form=form)
            current_user.set_password(form.new_password.data)

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    from app.services.dashboard_service import get_dashboard_stats

    stats = get_dashboard_stats(current_user.id)
    return render_template("auth/profile.html", form=form, stats=stats)


# -----------------------------------------------------------------------------
# REST API endpoints for backwards compatibility and automated testing
# -----------------------------------------------------------------------------


@auth_bp.route("/api/auth/register", methods=["POST"])
@csrf.exempt
def api_register():
    payload = request.get_json() or {}
    email = payload.get("email", "").lower().strip()
    password = payload.get("password", "")
    full_name = payload.get("fullName") or payload.get("full_name") or ""

    if not email or "@" not in email:
        return jsonify({"error": "A valid email address is required"}), 400
    if not password or len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    if not full_name:
        return jsonify({"error": "Full name is required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    user = User(email=email, full_name=full_name.strip(), role="USER")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return (
        jsonify({"message": "User registered successfully", "user": user.to_dict()}),
        201,
    )


@auth_bp.route("/api/auth/login", methods=["POST"])
@csrf.exempt
def api_login():
    payload = request.get_json() or {}
    email = payload.get("email", "").lower().strip()
    password = payload.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user)
    return (
        jsonify(
            {
                "message": "Login successful",
                "user": user.to_dict(),
                "token": "session_cookie_authenticated",
            }
        ),
        200,
    )


@auth_bp.route("/api/auth/logout", methods=["POST"])
@csrf.exempt
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/api/auth/profile", methods=["GET", "PUT"])
@auth_bp.route("/api/users/me", methods=["GET", "PUT"])
@csrf.exempt
def api_profile():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "GET":
        return jsonify(current_user.to_dict()), 200

    payload = request.get_json() or {}
    full_name = payload.get("fullName") or payload.get("full_name")
    if full_name:
        current_user.full_name = full_name.strip()
        db.session.commit()

    return jsonify(current_user.to_dict()), 200
