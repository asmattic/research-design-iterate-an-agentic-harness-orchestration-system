"""Example-fixture contract tests: every valid-* passes, every invalid-* fails."""

from __future__ import annotations

import json

import pytest

harness_protocol = pytest.importorskip("harness_protocol")

from protocol_testlib import collect_examples, example_id

VALID_EXAMPLES = collect_examples("valid")
INVALID_EXAMPLES = collect_examples("invalid")


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def test_examples_were_collected(examples_sanity):
    """Tripwire: parametrized tests vanish silently when collection is empty."""
    assert examples_sanity["valid"] or examples_sanity["invalid"]


@pytest.mark.parametrize(
    ("name", "path"),
    VALID_EXAMPLES,
    ids=[example_id(p) for p in VALID_EXAMPLES],
)
def test_valid_example_has_no_errors(name, path, examples_sanity):
    instance = _load(path)
    errors = harness_protocol.iter_errors(name, instance)
    assert errors == [], (
        f"{path.name} should validate against '{name}' but produced "
        f"{len(errors)} error(s): {errors}"
    )
    assert harness_protocol.is_valid(name, instance) is True


@pytest.mark.parametrize(
    ("name", "path"),
    INVALID_EXAMPLES,
    ids=[example_id(p) for p in INVALID_EXAMPLES],
)
def test_invalid_example_is_rejected(name, path, examples_sanity):
    instance = _load(path)
    assert harness_protocol.is_valid(name, instance) is False, (
        f"{path.name} is an invalid-* fixture but validated cleanly "
        f"against '{name}'"
    )
    assert harness_protocol.iter_errors(name, instance) != []


def test_load_schema_unknown_name_raises_keyerror():
    with pytest.raises(KeyError):
        harness_protocol.load_schema("nope")
