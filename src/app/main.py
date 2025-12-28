from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.api.router import api_router
from app.core.logging import configure_observability
from app.core.problem_details import problem_response
from app.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=None,
        redoc_url=None,
    )

    configure_observability(app)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # RFC 9457 / Problem Details
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return problem_response(request=request, status_code=exc.status_code, detail=detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return problem_response(
            request=request,
            status_code=422,
            title="Unprocessable Entity",
            detail="Validation error",
            extensions={"errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Avoid leaking internals by default; show details only in dev.
        detail = str(exc) if settings.app_env == "dev" else "Internal Server Error"
        return problem_response(
            request=request,
            status_code=500,
            title="Internal Server Error",
            detail=detail,
        )

    app.include_router(api_router)

    # Scalar docs (served separately from Swagger UI)
    @app.get("/docs", include_in_schema=False)
    def scalar_docs(request: Request):
        from scalar_fastapi import get_scalar_api_reference

        root_path = request.scope.get("root_path", "")
        openapi_url = None
        if app.openapi_url is not None:
            openapi_url = f"{root_path}{app.openapi_url}"

        return get_scalar_api_reference(
            openapi_url=openapi_url,
            title=f"{settings.app_name} API Reference",
        )

    return app


app = create_app()
