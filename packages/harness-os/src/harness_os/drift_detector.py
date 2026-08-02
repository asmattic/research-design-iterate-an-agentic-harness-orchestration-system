"""Drift detection wrapper (PRD §6.4.6).

Wraps the reference composite drift signal
(``harness_reference.drift_check``) and maps its status ladder onto
orchestrator actions plus an event-envelope-ready payload.

On ``pause_campaign`` / ``halt_campaign`` the §6.4.6 action is: pause the
campaign, surface the drift to the human, and require an explicit
continue/revise decision before resuming. Enforcement of that action is
the orchestrator's job — this module only decides.

The qualitative LLM-judge channel (the §11 upgrade path for signal_b)
is versioned at ``prompts/drift_judge.v1.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from harness_reference.drift_check import (
    DEFAULT_PAUSE_THRESHOLD,
    DEFAULT_WARN_THRESHOLD,
    DriftResult,
    drift_check,
)

__all__ = ["DriftEvent", "check_drift"]

_STATUS_TO_ACTION: dict[str, str] = {
    "ok": "continue",
    "warn": "surface_warning",
    "pause": "pause_campaign",
    "halt": "halt_campaign",
}


@dataclass(frozen=True)
class DriftEvent:
    """A drift decision: the raw result, the mapped action, and the payload."""

    result: Any  # harness_reference.drift_check.DriftResult
    action: str
    payload: dict[str, Any]


def check_drift(
    intent_text: str,
    state_summary: str,
    *,
    warn_threshold: float | None = None,
    pause_threshold: float | None = None,
) -> DriftEvent:
    """Measure drift of *state_summary* from *intent_text* and decide.

    ``None`` thresholds fall through to the harness_reference defaults.
    The payload is ready for an event-envelope ``drift_check`` entry, with
    floats rounded to 6 places.
    """
    warn = DEFAULT_WARN_THRESHOLD if warn_threshold is None else warn_threshold
    pause = DEFAULT_PAUSE_THRESHOLD if pause_threshold is None else pause_threshold

    result: DriftResult = drift_check(
        intent_text, state_summary, warn_threshold=warn, pause_threshold=pause
    )

    payload: dict[str, Any] = {
        "status": result.status,
        "signal_a": round(result.signal_a, 6),
        "signal_b": round(result.signal_b, 6),
        "composite": round(result.composite, 6),
        "warn_threshold": round(warn, 6),
        "pause_threshold": round(pause, 6),
    }
    return DriftEvent(
        result=result, action=_STATUS_TO_ACTION[result.status], payload=payload
    )
