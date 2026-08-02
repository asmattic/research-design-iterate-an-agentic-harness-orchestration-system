"""Behavior tests for harness_os.context_manager (PRD §6.4.1)."""

from __future__ import annotations

import json
import math
from typing import Any

import pytest

import os_ctx_testlib

cm = os_ctx_testlib.load_harness_os_module("context_manager")


def _compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _packet(task_id: str, payload: str = "x" * 40) -> dict[str, Any]:
    return {"task_id": task_id, "payload": payload}


FULL_STATE: dict[str, Any] = {
    "destination": "ship the zoning report",
    "intent_ref": "intent-001",
    "plan": {"steps": [1, 2]},
    "drift": "composite=0.12 status=ok",
    "budget": "spent=3.20 cap=10.00",
    "pending_approvals": ["deploy"],
}


class TestOrdering:
    def test_fixed_section_order_with_two_packets(self) -> None:
        packets = [_packet("t1"), _packet("t2")]  # chronological: t1 older
        bundle = cm.assemble_context(FULL_STATE, packets)
        names = tuple(name for name, _ in bundle.sections)
        assert names == (
            "intent",
            "plan",
            "drift",
            "budget",
            "approvals",
            "packet:t2",
            "packet:t1",
        )

    def test_packets_newest_first_bodies(self) -> None:
        packets = [_packet("t1"), _packet("t2")]
        bundle = cm.assemble_context(FULL_STATE, packets)
        packet_sections = [s for s in bundle.sections if s[0].startswith("packet:")]
        assert packet_sections[0] == ("packet:t2", _compact(_packet("t2")))
        assert packet_sections[1] == ("packet:t1", _compact(_packet("t1")))

    def test_intent_and_plan_bodies(self) -> None:
        bundle = cm.assemble_context(FULL_STATE, [])
        sections = dict(bundle.sections)
        assert "ship the zoning report" in sections["intent"]
        assert "intent-001" in sections["intent"]
        assert sections["plan"] == '{"steps":[1,2]}'


class TestOmission:
    def test_absent_sections_omitted(self) -> None:
        bundle = cm.assemble_context({"destination": "somewhere"}, [])
        assert tuple(name for name, _ in bundle.sections) == ("intent",)

    def test_empty_state_no_packets(self) -> None:
        bundle = cm.assemble_context({}, [])
        assert bundle.sections == ()
        assert bundle.token_estimate == 0
        assert bundle.dropped == ()


class TestTokenArithmetic:
    def test_exact_estimate_even_division(self) -> None:
        state = {"drift": "d" * 10, "budget": "b" * 6}  # 16 chars total
        bundle = cm.assemble_context(state, [])
        assert bundle.token_estimate == 4

    def test_exact_estimate_ceiling(self) -> None:
        state = {"drift": "d" * 11, "budget": "b" * 6}  # 17 chars -> ceil 5
        bundle = cm.assemble_context(state, [])
        assert bundle.token_estimate == 5


class TestBudgetDrops:
    CORE_STATE = {"drift": "core-drift"}  # 10-char core body

    def test_drop_oldest_until_fit(self) -> None:
        packets = [_packet("a"), _packet("b"), _packet("c")]  # c newest
        core_len = len(self.CORE_STATE["drift"])
        newest_len = len(_compact(_packet("c")))
        budget = math.ceil((core_len + newest_len) / 4)
        bundle = cm.assemble_context(self.CORE_STATE, packets, budget_tokens=budget)
        assert tuple(name for name, _ in bundle.sections) == ("drift", "packet:c")
        assert bundle.dropped == ("packet:a", "packet:b")
        assert bundle.token_estimate <= budget

    def test_never_drop_core(self) -> None:
        packets = [_packet("a"), _packet("b")]
        budget = math.ceil(len(self.CORE_STATE["drift"]) / 4)  # fits core only
        bundle = cm.assemble_context(self.CORE_STATE, packets, budget_tokens=budget)
        assert tuple(name for name, _ in bundle.sections) == ("drift",)
        assert bundle.dropped == ("packet:a", "packet:b")

    def test_core_alone_over_budget_raises(self) -> None:
        state = {"drift": "x" * 100}  # 25 tokens of core
        with pytest.raises(ValueError):
            cm.assemble_context(state, [_packet("a")], budget_tokens=2)

    @pytest.mark.parametrize("budget", [0, -5])
    def test_nonpositive_budget_raises(self, budget: int) -> None:
        with pytest.raises(ValueError):
            cm.assemble_context(FULL_STATE, [], budget_tokens=budget)


class TestBundleShape:
    def test_frozen_dataclass_with_tuples(self) -> None:
        bundle = cm.assemble_context(FULL_STATE, [_packet("t1")])
        assert isinstance(bundle, cm.ContextBundle)
        assert isinstance(bundle.sections, tuple)
        assert isinstance(bundle.dropped, tuple)
        with pytest.raises(AttributeError):
            bundle.token_estimate = 0  # type: ignore[misc]


PROMPT_FILES = (
    "bs_detector.v1.md",
    "context_summarizer.v1.md",
    "drift_judge.v1.md",
)


class TestPromptTemplates:
    @pytest.mark.parametrize("name", PROMPT_FILES)
    def test_exists_with_version_1_frontmatter(self, name: str) -> None:
        path = os_ctx_testlib.PROMPTS_DIR / name
        assert path.is_file(), f"missing prompt template: {path}"
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n"), "prompt must open with YAML frontmatter"
        frontmatter = text.split("---")[1]
        assert "version: 1" in frontmatter

    @pytest.mark.parametrize("name", PROMPT_FILES)
    def test_no_html_comments_article_i(self, name: str) -> None:
        text = (os_ctx_testlib.PROMPTS_DIR / name).read_text(encoding="utf-8")
        assert "<!--" not in text, "Constitution Article I: no HTML comments"
