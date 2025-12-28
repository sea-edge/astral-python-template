from __future__ import annotations

import pkgutil
from importlib import import_module

from app.core.model_registry import REGISTERED_MODEL_MODULES


def discover_slice_model_modules() -> set[str]:
    """Discover all `app.slices.<slice>.models` modules present in the package."""
    slices = import_module("app.slices")

    slices_path = getattr(slices, "__path__", None)
    slices_name = getattr(slices, "__name__", "app.slices")
    if slices_path is None:
        raise SystemExit("Expected 'app.slices' to be a package (missing __path__)")

    found: set[str] = set()
    for module_info in pkgutil.iter_modules(slices_path, slices_name + "."):
        if not module_info.ispkg:
            continue

        slice_pkg = import_module(module_info.name)

        slice_path = getattr(slice_pkg, "__path__", None)
        slice_name = getattr(slice_pkg, "__name__", module_info.name)
        if slice_path is None:
            continue

        for child in pkgutil.iter_modules(slice_path, slice_name + "."):
            if child.name.endswith(".models"):
                found.add(child.name)

    return found


def main() -> None:
    discovered = discover_slice_model_modules()
    registered = set(REGISTERED_MODEL_MODULES)

    missing = sorted(discovered - registered)
    extra = sorted(registered - discovered)

    if missing or extra:
        parts: list[str] = ["Model registry mismatch."]
        if missing:
            parts.append(f"Missing in REGISTERED_MODEL_MODULES: {missing}")
        if extra:
            parts.append(f"Not found on disk (remove?): {extra}")
        raise SystemExit("\n".join(parts))

    print(f"OK: model registry covers {len(discovered)} module(s)")


if __name__ == "__main__":
    main()
