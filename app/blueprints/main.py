from flask import Blueprint, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import csrf
from app.services.dashboard_service import get_dashboard_stats

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Application landing page."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard showing user contract statistics and recent documents."""
    stats = get_dashboard_stats(current_user.id)
    return render_template(
        "dashboard.html",
        stats=stats,
        documents=stats.get("recentDocuments", []),
        user=current_user,
    )


@main_bp.route("/api/dashboard/stats", methods=["GET"])
@csrf.exempt
def api_dashboard_stats():
    """Return JSON dashboard statistics for the authenticated user."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    stats = get_dashboard_stats(current_user.id)
    return jsonify(stats), 200
