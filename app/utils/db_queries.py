from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.entities.user import User

# ----------------------- USER QUERIES ------------------------:
def get_users(db: Session) -> List[User]:
    """
        Get all users.
    """
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return (
        db.query(User)
        .filter(
            User.id == user_id
        ).first()
    )

def get_user_by_email(db: Session, email: str):
    return (
        db.query(User)
        .filter(
            func.lower(User.email) == email.lower()
        ).first()
    )

def get_user_by_phone_number(db: Session, phone_number: str):
    return (
        db.query(User)
        .filter(
            User.phone_number == phone_number
        ).first()
    )