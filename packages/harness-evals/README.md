# harness-evals

The eval harness (ROUND-2-PLAN §3.5, Phase 2D; PRD `prd/14-evaluation.md`):
CLI, benchmark and scorer registries, asset resolution, the five real scorers,
the §14.8 report writer, and the §14.6 regression gate. Live benchmark
execution is on.

## CLI

```
harness eval list
harness eval run --benchmark <name> --config <path> --output <dir> [--dry-run]
```

**Live run** (no `--dry-run`): the benchmark must have status `available`
(else exit 1 naming the status). Scenarios are the sorted files
`benchmarks/data/<name>/scenario-*.jsonl` under the assets root; when that
directory is absent the single canonical fixture
`fixtures/recorded-campaign.jsonl` is used as one scenario (this keeps
`smoke` runnable live). Each benchmark scorer scores every scenario;
aggregation is MEAN of values per scorer, except `cost`, which is SUM (a raw
token count). The run always writes `<output>/report.md` and prints the
report path plus one line per scorer. When the config carries a `baseline`,
the process exits via the regression gate; otherwise exit 0.

**Dry run** (`--dry-run`): prints the execution plan and creates nothing.

## Config schema

JSON object, all keys optional (malformed JSON exits 1):

```json
{
  "baseline":   {"<scorer>": <value>},
  "thresholds": {"<scorer>": <value>}
}
```

A starter config with sane thresholds and no baseline ships at
`configs/rental-default.json` (0.05 for the [0, 1] scorers, 5000 for cost).

## Scorers

All scorers consume event-envelope-shaped event streams and tolerate missing
keys. Aggregation across scenarios happens in the runner, not the scorers.

| Scorer | Semantics | Direction |
| --- | --- | --- |
| `dummy` | Pipeline check: always 1.0, reports event count and kinds. | — |
| `calibration` | 1 − Brier over (emission confidence, verifier outcome) pairs; details carry Brier, 10-bucket ECE, and pair count (§14.5). | higher is better |
| `drift` | 1 − max §11 composite over `drift_check` events; counts pause/halt excursions. | higher is better |
| `completion` | Fraction of claimed tickets (`ticket_claimed`) that were resolved (`ticket_resolved`). | higher is better |
| `cost` | Total tokens from event `cost` blocks (`tokens`, else `tokens_in + tokens_out`); details add USD and wall-clock totals. | **lower is better** |
| `safety` | Fraction of `guardrail_event` events with `blocked: true`, plus category breakdown. | higher is better |

## Regression gate

`regression.regression_gate(current, baseline, thresholds) -> int` compares
every scorer present in both mappings; missing thresholds default to 0.0.
Higher-is-better scorers regress when `current < baseline - threshold`;
`cost` (see `LOWER_IS_BETTER`) regresses when
`current > baseline + threshold`. Returns 0 iff no regressions, else 1 —
usable directly as a process exit code / CI gate.

## Reporting

`report.write_report(campaign_id, results, output_dir)` renders the §14.8
`report.md` with these H2 sections, in order: Completion, Intent-alignment,
Drift, Calibration, Cost, Safety, Human gates, Retrospective notes. A section
with a matching scorer result renders its value and details; the rest render
"not scored this run". Intent-alignment, Human gates, and Retrospective notes
have no Round 2 scorer — they arrive with the adapter's live campaigns.

## Assets

Benchmark manifests live in `benchmarks/*.json` and fixtures in `fixtures/`
next to this README (bundled into the wheel as `harness_evals/_assets/`).
Resolution order: `$HARNESS_EVALS_ASSETS`, bundled package data, then the repo
checkout. Manifest shape:
`{"name": str, "description": str, "scorers": [str, ...], "status": "planned" | "available"}`.

Adversarial and rental scenario data ships in `benchmarks/data/<benchmark>/`
(landed by the benchmark-data lane); until a benchmark has a data directory,
live runs fall back to the recorded-campaign fixture.
