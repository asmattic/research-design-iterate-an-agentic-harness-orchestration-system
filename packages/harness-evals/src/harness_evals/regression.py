"""Regression gate: gates config changes per prd/14-evaluation.md §14.6 policy."""

from __future__ import annotations

from typing import Mapping

#: Scorers where a LOWER value is better; everything else is higher-is-better.
LOWER_IS_BETTER = frozenset({"cost"})


def regression_gate(
    current: Mapping[str, float],
    baseline: Mapping[str, float],
    thresholds: Mapping[str, float],
) -> int:
    """Return a process exit code: non-zero if any score regresses past threshold.

    Compares every scorer present in both *baseline* and *current*. The
    per-scorer threshold defaults to 0.0 (any regression trips the gate).
    Higher-is-better scorers regress when ``current < baseline - threshold``;
    scorers in :data:`LOWER_IS_BETTER` (cost) regress when
    ``current > baseline + threshold``. Returns 0 iff no regressions, else 1.
    """
    for name, base_value in baseline.items():
        if name not in current:
            continue
        threshold = thresholds.get(name, 0.0)
        current_value = current[name]
        if name in LOWER_IS_BETTER:
            if current_value > base_value + threshold:
                return 1
        elif current_value < base_value - threshold:
            return 1
    return 0
