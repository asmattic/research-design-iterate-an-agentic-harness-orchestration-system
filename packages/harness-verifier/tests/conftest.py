"""Fixtures only — shared module-level helpers live in verifier_testlib.py."""

from __future__ import annotations

import pytest

import verifier_testlib as tl


@pytest.fixture
def valid_envelope() -> dict:
    """A protocol instance known to validate against event-envelope."""
    return tl.load_valid_envelope()
