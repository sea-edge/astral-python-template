from __future__ import annotations

from sqlmodel import SQLModel


class UserCreate(SQLModel):
    email: str
    name: str


class UserRead(SQLModel):
    id: int
    email: str
    name: str
