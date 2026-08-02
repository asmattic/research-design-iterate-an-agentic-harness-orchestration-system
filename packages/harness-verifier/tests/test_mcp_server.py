"""MCP wrapper: optional extra — helpful ImportError without the SDK, 6 tools with it."""

from __future__ import annotations

import importlib
import importlib.util
import sys

import pytest

import verifier_testlib as tl  # noqa: F401

HAVE_MCP = importlib.util.find_spec("mcp") is not None


@pytest.mark.skipif(HAVE_MCP, reason="mcp SDK installed; error path untestable")
def test_import_without_mcp_raises_helpful_importerror() -> None:
    sys.modules.pop("harness_verifier.mcp_server", None)
    with pytest.raises(ImportError, match=r"harness-verifier\[mcp\]"):
        importlib.import_module("harness_verifier.mcp_server")


@pytest.mark.skipif(not HAVE_MCP, reason="mcp SDK not installed")
def test_server_registers_six_tools() -> None:
    import asyncio

    mod = importlib.import_module("harness_verifier.mcp_server")
    tools = asyncio.run(mod.server.list_tools())
    names = {tool.name for tool in tools}
    assert names == set(tl.EXPECTED_VERIFIER_NAMES) | {"run_claims"}
    assert len(tools) == 6


@pytest.mark.skipif(not HAVE_MCP, reason="mcp SDK not installed")
def test_server_main_is_exposed() -> None:
    mod = importlib.import_module("harness_verifier.mcp_server")
    assert callable(mod.main)
