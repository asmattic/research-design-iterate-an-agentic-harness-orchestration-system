"""Validator / Verifier bridge (PRD §6.4.3).

Routes testable claims from an expert emission to the deterministic
verifier (``harness_verifier``) and attaches the results to a new packet in
the §9.6 shape. Every claim that *can* be tested gets tested; untestable
claims come back from the verifier as ``"abstain"`` results, and LLM
judgment is the lower-signal fallback only when no deterministic option
exists (§6.4.3). This module never decides anything itself — it only
routes claims out and attaches results back. Packets carry evidence
*references* (``evidence_ref``); the event log carries the full evidence.

Mitigates F3 (compounding error) and F5 (unverifiable stochastic claims).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from harness_verifier import VerifierResult, run_claims

__all__ = ["route_claims", "attach_results"]


def route_claims(emission: Mapping[str, Any]) -> list[VerifierResult]:
    """Route an emission's claims to the deterministic verifier.

    Reads ``emission["claims"]`` — each claim already carries its
    ``"verifier"`` key — and delegates the whole list to
    :func:`harness_verifier.run_claims`, returning its results in order.

    An empty or missing ``claims`` field yields ``[]`` without invoking the
    verifier. A ``claims`` field that is present but not a list raises
    :class:`ValueError`.
    """
    if "claims" not in emission:
        return []
    claims = emission["claims"]
    if not isinstance(claims, list):
        raise ValueError(
            f"emission 'claims' must be a list, got {type(claims).__name__}"
        )
    if not claims:
        return []
    return list(run_claims(claims))


def attach_results(
    emission: Mapping[str, Any], results: Sequence[VerifierResult]
) -> dict[str, Any]:
    """Return a new packet dict with ``verifier_results`` in the §9.6 shape.

    The input emission is never mutated. Any pre-existing
    ``verifier_results`` on the emission is replaced, not appended to.
    Each entry is ``{"verifier_id", "result", "evidence_ref"}`` —
    ``evidence_ref`` is a ``None`` placeholder for now: the event log
    carries the full evidence, packets carry only references to it.
    """
    packet: dict[str, Any] = dict(emission)
    packet["verifier_results"] = [
        {
            "verifier_id": result.verifier_id,
            "result": result.result,
            "evidence_ref": None,
        }
        for result in results
    ]
    return packet
