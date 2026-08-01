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

## Status: Phase 2A (stubs)

Every public callable raises `NotImplementedError` with a one-line behavior
summary. Dataclasses, type aliases, and constants are fully defined — they
are contracts, not behavior. The behavior contract lives in `tests/` as
strict-xfail tests, which get flipped green in Phase 2B when the
implementations land. Only `templates_dir()` is fully implemented (asset
resolution, not Phase 2B behavior).

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
