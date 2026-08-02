"""Budget-aware context assembly (PRD §6.4.1).

Builds the orchestrator-bound context bundle from Orchestrator State plus
expert packets, in the fixed §6.3 section order, and enforces the token
budget by dropping the *oldest* packet sections first. The guidance is
≤40K tokens steady-state with an 80K peak; the rationale is context rot —
Liu et al. 2023 ("Lost in the Middle") show retrieval quality degrades as
context grows, so every load operation here is budget-aware by
construction (Anthropic context-engineering, 2025).

This module only *drops*; summarization (compressing a packet instead of
losing it) is the LLM layer — see ``prompts/context_summarizer.v1.md``.
Core state sections are never dropped: if the state alone exceeds the
budget, that is a §6.3 design-constraint violation and we raise rather
than silently truncate.

Token estimate = ceil(total section-body characters / 4), the standard
chars-per-token approximation for English/JSON payloads.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

__all__ = ["ContextBundle", "assemble_context"]

#: (section_name, state_key) for the never-dropped core sections, in the
#: fixed §6.3 order. "intent" is special-cased (two state keys).
_CORE_SCALARS: tuple[tuple[str, str], ...] = (
    ("drift", "drift"),
    ("budget", "budget"),
    ("approvals", "pending_approvals"),
)


@dataclass(frozen=True)
class ContextBundle:
    """An assembled, budget-fitted context: named sections plus audit data."""

    sections: tuple[tuple[str, str], ...]
    token_estimate: int
    dropped: tuple[str, ...]


def _compact(value: Any) -> str:
    """Deterministic compact JSON for plan/packet bodies."""
    return json.dumps(value, separators=(",", ":"), sort_keys=True, default=str)


def _body(value: Any) -> str:
    return value if isinstance(value, str) else _compact(value)


def _estimate(bodies_chars: int) -> int:
    return -(-bodies_chars // 4)  # ceil division


def _core_sections(state: Mapping[str, Any]) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []

    intent_parts = []
    if state.get("destination") is not None:
        intent_parts.append(f"destination: {state['destination']}")
    if state.get("intent_ref") is not None:
        intent_parts.append(f"intent_ref: {state['intent_ref']}")
    if intent_parts:
        sections.append(("intent", "\n".join(intent_parts)))

    if state.get("plan") is not None:
        sections.append(("plan", _compact(state["plan"])))

    for name, key in _CORE_SCALARS:
        if state.get(key) is not None:
            sections.append((name, _body(state[key])))

    return sections


def assemble_context(
    state: Mapping[str, Any],
    packets: Sequence[Mapping[str, Any]],
    *,
    budget_tokens: int = 40_000,
) -> ContextBundle:
    """Assemble the §6.3-ordered context bundle within *budget_tokens*.

    Sections with no source data are omitted. Packet sections are emitted
    newest-first (input order is chronological). Over budget, packet
    sections are dropped oldest-first and recorded in ``dropped``; core
    sections are never dropped. Raises ValueError if ``budget_tokens <= 0``
    or if the core sections alone exceed the budget.
    """
    if budget_tokens <= 0:
        raise ValueError(f"budget_tokens must be positive (got {budget_tokens})")

    core = _core_sections(state)
    core_chars = sum(len(body) for _, body in core)
    if _estimate(core_chars) > budget_tokens:
        raise ValueError(
            "core state sections alone exceed the context budget "
            f"({_estimate(core_chars)} > {budget_tokens} tokens): the state "
            "is too big — a §6.3 design-constraint violation, not something "
            "to silently truncate"
        )

    kept: list[tuple[str, str]] = [
        (f"packet:{packet.get('task_id', 'unknown')}", _compact(packet))
        for packet in reversed(list(packets))
    ]
    dropped: list[str] = []
    total_chars = core_chars + sum(len(body) for _, body in kept)
    while kept and _estimate(total_chars) > budget_tokens:
        name, body = kept.pop()  # end of newest-first list == oldest packet
        dropped.append(name)
        total_chars -= len(body)

    return ContextBundle(
        sections=tuple(core + kept),
        token_estimate=_estimate(total_chars),
        dropped=tuple(dropped),
    )
