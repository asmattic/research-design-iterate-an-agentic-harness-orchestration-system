"""Behavior specs for Phase 2D (formerly strict-xfail).

Phase 2D has landed: the xfail markers are gone and the assertions are live.
Test bodies are byte-identical to the Phase 2A contract.
"""

from __future__ import annotations

import pytest

import evals_testlib as tl

he = pytest.importorskip("harness_evals")

SECTION_HEADINGS = (
    "Completion", "Intent-alignment", "Drift", "Calibration",
    "Cost", "Safety", "Human gates", "Retrospective notes",
)


def test_write_report_produces_section_14_8_report(tmp_out):
    from harness_evals import report

    events = [tl.make_event(event_id=f"evt-{i}") for i in range(3)]
    results = [he.get_scorer("dummy").score(events)]
    report.write_report("camp-1", results, tmp_out)
    text = (tmp_out / "report.md").read_text(encoding="utf-8")
    assert "# Campaign camp-1 report" in text
    for heading in SECTION_HEADINGS:
        assert heading in text, f"missing section heading: {heading}"


def test_regression_gate_zero_on_equal_scores():
    from harness_evals import regression

    scores = {"dummy": 1.0, "completion": 0.8}
    assert regression.regression_gate(scores, dict(scores), {"dummy": 0.05}) == 0


def test_regression_gate_nonzero_on_regression():
    from harness_evals import regression

    baseline = {"completion": 0.9}
    current = {"completion": 0.5}
    assert regression.regression_gate(current, baseline, {"completion": 0.1}) != 0


def test_calibration_scorer_brier_and_ece():
    events = [
        tl.make_event(
            event_id=f"evt-{i}", kind="verifier_result",
            payload={"confidence": conf, "outcome": outcome},
        )
        for i, (conf, outcome) in enumerate(
            [(0.9, True), (0.8, True), (0.7, False), (0.3, False), (0.2, True)]
        )
    ]
    result = he.get_scorer("calibration").score(events)
    assert 0.0 <= result.value <= 1.0
    assert "brier" in result.details
    assert "ece" in result.details


def test_cost_scorer_sums_tokens_across_fixture(fixture_events):
    if not fixture_events:
        pytest.skip("canonical recorded-campaign.jsonl not yet present")
    result = he.get_scorer("cost").score(fixture_events)
    expected = sum(
        cost.get("tokens", cost.get("tokens_in", 0) + cost.get("tokens_out", 0))
        for event in fixture_events
        for cost in [event.get("cost", {})]
    )
    assert result.details.get("tokens", result.value) == expected
