"""Scorer registry: one real dummy scorer plus five Phase 2D stubs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ScoreResult:
    """A single scorer's output for one benchmark run."""

    scorer: str
    value: float
    details: dict[str, Any] = field(default_factory=dict)


SCORER_NAMES = ("dummy", "calibration", "drift", "completion", "cost", "safety")


class DummyScorer:
    """Trivial scorer proving the pipeline end-to-end: always scores 1.0."""

    name = "dummy"

    def score(self, events: Sequence[Mapping[str, Any]]) -> ScoreResult:
        """Summarize the event stream: count and distinct event kinds."""
        return ScoreResult(
            scorer=self.name,
            value=1.0,
            details={
                "event_count": len(events),
                "kinds": sorted({e.get("kind", "?") for e in events}),
            },
        )


class CalibrationScorer:
    """Stub: Brier + ECE over (claim, confidence, verifier-outcome) tuples."""

    name = "calibration"

    def score(self, events: Sequence[Mapping[str, Any]]) -> ScoreResult:
        raise NotImplementedError(
            "Phase 2D: compute Brier + ECE on testable claims (prd/14-evaluation.md §14.5)"
        )


class DriftScorer:
    """Stub: intent-vs-context drift via the composite signal."""

    name = "drift"

    def score(self, events: Sequence[Mapping[str, Any]]) -> ScoreResult:
        raise NotImplementedError(
            "Phase 2D: compute the §11 composite drift signal (prd/14-evaluation.md §14.5)"
        )


class CompletionScorer:
    """Stub: pass/partial/fail with per-criterion breakdown."""

    name = "completion"

    def score(self, events: Sequence[Mapping[str, Any]]) -> ScoreResult:
        raise NotImplementedError(
            "Phase 2D: score completion with criteria breakdown (prd/14-evaluation.md §14.8)"
        )


class CostScorer:
    """Stub: tokens, wall-clock, and USD from event-log accounting."""

    name = "cost"

    def score(self, events: Sequence[Mapping[str, Any]]) -> ScoreResult:
        raise NotImplementedError(
            "Phase 2D: integrate tokens / wall-clock / USD (prd/14-evaluation.md §14.5)"
        )


class SafetyScorer:
    """Stub: adversarial-benchmark pass rate."""

    name = "safety"

    def score(self, events: Sequence[Mapping[str, Any]]) -> ScoreResult:
        raise NotImplementedError(
            "Phase 2D: compute adversarial pass rate (prd/14-evaluation.md §14.4, §14.8)"
        )


_SCORERS = {
    "dummy": DummyScorer,
    "calibration": CalibrationScorer,
    "drift": DriftScorer,
    "completion": CompletionScorer,
    "cost": CostScorer,
    "safety": SafetyScorer,
}


def get_scorer(name: str) -> Any:
    """Return a scorer instance for *name*; KeyError lists the known names."""
    try:
        cls = _SCORERS[name]
    except KeyError:
        raise KeyError(
            f"unknown scorer {name!r}; known scorers: {', '.join(SCORER_NAMES)}"
        ) from None
    return cls()
