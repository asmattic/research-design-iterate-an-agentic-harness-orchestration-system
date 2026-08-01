"""Phase 2A contract pins: version, templates, dataclasses, constants, stub behavior."""

from __future__ import annotations

import dataclasses
import os

import pytest

TEMPLATE_NAMES = (
    "INTENT.md", "ORCHESTRATOR.md", "AGENTS.md", "COHORT.md",
    "SWARM.md", "CONSTITUTION.md", "HANDOFF.md",
)

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
event_log = pytest.importorskip("harness_reference.event_log")
memory_index = pytest.importorskip("harness_reference.memory_index")
drift_mod = pytest.importorskip("harness_reference.drift_check")
consensus = pytest.importorskip("harness_reference.consensus")
retro_mod = pytest.importorskip("harness_reference.retrospective")

INTENT_HEADINGS = (
    "# Goal",
    "# Success criteria (measurable)",
    "# Non-goals (explicitly excluded)",
    "# Hard constraints",
    '# What "done" looks like',
    "# Decision framework when something isn't specified",
    "# What changes this file",
)
ORCHESTRATOR_MENTIONS = ("frontier", "claim", "fog", "destination", "one ticket per session")


def _template_text(templates, name: str) -> str:
    path = templates / name
    if not path.is_file():
        pytest.skip(f"template lane not landed yet: {name} missing")
    return path.read_text(encoding="utf-8")


def test_version() -> None:
    assert hr.__version__ == "0.2.0"


def test_templates_dir_resolves(templates) -> None:
    assert templates.is_dir()


def test_templates_env_override(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HARNESS_REFERENCE_TEMPLATES", str(tmp_path))
    assert hr.templates_dir() == tmp_path


def test_all_seven_templates_exist(templates) -> None:
    missing = [n for n in TEMPLATE_NAMES if not (templates / n).is_file()]
    if missing and "HARNESS_REFERENCE_TEMPLATES" not in os.environ:
        pytest.skip(f"template lane in flight; missing: {missing}")
    assert missing == []


@pytest.mark.parametrize("name", TEMPLATE_NAMES, ids=[n[:-3] for n in TEMPLATE_NAMES])
def test_template_no_html_comments(templates, name) -> None:
    """Constitution Article I: HTML comments are banned in every template."""
    assert "<!--" not in _template_text(templates, name)


@pytest.mark.parametrize("name", TEMPLATE_NAMES, ids=[n[:-3] for n in TEMPLATE_NAMES])
def test_template_footer(templates, name) -> None:
    lines = [ln for ln in _template_text(templates, name).splitlines() if ln.strip()]
    assert lines, f"{name} is empty"
    assert "harness-reference v0.2.0" in lines[-1]


@pytest.mark.parametrize("heading", INTENT_HEADINGS,
                         ids=[h.lstrip("# ").split(" (")[0][:24] for h in INTENT_HEADINGS])
def test_intent_headings(templates, heading) -> None:
    assert heading in _template_text(templates, "INTENT.md")


@pytest.mark.parametrize("term", ORCHESTRATOR_MENTIONS, ids=[t.replace(" ", "-") for t in ORCHESTRATOR_MENTIONS])
def test_orchestrator_mentions(templates, term) -> None:
    assert term in _template_text(templates, "ORCHESTRATOR.md").lower()


@pytest.mark.parametrize("term", ("redact", "suggested skills"), ids=["redact", "suggested-skills"])
def test_handoff_mentions(templates, term) -> None:
    assert term in _template_text(templates, "HANDOFF.md").lower()


def test_drift_result_constructible_and_frozen() -> None:
    r = drift_mod.DriftResult(signal_a=0.1, signal_b=0.2, composite=0.15, status="ok")
    assert (r.signal_a, r.signal_b, r.composite, r.status) == (0.1, 0.2, 0.15, "ok")
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        r.status = "warn"  # type: ignore[misc]


def test_proposal_constructible() -> None:
    p = retro_mod.Proposal(kind="weight_adjustment", target="agent_x",
                           rationale="repeated verifier failures", payload={"delta": -0.1})
    assert p.kind == "weight_adjustment"
    assert p.target == "agent_x"
    assert p.payload == {"delta": -0.1}


def test_constants() -> None:
    assert drift_mod.DEFAULT_WARN_THRESHOLD == 0.35
    assert drift_mod.DEFAULT_PAUSE_THRESHOLD == 0.55
    assert drift_mod.DEFAULT_WARN_THRESHOLD <= drift_mod.DEFAULT_PAUSE_THRESHOLD
    assert consensus.DISSENT_FLOOR == 0.15


STUB_CALLS = [
    pytest.param(lambda: drift_mod.drift_check("intent text", "state summary"), id="drift_check"),
    pytest.param(lambda: consensus.aggregate([], campaign_id="c", cohort="x", task_id="t"),
                 id="consensus-aggregate"),
    pytest.param(lambda: retro_mod.retrospective([]), id="retrospective"),
    pytest.param(lambda: event_log.validate_envelope({}), id="validate_envelope"),
    pytest.param(lambda: event_log.EventLog("x"), id="EventLog-init"),
    pytest.param(lambda: memory_index.MemoryIndex("x"), id="MemoryIndex-init"),
]


@pytest.mark.parametrize("call", STUB_CALLS)
def test_stub_raises_phase2b(call) -> None:
    with pytest.raises(NotImplementedError, match="^Phase 2B"):
        call()
