from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

from app.connectors.database_connector import Base


class KeywordRestrictions(Base):
    __tablename__ = "keyword_restrictions"

    id: int = sa.Column(sa.Integer, primary_key=True, nullable=False) 
    title: str = sa.Column(sa.String(100), nullable=False)
    keywords: list[str] = sa.Column(JSON, nullable=False)
    created_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    created_by: int = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    updated_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_by: int = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)