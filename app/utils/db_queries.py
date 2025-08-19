from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.entities.chat import Chat
from app.entities.kid import Kid
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

# ----------------------- KIDS QUERIES ------------------------:
def get_kid_by_id(db: Session, kid_id: int) -> Kid:
    return db.query(Kid).filter(Kid.id == kid_id).first()

def get_chat_by_kid_and_chat_id(db: Session, kid_id: int, chat_id: int) -> Chat:
    return (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.kid_id == kid_id)
        .first()
    )

def get_chat_by_id(db: Session, chat_id: int) -> Chat:
    return db.query(Chat).filter(Chat.id == chat_id).first()