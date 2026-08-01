"""Module-level helpers and contract constants for the harness-protocol tests.

Lives in a uniquely-named module (not conftest.py) so it can be imported by
test modules even when several test suites run in one pytest invocation —
`conftest` is not a safe import target because every suite's conftest.py
competes for the same module name in sys.modules.
"""

from __future__ import annotations

from pathlib import Path

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
