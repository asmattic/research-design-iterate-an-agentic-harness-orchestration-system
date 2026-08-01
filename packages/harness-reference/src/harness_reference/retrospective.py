"""Retrospective proposal generation per PRD §13.2.

A retrospective replays a campaign's event stream and emits improvement
proposals: prompt diffs, memory entries, or agent-weight adjustments. It
never applies changes itself; proposals are reviewed upstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping


@dataclass(frozen=True)
class Proposal:
    """A single retrospective improvement proposal."""

    kind: Literal["prompt_diff", "memory_entry", "weight_adjustment"]
    target: str
    rationale: str
    payload: dict[str, Any]


def retrospective(events: Iterable[Mapping[str, Any]]) -> list[Proposal]:
    """Analyze *events* and return improvement proposals (possibly empty)."""
    raise NotImplementedError(
        "Phase 2B: mine the event stream for patterns and emit Proposal objects"
    )
