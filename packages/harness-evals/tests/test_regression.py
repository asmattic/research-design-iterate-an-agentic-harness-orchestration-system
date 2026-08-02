"""Regression gate semantics, including the cost lower-is-better direction."""

from __future__ import annotations

import pytest

pytest.importorskip("harness_evals")

from harness_evals import regression  # noqa: E402


def test_lower_is_better_names_cost():
    assert regression.LOWER_IS_BETTER == frozenset({"cost"})


def test_cost_increase_past_threshold_trips_gate():
    assert (
        regression.regression_gate(
            current={"cost": 16000.0}, baseline={"cost": 10000.0},
            thresholds={"cost": 5000.0},
        )
        == 1
    )


def test_cost_increase_within_threshold_passes():
    assert (
        regression.regression_gate(
            current={"cost": 14000.0}, baseline={"cost": 10000.0},
            thresholds={"cost": 5000.0},
        )
        == 0
    )


def test_cost_decrease_is_never_a_regression():
    assert (
        regression.regression_gate(
            current={"cost": 100.0}, baseline={"cost": 10000.0}, thresholds={}
        )
        == 0
    )


def test_higher_is_better_drop_within_threshold_passes():
    assert (
        regression.regression_gate(
            current={"completion": 0.87}, baseline={"completion": 0.9},
            thresholds={"completion": 0.05},
        )
        == 0
    )


def test_missing_threshold_defaults_to_zero():
    # Any drop trips the gate when no threshold is configured.
    assert (
        regression.regression_gate(
            current={"safety": 0.99}, baseline={"safety": 1.0}, thresholds={}
        )
        == 1
    )


def test_scorer_only_in_baseline_is_ignored():
    assert (
        regression.regression_gate(
            current={}, baseline={"completion": 0.9}, thresholds={"completion": 0.05}
        )
        == 0
    )


def test_improvement_on_higher_is_better_passes():
    assert (
        regression.regression_gate(
            current={"completion": 0.95}, baseline={"completion": 0.9}, thresholds={}
        )
        == 0
    )
