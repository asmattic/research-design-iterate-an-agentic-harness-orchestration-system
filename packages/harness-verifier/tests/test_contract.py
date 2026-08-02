"""Public API contract: VerifierResult, VERIFIER_NAMES, get_verifier."""

from __future__ import annotations

import dataclasses

import pytest

import verifier_testlib as tl  # noqa: F401  (sys.path setup)

import harness_verifier


def test_version() -> None:
    assert harness_verifier.__version__ == "0.2.0"


def test_verifier_names_exact_tuple() -> None:
    assert harness_verifier.VERIFIER_NAMES == tl.EXPECTED_VERIFIER_NAMES
    assert isinstance(harness_verifier.VERIFIER_NAMES, tuple)


def test_verifier_result_is_frozen_dataclass() -> None:
    result = harness_verifier.VerifierResult(
        verifier_id="type_check", result="pass", evidence={"actual_type": "int"}
    )
    assert dataclasses.is_dataclass(result)
    assert result.verifier_id == "type_check"
    assert result.result == "pass"
    assert result.evidence == {"actual_type": "int"}
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.result = "fail"  # type: ignore[misc]


def test_verifier_result_field_names_and_order() -> None:
    fields = [f.name for f in dataclasses.fields(harness_verifier.VerifierResult)]
    assert fields == ["verifier_id", "result", "evidence"]


@pytest.mark.parametrize("name", tl.EXPECTED_VERIFIER_NAMES)
def test_get_verifier_returns_named_verifier(name: str) -> None:
    verifier = harness_verifier.get_verifier(name)
    assert verifier.name == name
    assert callable(verifier.verify)


def test_get_verifier_unknown_raises_keyerror_listing_names() -> None:
    with pytest.raises(KeyError) as excinfo:
        harness_verifier.get_verifier("nope")
    message = str(excinfo.value)
    for name in tl.EXPECTED_VERIFIER_NAMES:
        assert name in message


def test_run_claims_exported() -> None:
    assert callable(harness_verifier.run_claims)
    assert harness_verifier.run_claims([]) == []
