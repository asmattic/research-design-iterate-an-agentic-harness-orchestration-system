"""Tiered memory index per PRD §10 / §15.6.

Memory entries are schema-validated dicts stored under a root directory,
organized by tier/scope/domain/tags, with supersedes chains linking revisions.
Phase 2B validation delegates to the harness-protocol memory-entry schema;
the import stays out of module scope to keep Phase 2A import-light.
"""

from __future__ import annotations

import os
from typing import Any, Mapping, Sequence


class MemoryIndex:
    """Index of memory entries rooted at a directory (PRD §15.6 layout)."""

    def __init__(self, root: os.PathLike[str] | str) -> None:
        """Bind the index to *root* (created lazily on first add)."""
        raise NotImplementedError(
            "Phase 2B: store the root path and prepare lazy directory creation"
        )

    def add(self, entry: Mapping[str, Any]) -> str:
        """Validate and store *entry*, returning its memory_id."""
        raise NotImplementedError(
            "Phase 2B: reject schema-invalid entries, persist, return memory_id"
        )

    def get(self, memory_id: str) -> dict[str, Any]:
        """Return the stored entry with *memory_id* (KeyError if absent)."""
        raise NotImplementedError("Phase 2B: load and return the entry by memory_id")

    def query(
        self,
        *,
        tier: str | None = None,
        scope: str | None = None,
        domain: str | None = None,
        tags: Sequence[str] | None = None,
        include_superseded: bool = False,
    ) -> list[dict[str, Any]]:
        """Return entries matching every provided filter, newest first."""
        raise NotImplementedError(
            "Phase 2B: filter entries by tier/scope/domain/tags, hiding superseded by default"
        )

    def resolve(self, memory_id: str) -> dict[str, Any]:
        """Follow the supersedes chain from *memory_id* to the newest entry."""
        raise NotImplementedError(
            "Phase 2B: walk supersedes links and return the terminal (newest) entry"
        )
