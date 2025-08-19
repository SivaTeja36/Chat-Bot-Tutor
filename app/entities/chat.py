from datetime import datetime

import sqlalchemy as sa

from app.connectors.database_connector import Base


class Chat(Base):
    __tablename__ = "chats"

    id: int = sa.Column(sa.Integer, primary_key=True, nullable=False) 
    kid_id: int = sa.Column(sa.Integer, sa.ForeignKey("kids.id"), nullable=False)
    title: str = sa.Column(sa.Text, nullable=False) 
    created_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())