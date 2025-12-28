from __future__ import annotations

from fastapi import HTTPException
from sqlmodel import Session

from app.slices.users.repo import create_user, get_user_by_email, list_users
from app.slices.users.schemas import UserCreate


def create_user_or_409(session: Session, data: UserCreate):
    existing = get_user_by_email(session, data.email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="email already exists")
    return create_user(session, data)


def list_all_users(session: Session):
    return list_users(session)
