"""Model registry for Alembic autogenerate.

SQLModel only adds tables to `SQLModel.metadata` once the model classes have been
imported. This module is the single place to import *all* model modules.

If you never publish this as a library, keeping this explicit is usually the
most reliable approach.

CI can additionally validate this registry covers every `app.slices.*.models`
module via `scripts/verify_model_registry.py`.
"""

from __future__ import annotations

# Keep these imports explicit.
# Add a new import here whenever you add a new slice with models.
import app.slices.users.models  # noqa: F401

# Used by CI to validate coverage.
REGISTERED_MODEL_MODULES: tuple[str, ...] = ("app.slices.users.models",)
