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

Hooks:
- `pre-commit`: runs `ruff format` / `ruff check` for staged `*.py` only (and re-stages formatted files)
- `pre-push`: runs `ty check` only when `src/**/*.py` changed

## Run Postgres

```bash
docker compose up -d db
```

## Migrate

```bash
uv run alembic upgrade head
```

## Add DB models (SQLModel)

SQLModel のテーブルは、モデルクラスが import されて初めて `SQLModel.metadata` に登録されます。
そのため Alembic の autogenerate が取りこぼさないように、モデル import を集約しています。

運用:
- 新しい slice に `models.py` を追加したら、[src/app/core/model_registry.py](src/app/core/model_registry.py) に import を1行追加
- 同じく `REGISTERED_MODEL_MODULES` にモジュール名を追加
- CI が [scripts/verify_model_registry.py](scripts/verify_model_registry.py) で `app.slices.*.models` を自動発見し、登録漏れがあると落とします

## Run API

```bash
uv run uvicorn app.main:app --reload
```

## Run API (Docker)

```bash
docker compose up -d --build api
```

Open:
- Scalar API Docs: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health: http://localhost:8000/health

## Dev Commands

```bash
uv run ruff check .
uv run ruff format .
uv run ty check
uv run pytest -q

# Optional: DB-backed tests
RUN_DB_TESTS=1 DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app uv run pytest -q
```
