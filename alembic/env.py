from __future__ import annotations

import time
from logging.config import fileConfig

from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel

import app.slices.users.models  # noqa: F401
from alembic import context
from app.core.db import engine
from app.core.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    config.set_main_option("sqlalchemy.url", settings.database_url)

    # Postgres can take a moment to accept connections after `docker compose up`.
    # Retrying here keeps migrations ergonomically reliable.
    last_error: Exception | None = None
    for _ in range(30):
        try:
            connection = engine.connect()
            break
        except OperationalError as exc:  # pragma: no cover
            last_error = exc
            time.sleep(1)
    else:  # pragma: no cover
        raise last_error or RuntimeError("Failed to connect to database")

    with connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
