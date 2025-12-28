from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # Keep DB-backed tests opt-in so local unit runs stay fast.
    if os.getenv("RUN_DB_TESTS") == "1":
        return

    skip_db = pytest.mark.skip(reason="DB tests disabled (set RUN_DB_TESTS=1)")
    for item in items:
        if item.get_closest_marker("db") is not None:
            item.add_marker(skip_db)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
