from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

PROBLEM_MEDIA_TYPE = "application/problem+json"
PROBLEM_SCHEMA_REF = {"$ref": "#/components/schemas/ProblemDetails"}


def problem_details_schema() -> dict[str, Any]:
    # RFC 9457 Problem Details for HTTP APIs
    # Extensions are allowed, so we keep it flexible.
    return {
        "type": "object",
        "required": ["type", "title", "status"],
        "properties": {
            "type": {"type": "string", "format": "uri-reference", "example": "about:blank"},
            "title": {"type": "string"},
            "status": {"type": "integer", "format": "int32"},
            "detail": {"type": "string"},
            "instance": {"type": "string", "format": "uri-reference"},
            # Common extension we include for 422 validation errors.
            "errors": {"type": "array", "items": {"type": "object"}},
        },
        "additionalProperties": True,
    }


def _default_title(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Error"


def problem_response(
    *,
    request: Request,
    status_code: int,
    detail: str | None = None,
    title: str | None = None,
    type_: str = "about:blank",
    instance: str | None = None,
    extensions: dict[str, Any] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "type": type_,
        "title": title or _default_title(status_code),
        "status": status_code,
    }

    if detail is not None:
        payload["detail"] = detail

    payload["instance"] = instance or request.url.path

    if extensions:
        payload.update(extensions)

    return JSONResponse(status_code=status_code, content=payload, media_type=PROBLEM_MEDIA_TYPE)
