"""Behavior tests for harness_os.validator (PRD §6.4.3, §9.6 packet shape).

Loads the module directly from its file path so collection never depends on
sibling-lane modules re-exported by ``harness_os/__init__.py``. If the real
``harness_verifier`` package has not landed yet, a contract-conformant stub
is installed in ``sys.modules`` first (the declared Phase 2C contract:
frozen ``VerifierResult`` dataclass + ``run_claims`` that never raises and
returns abstain for unknown verifiers).
"""

from __future__ import annotations

import importlib.util
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src" / "harness_os"

try:  # pragma: no cover - depends on sibling-lane timing
    import harness_verifier  # noqa: F401

    HAS_REAL_VERIFIER = True
except ImportError:  # pragma: no cover - stub matches the declared contract
    HAS_REAL_VERIFIER = False

    @dataclass(frozen=True)
    class _StubVerifierResult:
        verifier_id: str
        result: str
        evidence: dict = field(default_factory=dict)

    def _stub_run_claims(claims: Sequence[Mapping[str, Any]]) -> list[Any]:
        return [
            _StubVerifierResult(str(c.get("verifier", "unknown")), "abstain", {})
            for c in claims
        ]

    _stub = types.ModuleType("harness_verifier")
    _stub.VerifierResult = _StubVerifierResult  # type: ignore[attr-defined]
    _stub.run_claims = _stub_run_claims  # type: ignore[attr-defined]
    sys.modules["harness_verifier"] = _stub


def _load(name: str) -> types.ModuleType:
    path = _SRC / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"harness_os_lane_{name}", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


validator = _load("validator")

from harness_verifier import VerifierResult  # noqa: E402


def _result(verifier_id: str, result: str) -> Any:
    return VerifierResult(verifier_id=verifier_id, result=result, evidence={})


class TestRouteClaims:
    def test_delegates_claims_verbatim_and_returns_results(self, monkeypatch):
        seen: list[Any] = []
        canned = [_result("code_runner", "pass"), _result("sql_check", "fail")]

        def fake_run_claims(claims):
            seen.append(claims)
            return list(canned)

        monkeypatch.setattr(validator, "run_claims", fake_run_claims)
        claims = [
            {"verifier": "code_runner", "text": "2+2==4"},
            {"verifier": "sql_check", "text": "SELECT 1"},
        ]
        out = validator.route_claims({"claims": claims})
        assert out == canned
        assert seen == [claims]  # passed through verbatim, one call

    def test_missing_claims_returns_empty_without_calling_verifier(self, monkeypatch):
        def boom(claims):  # pragma: no cover - must not run
            raise AssertionError("run_claims must not be called")

        monkeypatch.setattr(validator, "run_claims", boom)
        assert validator.route_claims({}) == []

    def test_empty_claims_returns_empty(self, monkeypatch):
        monkeypatch.setattr(validator, "run_claims", lambda claims: [])
        assert validator.route_claims({"claims": []}) == []

    @pytest.mark.parametrize("bad", ["not-a-list", {"verifier": "x"}, 42, None])
    def test_non_list_claims_raises_value_error(self, bad):
        with pytest.raises(ValueError):
            validator.route_claims({"claims": bad})

    @pytest.mark.skipif(not HAS_REAL_VERIFIER, reason="harness_verifier not landed")
    def test_real_verifier_unknown_verifier_abstains(self):
        out = validator.route_claims(
            {"claims": [{"verifier": "no_such_verifier_xyz", "text": "?"}]}
        )
        assert len(out) == 1
        assert out[0].result == "abstain"


class TestAttachResults:
    def test_attaches_section_9_6_shape(self):
        emission = {"agent_id": "budget-expert", "claims": [{"verifier": "v"}]}
        results = [_result("code_runner", "pass"), _result("url_check", "abstain")]
        out = validator.attach_results(emission, results)
        assert out["verifier_results"] == [
            {"verifier_id": "code_runner", "result": "pass", "evidence_ref": None},
            {"verifier_id": "url_check", "result": "abstain", "evidence_ref": None},
        ]
        assert out["agent_id"] == "budget-expert"

    def test_returns_new_dict_and_never_mutates_input(self):
        emission = {"agent_id": "a", "verifier_results": [{"verifier_id": "old"}]}
        snapshot = dict(emission)
        out = validator.attach_results(emission, [_result("new", "pass")])
        assert out is not emission
        assert emission == snapshot  # input untouched

    def test_existing_verifier_results_replaced_not_appended(self):
        emission = {
            "verifier_results": [
                {"verifier_id": "stale", "result": "fail", "evidence_ref": None}
            ]
        }
        out = validator.attach_results(emission, [_result("fresh", "pass")])
        assert out["verifier_results"] == [
            {"verifier_id": "fresh", "result": "pass", "evidence_ref": None}
        ]

    def test_empty_results_attach_empty_list(self):
        out = validator.attach_results({"x": 1}, [])
        assert out["verifier_results"] == []
        assert out["x"] == 1
