"""numeric_bound: low ≤ value ≤ high, bool is NOT numeric, abstain without bounds."""

from __future__ import annotations

import verifier_testlib as tl  # noqa: F401

from harness_verifier import get_verifier


def _verify(claim: dict):
    return get_verifier("numeric_bound").verify(claim)


def test_pass_within_both_bounds() -> None:
    result = _verify({"value": 5, "low": 1, "high": 10})
    assert result.verifier_id == "numeric_bound"
    assert result.result == "pass"


def test_pass_on_boundary_equality() -> None:
    assert _verify({"value": 1, "low": 1, "high": 10}).result == "pass"
    assert _verify({"value": 10, "low": 1, "high": 10}).result == "pass"


def test_pass_low_only_and_high_only() -> None:
    assert _verify({"value": 100, "low": 1}).result == "pass"
    assert _verify({"value": -100, "high": 1}).result == "pass"


def test_pass_with_floats() -> None:
    assert _verify({"value": 0.5, "low": 0.0, "high": 1.0}).result == "pass"


def test_fail_below_low_names_low() -> None:
    result = _verify({"value": 0, "low": 1, "high": 10})
    assert result.result == "fail"
    assert "low" in str(result.evidence)


def test_fail_above_high_names_high() -> None:
    result = _verify({"value": 11, "low": 1, "high": 10})
    assert result.result == "fail"
    assert "high" in str(result.evidence)


def test_abstain_when_no_bounds_provided() -> None:
    assert _verify({"value": 5}).result == "abstain"


def test_abstain_on_non_numeric_value() -> None:
    assert _verify({"value": "5", "low": 1}).result == "abstain"
    assert _verify({"value": None, "low": 1}).result == "abstain"
    assert _verify({"low": 1, "high": 2}).result == "abstain"  # value missing


def test_bool_is_not_numeric() -> None:
    # Python bool is an int subclass; the verifier must abstain, not compare.
    assert _verify({"value": True, "low": 0, "high": 2}).result == "abstain"
    assert _verify({"value": False, "low": -1}).result == "abstain"
