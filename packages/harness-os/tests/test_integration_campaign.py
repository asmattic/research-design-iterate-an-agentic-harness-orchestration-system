"""The Phase 2C milestone gate: replay a recorded campaign through all six
Orchestrator System modules end to end (ROUND-2-PLAN §6, Phase 2C milestone:
"recorded-campaign integration test passes in harness-os").

Written by the integrating orchestrator, deliberately not by any module's
implementation lane — it exercises the modules the way the §6.4 pipeline
composes them, against the schema-valid fixture in fixtures/.
"""

from __future__ import annotations

import json
import pathlib

import pytest

harness_os = pytest.importorskip("harness_os")
harness_protocol = pytest.importorskip("harness_protocol")
harness_reference = pytest.importorskip("harness_reference")

FIXTURE = pathlib.Path(__file__).parents[1] / "fixtures" / "recorded-campaign.jsonl"


@pytest.fixture(scope="module")
def campaign_events() -> list[dict]:
    lines = FIXTURE.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


@pytest.fixture(scope="module")
def emissions(campaign_events) -> list[dict]:
    return [e["payload"] for e in campaign_events if e["kind"] == "emission"]


def test_fixture_is_schema_valid_and_replayable(tmp_path, campaign_events):
    log = harness_reference.EventLog(tmp_path / "replay.jsonl")
    for event in campaign_events:
        log.append(event)
    assert len(log) == len(campaign_events) == 12
    assert len(list(log.events(kind="emission"))) == 3


def test_bs_detector_flags_the_fixture_emissions(emissions):
    conservative, aggressive, tax = emissions
    assert harness_os.inspect_emission(conservative).flags == ("clean",)
    aggressive_report = harness_os.inspect_emission(aggressive)
    assert "over_confident" in aggressive_report.flags
    assert "unsupported" in aggressive_report.flags
    tax_report = harness_os.inspect_emission(tax)
    assert "hallucinated" in tax_report.flags  # "hcpafl bad://source"


def test_validator_routes_fixture_claims_to_real_verifiers(emissions):
    conservative, _aggressive, tax = emissions
    results = harness_os.route_claims(conservative)
    assert [r.result for r in results] == ["pass", "pass"]
    tax_results = harness_os.route_claims(tax)
    by_id = {r.verifier_id: r.result for r in tax_results}
    assert by_id["numeric_bound"] == "pass"
    assert by_id["schema_validator"] == "fail"  # instance misses required fields
    attached = harness_os.attach_results(tax, tax_results)
    assert attached is not tax
    assert {vr["verifier_id"] for vr in attached["verifier_results"]} == set(by_id)


def test_signal_noise_ranks_verified_clean_agent_first(emissions):
    conservative, aggressive, _tax = emissions
    claims = [
        {"agent_id": conservative["agent_id"], "calibration": 0.9,
         "verifier_result": "pass", "agreement": 0.8,
         "bs_flags": list(harness_os.inspect_emission(conservative).flags),
         "authority": 0.7},
        {"agent_id": aggressive["agent_id"], "calibration": 0.6,
         "verifier_result": "fail", "agreement": 0.4,
         "bs_flags": [f for f in harness_os.inspect_emission(aggressive).flags],
         "authority": 0.5},
    ]
    ranked = harness_os.weigh(claims)
    assert ranked[0].claim["agent_id"] == conservative["agent_id"]
    assert ranked[0].weight > ranked[1].weight


def test_consensus_packet_feeds_context_manager(campaign_events, emissions):
    conservative, aggressive, _tax = emissions
    packet = harness_reference.aggregate(
        [{"agent_id": e["agent_id"], "value": e["value"], "weight": w,
          "confidence": e["confidence"], "reasoning": e["reasoning"]}
         for e, w in ((conservative, 1.0), (aggressive, 0.6))],
        campaign_id="camp_os_replay", cohort="finance", task_id="task_rent_comps")
    assert harness_protocol.iter_errors("consensus-packet", packet) == []

    state = {
        "destination": "A decision-complete underwriting spec for camp_os_replay",
        "intent_ref": "campaigns/os-replay/INTENT.md",
        "plan": {"steps": [{"step_id": "s1", "status": "in_progress"}], "current_step": 1},
        "drift": {"status": "ok", "composite": 0.2},
        "budget": {"tokens_used": 9000, "tokens_budget": 2_000_000},
        "pending_approvals": [],
    }
    bundle = harness_os.assemble_context(state, [packet])
    names = [name for name, _ in bundle.sections]
    assert names[0] == "intent"
    assert any(name.startswith("packet:") for name in names)
    assert bundle.dropped == ()

    tight = harness_os.assemble_context(state, [packet], budget_tokens=120)
    assert any(name.startswith("packet:") for name in tight.dropped)


def test_drift_detector_maps_statuses_to_campaign_actions():
    same = "Underwrite the Tampa rental portfolio conservatively within budget."
    ok = harness_os.check_drift(same, same)
    assert ok.action == "continue"
    forced = harness_os.check_drift(
        same, "Compiling zsh plugins and benchmarking GPU shader kernels overnight.")
    assert forced.action in ("pause_campaign", "halt_campaign")
    assert set(forced.payload) == {"status", "signal_a", "signal_b",
                                   "composite", "warn_threshold", "pause_threshold"}


def test_retrospective_feeds_weight_tweaker(campaign_events):
    proposals = harness_reference.retrospective(campaign_events_payloadless(campaign_events))
    kinds = {p.kind for p in proposals}
    assert "weight_adjustment" in kinds  # citation_resolver fail on aggressive agent
    assert "memory_entry" in kinds       # the pause drift excursion
    table = harness_os.apply_proposals(
        {"finance_budget_conservative_v2": 1.0}, proposals)
    assert table["finance_budget_conservative_v2"] == 1.0
    assert table["finance_budget_aggressive_v1"] == pytest.approx(0.95)


def campaign_events_payloadless(events):
    """The retrospective consumes envelope-shaped mappings directly."""
    return events


def test_campaign_ends_with_a_human_cleared_decision(campaign_events):
    kinds = [e["kind"] for e in campaign_events]
    assert kinds[-1] == "decision"
    approval = [e for e in campaign_events if e["kind"] == "approval_decision"]
    assert approval and approval[0]["emitter"]["kind"] == "human"
