"""Fixtures only — shared module-level helpers live in evals_testlib.py."""

from __future__ import annotations

import json

import pytest

import evals_testlib as tl


@pytest.fixture
def fixture_events() -> list[dict]:
    """Events parsed from the canonical recorded campaign ([] while absent)."""
    return tl.load_fixture_events()


@pytest.fixture
def tmp_out(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    return out


@pytest.fixture
def stub_assets(tmp_path, monkeypatch):
    """Minimal assets tree + HARNESS_EVALS_ASSETS override, hermetic to lanes."""
    root = tmp_path / "assets"
    (root / "benchmarks").mkdir(parents=True)
    (root / "fixtures").mkdir()
    manifest = {
        "name": "smoke",
        "description": "Stub smoke benchmark for hermetic CLI tests",
        "scorers": ["dummy", "calibration", "drift", "completion", "cost", "safety"],
        "status": "available",
    }
    (root / "benchmarks" / "smoke.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    # No benchmarks/data/smoke/ dir on purpose: the live runner must fall back
    # to this single fixture as the one scenario.
    events = [
        tl.make_event(event_id=f"evt-{i}", cost={"tokens_in": 10, "tokens_out": 5})
        for i in range(2)
    ]
    events.append(
        tl.make_event(
            event_id="evt-claim", kind="ticket_claimed",
            payload={"ticket_ref": "tkt-1"},
        )
    )
    events.append(
        tl.make_event(
            event_id="evt-resolve", kind="ticket_resolved",
            payload={"ticket_ref": "tkt-1"},
        )
    )
    (root / "fixtures" / "recorded-campaign.jsonl").write_text(
        "\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8"
    )
    monkeypatch.setenv("HARNESS_EVALS_ASSETS", str(root))
    return root
