"""Consensus aggregation per PRD §9.2 — deterministic, no LLM.

Round 2 replaces §9.2's LLM-as-judge semantic grouping with deterministic
clustering: non-numeric values cluster by exact equality; numeric values
cluster greedily by relative proximity (an emission joins the first cluster
whose representative — the first-seen value — differs by <= 5%). The
leading cluster is the one with the highest total weight (ties broken by
larger cluster size, then lowest representative, for determinism).

The consensus value is the weighted mean of the leading cluster for numeric
claims (the representative otherwise), with a min/max interval padded by
the weighted stddev (k=1). Dissenting clusters whose weight share meets the
dissent floor are preserved in the packet; smaller ones are dropped.

``outcome_type`` is always ``"strengthened"`` in Round 2: there is no prior
consensus state to revise or calibrate against yet, so every aggregation is
treated as strengthening a fresh position. Rounds with persisted prior
packets will derive revised/unchanged_but_calibrated.

The returned packet validates against the harness-protocol
``consensus-packet`` schema (self-checked via ``harness_protocol.iter_errors``).
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

DISSENT_FLOOR: float = 0.15

#: Relative proximity for a numeric emission to join an existing cluster.
_NUMERIC_JOIN_TOLERANCE: float = 0.05

_VALUE_PRECISION: int = 6
_SHARE_PRECISION: int = 4


def _is_numeric(value: Any) -> bool:
    """True for int/float values (bools are categorical, not numeric)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _joins_numeric_cluster(value: float, representative: float) -> bool:
    """Relative proximity <= 5% of the representative (exact match when rep is 0)."""
    if representative == 0:
        return value == 0
    return abs(value - representative) / abs(representative) <= _NUMERIC_JOIN_TOLERANCE


def _rep_sort_key(cluster: dict[str, Any]) -> tuple[int, Any]:
    """Deterministic ordering key for representatives across value types."""
    rep = cluster["representative"]
    if cluster["numeric"]:
        return (0, float(rep))
    return (1, repr(rep))


def _weighted_mean(values: list[float], weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        return sum(values) / len(values)
    return sum(v * w for v, w in zip(values, weights)) / total


def _weighted_stddev(values: list[float], weights: list[float], mean: float) -> float:
    total = sum(weights)
    if total <= 0:
        variance = sum((v - mean) ** 2 for v in values) / len(values)
    else:
        variance = sum(w * (v - mean) ** 2 for v, w in zip(values, weights)) / total
    return math.sqrt(variance)


def aggregate(
    emissions: Sequence[Mapping[str, Any]],
    *,
    campaign_id: str,
    cohort: str,
    task_id: str,
    dissent_floor: float = DISSENT_FLOOR,
) -> dict[str, Any]:
    """Aggregate agent *emissions* into a schema-valid consensus packet.

    Each emission is a mapping with keys ``agent_id``, ``value``,
    ``reasoning``, ``weight``, and ``confidence`` (weight >= 0).
    Raises ValueError on empty emissions or a negative weight.
    """
    if not emissions:
        raise ValueError("aggregate() requires at least one emission")
    for emission in emissions:
        if float(emission["weight"]) < 0:
            raise ValueError(
                f"emission weight must be >= 0 (agent {emission.get('agent_id')!r})"
            )

    # 1. Greedy deterministic clustering (first-seen representatives).
    clusters: list[dict[str, Any]] = []
    for emission in emissions:
        value = emission["value"]
        numeric = _is_numeric(value)
        target = None
        for cluster in clusters:
            if cluster["numeric"] != numeric:
                continue
            if numeric:
                if _joins_numeric_cluster(float(value), float(cluster["representative"])):
                    target = cluster
                    break
            elif cluster["representative"] == value:
                target = cluster
                break
        if target is None:
            target = {"representative": value, "numeric": numeric, "members": []}
            clusters.append(target)
        target["members"].append(emission)

    for cluster in clusters:
        cluster["weight"] = sum(float(e["weight"]) for e in cluster["members"])

    # 2. Leading cluster: highest weight, then larger cluster, then lowest rep.
    ordered = sorted(
        clusters,
        key=lambda c: (-c["weight"], -len(c["members"]), _rep_sort_key(c)),
    )
    leading = ordered[0]
    total_weight = sum(c["weight"] for c in clusters)

    # 3. Consensus block: value, type, interval (numeric only), confidence.
    if leading["numeric"]:
        values = [float(e["value"]) for e in leading["members"]]
        weights = [float(e["weight"]) for e in leading["members"]]
        mean = _weighted_mean(values, weights)
        value: Any = round(mean, _VALUE_PRECISION)
        stddev = _weighted_stddev(values, weights, mean)
        low = round(min(values) - stddev, _VALUE_PRECISION)
        high = round(max(values) + stddev, _VALUE_PRECISION)
        interval = {"low": min(low, value), "high": max(high, value), "units": ""}
        value_type = "numeric"
    else:
        value = leading["representative"]
        interval = None
        value_type = "categorical"

    if total_weight > 0:
        confidence = max(0.0, min(1.0, leading["weight"] / total_weight))
    else:
        confidence = 0.0

    consensus_block: dict[str, Any] = {
        "value": value,
        "value_type": value_type,
        "confidence": confidence,
    }
    if interval is not None:
        consensus_block["interval"] = interval

    # 4. Dissent: non-leading clusters at or above the floor by weight share.
    dissent: list[dict[str, Any]] = []
    for cluster in ordered[1:]:
        share = cluster["weight"] / total_weight if total_weight > 0 else 0.0
        if share < dissent_floor:
            continue
        dissent.append(
            {
                "position": cluster["representative"],
                "agents": [e["agent_id"] for e in cluster["members"]],
                "reasoning": "; ".join(e["reasoning"] for e in cluster["members"]),
                "weight_share": round(share, _SHARE_PRECISION),
            }
        )

    # 5. Packet assembly ("strengthened": no prior state exists in Round 2).
    packet: dict[str, Any] = {
        "campaign_id": campaign_id,
        "cohort": cohort,
        "task_id": task_id,
        "outcome_type": "strengthened",
        "consensus": consensus_block,
        "dissent": dissent,
        "contributing_agents": [
            {"agent_id": e["agent_id"], "weight": float(e["weight"])}
            for e in emissions
        ],
    }

    # Self-check against the protocol schema when the package is available.
    try:
        import harness_protocol
    except ImportError:  # pragma: no cover - protocol package optional at runtime
        pass
    else:
        errors = harness_protocol.iter_errors("consensus-packet", packet)
        if errors:
            raise ValueError(
                "aggregate() produced a schema-invalid consensus packet: "
                + "; ".join(errors)
            )
    return packet
