"""Behavior tests for harness_os.signal_noise (PRD §6.4.4, §9.1 factor table).

Loads the module directly from its file path so collection never depends on
sibling-lane modules re-exported by ``harness_os/__init__.py``.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src" / "harness_os"


def _load(name: str) -> types.ModuleType:
    path = _SRC / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"harness_os_lane_{name}", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


signal_noise = _load("signal_noise")


class TestDefaults:
    def test_default_factor_weights_match_section_9_1(self):
        assert signal_noise.DEFAULT_FACTOR_WEIGHTS == {
            "calibration": 0.30,
            "verifier": 0.30,
            "agreement": 0.20,
            "bs": 0.15,
            "authority": 0.05,
        }

    def test_weighted_claim_is_frozen(self):
        wc = signal_noise.WeightedClaim(claim={}, weight=0.5, factors={})
        with pytest.raises(Exception):
            wc.weight = 0.9  # type: ignore[misc]


class TestArithmetic:
    def test_hand_computed_weight_from_section_9_1(self):
        # .30*.9 + .30*1.0 + .20*.75 + .15*1.0 + .05*.5 = 0.895
        claim = {
            "calibration": 0.9,
            "verifier_result": "pass",
            "agreement": 0.75,
            "bs_flags": ["clean"],
            "authority": 0.5,
        }
        [wc] = signal_noise.weigh([claim])
        assert wc.weight == pytest.approx(0.895)
        assert wc.factors == {
            "calibration": 0.9,
            "verifier": 1.0,
            "agreement": 0.75,
            "bs": 1.0,
            "authority": 0.5,
        }
        assert wc.claim is claim

    def test_all_defaults_when_metadata_missing(self):
        # every factor defaults to 0.5 except bs (empty flags -> 1.0)
        [wc] = signal_noise.weigh([{}])
        assert wc.factors == {
            "calibration": 0.5,
            "verifier": 0.5,
            "agreement": 0.5,
            "bs": 1.0,
            "authority": 0.5,
        }
        assert wc.weight == pytest.approx(
            0.30 * 0.5 + 0.30 * 0.5 + 0.20 * 0.5 + 0.15 * 1.0 + 0.05 * 0.5
        )

    @pytest.mark.parametrize(
        ("verifier_result", "factor"),
        [("pass", 1.0), ("fail", 0.0), ("abstain", 0.5)],
    )
    def test_verifier_result_factor_mapping(self, verifier_result, factor):
        [wc] = signal_noise.weigh([{"verifier_result": verifier_result}])
        assert wc.factors["verifier"] == factor

    @pytest.mark.parametrize(
        ("bs_flags", "factor"),
        [
            ([], 1.0),
            (["clean"], 1.0),
            (["over_confident"], 0.5),
            (["unsupported"], 0.5),
            (["over_confident", "unsupported"], 0.5),
            (["hallucinated"], 0.0),
            (["over_confident", "hallucinated"], 0.0),
        ],
    )
    def test_bs_flags_factor_mapping(self, bs_flags, factor):
        [wc] = signal_noise.weigh([{"bs_flags": bs_flags}])
        assert wc.factors["bs"] == factor


class TestOrdering:
    def test_sorted_by_weight_descending(self):
        low = {"name": "low", "verifier_result": "fail", "calibration": 0.0}
        high = {"name": "high", "verifier_result": "pass", "calibration": 1.0}
        mid = {"name": "mid"}
        out = signal_noise.weigh([low, high, mid])
        assert [wc.claim["name"] for wc in out] == ["high", "mid", "low"]
        assert out[0].weight >= out[1].weight >= out[2].weight

    def test_ties_are_stable_by_input_order(self):
        a = {"name": "first"}
        b = {"name": "second"}
        c = {"name": "third"}
        out = signal_noise.weigh([a, b, c])  # identical weights
        assert [wc.claim["name"] for wc in out] == ["first", "second", "third"]

    def test_empty_input_yields_empty_output(self):
        assert signal_noise.weigh([]) == []


class TestCustomFactorWeights:
    def test_custom_weights_are_used(self):
        weights = {
            "calibration": 1.0,
            "verifier": 0.0,
            "agreement": 0.0,
            "bs": 0.0,
            "authority": 0.0,
        }
        [wc] = signal_noise.weigh(
            [{"calibration": 0.25, "verifier_result": "pass"}],
            factor_weights=weights,
        )
        assert wc.weight == pytest.approx(0.25)

    def test_missing_key_raises(self):
        weights = {"calibration": 0.5, "verifier": 0.5}
        with pytest.raises(ValueError):
            signal_noise.weigh([], factor_weights=weights)

    def test_extra_key_raises(self):
        weights = dict(signal_noise.DEFAULT_FACTOR_WEIGHTS, vibes=0.0)
        with pytest.raises(ValueError):
            signal_noise.weigh([], factor_weights=weights)

    def test_sum_not_one_raises(self):
        weights = {
            "calibration": 0.30,
            "verifier": 0.30,
            "agreement": 0.20,
            "bs": 0.15,
            "authority": 0.10,  # sums to 1.05
        }
        with pytest.raises(ValueError):
            signal_noise.weigh([], factor_weights=weights)

    def test_sum_within_tolerance_accepted(self):
        weights = {
            "calibration": 0.30,
            "verifier": 0.30,
            "agreement": 0.20,
            "bs": 0.15,
            "authority": 0.05 + 5e-10,
        }
        assert signal_noise.weigh([], factor_weights=weights) == []


class TestOutOfRangeClaims:
    @pytest.mark.parametrize(
        "claim",
        [
            {"calibration": 1.5},
            {"calibration": -0.1},
            {"agreement": 2.0},
            {"authority": -1.0},
        ],
    )
    def test_out_of_range_value_raises_naming_index(self, claim):
        with pytest.raises(ValueError, match="claim 1"):
            signal_noise.weigh([{}, claim])

    def test_unknown_verifier_result_raises_naming_index(self):
        with pytest.raises(ValueError, match="claim 0"):
            signal_noise.weigh([{"verifier_result": "maybe"}])
