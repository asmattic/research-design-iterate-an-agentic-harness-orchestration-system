"""Phase 2B behavior contract for harness_reference.memory_index.

Split out of test_phase2b_behavior.py; see test_2b_event_log.py docstring for
the marker protocol.
"""

from __future__ import annotations

import pytest

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
memory_index = pytest.importorskip("harness_reference.memory_index")


def xfail2b(reason: str):
    return pytest.mark.xfail(strict=True, raises=NotImplementedError,
                             reason=f"Phase 2B: {reason}")


@xfail2b("MemoryIndex add/get round-trip and tier/tag query filters")
def test_memory_index_roundtrip_and_query(tmp_path, valid_memory_entry):
    idx = memory_index.MemoryIndex(tmp_path)
    mid = idx.add(valid_memory_entry)
    assert mid == valid_memory_entry["memory_id"]
    assert idx.get(mid)["memory_id"] == mid
    hits = idx.query(tier=valid_memory_entry["tier"], tags=["tampa"])
    assert [e["memory_id"] for e in hits] == [mid]
    assert idx.query(tier="L1") == []
    assert idx.query(tags=["no-such-tag"]) == []


@xfail2b("resolve follows supersedes chain; superseded entries hidden unless requested")
def test_memory_index_supersedes_chain(tmp_path, valid_memory_entry):
    idx = memory_index.MemoryIndex(tmp_path)
    first = dict(valid_memory_entry, supersedes=None)
    newer = dict(valid_memory_entry,
                 memory_id="mem_20260501_rental_tampa_zoning",
                 freshness="2026-05-01", supersedes=first["memory_id"])
    idx.add(first)
    idx.add(newer)
    assert idx.resolve(first["memory_id"])["memory_id"] == newer["memory_id"]
    assert idx.resolve(newer["memory_id"])["memory_id"] == newer["memory_id"]
    visible = {e["memory_id"] for e in idx.query(domain=first["domain"])}
    assert visible == {newer["memory_id"]}
    everything = {e["memory_id"]
                  for e in idx.query(domain=first["domain"], include_superseded=True)}
    assert everything == {first["memory_id"], newer["memory_id"]}
