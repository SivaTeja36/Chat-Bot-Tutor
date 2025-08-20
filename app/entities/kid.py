from datetime import datetime

import sqlalchemy as sa

from app.connectors.database_connector import Base


class Kid(Base):
    __tablename__ = "kids"

    id: int = sa.Column(sa.Integer, primary_key=True, nullable=False) 
    parent_id: int = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    name: str = sa.Column(sa.String(50), nullable=False) 
    age: float = sa.Column(sa.REAL, nullable=False) 
    gender: str = sa.Column(sa.String(10), nullable=False)  
    school: str = sa.Column(sa.String(100), nullable=False)  
    standard: str = sa.Column(sa.String(50), nullable=False)  
    created_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    created_by: int = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    updated_at: datetime = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_by: int = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)
    is_active: bool = sa.Column(sa.Boolean, nullable=False, default=True)