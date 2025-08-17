from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import func

from app.connectors.database_connector import Base
from app.models.email_models import Attachments


class EmailNotification(Base):
    __tablename__ = "email_notifications"

    id: str = sa.Column(sa.String, primary_key=True, nullable=False)  # type: ignore
    content: str = sa.Column(sa.Text, nullable=False)  # type: ignore
    recipients: list[str] = sa.Column(sa.ARRAY(sa.String), nullable=False)  # type: ignore
    cc: list[str] = sa.Column(sa.ARRAY(sa.String))  # type: ignore
    bcc: list[str] = sa.Column(sa.ARRAY(sa.String))  # type: ignore
    subject: str = sa.Column(sa.Text)  # type: ignore
    attachments: list[Attachments] = sa.Column(sa.ARRAY(sa.JSON))  # type: ignore
    payload: dict = sa.Column(sa.JSON)  # type: ignore
    template_identifier: str | None = sa.Column(sa.String(255))  # type: ignore
    is_direct_request: bool = sa.Column(sa.Boolean, nullable=False, default=False)  # type: ignore
    status: str = sa.Column(sa.String(50), nullable=False)  # type: ignore
    created_at: datetime = sa.Column(sa.DateTime, default=func.now(), nullable=False)  # type: ignore
    updated_at: datetime = sa.Column(sa.DateTime, default=func.now(), nullable=False)  # type: ignore
    is_sent_successfully: bool = sa.Column(sa.Boolean, nullable=False, default=False)  # type: ignore
    fail_reason: str = sa.Column(sa.Text)  # type: ignore