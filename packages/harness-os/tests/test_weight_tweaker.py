"""Behavior tests for harness_os.weight_tweaker (PRD §6.4.5).

Loads the module directly from its file path so collection never depends on
sibling-lane modules re-exported by ``harness_os/__init__.py``. The tests
that exercise real ``harness_reference.retrospective.Proposal`` objects
importorskip that package (installed in this checkout's src tree).
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


weight_tweaker = _load("weight_tweaker")


def _adjustment(agent_id: str, delta: float) -> dict:
    return {
        "kind": "weight_adjustment",
        "target": agent_id,
        "rationale": "test",
        "payload": {"agent_id": agent_id, "suggested_delta": delta},
    }


class TestPlainMappingProposals:
    def test_applies_delta_to_existing_agent(self):
        out = weight_tweaker.apply_proposals(
            {"budget-expert": 1.0}, [_adjustment("budget-expert", 0.2)]
        )
        assert out["budget-expert"] == pytest.approx(1.2)

    def test_missing_agent_starts_at_default_weight(self):
        out = weight_tweaker.apply_proposals({}, [_adjustment("new-agent", -0.3)])
        assert out["new-agent"] == pytest.approx(0.7)

    def test_custom_default_weight(self):
        out = weight_tweaker.apply_proposals(
            {}, [_adjustment("a", 0.0)], default_weight=1.5
        )
        assert out["a"] == pytest.approx(1.5)

    def test_clamped_to_ceiling(self):
        out = weight_tweaker.apply_proposals(
            {"a": 1.9}, [_adjustment("a", 5.0)]
        )
        assert out["a"] == pytest.approx(2.0)

    def test_clamped_to_floor(self):
        out = weight_tweaker.apply_proposals(
            {"a": 0.2}, [_adjustment("a", -5.0)]
        )
        assert out["a"] == pytest.approx(0.1)

    def test_custom_floor_and_ceiling(self):
        out = weight_tweaker.apply_proposals(
            {"a": 1.0},
            [_adjustment("a", 10.0), _adjustment("b", -10.0)],
            floor=0.5,
            ceiling=3.0,
        )
        assert out["a"] == pytest.approx(3.0)
        assert out["b"] == pytest.approx(0.5)

    def test_non_weight_kinds_ignored_silently(self):
        proposals = [
            {"kind": "prompt_diff", "target": "p", "payload": {"diff": "x"}},
            {"kind": "memory_entry", "target": "m", "payload": {"note": "y"}},
        ]
        out = weight_tweaker.apply_proposals({"a": 1.0}, proposals)
        assert out == {"a": 1.0}

    def test_input_table_never_mutated_and_new_dict_returned(self):
        table = {"a": 1.0, "b": 0.5}
        snapshot = dict(table)
        out = weight_tweaker.apply_proposals(table, [_adjustment("a", 0.5)])
        assert out is not table
        assert table == snapshot
        assert set(out) == {"a", "b"}  # every input agent carried over

    def test_sequential_deltas_accumulate(self):
        out = weight_tweaker.apply_proposals(
            {"a": 1.0}, [_adjustment("a", 0.3), _adjustment("a", 0.3)]
        )
        assert out["a"] == pytest.approx(1.6)

    def test_floor_above_ceiling_raises(self):
        with pytest.raises(ValueError):
            weight_tweaker.apply_proposals({}, [], floor=2.0, ceiling=0.1)

    def test_empty_proposals_returns_copy_of_table(self):
        table = {"a": 0.9}
        out = weight_tweaker.apply_proposals(table, [])
        assert out == table
        assert out is not table


@pytest.fixture()
def make_proposal():
    """Build real harness_reference.retrospective.Proposal objects (or skip)."""
    retro = pytest.importorskip("harness_reference.retrospective")

    def _make(kind: str, payload: dict):
        return retro.Proposal(
            kind=kind, target="agent-weights", rationale="test", payload=payload
        )

    return _make


class TestRealProposalObjects:
    """Same behaviors driven through harness_reference.retrospective.Proposal."""

    def test_proposal_object_applies_delta(self, make_proposal):
        p = make_proposal(
            "weight_adjustment", {"agent_id": "tax-expert", "suggested_delta": -0.25}
        )
        out = weight_tweaker.apply_proposals({"tax-expert": 1.0}, [p])
        assert out["tax-expert"] == pytest.approx(0.75)

    def test_proposal_object_clamps_and_defaults(self, make_proposal):
        up = make_proposal(
            "weight_adjustment", {"agent_id": "fresh", "suggested_delta": 9.0}
        )
        out = weight_tweaker.apply_proposals({}, [up])
        assert out["fresh"] == pytest.approx(2.0)  # default 1.0 + 9.0, clamped

    def test_proposal_object_non_weight_kind_ignored(self, make_proposal):
        p = make_proposal("prompt_diff", {"diff": "irrelevant"})
        out = weight_tweaker.apply_proposals({"a": 1.0}, [p])
        assert out == {"a": 1.0}

    def test_mixed_proposal_objects_and_mappings(self, make_proposal):
        p = make_proposal(
            "weight_adjustment", {"agent_id": "a", "suggested_delta": 0.1}
        )
        out = weight_tweaker.apply_proposals(
            {"a": 1.0}, [p, _adjustment("a", 0.1)]
        )
        assert out["a"] == pytest.approx(1.2)
