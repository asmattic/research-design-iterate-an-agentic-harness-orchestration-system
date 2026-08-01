"""Campaign report writer (Phase 2D stub).

The report contract is prd/14-evaluation.md §14.8: per campaign, a
``report.md`` is generated in the campaign folder with these sections:

- Completion         [pass/partial/fail] — criteria breakdown
- Intent-alignment   0.XX — rubric breakdown
- Drift              max 0.XX, final 0.XX — arc
- Calibration        Brier 0.XX, ECE 0.XX — per-cohort
- Cost               tokens, wall-clock, USD
- Safety             adversarial pass rate
- Human gates        N triggered, N approved, N rejected
- Retrospective notes (proposals for agent prompts, weights, memory)

All claims in the report must be traceable to the event log.
"""

from __future__ import annotations

import os
import pathlib
from typing import Sequence

from .scorers import ScoreResult


def write_report(
    campaign_id: str,
    results: Sequence[ScoreResult],
    output_dir: os.PathLike[str] | str,
) -> pathlib.Path:
    """Render ``report.md`` for one campaign and return its path."""
    raise NotImplementedError("Phase 2D: render report.md in the §14.8 format")
