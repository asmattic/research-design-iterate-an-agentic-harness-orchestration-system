"""schema_validator: pass on valid instance, fail with errors, abstain on unknown schema."""

from __future__ import annotations

import verifier_testlib as tl  # noqa: F401

from harness_verifier import get_verifier


def _verify(claim: dict):
    return get_verifier("schema_validator").verify(claim)


def test_pass_on_valid_instance(valid_envelope: dict) -> None:
    result = _verify({"schema": "event-envelope", "instance": valid_envelope})
    assert result.verifier_id == "schema_validator"
    assert result.result == "pass"


def test_fail_on_invalid_instance() -> None:
    result = _verify({"schema": "event-envelope", "instance": {}})
    assert result.result == "fail"
    errors = result.evidence["errors"]
    assert isinstance(errors, list)
    assert errors  # at least one human-readable error


def test_abstain_on_unknown_schema_name() -> None:
    result = _verify({"schema": "no-such-schema", "instance": {}})
    assert result.result == "abstain"


def test_abstain_on_missing_schema_key() -> None:
    result = _verify({"instance": {}})
    assert result.result == "abstain"
