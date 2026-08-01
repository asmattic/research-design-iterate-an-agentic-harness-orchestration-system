"""Locate the eval assets (benchmarks/ and fixtures/) on disk."""

from __future__ import annotations

import os
import pathlib

_ENV_VAR = "HARNESS_EVALS_ASSETS"


def _candidates() -> list[tuple[str, pathlib.Path, bool]]:
    """Return (label, path, require_benchmarks) candidates in priority order.

    The repo-checkout fallback (``packages/harness-evals``) always exists as a
    directory, so it only counts if it actually contains a ``benchmarks``
    subdirectory (which the fixtures lane provides).
    """
    out: list[tuple[str, pathlib.Path, bool]] = []
    env = os.environ.get(_ENV_VAR)
    if env:
        out.append((f"env {_ENV_VAR}", pathlib.Path(env), False))
    here = pathlib.Path(__file__).resolve()
    out.append(("bundled package data", here.parent / "_assets", False))
    out.append(("repo checkout root", here.parents[2], True))
    return out


def assets_root() -> pathlib.Path:
    """Return the directory containing ``benchmarks/`` and ``fixtures/``.

    Resolution order: the ``HARNESS_EVALS_ASSETS`` environment variable,
    bundled package data (``harness_evals/_assets``), then the repo-checkout
    package root ``packages/harness-evals`` (accepted only when it contains a
    ``benchmarks`` subdirectory). Raises RuntimeError naming every attempted
    location if none resolves.
    """
    tried: list[str] = []
    for label, path, require_benchmarks in _candidates():
        if path.is_dir() and (not require_benchmarks or (path / "benchmarks").is_dir()):
            return path
        tried.append(f"{label}: {path}")
    raise RuntimeError(
        "harness-evals assets not found; no attempted location exists. "
        "Tried (in order): " + "; ".join(tried)
        + f". Set ${_ENV_VAR} to a directory containing benchmarks/ and fixtures/."
    )
