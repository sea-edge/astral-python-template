from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.slices.users.schemas import UserCreate, UserRead
from app.slices.users.service import create_user_or_409, list_all_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session)):
    return list_all_users(session)


@router.post("", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    return create_user_or_409(session, data)
