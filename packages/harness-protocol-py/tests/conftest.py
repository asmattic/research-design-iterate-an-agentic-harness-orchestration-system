"""Shared fixtures and collection helpers for the harness-protocol test suite.

These tests are written against the harness_protocol contract (v0.2.0). The
implementation may not exist yet when this file is collected, so every import
of harness_protocol is guarded: collection helpers return empty lists and
fixtures skip when the package is unavailable, rather than hard-erroring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

try:  # pragma: no cover - trivial import guard
    import harness_protocol
except Exception:  # ImportError or anything raised at package import time
    harness_protocol = None  # type: ignore[assignment]

# Contract constants (source of truth: harness-protocol CONTRACT v0.2.0).
EXPECTED_VERSION = "0.2.0"
EXPECTED_SCHEMA_NAMES = (
    "agent-contract",
    "event-envelope",
    "consensus-packet",
    "orchestrator-state",
    "memory-index",
)
SCHEMA_ID_TEMPLATE = "https://harness.example/schemas/v0.2/{name}.schema.json"


def _safe_assets_root():
    """Return harness_protocol.assets_root() or None if unavailable."""
    if harness_protocol is None:
        return None
    try:
        return Path(harness_protocol.assets_root())
    except Exception:
        return None


def collect_examples(kind):
    """Enumerate (schema_name, path) pairs for ``valid`` or ``invalid`` examples.

    Module-level (usable at parametrize/collection time). Returns [] when the
    package or the examples directory is missing so collection never errors.
    """
    root = _safe_assets_root()
    if root is None:
        return []
    examples = root / "examples"
    if not examples.is_dir():
        return []
    pairs = []
    for schema_dir in sorted(p for p in examples.iterdir() if p.is_dir()):
        for path in sorted(schema_dir.glob(f"{kind}-*.json")):
            pairs.append((schema_dir.name, path))
    return pairs


def example_id(pair):
    """Readable pytest id naming the fixture file: '<schema>/<file>'."""
    name, path = pair
    return f"{name}/{path.name}"


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
