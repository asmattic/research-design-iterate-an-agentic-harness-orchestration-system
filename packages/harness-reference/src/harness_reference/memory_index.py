"""Tiered memory index per PRD §10 / §15.6.

Memory entries are schema-validated dicts persisted one-per-file under a root
directory (``<root>/<memory_id>.json``), filterable by tier/scope/domain/tags,
with supersedes chains linking revisions. Validation delegates to the
harness-protocol ``memory-index`` schema. The directory is the source of
truth — queries re-read it on every call.
"""

from __future__ import annotations

import json
import os
import pathlib
from typing import Any, Mapping, Sequence

from harness_protocol import iter_errors


class MemoryIndex:
    """Index of memory entries rooted at a directory (PRD §15.6 layout)."""

    def __init__(self, root: os.PathLike[str] | str) -> None:
        """Bind the index to *root* (created on first add if missing)."""
        self._root = pathlib.Path(root)

    def _entry_path(self, memory_id: str) -> pathlib.Path:
        return self._root / f"{memory_id}.json"

    def _all_entries(self) -> dict[str, dict[str, Any]]:
        """Load every persisted entry, keyed by memory_id."""
        entries: dict[str, dict[str, Any]] = {}
        if not self._root.is_dir():
            return entries
        for path in self._root.glob("*.json"):
            entry: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
            entries[entry["memory_id"]] = entry
        return entries

    def add(self, entry: Mapping[str, Any]) -> str:
        """Validate and store *entry* as ``<root>/<memory_id>.json``.

        Raises ValueError (message lists every schema error) on an invalid
        entry. A ``supersedes`` reference to an id that is not (yet) stored
        is allowed. Returns the entry's memory_id.
        """
        errors = iter_errors("memory-index", entry)
        if errors:
            raise ValueError("invalid memory entry: " + "; ".join(errors))
        self._root.mkdir(parents=True, exist_ok=True)
        memory_id = str(entry["memory_id"])
        self._entry_path(memory_id).write_text(
            json.dumps(dict(entry), ensure_ascii=False), encoding="utf-8"
        )
        return memory_id

    def get(self, memory_id: str) -> dict[str, Any]:
        """Return the stored entry with *memory_id* (KeyError if absent)."""
        path = self._entry_path(memory_id)
        if not path.is_file():
            raise KeyError(memory_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def query(
        self,
        *,
        tier: str | None = None,
        scope: str | None = None,
        domain: str | None = None,
        tags: Sequence[str] | None = None,
        include_superseded: bool = False,
    ) -> list[dict[str, Any]]:
        """Return entries matching every provided filter, sorted by memory_id.

        tier/scope/domain filter by equality; *tags* matches entries carrying
        ALL requested tags. Entries superseded by another stored entry are
        excluded unless *include_superseded* is true.
        """
        entries = self._all_entries()
        superseded_ids = {
            e["supersedes"] for e in entries.values() if e.get("supersedes")
        }
        results: list[dict[str, Any]] = []
        for memory_id, entry in entries.items():
            if not include_superseded and memory_id in superseded_ids:
                continue
            if tier is not None and entry.get("tier") != tier:
                continue
            if scope is not None and entry.get("scope") != scope:
                continue
            if domain is not None and entry.get("domain") != domain:
                continue
            if tags is not None:
                entry_tags = set(entry.get("tags") or [])
                if not set(tags).issubset(entry_tags):
                    continue
            results.append(entry)
        results.sort(key=lambda e: e["memory_id"])
        return results

    def resolve(self, memory_id: str) -> dict[str, Any]:
        """Follow the supersedes chain forward from *memory_id* to the newest entry.

        Starting from any id in the chain, repeatedly steps to the stored
        entry that supersedes the current one until reaching the entry that
        nobody supersedes. Raises KeyError for an unknown id and ValueError
        if the chain contains a cycle.
        """
        entries = self._all_entries()
        if memory_id not in entries:
            raise KeyError(memory_id)
        superseder_of: dict[str, str] = {}
        for mid, entry in sorted(entries.items()):
            prior = entry.get("supersedes")
            if prior and prior not in superseder_of:
                superseder_of[prior] = mid
        current = memory_id
        seen = {current}
        while current in superseder_of:
            current = superseder_of[current]
            if current in seen:
                raise ValueError(
                    f"supersedes cycle detected while resolving {memory_id!r}"
                )
            seen.add(current)
        return entries[current]
