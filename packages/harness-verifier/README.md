# harness-verifier

Deterministic verifier layer for the agentic harness (PRD §6.7, §15; ROUND-2-PLAN §3.4):
a claim runner, five built-in verifiers, a CLI, and an optional MCP wrapper.

## Precedence (§6.7)

When a deterministic verifier says **pass** or **fail**, that verdict wins —
**always** — over any LLM opinion. When it **abstains**, the claim was not
testable here (offline, unknown schema, wrong types, missing target); abstain
is not a verdict and never fails a run.

## The five verifiers

| Verifier | Claim shape | pass | fail | abstain |
|---|---|---|---|---|
| `code_test_runner` | `{"verifier": "code_test_runner", "pytest_target": "<path>", "timeout_s": 60}` | pytest exits 0 | nonzero exit (`{"exit_code", "tail"}`) or timeout (`{"timeout": true}`) | target path does not exist |
| `schema_validator` | `{"verifier": "schema_validator", "schema": "<harness_protocol.SCHEMA_NAMES>", "instance": <obj>}` | no schema errors | `{"errors": [...]}` | unknown schema name |
| `citation_resolver` | `{"verifier": "citation_resolver", "url": "<http(s)://...>"}` | fetcher status < 400 | malformed URL, or status >= 400 (`{"status": ...}`) | well-formed URL but no fetcher: `{"reason": "offline"}` |
| `numeric_bound` | `{"verifier": "numeric_bound", "value": <num>, "low": <num>?, "high": <num>?}` | low <= value <= high for the provided bounds | `{"violated_bound": "low"\|"high", ...}` | value not numeric (bool is NOT numeric), or no bounds given |
| `type_check` | `{"verifier": "type_check", "value": <any>, "expected_type": "int"\|"float"\|"number"\|"str"\|"bool"\|"list"\|"dict"\|"null"}` | type matches (`"number"` = int or float; bool never passes as int/number) | `{"actual_type": ...}` | unknown `expected_type` |

Every verifier returns a frozen `VerifierResult(verifier_id, result, evidence)`
with `result` in `{"pass", "fail", "abstain"}`. `run_claims(claims)` dispatches
each claim on its `"verifier"` key and is total: unknown names and raising
verifiers become abstains with error evidence — it never raises.

The default `citation_resolver` registry instance has `fetcher=None`, so the
library, CLI, tests, and CI never touch the network. Opt into live checking
with `CitationResolver(fetcher=default_fetcher)` (urllib HEAD, 5 s timeout).

## CLI

```
harness-verify list
harness-verify run --claims claims.json    # claims.json = JSON array of claims
python -m harness_verifier.cli list        # same entry point
```

`run` prints one JSON result object per line to stdout and a summary line to
stderr. Exit codes: `0` no fails (abstains don't fail the run), `1` at least
one fail, `2` usage error or unreadable/invalid claims file.

## MCP server (optional extra)

```
pip install "harness-verifier[mcp]"
harness-verify-mcp                          # FastMCP server over stdio
```

Exposes one tool per verifier plus a `run_claims` batch tool (6 tools total).
Without the extra installed, `import harness_verifier.mcp_server` raises an
ImportError pointing at the install line above. The MCP citation tool opts
into `default_fetcher` (live HEAD requests); everything else stays offline.
