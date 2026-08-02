"""type_check: expected_type matching with the bool-is-int footgun handled."""

from __future__ import annotations

import pytest

import verifier_testlib as tl  # noqa: F401

from harness_verifier import get_verifier


def _verify(claim: dict):
    return get_verifier("type_check").verify(claim)


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [
        (3, "int"),
        (3.5, "float"),
        (3, "number"),
        (3.5, "number"),
        ("hi", "str"),
        (True, "bool"),
        (False, "bool"),
        ([1, 2], "list"),
        ({"a": 1}, "dict"),
        (None, "null"),
    ],
)
def test_pass_cases(value, expected_type) -> None:
    result = _verify({"value": value, "expected_type": expected_type})
    assert result.verifier_id == "type_check"
    assert result.result == "pass"


def test_fail_with_actual_type_evidence() -> None:
    result = _verify({"value": 3, "expected_type": "str"})
    assert result.result == "fail"
    assert result.evidence["actual_type"] == "int"


@pytest.mark.parametrize("expected_type", ["int", "float", "number"])
def test_bool_never_passes_as_numeric(expected_type: str) -> None:
    result = _verify({"value": True, "expected_type": expected_type})
    assert result.result == "fail"
    assert result.evidence["actual_type"] == "bool"


def test_int_is_not_bool() -> None:
    result = _verify({"value": 1, "expected_type": "bool"})
    assert result.result == "fail"
    assert result.evidence["actual_type"] == "int"


def test_int_does_not_pass_as_float() -> None:
    result = _verify({"value": 3, "expected_type": "float"})
    assert result.result == "fail"
    assert result.evidence["actual_type"] == "int"


def test_none_actual_type_is_null() -> None:
    result = _verify({"value": None, "expected_type": "str"})
    assert result.result == "fail"
    assert result.evidence["actual_type"] == "null"


def test_abstain_on_unknown_expected_type() -> None:
    assert _verify({"value": 3, "expected_type": "tuple"}).result == "abstain"


def test_abstain_on_missing_expected_type() -> None:
    assert _verify({"value": 3}).result == "abstain"
