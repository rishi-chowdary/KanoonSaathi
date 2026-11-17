from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.models.document import Document

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
    recent_documents = (
        Document.query.filter_by(user_id=current_user.id)
        .order_by(Document.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard.html",
        documents=recent_documents,
        user=current_user,
    )
