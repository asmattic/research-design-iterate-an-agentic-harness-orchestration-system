# harness-evals

Phase 2A **skeleton** of the eval harness (ROUND-2-PLAN §3.5): the CLI parser,
the benchmark and scorer registries, asset resolution, and one working dummy
scorer. The real scorers, report writer, regression gate, and live benchmark
execution land in Phase 2D.

## CLI

```
harness eval list
harness eval run --benchmark <name> --config <path> --output <dir> --dry-run
```

**Dry-run only.** Live benchmark execution is gated until Phase 2D as a cost
risk mitigation (ROUND-2-PLAN §8): without `--dry-run`, `harness eval run`
prints a refusal and exits 1. With `--dry-run` it prints the execution plan and
creates nothing.

## Scorers

| Scorer | Status |
| --- | --- |
| `dummy` | real — always 1.0, reports event count and kinds |
| `calibration` | Phase 2D stub (Brier + ECE, §14.5) |
| `drift` | Phase 2D stub (§11 composite signal) |
| `completion` | Phase 2D stub (criteria breakdown) |
| `cost` | Phase 2D stub (tokens, wall-clock, USD) |
| `safety` | Phase 2D stub (adversarial pass rate) |

## Assets

Benchmark manifests live in `benchmarks/*.json` and fixtures in `fixtures/`
next to this README (bundled into the wheel as `harness_evals/_assets/`).
Resolution order: `$HARNESS_EVALS_ASSETS`, bundled package data, then the repo
checkout. Manifest shape:
`{"name": str, "description": str, "scorers": [str, ...], "status": "planned" | "available"}`.

## Reporting

`report.py` will render the per-campaign `report.md` in the format defined by
`prd/14-evaluation.md` §14.8 (Completion, Intent-alignment, Drift, Calibration,
Cost, Safety, Human gates, Retrospective notes).
