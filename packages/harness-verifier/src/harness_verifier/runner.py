"""The claim runner: dispatch each claim to its verifier, never raise."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from harness_verifier.results import VerifierResult
from harness_verifier.verifiers import VERIFIER_NAMES, get_verifier


def run_claims(claims: Sequence[Mapping[str, Any]]) -> list[VerifierResult]:
    """Verify each claim (dispatch on claim["verifier"]), in order.

    Total function: an unknown verifier name or a verifier that raises
    becomes an abstain result with error evidence — no exception ever
    escapes the runner.
    """
    results: list[VerifierResult] = []
    for claim in claims:
        name = claim.get("verifier")
        try:
            verifier = get_verifier(name)
        except (KeyError, TypeError):  # TypeError: unhashable "verifier" value
            results.append(
                VerifierResult(
                    str(name),
                    "abstain",
                    {
                        "error": f"unknown verifier {name!r}; "
                        f"known verifiers: {', '.join(VERIFIER_NAMES)}"
                    },
                )
            )
            continue
        try:
            results.append(verifier.verify(claim))
        except Exception as exc:  # noqa: BLE001 — the runner must be total
            results.append(VerifierResult(str(name), "abstain", {"error": repr(exc)}))
    return results
