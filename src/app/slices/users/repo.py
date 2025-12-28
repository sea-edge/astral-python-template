from __future__ import annotations

from sqlmodel import Session, select

from app.slices.users.models import User
from app.slices.users.schemas import UserCreate


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def create_user(session: Session, data: UserCreate) -> User:
    user = User(email=data.email, name=data.name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def list_users(session: Session) -> list[User]:
    return list(session.exec(select(User)))
