from app.blueprints.analysis import analysis_bp
from app.blueprints.auth import auth_bp
from app.blueprints.chat import chat_bp
from app.blueprints.documents import documents_bp
from app.blueprints.main import main_bp
from app.blueprints.reports import reports_bp
from app.blueprints.studio import studio_bp

__all__ = [
    "analysis_bp",
    "auth_bp",
    "chat_bp",
    "documents_bp",
    "main_bp",
    "reports_bp",
    "studio_bp",
]
