from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

PROBLEM_MEDIA_TYPE = "application/problem+json"


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
