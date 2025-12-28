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
