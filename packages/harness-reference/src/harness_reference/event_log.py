"""L3 event log: append-only JSONL per PRD §15.3 / §10.

Every envelope appended to the log must validate against the protocol's
``event-envelope`` schema; :func:`validate_envelope` delegates to
``harness_protocol.iter_errors("event-envelope", ...)``. The JSONL file on
disk is the single source of truth — reads stream from disk on every call, so
there is no in-memory cache that can drift from the file.

Concurrency: Round 2 assumes a **single writer** per log file (one
orchestrator process owns each campaign's L3 log). Appends are single
``write()`` calls on an append-mode handle, which is line-atomic on local
POSIX filesystems for typical envelope sizes, but nothing here locks the
file — multi-emitter convergence on one log gets explicit locking in Phase
2C when harness-os introduces concurrent emitters.
"""

from __future__ import annotations

import json
import os
import pathlib
from typing import Any, Iterator, Mapping

from harness_protocol import iter_errors


def validate_envelope(envelope: Mapping[str, Any]) -> list[str]:
    """Return schema-validation error strings for *envelope* (empty if valid)."""
    return iter_errors("event-envelope", envelope)


class EventLog:
    """Append-only JSONL event log (PRD §15.3): one envelope per line."""

    def __init__(self, path: os.PathLike[str] | str) -> None:
        """Bind the log to a JSONL file at *path* (created lazily on append)."""
        self._path = pathlib.Path(path)

    def append(self, envelope: Mapping[str, Any]) -> str:
        """Validate and append *envelope*, returning its event_id.

        Raises ValueError (message lists every schema error) on an invalid
        envelope; nothing is written in that case. On success exactly one
        JSON line is appended to the log file.
        """
        errors = validate_envelope(envelope)
        if errors:
            raise ValueError(
                "invalid event envelope: " + "; ".join(errors)
            )
        self._path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(dict(envelope), ensure_ascii=False)
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return str(envelope["event_id"])

    def _read_lines(self) -> Iterator[str]:
        """Yield non-empty JSONL lines from disk; a missing file is an empty log."""
        if not self._path.is_file():
            return
        with open(self._path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if line:
                    yield line

    def events(
        self, *, kind: str | None = None, task_id: str | None = None
    ) -> Iterator[dict[str, Any]]:
        """Iterate stored envelopes, optionally filtered by kind and/or task_id."""
        for line in self._read_lines():
            envelope: dict[str, Any] = json.loads(line)
            if kind is not None and envelope.get("kind") != kind:
                continue
            if task_id is not None and envelope.get("task_id") != task_id:
                continue
            yield envelope

    def __len__(self) -> int:
        """Return the number of envelopes in the log."""
        return sum(1 for _ in self._read_lines())
