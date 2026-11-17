import os
from datetime import UTC, datetime

from flask import Flask, jsonify, render_template, request

import app.models as _models  # noqa: F401
from app.config import Config
from app.extensions import csrf, db, limiter, login_manager, migrate


def create_app(config_class=Config) -> Flask:
    """Application factory for LexiLegal AI."""
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    upload_dir = app.config.get("UPLOAD_FOLDER")
    if upload_dir:
        os.makedirs(upload_dir, exist_ok=True)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.documents import documents_bp
    from app.blueprints.main import main_bp
    from app.blueprints.studio import studio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(studio_bp)

    # Global template context
    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.now(UTC).year,
            "app_name": "LexiLegal AI",
        }

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found", "status": 404}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Access forbidden", "status": 403}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def payload_too_large(error):
        if request.path.startswith("/api/"):
            return (
                jsonify({"error": "File size exceeds the 10MB limit", "status": 413}),
                413,
            )
        return (
            render_template(
                "errors/error.html",
                code=413,
                title="Payload Too Large",
                message="File size exceeds the 10MB limit.",
            ),
            413,
        )

    @app.errorhandler(429)
    def ratelimit_handler(e):
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {"error": "Too many requests. Please slow down.", "status": 429}
                ),
                429,
            )
        return (
            render_template(
                "errors/error.html",
                code=429,
                title="Rate Limit Exceeded",
                message="You have sent too many requests. Please wait a moment.",
            ),
            429,
        )

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith("/api/"):
            return (
                jsonify({"error": "An internal error occurred", "status": 500}),
                500,
            )
        return render_template("errors/500.html"), 500

    return app
