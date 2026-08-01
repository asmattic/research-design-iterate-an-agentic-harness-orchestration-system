"""Regression gate (Phase 2D stub): gates config changes per §14.6 policy."""

from __future__ import annotations

from typing import Mapping


def regression_gate(
    current: Mapping[str, float],
    baseline: Mapping[str, float],
    thresholds: Mapping[str, float],
) -> int:
    """Return a process exit code: non-zero if any score regresses past threshold."""
    raise NotImplementedError(
        "Phase 2D: non-zero exit when any score regresses past threshold"
    )
