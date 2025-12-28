# astral-python-template

FastAPI + SQLModel + Alembic + Postgres (v18) のバックエンド雛形です。
Vertical Slice Architecture (VSA) を意識して `src/app/slices/*` に機能を閉じ込めます。

## Prerequisites

- Docker (Postgres 起動用)
- mise (Python / uv 管理)

## Setup

```bash
mise install
uv sync --group dev
```

## Git Hooks (lefthook)

```bash
mise x -- lefthook install
```

## Run Postgres

```bash
docker compose up -d
```

## Migrate

```bash
uv run alembic upgrade head
```

## Run API

```bash
uv run uvicorn app.main:app --reload
```

Open:
- Scalar API Docs: http://localhost:8000/scalar
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health: http://localhost:8000/health

## Dev Commands

```bash
uv run ruff check .
uv run ruff format .
uv run ty check
```
