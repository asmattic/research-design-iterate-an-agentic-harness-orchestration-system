"""Phase 2B acceptance suite for harness_reference.retrospective.

Split out of test_phase2b_behavior.py. The strict-xfail markers were removed
when the implementation landed; these tests now run green as the acceptance
contract.
"""

from __future__ import annotations

import pytest

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
retro_mod = pytest.importorskip("harness_reference.retrospective")


def test_retrospective_weight_adjustment(valid_event):
    agent_id = valid_event["emitter"]["id"]
    failure = dict(valid_event,
                   event_id="evt_01jg8w3k9r2qazy2", kind="verifier_result",
                   payload={"result": "fail", "agent_id": agent_id,
                            "verifier_id": "numeric_bounds_verifier"})
    proposals = retro_mod.retrospective([valid_event, failure])
    adjustments = [p for p in proposals if p.kind == "weight_adjustment"]
    assert adjustments
    assert any(agent_id in p.target for p in adjustments)


def test_retrospective_empty_stream():
    assert retro_mod.retrospective([]) == []


def test_retrospective_drift_pause_yields_memory_entry(valid_event):
    drift = dict(valid_event,
                 event_id="evt_01jg8w3k9r2qazy3", kind="drift_check",
                 payload={"status": "pause", "score": 0.71})
    proposals = retro_mod.retrospective([valid_event, drift])
    entries = [p for p in proposals if p.kind == "memory_entry"]
    assert len(entries) == 1
    assert entries[0].target == "campaign"
    assert entries[0].payload == {"note": "drift excursion",
                                  "event_id": "evt_01jg8w3k9r2qazy3"}
