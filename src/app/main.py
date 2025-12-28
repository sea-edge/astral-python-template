from __future__ import annotations

from fastapi import FastAPI, Request

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
    def scalar_docs(request: Request):
        from scalar_fastapi import get_scalar_api_reference

        root_path = request.scope.get("root_path", "")
        openapi_url = None
        if app.openapi_url is not None:
            openapi_url = f"{root_path}{app.openapi_url}"

        return get_scalar_api_reference(
            openapi_url=openapi_url,
            title=f"{settings.app_name} API Reference",
            scalar_js_url=settings.scalar_js_url,
            scalar_proxy_url=settings.scalar_proxy_url,
        )

    return app


app = create_app()
