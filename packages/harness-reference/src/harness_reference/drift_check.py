"""Composite drift signal per PRD §11.

Round 2 computes a lexical composite from two sub-signals (signal_a,
signal_b); vector-based signals are deferred per the §22 kickoff question.
Thresholds map the composite onto a status ladder:
ok < warn_threshold <= warn < pause_threshold <= pause (halt is reserved
for escalation policy layered above this module).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DEFAULT_WARN_THRESHOLD: float = 0.35
DEFAULT_PAUSE_THRESHOLD: float = 0.55


@dataclass(frozen=True)
class DriftResult:
    """Outcome of a drift check: sub-signals, composite, and status."""

    signal_a: float
    signal_b: float
    composite: float
    status: Literal["ok", "warn", "pause", "halt"]


def drift_check(
    intent_text: str,
    state_summary: str,
    *,
    warn_threshold: float = DEFAULT_WARN_THRESHOLD,
    pause_threshold: float = DEFAULT_PAUSE_THRESHOLD,
) -> DriftResult:
    """Compare *state_summary* against *intent_text* and return a DriftResult."""
    raise NotImplementedError(
        "Phase 2B: compute lexical sub-signals, combine into a composite, map to status"
    )
