"""Campaign report writer.

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

A section with a matching :class:`ScoreResult` (by scorer name) renders the
value plus its details; anything else renders "not scored this run".
Intent-alignment, Human gates, and Retrospective notes have no Round 2
scorer — they arrive with the adapter's live campaigns.

All claims in the report must be traceable to the event log.
"""

from __future__ import annotations

import os
import pathlib
from typing import Sequence

from .scorers import ScoreResult

#: §14.8 section headings, in order, mapped to the scorer that feeds them
#: (None: no Round 2 scorer exists for the section).
SECTIONS: tuple[tuple[str, str | None], ...] = (
    ("Completion", "completion"),
    ("Intent-alignment", None),
    ("Drift", "drift"),
    ("Calibration", "calibration"),
    ("Cost", "cost"),
    ("Safety", "safety"),
    ("Human gates", None),
    ("Retrospective notes", None),
)

NOT_SCORED = "not scored this run"


def _format_value(value: float) -> str:
    if isinstance(value, float) and value != int(value):
        return f"{value:.4f}"
    return str(int(value)) if isinstance(value, float) else str(value)


def _render_section(heading: str, result: ScoreResult | None) -> list[str]:
    lines = [f"## {heading}", ""]
    if result is None:
        lines.append(NOT_SCORED)
    else:
        lines.append(f"value: {_format_value(result.value)}")
        for key, val in result.details.items():
            lines.append(f"- {key}: {val}")
    lines.append("")
    return lines


def write_report(
    campaign_id: str,
    results: Sequence[ScoreResult],
    output_dir: os.PathLike[str] | str,
) -> pathlib.Path:
    """Render ``report.md`` for one campaign and return its path.

    ``output_dir`` is created if absent. Sections follow the §14.8 order;
    each renders its matching result or "not scored this run".
    """
    out_dir = pathlib.Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    by_scorer = {result.scorer: result for result in results}
    lines: list[str] = [f"# Campaign {campaign_id} report", ""]
    for heading, scorer_name in SECTIONS:
        result = by_scorer.get(scorer_name) if scorer_name is not None else None
        lines.extend(_render_section(heading, result))
    path = out_dir / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
