from __future__ import annotations


def test_docs_page(client):
    resp = client.get("/docs")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_openapi_json(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    body = resp.json()
    assert "openapi" in body
    assert "paths" in body

    users_post = body["paths"]["/users"]["post"]
    responses = users_post["responses"]

    # Validation error advertised as RFC 9457 Problem Details
    assert "application/problem+json" in responses["422"]["content"]

    # Conflict advertised (email already exists)
    assert "application/problem+json" in responses["409"]["content"]
