"""Deterministic BS tripwires (PRD §6.4.2).

These heuristics are tripwires, not judgment: cheap, deterministic checks
that catch the obvious failure shapes — over-confident claims with no
verification, values asserted without sources, and citations that are not
even syntactically plausible. The actual judgment layer is an LLM-as-judge
against a skeptic rubric, versioned at ``prompts/bs_detector.v1.md`` and
calibrated per Kadavath et al. 2022 (self-calibration) and Zheng et al.
2024 (LLM-as-judge) — the §6.4.2 citations. Flagged content routes back
to the emitting cohort with a reject reason rather than reaching the
primary orchestrator.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urlparse

__all__ = ["BSReport", "inspect_emission"]

#: Canonical flag vocabulary; "clean" appears alone, the rest may combine.
FLAGS: tuple[str, ...] = ("clean", "over_confident", "unsupported", "hallucinated")

_CONFIDENCE_TRIPWIRE = 0.95


@dataclass(frozen=True)
class BSReport:
    """Tripwire outcome: flags plus reasons parallel to the non-clean flags."""

    flags: tuple[str, ...]
    reasons: tuple[str, ...]


def _has_verifier_pass(emission: Mapping[str, Any]) -> bool:
    results = emission.get("verifier_results") or []
    return any(
        isinstance(entry, Mapping) and entry.get("result") == "pass"
        for entry in results
    )


def _source_is_plausible(source: Any) -> bool:
    """http(s) URL with a netloc, or any non-empty non-URL-shaped string."""
    if not isinstance(source, str) or not source.strip():
        return False
    if "://" not in source:
        return True  # plausible doc/file reference, e.g. "docs/zoning.pdf"
    parsed = urlparse(source)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def inspect_emission(emission: Mapping[str, Any]) -> BSReport:
    """Run the deterministic tripwires over one expert emission.

    Tolerates missing keys. Each heuristic is independent; no fired flags
    yields ``("clean",)`` with empty reasons.
    """
    flags: list[str] = []
    reasons: list[str] = []
    verified = _has_verifier_pass(emission)

    confidence = emission.get("confidence")
    if (
        isinstance(confidence, (int, float))
        and confidence >= _CONFIDENCE_TRIPWIRE
        and not verified
    ):
        flags.append("over_confident")
        reasons.append(
            f"confidence {confidence} >= {_CONFIDENCE_TRIPWIRE} with no "
            "passing verifier result"
        )

    sources = emission.get("sources") or []
    if emission.get("value") is not None and not sources and not verified:
        flags.append("unsupported")
        reasons.append(
            "value emitted with no sources and no passing verifier result"
        )

    implausible = [s for s in sources if not _source_is_plausible(s)]
    if implausible:
        flags.append("hallucinated")
        reasons.append(
            "implausible source citation(s): "
            + ", ".join(repr(s) for s in implausible)
        )

    if not flags:
        return BSReport(flags=("clean",), reasons=())
    return BSReport(flags=tuple(flags), reasons=tuple(reasons))
