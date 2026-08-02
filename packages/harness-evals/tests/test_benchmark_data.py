"""Phase 2D benchmark seed data: every committed scenario line is a valid
event envelope, scenarios are internally coherent, and the two seeded
benchmarks (rental-synthetic, adversarial-safety) satisfy their data contracts.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import evals_testlib as tl

hp = pytest.importorskip("harness_protocol")

DATA_DIR = tl.canonical_benchmarks_dir() / "data"
RENTAL_DIR = DATA_DIR / "rental-synthetic"
ADVERSARIAL_DIR = DATA_DIR / "adversarial-safety"


def _scenario_files() -> list[Path]:
    if not DATA_DIR.is_dir():
        return []
    return sorted(DATA_DIR.glob("*/scenario-*.jsonl"))


SCENARIO_FILES = _scenario_files()

pytestmark = pytest.mark.skipif(
    not SCENARIO_FILES, reason="benchmarks/data/ scenario files not yet present"
)


def _events(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _param_id(path: Path) -> str:
    return f"{path.parent.name}/{path.name}"


# ------------------------------------------------------------- envelope ----


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=_param_id)
def test_every_line_validates_against_event_envelope(path: Path):
    for idx, event in enumerate(_events(path)):
        errors = hp.iter_errors("event-envelope", event)
        assert errors == [], f"{_param_id(path)} line {idx} invalid: {errors}"


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=_param_id)
def test_scenario_event_ids_unique(path: Path):
    ids = [e["event_id"] for e in _events(path)]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=_param_id)
def test_scenario_single_campaign_id(path: Path):
    campaigns = {e["campaign_id"] for e in _events(path)}
    assert len(campaigns) == 1, f"expected one campaign_id, got {campaigns}"


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=_param_id)
def test_scenario_timestamps_non_decreasing(path: Path):
    stamps = [e["t"] for e in _events(path)]
    assert stamps == sorted(stamps), f"timestamps out of order in {_param_id(path)}"


# --------------------------------------------------------------- rental ----


def test_rental_has_exactly_twenty_scenarios():
    files = sorted(RENTAL_DIR.glob("scenario-*.jsonl"))
    assert len(files) == 20
    assert [f.name for f in files] == [
        f"scenario-{n:02d}.jsonl" for n in range(1, 21)
    ]


# ---------------------------------------------------------- adversarial ----


def _adversarial_cases() -> list[dict]:
    cases = []
    for path in sorted(ADVERSARIAL_DIR.glob("scenario-*.jsonl")):
        for event in _events(path):
            if event["kind"] == "guardrail_event":
                cases.append(event["payload"])
    return cases


def test_adversarial_has_at_least_twenty_distinct_cases():
    case_ids = [c["case_id"] for c in _adversarial_cases()]
    assert len(case_ids) == len(set(case_ids)), "duplicate case_ids"
    assert len(set(case_ids)) >= 20


def test_adversarial_covers_at_least_six_categories():
    categories = {c["category"] for c in _adversarial_cases()}
    assert len(categories) >= 6, f"only {len(categories)} categories: {categories}"


def test_adversarial_exactly_three_unblocked_cases():
    unblocked = [c["case_id"] for c in _adversarial_cases() if c["blocked"] is False]
    assert len(unblocked) == 3, f"expected 3 blocked=false cases, got {unblocked}"


def test_adversarial_payload_text_short_and_defanged():
    for case in _adversarial_cases():
        text = case["payload_text"]
        assert isinstance(text, str) and text
        assert len(text) <= 120, f"{case['case_id']} payload_text is {len(text)} chars"


# ------------------------------------------------------------- manifests ----


@pytest.mark.parametrize("name", ["rental-synthetic", "adversarial-safety"])
def test_seeded_benchmark_manifest_is_available(name: str):
    manifest_path = tl.canonical_benchmarks_dir() / f"{name}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "available"
    assert manifest["name"] == name
