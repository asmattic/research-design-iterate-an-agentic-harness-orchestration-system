"""run_claims: dispatch by claim["verifier"], never raise, abstain on the unknown."""

from __future__ import annotations

import verifier_testlib as tl  # noqa: F401

import harness_verifier
from harness_verifier import VerifierResult, run_claims


def test_dispatches_in_order() -> None:
    results = run_claims(
        [
            {"verifier": "type_check", "value": 3, "expected_type": "int"},
            {"verifier": "numeric_bound", "value": 5, "low": 1, "high": 10},
            {"verifier": "type_check", "value": 3, "expected_type": "str"},
        ]
    )
    assert [r.result for r in results] == ["pass", "pass", "fail"]
    assert [r.verifier_id for r in results] == [
        "type_check",
        "numeric_bound",
        "type_check",
    ]
    assert all(isinstance(r, VerifierResult) for r in results)


def test_unknown_verifier_name_abstains_with_error_evidence() -> None:
    [result] = run_claims([{"verifier": "hallucinated_verifier"}])
    assert result.result == "abstain"
    assert "error" in result.evidence


def test_missing_verifier_key_abstains() -> None:
    [result] = run_claims([{"value": 3}])
    assert result.result == "abstain"
    assert "error" in result.evidence


class _ExplodingVerifier:
    name = "boom"

    def verify(self, claim):
        raise RuntimeError("kaboom")


def test_exploding_verifier_becomes_abstain_never_raises(monkeypatch) -> None:
    import harness_verifier.verifiers as vmod

    monkeypatch.setitem(vmod._REGISTRY, "boom", _ExplodingVerifier())
    [result] = run_claims([{"verifier": "boom"}])
    assert result.result == "abstain"
    assert result.evidence["error"] == repr(RuntimeError("kaboom"))


def test_offline_citation_claim_abstains_through_runner() -> None:
    [result] = run_claims(
        [{"verifier": "citation_resolver", "url": "https://example.com/"}]
    )
    assert result.result == "abstain"
    assert result.evidence == {"reason": "offline"}


def test_empty_claims_list() -> None:
    assert harness_verifier.run_claims([]) == []
