"""Retrospective proposal generation per PRD §13.2.

A retrospective replays a campaign's event stream and emits improvement
proposals: prompt diffs, memory entries, or agent-weight adjustments. It
never applies changes itself; proposals are reviewed upstream.

This Round 2 implementation is fully deterministic — two cheap rules mined
straight from the event stream, no LLM involved:

1. **Verifier failures → weight adjustments.** Each ``verifier_result``
   event whose payload reports ``result == "fail"`` is attributed to an
   agent (``payload.agent_id``, falling back to the emitter when the
   emitter is an agent). Per-agent failure counts become one
   ``weight_adjustment`` proposal each, with a suggested delta of
   ``-0.05`` per failure, floored at ``-0.25``.
2. **Drift excursions → memory entries.** Each ``drift_check`` event whose
   payload reports a status of ``"pause"`` or ``"halt"`` yields one
   ``memory_entry`` proposal targeting the campaign (at most one proposal
   per event).

The LLM-as-judge layer described in §13.2 (prompt diffs, rubric scoring)
arrives with harness-os; this module intentionally stops at what can be
computed deterministically from the event log.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping

#: Suggested weight decrease per attributed verifier failure.
_DELTA_PER_FAILURE = -0.05

#: Most negative suggested delta a single proposal may carry.
_DELTA_FLOOR = -0.25

#: Drift statuses that count as excursions worth remembering.
_DRIFT_EXCURSION_STATUSES = frozenset({"pause", "halt"})


@dataclass(frozen=True)
class Proposal:
    """A single retrospective improvement proposal."""

    kind: Literal["prompt_diff", "memory_entry", "weight_adjustment"]
    target: str
    rationale: str
    payload: dict[str, Any]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    """Return *value* if it is a mapping, else an empty mapping."""
    return value if isinstance(value, Mapping) else {}


def _attributed_agent(event: Mapping[str, Any]) -> str | None:
    """Resolve which agent a verifier failure belongs to, or None to skip."""
    payload = _as_mapping(event.get("payload"))
    agent_id = payload.get("agent_id")
    if isinstance(agent_id, str) and agent_id:
        return agent_id
    emitter = _as_mapping(event.get("emitter"))
    if emitter.get("kind") == "agent":
        emitter_id = emitter.get("id")
        if isinstance(emitter_id, str) and emitter_id:
            return emitter_id
    return None


def retrospective(events: Iterable[Mapping[str, Any]]) -> list[Proposal]:
    """Analyze *events* and return improvement proposals (possibly empty).

    Events are mappings shaped like event envelopes; partial events are
    tolerated (missing keys never raise). Output order is deterministic:
    ``weight_adjustment`` proposals sorted by agent id, then
    ``memory_entry`` proposals in event order.
    """
    failure_counts: dict[str, int] = {}
    verifier_ids: dict[str, list[str]] = {}
    drift_proposals: list[Proposal] = []

    for event in events:
        if not isinstance(event, Mapping):
            continue
        kind = event.get("kind")
        payload = _as_mapping(event.get("payload"))

        if kind == "verifier_result" and payload.get("result") == "fail":
            agent_id = _attributed_agent(event)
            if agent_id is None:
                continue
            failure_counts[agent_id] = failure_counts.get(agent_id, 0) + 1
            verifier_id = payload.get("verifier_id")
            ids = verifier_ids.setdefault(agent_id, [])
            if isinstance(verifier_id, str) and verifier_id and verifier_id not in ids:
                ids.append(verifier_id)

        elif kind == "drift_check" and payload.get("status") in _DRIFT_EXCURSION_STATUSES:
            event_id = event.get("event_id")
            drift_proposals.append(
                Proposal(
                    kind="memory_entry",
                    target="campaign",
                    rationale=(
                        f"drift_check reported status "
                        f"{payload.get('status')!r} (event {event_id!r}); "
                        "record the excursion for future planning"
                    ),
                    payload={"note": "drift excursion", "event_id": event_id},
                )
            )

    adjustments: list[Proposal] = []
    for agent_id in sorted(failure_counts):
        count = failure_counts[agent_id]
        ids = verifier_ids.get(agent_id, [])
        verifier_desc = ", ".join(ids) if ids else "unidentified verifiers"
        adjustments.append(
            Proposal(
                kind="weight_adjustment",
                target=agent_id,
                rationale=(
                    f"agent {agent_id} accumulated {count} verifier "
                    f"failure(s) from: {verifier_desc}"
                ),
                payload={
                    "agent_id": agent_id,
                    "verifier_failures": count,
                    "suggested_delta": max(_DELTA_FLOOR, _DELTA_PER_FAILURE * count),
                },
            )
        )

    return adjustments + drift_proposals
