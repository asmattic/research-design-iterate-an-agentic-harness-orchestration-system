"""Phase 2B behavior contract for harness_reference.retrospective.

Split out of test_phase2b_behavior.py; see test_2b_event_log.py docstring for
the marker protocol.
"""

from __future__ import annotations

import pytest

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
retro_mod = pytest.importorskip("harness_reference.retrospective")


def xfail2b(reason: str):
    return pytest.mark.xfail(strict=True, raises=NotImplementedError,
                             reason=f"Phase 2B: {reason}")


@xfail2b("verifier failure events yield a weight_adjustment proposal for that agent")
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


@xfail2b("an empty event stream yields no proposals")
def test_retrospective_empty_stream():
    assert retro_mod.retrospective([]) == []
