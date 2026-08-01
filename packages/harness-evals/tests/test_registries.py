"""Scorer and benchmark registries per the harness_evals 0.2.0 contract."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

import evals_testlib as tl

he = pytest.importorskip("harness_evals")

EXPECTED_SCORERS = ("dummy", "calibration", "drift", "completion", "cost", "safety")
STUB_SCORERS = EXPECTED_SCORERS[1:]


def test_version():
    assert he.__version__ == "0.2.0"


def test_scorer_names_exact():
    assert he.SCORER_NAMES == EXPECTED_SCORERS


def test_get_scorer_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        he.get_scorer("no-such-scorer")


def test_dummy_scorer_on_synthetic_events():
    events = [tl.make_event(event_id=f"evt-{i}") for i in range(3)]
    scorer = he.get_scorer("dummy")
    assert scorer.name == "dummy"
    result = scorer.score(events)
    assert result.value == 1.0
    assert result.details["event_count"] == 3
    assert result.scorer == "dummy"


def test_dummy_scorer_on_fixture_events(fixture_events):
    if not fixture_events:
        pytest.skip("canonical recorded-campaign.jsonl not yet present")
    result = he.get_scorer("dummy").score(fixture_events)
    assert result.value == 1.0
    assert result.details["event_count"] == len(fixture_events)


@pytest.mark.parametrize("name", STUB_SCORERS)
def test_stub_scorers_raise_phase_2d(name):
    scorer = he.get_scorer(name)
    assert scorer.name == name
    with pytest.raises(NotImplementedError, match=r"^Phase 2D"):
        scorer.score([])


def test_benchmark_dataclass_is_frozen():
    bench = he.Benchmark(
        name="frozen-check",
        description="frozen dataclass check",
        scorer_names=("dummy",),
        status="available",
        manifest_path=Path("frozen-check.json"),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        bench.name = "mutated"  # type: ignore[misc]


def test_list_benchmarks_sorted_and_canonical(monkeypatch):
    monkeypatch.delenv("HARNESS_EVALS_ASSETS", raising=False)
    if not tl.canonical_benchmarks_dir().is_dir():
        pytest.skip("canonical benchmark manifests not yet present")
    benchmarks = he.list_benchmarks()
    names = [b.name for b in benchmarks]
    assert names == sorted(names)
    for expected in tl.CANONICAL_BENCHMARK_NAMES:
        assert expected in names
    smoke = he.get_benchmark("smoke")
    assert smoke.status == "available"
    assert smoke.scorer_names == ("dummy",)


def test_get_benchmark_keyerror_lists_known_names(stub_assets):
    with pytest.raises(KeyError) as excinfo:
        he.get_benchmark("no-such-benchmark")
    assert "smoke" in str(excinfo.value)


def test_manifest_with_unknown_scorer_raises_valueerror(stub_assets):
    bad = {
        "name": "bad-scorer",
        "description": "manifest naming a scorer that does not exist",
        "scorers": ["not-a-scorer"],
        "status": "available",
    }
    (stub_assets / "benchmarks" / "bad-scorer.json").write_text(
        json.dumps(bad), encoding="utf-8"
    )
    with pytest.raises(ValueError):
        he.list_benchmarks()
