from datetime import datetime

import sqlalchemy as sa

from app.connectors.database_connector import Base


class ChatConversation(Base):
    __tablename__ = "chat_conversation"

    id: int = sa.Column(sa.Integer, primary_key=True, nullable=False) 
    chat_id: int = sa.Column(sa.Integer, sa.ForeignKey("chats.id"), nullable=False)
    question: str = sa.Column(sa.TEXT, nullable=False) 
    answer: str = sa.Column(sa.TEXT, nullable=False)  
    subject: str = sa.Column(sa.String(100), nullable=False)
    created_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())