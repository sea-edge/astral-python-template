from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException

from app.api.router import api_router
from app.core.logging import configure_observability
from app.core.problem_details import (
    PROBLEM_MEDIA_TYPE,
    PROBLEM_SCHEMA_REF,
    problem_details_schema,
    problem_response,
)
from app.core.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=None,
        redoc_url=None,
    )

    configure_observability(app)

    def custom_openapi():
        if app.openapi_schema is not None:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
        )

        components = schema.setdefault("components", {})
        schemas = components.setdefault("schemas", {})
        schemas.setdefault("ProblemDetails", problem_details_schema())

        error_responses: dict[int, str] = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
        }

        paths_obj = schema.get("paths", {})
        if not isinstance(paths_obj, dict):
            app.openapi_schema = schema
            return app.openapi_schema

        for path_item in paths_obj.values():
            if not isinstance(path_item, dict):
                continue

            for method, operation in path_item.items():
                if method not in {
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "head",
                    "options",
                    "trace",
                }:
                    continue

                if not isinstance(operation, dict):
                    continue

                responses = operation.setdefault("responses", {})
                if not isinstance(responses, dict):
                    continue

                for status_code, title in error_responses.items():
                    key = str(status_code)
                    resp_obj = responses.get(key)

                    # Replace FastAPI's default 422 schema (application/json) with Problem Details,
                    # since we actually return application/problem+json at runtime.
                    if status_code == 422:
                        responses[key] = {
                            "description": title,
                            "content": {PROBLEM_MEDIA_TYPE: {"schema": PROBLEM_SCHEMA_REF}},
                        }
                        continue

                    if resp_obj is None or not isinstance(resp_obj, dict):
                        resp_obj = {"description": title}
                        responses[key] = resp_obj

                    content_obj = resp_obj.setdefault("content", {})
                    if not isinstance(content_obj, dict):
                        continue
                    content_obj.setdefault(PROBLEM_MEDIA_TYPE, {"schema": PROBLEM_SCHEMA_REF})

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]

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
