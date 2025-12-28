from __future__ import annotations

from fastapi import FastAPI

from app.core.settings import settings


def configure_observability(app: FastAPI) -> None:
    import logfire

    logfire.configure(
        service_name=settings.app_name,
        environment=settings.app_env,
        token=settings.logfire_token,
        send_to_logfire="if-token-present",
    )
    logfire.instrument_fastapi(app)
