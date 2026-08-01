"""Shared fixtures for the harness-reference suite (Phase 2A pins + Phase 2B contract)."""

from __future__ import annotations

import json
import pathlib

import pytest

TEMPLATE_NAMES = (
    "INTENT.md",
    "ORCHESTRATOR.md",
    "AGENTS.md",
    "COHORT.md",
    "SWARM.md",
    "CONSTITUTION.md",
    "HANDOFF.md",
)


def _protocol_example(schema: str, filename: str) -> dict:
    """Load a canonical harness-protocol example fixture as a dict."""
    harness_protocol = pytest.importorskip(
        "harness_protocol", reason="harness-protocol not installed"
    )
    path = harness_protocol.assets_root() / "examples" / schema / filename
    if not path.is_file():
        pytest.skip(f"canonical protocol fixture missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def templates() -> pathlib.Path:
    """The resolved templates directory; skips while the template lane is unlanded."""
    harness_reference = pytest.importorskip(
        "harness_reference", reason="harness-reference stub lane not landed"
    )
    if not hasattr(harness_reference, "templates_dir"):
        pytest.skip("harness_reference.templates_dir not landed yet")
    try:
        return harness_reference.templates_dir()
    except RuntimeError as exc:
        pytest.skip(f"templates not resolvable yet: {exc}")


@pytest.fixture
def valid_event() -> dict:
    """A schema-valid event-envelope instance from the canonical protocol examples."""
    return _protocol_example("event-envelope", "valid-agent-emission.json")


@pytest.fixture
def valid_memory_entry() -> dict:
    """A schema-valid memory-index entry from the canonical protocol examples."""
    return _protocol_example("memory-index", "valid-tampa-zoning.json")


@pytest.fixture
def tmp_log_path(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "events.jsonl"
