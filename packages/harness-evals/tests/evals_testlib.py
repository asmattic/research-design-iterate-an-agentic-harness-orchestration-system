"""Shared helpers for the harness-evals test suite.

Deliberately NOT named conftest — module-level helpers live here so combined
pytest runs across suites never hit conftest name collisions.
"""

from __future__ import annotations

import json
from pathlib import Path

try:  # guarded: sibling lanes may not have landed the implementation yet
    import harness_evals  # noqa: F401
except ImportError:  # pragma: no cover
    harness_evals = None  # type: ignore[assignment]

try:
    import harness_protocol  # noqa: F401
except ImportError:  # pragma: no cover
    harness_protocol = None  # type: ignore[assignment]

TESTS_DIR = Path(__file__).resolve().parent
EVALS_PKG_DIR = TESTS_DIR.parent  # packages/harness-evals
REPO_ROOT = EVALS_PKG_DIR.parent.parent
EVALS_SRC = EVALS_PKG_DIR / "src"
PROTOCOL_SRC = REPO_ROOT / "packages" / "harness-protocol-py" / "src"

CANONICAL_BENCHMARK_NAMES = (
    "adversarial-safety",
    "protocol-conformance",
    "rental-synthetic",
    "smoke",
)


def canonical_benchmarks_dir() -> Path:
    return EVALS_PKG_DIR / "benchmarks"


def canonical_fixture_path() -> Path:
    return EVALS_PKG_DIR / "fixtures" / "recorded-campaign.jsonl"


def load_fixture_lines() -> list[str]:
    """Raw non-empty lines of the canonical recorded campaign; [] if absent."""
    path = canonical_fixture_path()
    if not path.is_file():
        return []
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def load_fixture_events() -> list[dict]:
    """Parsed events from the canonical recorded campaign; [] if absent."""
    return [json.loads(line) for line in load_fixture_lines()]


def make_event(
    campaign_id: str = "camp-stub",
    event_id: str = "evt-1",
    kind: str = "emission",
    payload: dict | None = None,
    cost: dict | None = None,
) -> dict:
    """A minimal event valid against harness_protocol's event-envelope schema."""
    event = {
        "event_id": event_id,
        "campaign_id": campaign_id,
        "t": "2026-08-01T00:00:00Z",
        "emitter": {"kind": "agent", "id": "agent-1"},
        "kind": kind,
        "payload": payload or {},
    }
    if cost is not None:
        event["cost"] = cost
    return event


def run_cli(argv: list[str], capsys=None) -> tuple[int, str]:
    """Invoke harness_evals.cli.main in-process; return (exit_code, stdout)."""
    from harness_evals import cli

    code = cli.main(list(argv))
    out = capsys.readouterr().out if capsys is not None else ""
    return code, out
