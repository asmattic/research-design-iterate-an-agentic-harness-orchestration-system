# harness-reference

Reference scaffolding for the harness orchestration protocol: campaign
**templates** (under `templates/`, bundled into the wheel as
`harness_reference/_templates`) and five executable **modules**:

| Module | Entry point | PRD |
| --- | --- | --- |
| `event_log` | `EventLog`, `validate_envelope` | §15.3 / §10 |
| `memory_index` | `MemoryIndex` | §10 / §15.6 |
| `drift_check` | `drift_check`, `DriftResult` | §11 |
| `consensus` | `aggregate` | §9.2 |
| `retrospective` | `retrospective`, `Proposal` | §13.2 |

## Status: Phase 2B (implemented)

All five modules are implemented:

- `event_log` — JSONL append-only event log with schema validation on write.
- `memory_index` — directory-backed memory store with supersedes resolution.
- `drift_check` — lexical Jaccard composite drift score against INTENT.
- `consensus` — deterministic weighted clustering with a dissent floor.
- `retrospective` — deterministic rules over the event stream: verifier
  failures become per-agent weight-adjustment proposals; drift pause/halt
  excursions become campaign memory-entry proposals.

The strict-xfail markers have been removed from `tests/`; the test suite is
now the acceptance suite and runs green. Deferred to later phases: the
LLM-as-judge retrospective layer (prompt diffs, rubric scoring — arrives
with harness-os), vector-based drift signals (Round 3), and template worked
examples.

Per ROUND-2-PLAN §3.2, each module stays at or under 500 lines through
Phase 2B.

## Install

```sh
pip install -e "packages/harness-protocol-py" -e "packages/harness-reference[test]"
```

## Template resolution

`harness_reference.templates_dir()` resolves in order:

1. `HARNESS_REFERENCE_TEMPLATES` environment variable, if set
2. bundled package data (`harness_reference/_templates`, present in wheels)
3. repo-checkout fallback (`packages/harness-reference/templates/`)

and raises `RuntimeError` naming every attempted location if none exists.
