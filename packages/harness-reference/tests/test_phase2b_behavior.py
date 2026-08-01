"""Phase 2B behavior contract, encoded as strict xfails against today's stubs.

Every test calls the real API with real fixtures and asserts real outcomes.
Today each call raises NotImplementedError, which must escape the test body so
strict xfail records XFAIL. In Phase 2B, remove the marker from a test and it
becomes the acceptance test for that behavior; an accidentally implemented
stub flips the test to XPASS and (strict=True) turns the suite red.
"""

from __future__ import annotations

import json

import pytest

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
event_log = pytest.importorskip("harness_reference.event_log")
memory_index = pytest.importorskip("harness_reference.memory_index")
drift_mod = pytest.importorskip("harness_reference.drift_check")
consensus = pytest.importorskip("harness_reference.consensus")
retro_mod = pytest.importorskip("harness_reference.retrospective")


def xfail2b(reason: str):
    return pytest.mark.xfail(strict=True, raises=NotImplementedError,
                             reason=f"Phase 2B: {reason}")


def _emission(agent_id: str, value: float, weight: float, confidence: float = 0.8) -> dict:
    return {"agent_id": agent_id, "value": value, "weight": weight,
            "confidence": confidence, "reasoning": f"{agent_id} rationale"}


@xfail2b("EventLog append returns event_id; events() filters; JSONL is append-only")
def test_event_log_append_filter_jsonl(tmp_log_path, valid_event):
    log = event_log.EventLog(tmp_log_path)  # raises today
    eid = log.append(valid_event)
    assert eid == valid_event["event_id"]
    assert len(log) == 1
    assert [e["event_id"] for e in log.events(kind=valid_event["kind"])] == [eid]
    assert list(log.events(kind="decision")) == []
    assert [e["event_id"] for e in log.events(task_id=valid_event["task_id"])] == [eid]
    second = dict(valid_event, event_id="evt_01jg8w3k9r2qazy1")
    log.append(second)
    lines = tmp_log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["event_id"] == eid
    assert json.loads(lines[1])["event_id"] == second["event_id"]


@xfail2b("schema-invalid envelopes are rejected with ValueError, nothing written")
def test_event_log_rejects_invalid(tmp_log_path):
    log = event_log.EventLog(tmp_log_path)  # raises today
    with pytest.raises(ValueError):
        log.append({"kind": "not-a-real-kind"})
    assert len(log) == 0


@xfail2b("MemoryIndex add/get round-trip and tier/tag query filters")
def test_memory_index_roundtrip_and_query(tmp_path, valid_memory_entry):
    idx = memory_index.MemoryIndex(tmp_path)  # raises today
    mid = idx.add(valid_memory_entry)
    assert mid == valid_memory_entry["memory_id"]
    assert idx.get(mid)["memory_id"] == mid
    hits = idx.query(tier=valid_memory_entry["tier"], tags=["tampa"])
    assert [e["memory_id"] for e in hits] == [mid]
    assert idx.query(tier="L1") == []
    assert idx.query(tags=["no-such-tag"]) == []


@xfail2b("resolve follows supersedes chain; superseded entries hidden unless requested")
def test_memory_index_supersedes_chain(tmp_path, valid_memory_entry):
    idx = memory_index.MemoryIndex(tmp_path)  # raises today
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


@xfail2b("identical intent and state score composite ~0 with status ok")
def test_drift_identical_is_ok():
    text = "Underwrite the Tampa rental portfolio conservatively within budget."
    result = drift_mod.drift_check(text, text)  # raises today
    assert result.composite == pytest.approx(0.0, abs=0.05)
    assert result.status == "ok"


@xfail2b("disjoint intent and state exceed the pause threshold")
def test_drift_disjoint_pauses():
    result = drift_mod.drift_check(
        "Underwrite the Tampa rental portfolio conservatively within budget.",
        "Compiling zsh plugins and benchmarking GPU shader kernels overnight.",
    )
    assert result.composite > drift_mod.DEFAULT_PAUSE_THRESHOLD
    assert result.status in ("pause", "halt")


@xfail2b("status respects warn <= pause threshold ordering")
def test_drift_threshold_monotonic():
    intent = "Plan the campaign roadmap."
    state = "Plan the campaign roadmap and also restructure the billing stack."
    strict = drift_mod.drift_check(intent, state,
                                   warn_threshold=0.0, pause_threshold=1.0)
    lax = drift_mod.drift_check(intent, state,
                                warn_threshold=0.99, pause_threshold=0.999)
    if strict.composite > 0.0:
        assert strict.status != "ok"
    if lax.composite <= 0.99:
        assert lax.status == "ok"
    assert strict.composite == pytest.approx(lax.composite)


@xfail2b("aggregate returns a schema-valid consensus packet preserving dissent")
def test_consensus_preserves_dissent(valid_event):
    emissions = [_emission("a1", 100.0, 1.0), _emission("a2", 102.0, 1.0),
                 _emission("a3", 99.0, 1.0), _emission("dissenter", 250.0, 0.6)]
    packet = consensus.aggregate(  # raises today
        emissions, campaign_id="camp_2026_04_tampa", cohort="finance",
        task_id="task_underwriting_01")
    harness_protocol = pytest.importorskip("harness_protocol")
    assert harness_protocol.iter_errors("consensus-packet", packet) == []
    assert len(packet["dissent"]) >= 1
    block = packet["consensus"]
    assert 0.0 <= block["confidence"] <= 1.0
    assert block["interval"]["low"] <= block["value"] <= block["interval"]["high"]


@xfail2b("a dissenter below the dissent floor is dropped from the dissent block")
def test_consensus_floor_drops_small_dissent():
    emissions = [_emission("a1", 100.0, 1.0), _emission("a2", 102.0, 1.0),
                 _emission("a3", 99.0, 1.0), _emission("dissenter", 250.0, 0.3)]
    packet = consensus.aggregate(  # raises today
        emissions, campaign_id="camp_2026_04_tampa", cohort="finance",
        task_id="task_underwriting_01", dissent_floor=consensus.DISSENT_FLOOR)
    assert packet["dissent"] == []


@xfail2b("verifier failure events yield a weight_adjustment proposal for that agent")
def test_retrospective_weight_adjustment(valid_event):
    agent_id = valid_event["emitter"]["id"]
    failure = dict(valid_event,
                   event_id="evt_01jg8w3k9r2qazy2", kind="verifier_result",
                   payload={"result": "fail", "agent_id": agent_id,
                            "verifier_id": "numeric_bounds_verifier"})
    proposals = retro_mod.retrospective([valid_event, failure])  # raises today
    adjustments = [p for p in proposals if p.kind == "weight_adjustment"]
    assert adjustments
    assert any(agent_id in p.target for p in adjustments)


@xfail2b("an empty event stream yields no proposals")
def test_retrospective_empty_stream():
    assert retro_mod.retrospective([]) == []
