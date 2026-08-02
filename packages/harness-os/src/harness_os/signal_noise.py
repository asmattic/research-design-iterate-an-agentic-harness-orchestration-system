"""Signal / Noise Attributor (PRD §6.4.4, factor table §9.1).

Assigns each incoming claim a signal-weight from five factors with the
§9.1 default weights: agent calibration score (0.30), deterministic
verifier result (0.30), cross-agent agreement (0.20), BS-detector flags
(0.15), and tool-result authority (0.05). Weights are configurable per
cohort — e.g. a legal cohort weights primary-source authority more
heavily, a research cohort weights cross-agent agreement less heavily
because dissent is the point there (§9.1). Output is the ranked list of
weighted claims consumed by the orchestrator packet builder.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

__all__ = ["DEFAULT_FACTOR_WEIGHTS", "WeightedClaim", "weigh"]

DEFAULT_FACTOR_WEIGHTS: dict[str, float] = {
    "calibration": 0.30,
    "verifier": 0.30,
    "agreement": 0.20,
    "bs": 0.15,
    "authority": 0.05,
}

_VERIFIER_FACTORS: dict[str, float] = {"pass": 1.0, "fail": 0.0, "abstain": 0.5}
_SOFT_BS_FLAGS = frozenset({"over_confident", "unsupported"})
_KNOWN_BS_FLAGS = _SOFT_BS_FLAGS | {"clean", "hallucinated"}
_SUM_TOLERANCE = 1e-9


@dataclass(frozen=True)
class WeightedClaim:
    """A claim with its computed signal-weight and per-factor breakdown."""

    claim: Mapping[str, Any]
    weight: float
    factors: dict[str, float]


def _validated_weights(
    factor_weights: Mapping[str, float] | None,
) -> Mapping[str, float]:
    if factor_weights is None:
        return DEFAULT_FACTOR_WEIGHTS
    expected = set(DEFAULT_FACTOR_WEIGHTS)
    got = set(factor_weights)
    if got != expected:
        raise ValueError(
            f"factor_weights must have exactly the keys {sorted(expected)}, "
            f"got {sorted(got)}"
        )
    total = sum(factor_weights.values())
    if abs(total - 1.0) > _SUM_TOLERANCE:
        raise ValueError(f"factor_weights must sum to 1.0, got {total}")
    return factor_weights


def _unit_factor(claim: Mapping[str, Any], key: str, index: int) -> float:
    value = claim.get(key, 0.5)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"claim {index}: {key!r} must be a number, got {value!r}")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"claim {index}: {key!r} value {value} not in [0, 1]")
    return value


def _verifier_factor(claim: Mapping[str, Any], index: int) -> float:
    result = claim.get("verifier_result")
    if result is None:
        return 0.5
    factor = _VERIFIER_FACTORS.get(result)
    if factor is None:
        raise ValueError(
            f"claim {index}: unknown verifier_result {result!r} "
            f"(expected one of {sorted(_VERIFIER_FACTORS)})"
        )
    return factor


def _bs_factor(claim: Mapping[str, Any], index: int) -> float:
    flags = claim.get("bs_flags", [])
    if not isinstance(flags, list):
        raise ValueError(
            f"claim {index}: 'bs_flags' must be a list, got {type(flags).__name__}"
        )
    unknown = [f for f in flags if f not in _KNOWN_BS_FLAGS]
    if unknown:
        raise ValueError(f"claim {index}: unknown bs_flags {unknown!r}")
    if "hallucinated" in flags:
        return 0.0
    if any(f in _SOFT_BS_FLAGS for f in flags):
        return 0.5
    return 1.0


def weigh(
    claims: Sequence[Mapping[str, Any]],
    *,
    factor_weights: Mapping[str, float] | None = None,
) -> list[WeightedClaim]:
    """Weight and rank claims per the §9.1 factor table.

    Each claim may carry ``calibration``, ``verifier_result``,
    ``agreement``, ``bs_flags``, and ``authority`` metadata; missing
    numeric factors default to 0.5 (uninformative), missing/clean BS flags
    to 1.0. The result is sorted by weight descending; ties keep input
    order. Out-of-range factor values raise :class:`ValueError` naming the
    claim index. Custom ``factor_weights`` must carry exactly the five
    §9.1 keys and sum to 1.0.
    """
    weights = _validated_weights(factor_weights)
    weighted: list[WeightedClaim] = []
    for index, claim in enumerate(claims):
        factors = {
            "calibration": _unit_factor(claim, "calibration", index),
            "verifier": _verifier_factor(claim, index),
            "agreement": _unit_factor(claim, "agreement", index),
            "bs": _bs_factor(claim, index),
            "authority": _unit_factor(claim, "authority", index),
        }
        weight = sum(factors[name] * weights[name] for name in factors)
        weighted.append(WeightedClaim(claim=claim, weight=weight, factors=factors))
    weighted.sort(key=lambda wc: -wc.weight)  # stable: ties keep input order
    return weighted
