"""Weight Tweaker (PRD §6.4.5).

Adjusts per-agent trust weights over time from retrospective outcomes: if
the budget-expert has been right 92% of the time and the tax-expert 71%,
their claims get scaled accordingly. Consumes ``weight_adjustment``
proposals produced by the retrospective engine
(``harness_reference.retrospective.Proposal``) and emits the updated
weight table used by the Signal/Noise Attributor (§6.4.4).

Cadence: per-task update and per-campaign recalibration — never per-turn,
which would overfit to individual emissions (§6.4.5).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = ["apply_proposals"]


def _field(proposal: Any, name: str, default: Any = None) -> Any:
    """Read *name* from a Proposal object or a plain mapping."""
    if isinstance(proposal, Mapping):
        return proposal.get(name, default)
    return getattr(proposal, name, default)


def apply_proposals(
    table: Mapping[str, float],
    proposals: Sequence[Any],
    *,
    floor: float = 0.1,
    ceiling: float = 2.0,
    default_weight: float = 1.0,
) -> dict[str, float]:
    """Apply retrospective weight-adjustment proposals to a trust table.

    Accepts both ``harness_reference.retrospective.Proposal`` objects and
    plain mappings with the same fields. Only ``kind ==
    "weight_adjustment"`` entries apply — their ``payload`` carries
    ``agent_id`` and ``suggested_delta``; every other kind is ignored
    silently (they belong to other retrospective consumers). Agents absent
    from the table start at *default_weight*. Results are clamped to
    ``[floor, ceiling]``. Returns a NEW dict containing every agent from
    the input table plus any newly-adjusted agents; the input is never
    mutated. ``floor > ceiling`` raises :class:`ValueError`.
    """
    if floor > ceiling:
        raise ValueError(f"floor {floor} must not exceed ceiling {ceiling}")
    updated: dict[str, float] = dict(table)
    for proposal in proposals:
        if _field(proposal, "kind") != "weight_adjustment":
            continue
        payload = _field(proposal, "payload") or {}
        agent_id = payload["agent_id"]
        delta = payload["suggested_delta"]
        current = updated.get(agent_id, default_weight)
        updated[agent_id] = min(ceiling, max(floor, current + delta))
    return updated
