# harness-protocol (Python)

Python bindings for the harness-agnostic orchestration protocol: schema
loading, instance validation, and a conformance runner. Protocol version
**0.2.0** (dist name `harness-protocol`, import name `harness_protocol`).

## Install

```bash
pip install -e "packages/harness-protocol-py[test]"
```

## Conformance

```bash
python -m harness_protocol.conform            # uses bundled/repo assets
python -m harness_protocol.conform --assets packages/harness-protocol
```

Checks every schema for meta-validity and versioned `$id`, expects every
`examples/<name>/valid-*.json` to pass and every `invalid-*.json` to fail,
and exits 0 only when all checks pass.

## Canonical assets

Canonical schemas live in `packages/harness-protocol/schemas/` (see PRD
Appendix D and §15); examples live in `packages/harness-protocol/examples/`.
Resolution order: `HARNESS_PROTOCOL_ASSETS` env var, bundled wheel data
(`harness_protocol/_assets`), then the repo-checkout sibling directory.

## Versioning (PRD D.6, in two lines)

Schema `$id`s embed the minor version path (`.../schemas/v0.2/...`); additive
changes bump minor, breaking changes bump major and get a new version path.
Package `__version__` and `PROTOCOL_VERSION` track the protocol version 0.2.0.
