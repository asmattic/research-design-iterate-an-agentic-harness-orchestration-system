"""Phase 2B behavior contract for harness_reference.consensus.

Split out of test_phase2b_behavior.py; see test_2b_event_log.py docstring for
the marker protocol.
"""

from __future__ import annotations

import pytest

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
consensus = pytest.importorskip("harness_reference.consensus")


def xfail2b(reason: str):
    return pytest.mark.xfail(strict=True, raises=NotImplementedError,
                             reason=f"Phase 2B: {reason}")


def _emission(agent_id: str, value: float, weight: float, confidence: float = 0.8) -> dict:
    return {"agent_id": agent_id, "value": value, "weight": weight,
            "confidence": confidence, "reasoning": f"{agent_id} rationale"}


@xfail2b("aggregate returns a schema-valid consensus packet preserving dissent")
def test_consensus_preserves_dissent(valid_event):
    emissions = [_emission("a1", 100.0, 1.0), _emission("a2", 102.0, 1.0),
                 _emission("a3", 99.0, 1.0), _emission("dissenter", 250.0, 0.6)]
    packet = consensus.aggregate(
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
    packet = consensus.aggregate(
        emissions, campaign_id="camp_2026_04_tampa", cohort="finance",
        task_id="task_underwriting_01", dissent_floor=consensus.DISSENT_FLOOR)
    assert packet["dissent"] == []
