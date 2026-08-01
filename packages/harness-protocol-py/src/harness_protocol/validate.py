"""Load protocol JSON Schemas and validate instances against them."""

from __future__ import annotations

import functools
import json
from typing import Any

from jsonschema import Draft202012Validator

from harness_protocol.assets import schemas_dir

#: Canonical schema names shipped with protocol v0.2. Re-exported by the
#: package root as ``harness_protocol.SCHEMA_NAMES``.
SCHEMA_NAMES: tuple[str, ...] = (
    "agent-contract",
    "event-envelope",
    "consensus-packet",
    "orchestrator-state",
    "memory-index",
)


@functools.lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    """Return the parsed JSON Schema for *name*; treat the result as read-only.

    Reads ``<schemas_dir>/<name>.schema.json``. The returned dict is cached
    and shared between callers — do NOT mutate it; copy.deepcopy first if you
    need a mutable schema. Raises KeyError (listing the known names) when
    *name* is not one of SCHEMA_NAMES.
    """
    if name not in SCHEMA_NAMES:
        raise KeyError(
            f"unknown schema {name!r}; known schemas: {', '.join(SCHEMA_NAMES)}"
        )
    path = schemas_dir() / f"{name}.schema.json"
    with open(path, encoding="utf-8") as fh:
        schema: dict[str, Any] = json.load(fh)
    return schema


def iter_errors(name: str, instance: Any) -> list[str]:
    """Return sorted human-readable validation errors ("<json_path>: <message>")."""
    validator = Draft202012Validator(load_schema(name))
    return sorted(
        f"{error.json_path}: {error.message}"
        for error in validator.iter_errors(instance)
    )


def is_valid(name: str, instance: Any) -> bool:
    """Return True iff *instance* validates against the schema *name*."""
    return not iter_errors(name, instance)
