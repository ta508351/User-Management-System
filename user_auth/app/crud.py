from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app import models


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, hashed_password: str):
    user = models.User(
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_password_reset_token(db: Session, user_id: int):
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=30)

    reset_token = models.PasswordReset(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        used=False
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token


def validate_reset_token(db: Session, token: str):
    reset_token = (
        db.query(models.PasswordReset)
        .filter(models.PasswordReset.token == token)
        .first()
    )

    if not reset_token:
        return None

    if reset_token.used:
        return None

    if reset_token.expires_at < datetime.utcnow():
        return None

    return reset_token


def update_user_password(db: Session, user_id: int, new_hashed_password: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(user)
    return user
