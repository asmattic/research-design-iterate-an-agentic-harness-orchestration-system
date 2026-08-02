"""Live benchmark runner: scenario discovery, scoring, and aggregation.

Scenarios for benchmark ``<name>`` are the sorted files
``assets_root()/benchmarks/data/<name>/scenario-*.jsonl``. When that
directory is absent, the single canonical fixture
``assets_root()/fixtures/recorded-campaign.jsonl`` is used as one scenario
(this keeps the ``smoke`` benchmark runnable live before per-benchmark data
lands). Aggregation across scenarios is MEAN of per-scenario values for every
scorer except ``cost``, which is SUM (a raw token count, lower is better).
"""

from __future__ import annotations

import json
import pathlib
from typing import Any, Mapping

from ._assets import assets_root
from .benchmarks import Benchmark
from .scorers import ScoreResult, get_scorer


def discover_scenarios(benchmark_name: str) -> list[pathlib.Path]:
    """Scenario JSONL files for *benchmark_name* (fixture fallback; may be [])."""
    root = assets_root()
    data_dir = root / "benchmarks" / "data" / benchmark_name
    if data_dir.is_dir():
        return sorted(data_dir.glob("scenario-*.jsonl"))
    fallback = root / "fixtures" / "recorded-campaign.jsonl"
    if fallback.is_file():
        return [fallback]
    return []


def load_events(path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse one scenario's JSONL lines; ValueError names the bad line."""
    events: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSONL in {path} line {lineno}: {exc}") from exc
    return events


def load_config(path: pathlib.Path) -> dict[str, Any]:
    """Parse the JSON run config ({} keys all optional); ValueError if malformed.

    Schema: ``{"baseline": {scorer: value}, "thresholds": {scorer: value}}``.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"malformed config JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"config at {path} must be a JSON object")
    return data


def aggregate(scorer_name: str, per_scenario: list[ScoreResult]) -> ScoreResult:
    """Fold per-scenario results into one: MEAN of values (cost: SUM)."""
    n = len(per_scenario)
    if n == 1:
        only = per_scenario[0]
        return ScoreResult(
            scorer=scorer_name,
            value=only.value,
            details={**only.details, "scenarios": 1},
        )
    values = [r.value for r in per_scenario]
    if scorer_name == "cost":
        details: dict[str, Any] = {
            key: sum(r.details.get(key, 0) for r in per_scenario)
            for key in ("tokens", "usd", "wall_clock_ms")
        }
        details["scenarios"] = n
        return ScoreResult(scorer=scorer_name, value=sum(values), details=details)
    return ScoreResult(
        scorer=scorer_name,
        value=sum(values) / n,
        details={"scenarios": n, "scenario_values": values},
    )


def run_benchmark(
    benchmark: Benchmark, scenarios: list[pathlib.Path]
) -> list[ScoreResult]:
    """Score every scenario with every benchmark scorer; return aggregates."""
    events_per_scenario = [load_events(path) for path in scenarios]
    results: list[ScoreResult] = []
    for name in benchmark.scorer_names:
        scorer = get_scorer(name)
        per_scenario = [scorer.score(events) for events in events_per_scenario]
        results.append(aggregate(name, per_scenario))
    return results


def current_scores(results: list[ScoreResult]) -> Mapping[str, float]:
    """{scorer: aggregated value} for the regression gate."""
    return {result.scorer: result.value for result in results}
