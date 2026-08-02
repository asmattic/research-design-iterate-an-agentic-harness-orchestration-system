"""Hand-computed scorer behavior on small synthetic event streams."""

from __future__ import annotations

import pytest

import evals_testlib as tl

he = pytest.importorskip("harness_evals")


def _emission(agent_id: str, confidence: float, event_id: str) -> dict:
    return tl.make_event(
        event_id=event_id, kind="emission",
        payload={"agent_id": agent_id, "confidence": confidence},
    )


def _verifier(agent_id: str, result: str, event_id: str) -> dict:
    return tl.make_event(
        event_id=event_id, kind="verifier_result",
        payload={"agent_id": agent_id, "result": result},
    )


# --- calibration -----------------------------------------------------------


def test_calibration_hand_computed_two_pairs():
    # conf 0.9 / outcome 1 and conf 0.6 / outcome 0:
    # brier = ((0.9-1)^2 + (0.6-0)^2) / 2 = (0.01 + 0.36) / 2 = 0.185
    # value = 1 - brier = 0.815
    # ece (10 buckets, one pair each) = 0.5*|0.9-1| + 0.5*|0.6-0| = 0.35
    events = [
        _emission("a1", 0.9, "evt-1"),
        _verifier("a1", "pass", "evt-2"),
        _emission("a2", 0.6, "evt-3"),
        _verifier("a2", "fail", "evt-4"),
    ]
    result = he.get_scorer("calibration").score(events)
    assert result.details["pairs"] == 2
    assert result.details["brier"] == pytest.approx(0.185)
    assert result.value == pytest.approx(0.815)
    assert result.details["ece"] == pytest.approx(0.35)


def test_calibration_outcome_requires_all_verifiers_passing():
    events = [
        _emission("a1", 0.9, "evt-1"),
        _verifier("a1", "pass", "evt-2"),
        _verifier("a1", "fail", "evt-3"),  # one failure flips the outcome to 0
    ]
    result = he.get_scorer("calibration").score(events)
    assert result.details["pairs"] == 1
    assert result.details["brier"] == pytest.approx(0.81)  # (0.9 - 0)^2


def test_calibration_agent_without_verifier_events_contributes_no_pair():
    events = [
        _emission("a1", 0.9, "evt-1"),
        _emission("a2", 0.4, "evt-2"),
        _verifier("a2", "pass", "evt-3"),
    ]
    result = he.get_scorer("calibration").score(events)
    assert result.details["pairs"] == 1


def test_calibration_zero_pairs_scores_zero_with_none_details():
    result = he.get_scorer("calibration").score([tl.make_event()])
    assert result.value == 0.0
    assert result.details == {"brier": None, "ece": None, "pairs": 0}


# --- drift -----------------------------------------------------------------


def test_drift_value_is_one_minus_max_composite():
    events = [
        tl.make_event(event_id="d1", kind="drift_check",
                      payload={"composite": 0.2, "status": "ok"}),
        tl.make_event(event_id="d2", kind="drift_check",
                      payload={"composite": 0.6, "status": "pause"}),
        tl.make_event(event_id="d3", kind="drift_check",
                      payload={"composite": 0.3, "status": "halt"}),
    ]
    result = he.get_scorer("drift").score(events)
    assert result.value == pytest.approx(0.4)  # 1 - max(0.2, 0.6, 0.3)
    assert result.details["max_composite"] == pytest.approx(0.6)
    assert result.details["final_composite"] == pytest.approx(0.3)
    assert result.details["excursions"] == 2  # one pause + one halt


def test_drift_without_drift_checks_scores_one():
    result = he.get_scorer("drift").score([tl.make_event()])
    assert result.value == 1.0
    assert result.details["excursions"] == 0
    assert "note" in result.details


# --- completion ------------------------------------------------------------


def test_completion_is_resolved_over_claimed():
    events = [
        tl.make_event(event_id="c1", kind="ticket_claimed",
                      payload={"ticket_ref": "tkt-1"}),
        tl.make_event(event_id="c2", kind="ticket_claimed",
                      payload={"ticket_ref": "tkt-2"}),
        tl.make_event(event_id="r1", kind="ticket_resolved",
                      payload={"ticket_ref": "tkt-1"}),
        tl.make_event(event_id="r2", kind="ticket_resolved",
                      payload={"ticket_ref": "tkt-unclaimed"}),  # not claimed
        tl.make_event(event_id="dec", kind="decision",
                      payload={"decision": "ship"}),
    ]
    result = he.get_scorer("completion").score(events)
    assert result.value == pytest.approx(0.5)  # tkt-1 only, of 2 claimed
    assert result.details["claimed"] == 2
    assert result.details["resolved"] == 2
    assert result.details["has_final_decision"] is True


def test_completion_zero_when_nothing_claimed():
    result = he.get_scorer("completion").score([tl.make_event()])
    assert result.value == 0.0
    assert result.details["has_final_decision"] is False


# --- cost ------------------------------------------------------------------


def test_cost_prefers_explicit_tokens_over_in_out_sum():
    events = [
        tl.make_event(event_id="e1", cost={"tokens": 100, "tokens_in": 1,
                                           "tokens_out": 1}),
        tl.make_event(event_id="e2", cost={"tokens_in": 10, "tokens_out": 5,
                                           "usd": 0.02, "wall_clock_ms": 300}),
        tl.make_event(event_id="e3"),  # no cost block
    ]
    result = he.get_scorer("cost").score(events)
    assert result.value == 115.0
    assert result.details["tokens"] == 115
    assert result.details["usd"] == pytest.approx(0.02)
    assert result.details["wall_clock_ms"] == 300


# --- safety ----------------------------------------------------------------


def test_safety_blocked_fraction_and_categories():
    events = [
        tl.make_event(event_id="g1", kind="guardrail_event",
                      payload={"blocked": True, "category": "prompt_injection"}),
        tl.make_event(event_id="g2", kind="guardrail_event",
                      payload={"blocked": False, "category": "harmful_content"}),
        tl.make_event(event_id="g3", kind="guardrail_event",
                      payload={"blocked": True, "category": "prompt_injection"}),
        tl.make_event(event_id="g4", kind="guardrail_event",
                      payload={}),  # missing blocked counts as not blocked
    ]
    result = he.get_scorer("safety").score(events)
    assert result.value == pytest.approx(0.5)  # 2 of 4 blocked
    assert result.details["cases"] == 4
    assert result.details["blocked"] == 2
    assert result.details["categories"] == ["harmful_content", "prompt_injection"]


def test_safety_direction_is_blocked_fraction_not_its_complement():
    """Asymmetric split so an inverted blocked-check cannot score the same.

    Added after a mutation test showed the symmetric 2-of-4 case above
    survives `is True` -> `is not True`; 3-of-4 pins the direction.
    """
    events = [
        tl.make_event(event_id=f"g{i}", kind="guardrail_event",
                      payload={"blocked": b, "category": "prompt_injection"})
        for i, b in enumerate([True, True, True, False])
    ]
    result = he.get_scorer("safety").score(events)
    assert result.value == pytest.approx(0.75)
    assert result.details["blocked"] == 3


def test_safety_no_guardrail_events_scores_zero():
    result = he.get_scorer("safety").score([tl.make_event()])
    assert result.value == 0.0
    assert result.details == {"cases": 0}
