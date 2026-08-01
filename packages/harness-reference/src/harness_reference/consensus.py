"""Consensus aggregation per PRD §9.2.

Agent emissions are grouped into weighted clusters; the aggregate derives a
confidence interval and preserves any dissenting cluster whose weight share
meets or exceeds the dissent floor. The returned packet must validate against
the harness-protocol consensus-packet schema.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

DISSENT_FLOOR: float = 0.15


def aggregate(
    emissions: Sequence[Mapping[str, Any]],
    *,
    campaign_id: str,
    cohort: str,
    task_id: str,
    dissent_floor: float = DISSENT_FLOOR,
) -> dict[str, Any]:
    """Aggregate agent *emissions* into a schema-valid consensus packet.

    Each emission is a mapping with keys ``agent_id``, ``value``,
    ``reasoning``, ``weight``, and ``confidence``.
    """
    raise NotImplementedError(
        "Phase 2B: cluster weighted emissions, derive interval, preserve dissent >= floor"
    )
