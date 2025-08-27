from datetime import datetime

import sqlalchemy as sa

from app.connectors.database_connector import Base


class KidKeywordRestrictions(Base):
    __tablename__ = "kids_keyword_restrictions"

    id: int = sa.Column(sa.Integer, primary_key=True, nullable=False) 
    kid_id: int = sa.Column(sa.Integer, sa.ForeignKey("kids.id"), nullable=False)
    restriction_id: int = sa.Column(sa.Integer, sa.ForeignKey("keyword_restrictions.id"), nullable=False)
    created_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    created_by: int = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    updated_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_by: int = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)