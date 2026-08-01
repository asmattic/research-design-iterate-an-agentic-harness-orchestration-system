"""L3 event log: append-only JSONL per PRD §15.3 / §10.

Every envelope appended to the log must validate against the protocol's
``event-envelope`` schema. In Phase 2B, :func:`validate_envelope` delegates to
``harness_protocol.iter_errors("event-envelope", ...)``; the import is kept
out of module scope so this package imports even without harness-protocol.
"""

from __future__ import annotations

import os
from typing import Any, Iterator, Mapping


def validate_envelope(envelope: Mapping[str, Any]) -> list[str]:
    """Return schema-validation error strings for *envelope* (empty if valid)."""
    raise NotImplementedError(
        "Phase 2B: delegate to harness_protocol.iter_errors('event-envelope', envelope)"
    )


class EventLog:
    """Append-only JSONL event log (PRD §15.3): one envelope per line."""

    def __init__(self, path: os.PathLike[str] | str) -> None:
        """Bind the log to a JSONL file at *path* (created lazily on append)."""
        raise NotImplementedError(
            "Phase 2B: store the path and prepare lazy JSONL file creation"
        )

    def append(self, envelope: Mapping[str, Any]) -> str:
        """Validate and append *envelope*, returning its event_id."""
        raise NotImplementedError(
            "Phase 2B: reject schema-invalid envelopes, append one JSONL line, return event_id"
        )

    def events(
        self, *, kind: str | None = None, task_id: str | None = None
    ) -> Iterator[dict[str, Any]]:
        """Iterate stored envelopes, optionally filtered by kind and/or task_id."""
        raise NotImplementedError(
            "Phase 2B: stream JSONL lines as dicts, filtering on kind and task_id"
        )

    def __len__(self) -> int:
        """Return the number of envelopes in the log."""
        raise NotImplementedError("Phase 2B: count JSONL lines in the log file")
