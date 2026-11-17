import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime

from app.extensions import db


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:

    created_at = db.Column(DateTime, default=utc_now, nullable=False)
    updated_at = db.Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
