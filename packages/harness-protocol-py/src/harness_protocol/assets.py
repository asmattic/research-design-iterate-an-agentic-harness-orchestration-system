"""Locate the canonical protocol assets (schemas/ and examples/) on disk."""

from __future__ import annotations

import os
import pathlib

_ENV_VAR = "HARNESS_PROTOCOL_ASSETS"


def _candidates() -> list[tuple[str, pathlib.Path]]:
    """Return (label, path) candidates in resolution priority order."""
    out: list[tuple[str, pathlib.Path]] = []
    env = os.environ.get(_ENV_VAR)
    if env:
        out.append((f"env {_ENV_VAR}", pathlib.Path(env)))
    here = pathlib.Path(__file__).resolve()
    out.append(("bundled package data", here.parent / "_assets"))
    out.append(("repo checkout sibling", here.parents[3] / "harness-protocol"))
    return out


def assets_root(override: str | os.PathLike[str] | None = None) -> pathlib.Path:
    """Return the directory containing ``schemas/`` (and ``examples/``).

    Resolution order: explicit *override* argument, the
    ``HARNESS_PROTOCOL_ASSETS`` environment variable, bundled package data
    (``harness_protocol/_assets``), then the repo-checkout sibling directory
    ``packages/harness-protocol``. Raises RuntimeError naming every attempted
    location if none contains a ``schemas`` subdirectory.
    """
    if override is not None:
        root = pathlib.Path(override)
        if (root / "schemas").is_dir():
            return root
        raise RuntimeError(
            f"harness-protocol assets override {root} has no 'schemas' subdirectory"
        )
    tried: list[str] = []
    for label, path in _candidates():
        if (path / "schemas").is_dir():
            return path
        tried.append(f"{label}: {path}")
    raise RuntimeError(
        "harness-protocol assets not found; no attempted location contains a "
        "'schemas' subdirectory. Tried (in order): " + "; ".join(tried)
        + f". Set ${_ENV_VAR} to a directory containing schemas/ and examples/."
    )


def schemas_dir(override: str | os.PathLike[str] | None = None) -> pathlib.Path:
    """Return the ``schemas/`` directory under :func:`assets_root`."""
    return assets_root(override) / "schemas"


def examples_dir(override: str | os.PathLike[str] | None = None) -> pathlib.Path:
    """Return the ``examples/`` directory under :func:`assets_root`."""
    return assets_root(override) / "examples"
