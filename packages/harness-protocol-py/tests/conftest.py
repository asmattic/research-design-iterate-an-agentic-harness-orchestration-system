"""Shared fixtures for the harness-protocol test suite.

These tests are written against the harness_protocol contract (v0.2.0). The
implementation may not exist yet when this file is collected, so every import
of harness_protocol is guarded: fixtures skip when the package is unavailable
rather than hard-erroring. Module-level collection helpers and contract
constants live in protocol_testlib.py (importable by name from test modules;
conftest is not a safe cross-module import target).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from protocol_testlib import _safe_assets_root, collect_examples, harness_protocol


@pytest.fixture(scope="session")
def assets_root():
    if harness_protocol is None:
        pytest.skip("harness_protocol is not importable")
    return Path(harness_protocol.assets_root())


@pytest.fixture(scope="session")
def schemas_dir(assets_root):
    return assets_root / "schemas"


@pytest.fixture(scope="session")
def examples_dir(assets_root):
    return assets_root / "examples"


@pytest.fixture(scope="session")
def examples_sanity():
    """Fail loudly if the package is importable but zero examples were found.

    Parametrized example tests silently vanish when collection yields nothing,
    so this fixture is the tripwire that makes an empty fixture set a hard
    failure instead of a quietly green suite.
    """
    if harness_protocol is None:
        pytest.skip("harness_protocol is not importable")
    valid = collect_examples("valid")
    invalid = collect_examples("invalid")
    if not valid and not invalid:
        pytest.fail(
            "No example fixtures were collected from "
            f"{_safe_assets_root()}/examples — expected valid-*.json and "
            "invalid-*.json files under per-schema subdirectories."
        )
    return {"valid": valid, "invalid": invalid}
