"""Locate the campaign templates directory bundled with harness-reference."""

from __future__ import annotations

import os
import pathlib

_ENV_VAR = "HARNESS_REFERENCE_TEMPLATES"


def _candidates() -> list[tuple[str, pathlib.Path]]:
    """Return (label, path) candidates in resolution priority order."""
    out: list[tuple[str, pathlib.Path]] = []
    env = os.environ.get(_ENV_VAR)
    if env:
        out.append((f"env {_ENV_VAR}", pathlib.Path(env)))
    here = pathlib.Path(__file__).resolve()
    out.append(("bundled package data", here.parent / "_templates"))
    out.append(("repo checkout sibling", here.parents[2] / "templates"))
    return out


def templates_dir() -> pathlib.Path:
    """Return the directory containing the campaign templates.

    Resolution order: the ``HARNESS_REFERENCE_TEMPLATES`` environment
    variable, bundled package data (``harness_reference/_templates``), then
    the repo-checkout sibling directory ``packages/harness-reference/templates``.
    Raises RuntimeError naming every attempted location if none exists.
    """
    tried: list[str] = []
    for label, path in _candidates():
        if path.is_dir():
            return path
        tried.append(f"{label}: {path}")
    raise RuntimeError(
        "harness-reference templates not found; no attempted location exists. "
        "Tried (in order): " + "; ".join(tried)
        + f". Set ${_ENV_VAR} to a directory containing the campaign templates."
    )
