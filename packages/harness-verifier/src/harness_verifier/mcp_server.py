"""MCP wrapper: one tool per verifier plus a run_claims batch tool.

Thin by design — every tool delegates to the core verifiers. Requires the
optional ``mcp`` extra; the citation tool here opts into live fetching via
``default_fetcher`` (the library/CLI default stays offline).
"""

from __future__ import annotations

import dataclasses
from typing import Any

# The SDK moved/renamed its high-level server class between major versions:
# mcp 1.x ships mcp.server.fastmcp.FastMCP, mcp >= 2.0 ships
# mcp.server.mcpserver.MCPServer (same tool()/run()/list_tools() surface).
try:
    from mcp.server.mcpserver import MCPServer as _ServerClass  # mcp >= 2.0
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as _ServerClass  # mcp 1.x
    except ImportError as exc:  # pragma: no cover — exercised only without the SDK
        raise ImportError(
            "the MCP server requires the optional 'mcp' extra; "
            'install it with: pip install "harness-verifier[mcp]"'
        ) from exc

from harness_verifier.runner import run_claims as _run_claims
from harness_verifier.verifiers import CitationResolver, default_fetcher, get_verifier

server = _ServerClass("harness-verifier")

_live_citation_resolver = CitationResolver(fetcher=default_fetcher)


def _as_dict(result: Any) -> dict[str, Any]:
    return dataclasses.asdict(result)


@server.tool()
def code_test_runner(pytest_target: str, timeout_s: int = 60) -> dict[str, Any]:
    """Run pytest on a target path; pass iff it exits 0."""
    claim = {"pytest_target": pytest_target, "timeout_s": timeout_s}
    return _as_dict(get_verifier("code_test_runner").verify(claim))


@server.tool()
def schema_validator(schema: str, instance: Any) -> dict[str, Any]:
    """Validate an instance against a named harness-protocol JSON Schema."""
    return _as_dict(
        get_verifier("schema_validator").verify(
            {"schema": schema, "instance": instance}
        )
    )


@server.tool()
def citation_resolver(url: str) -> dict[str, Any]:
    """Check that a citation URL is well-formed and resolves (live HEAD)."""
    return _as_dict(_live_citation_resolver.verify({"url": url}))


@server.tool()
def numeric_bound(
    value: Any, low: float | None = None, high: float | None = None
) -> dict[str, Any]:
    """Check low <= value <= high for whichever bounds are provided."""
    claim: dict[str, Any] = {"value": value}
    if low is not None:
        claim["low"] = low
    if high is not None:
        claim["high"] = high
    return _as_dict(get_verifier("numeric_bound").verify(claim))


@server.tool()
def type_check(value: Any, expected_type: str) -> dict[str, Any]:
    """Check a value's runtime type against a JSON-ish type name."""
    return _as_dict(
        get_verifier("type_check").verify(
            {"value": value, "expected_type": expected_type}
        )
    )


@server.tool()
def run_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Verify a batch of claims; each carries "verifier" plus its params."""
    return [_as_dict(result) for result in _run_claims(claims)]


def main() -> None:
    """Console entry point: serve over stdio."""
    server.run()


if __name__ == "__main__":
    main()
