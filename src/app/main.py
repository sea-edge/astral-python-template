from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.logging import configure_observability
from app.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=None,
        redoc_url=None,
    )

    configure_observability(app)

    app.include_router(api_router)

    # Scalar docs (served separately from Swagger UI)
    @app.get("/scalar", include_in_schema=False)
    def scalar_docs():
        from scalar_fastapi import get_scalar_api_reference

        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=f"{settings.app_name} API Reference",
        )

    return app


app = create_app()
