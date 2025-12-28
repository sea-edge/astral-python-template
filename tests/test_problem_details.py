from __future__ import annotations

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.db import get_session
from app.main import app


def test_problem_details_for_validation_error(client):
    resp = client.post("/users", json={})
    assert resp.status_code == 422
    assert resp.headers["content-type"].startswith("application/problem+json")

    body = resp.json()
    assert body["type"] == "about:blank"
    assert body["title"] == "Unprocessable Entity"
    assert body["status"] == 422
    assert body["detail"] == "Validation error"
    assert body["instance"] == "/users"
    assert isinstance(body["errors"], list)
    assert body["errors"], "expected at least one validation error"


def test_problem_details_for_http_exception(client):
    def _override_session():
        raise HTTPException(status_code=409, detail="email already exists")

    app.dependency_overrides[get_session] = _override_session
    try:
        resp = client.get("/users")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 409
    assert resp.headers["content-type"].startswith("application/problem+json")

    body = resp.json()
    assert body["type"] == "about:blank"
    assert body["title"] == "Conflict"
    assert body["status"] == 409
    assert body["detail"] == "email already exists"
    assert body["instance"] == "/users"


def test_problem_details_for_unhandled_exception(client):
    def _override_session():
        raise RuntimeError("boom")

    app.dependency_overrides[get_session] = _override_session
    try:
        local_client = TestClient(app, raise_server_exceptions=False)
        resp = local_client.get("/users")
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 500
    assert resp.headers["content-type"].startswith("application/problem+json")

    body = resp.json()
    assert body["type"] == "about:blank"
    assert body["title"] == "Internal Server Error"
    assert body["status"] == 500
    # In tests we set APP_ENV=test, so details should not leak.
    assert body["detail"] == "Internal Server Error"
    assert body["instance"] == "/users"
