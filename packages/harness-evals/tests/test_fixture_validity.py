"""Canonical recorded-campaign.jsonl validates against the protocol schema."""

from __future__ import annotations

import json

import pytest

import evals_testlib as tl

hp = pytest.importorskip("harness_protocol")

LINES = tl.load_fixture_lines()

pytestmark = pytest.mark.skipif(
    not LINES, reason="canonical fixtures/recorded-campaign.jsonl not yet present"
)


def test_fixture_has_eight_lines():
    assert len(LINES) == 8


@pytest.mark.parametrize("idx", range(len(LINES)))
def test_line_validates_against_event_envelope(idx):
    event = json.loads(LINES[idx])
    errors = hp.iter_errors("event-envelope", event)
    assert errors == [], f"line {idx} invalid: {errors}"


def test_all_lines_share_one_campaign_id():
    campaign_ids = {json.loads(line)["campaign_id"] for line in LINES}
    assert len(campaign_ids) == 1


def test_event_ids_unique():
    event_ids = [json.loads(line)["event_id"] for line in LINES]
    assert len(event_ids) == len(set(event_ids))
