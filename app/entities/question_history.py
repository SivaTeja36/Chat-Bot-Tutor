from datetime import datetime

import sqlalchemy as sa

from app.connectors.database_connector import Base


class QuestionHistory(Base):
    __tablename__ = "questions_history"

    id: str = sa.Column(sa.String, primary_key=True, nullable=False) 
    kid_id: int = sa.Column(sa.Integer, sa.ForeignKey("kids.id"), nullable=False)
    question: str = sa.Column(sa.TEXT, nullable=False) 
    answer: str = sa.Column(sa.TEXT, nullable=False)  
    subject: str = sa.Column(sa.String(100), nullable=False)
    created_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())