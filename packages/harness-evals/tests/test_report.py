"""Report writer contract: §14.8 section order and not-scored rendering."""

from __future__ import annotations

import re

import pytest

he = pytest.importorskip("harness_evals")

from harness_evals import report  # noqa: E402
from harness_evals.scorers import ScoreResult  # noqa: E402

EXPECTED_ORDER = [
    "Completion", "Intent-alignment", "Drift", "Calibration",
    "Cost", "Safety", "Human gates", "Retrospective notes",
]


def _headings(text: str) -> list[str]:
    return re.findall(r"^## (.+)$", text, flags=re.MULTILINE)


def test_sections_render_in_exact_14_8_order(tmp_out):
    path = report.write_report("camp-order", [], tmp_out)
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Campaign camp-order report")
    assert _headings(text) == EXPECTED_ORDER


def test_unscored_sections_say_not_scored(tmp_out):
    results = [ScoreResult(scorer="completion", value=0.75, details={"claimed": 4})]
    text = report.write_report("camp-mix", results, tmp_out).read_text(encoding="utf-8")
    sections = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    by_heading = {s.splitlines()[0]: s for s in sections}
    assert "not scored this run" not in by_heading["Completion"]
    assert "value: 0.75" in by_heading["Completion"]
    assert "claimed: 4" in by_heading["Completion"]
    for unscored in ("Intent-alignment", "Human gates", "Retrospective notes", "Drift"):
        assert "not scored this run" in by_heading[unscored]


def test_scored_sections_render_value_and_details(tmp_out):
    results = [
        ScoreResult(scorer="calibration", value=0.815,
                    details={"brier": 0.185, "ece": 0.35, "pairs": 2}),
        ScoreResult(scorer="cost", value=1500.0,
                    details={"tokens": 1500, "usd": 0.0, "wall_clock_ms": 900}),
    ]
    text = report.write_report("camp-2", results, tmp_out).read_text(encoding="utf-8")
    assert "brier: 0.185" in text
    assert "ece: 0.35" in text
    assert "tokens: 1500" in text


def test_output_dir_is_created(tmp_path):
    target = tmp_path / "nested" / "campaign-out"
    path = report.write_report("camp-3", [], target)
    assert path == target / "report.md"
    assert path.is_file()


def test_dummy_result_matches_no_section(tmp_out):
    events = []
    results = [he.get_scorer("dummy").score(events)]
    text = report.write_report("camp-4", results, tmp_out).read_text(encoding="utf-8")
    assert text.count("not scored this run") == len(EXPECTED_ORDER)
