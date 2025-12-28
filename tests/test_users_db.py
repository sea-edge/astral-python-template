from __future__ import annotations

import os
import uuid

import pytest


def _sqlalchemy_url_to_psycopg_dsn(database_url: str) -> str:
    # SQLAlchemy URL: postgresql+psycopg://...
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    return database_url


# Keep DB-backed tests opt-in so local unit runs stay fast.
if os.getenv("RUN_DB_TESTS") != "1":
    pytest.skip("DB tests disabled (set RUN_DB_TESTS=1)", allow_module_level=True)


def test_users_create_and_list_with_db(client):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is not set")

    # For type checkers.
    assert database_url is not None

    # Quick preflight: ensure DB is reachable and migrations ran.
    import psycopg

    dsn = _sqlalchemy_url_to_psycopg_dsn(database_url)
    try:
        with psycopg.connect(dsn, connect_timeout=1) as conn, conn.cursor() as cur:
            cur.execute("select to_regclass('public.user')")
            row = cur.fetchone()
            table = row[0] if row is not None else None
    except Exception as exc:
        pytest.skip(f"Database not reachable: {exc}")

    if table is None:
        pytest.skip("Database reachable but migrations not applied (missing table 'user')")

    email = f"test-{uuid.uuid4()}@example.com"
    payload = {"email": email, "name": "Test User"}

    created = client.post("/users", json=payload)
    assert created.status_code == 201
    body = created.json()
    assert body["email"] == email

    listed = client.get("/users")
    assert listed.status_code == 200
    emails = {u["email"] for u in listed.json()}
    assert email in emails
