"""Behavior tests for harness_os.drift_detector (PRD §6.4.6)."""

from __future__ import annotations

from harness_reference.drift_check import (
    DEFAULT_PAUSE_THRESHOLD,
    DEFAULT_WARN_THRESHOLD,
    DriftResult,
)

import os_ctx_testlib

dd = os_ctx_testlib.load_harness_os_module("drift_detector")

INTENT = "renovate the duplex within the approved zoning budget"


class TestStatusToActionMapping:
    def test_ok_maps_to_continue(self) -> None:
        event = dd.check_drift(INTENT, INTENT)
        assert event.result.status == "ok"
        assert event.action == "continue"

    def test_warn_maps_to_surface_warning(self) -> None:
        event = dd.check_drift(
            "alpha beta", "alpha gamma", warn_threshold=0.0, pause_threshold=0.99
        )
        assert event.result.status == "warn"
        assert event.action == "surface_warning"

    def test_pause_maps_to_pause_campaign(self) -> None:
        event = dd.check_drift(
            "alpha beta", "alpha gamma", warn_threshold=0.0, pause_threshold=0.0
        )
        assert event.result.status == "pause"
        assert event.action == "pause_campaign"

    def test_halt_maps_to_halt_campaign(self) -> None:
        event = dd.check_drift("aaaa", "zzzz")  # fully disjoint -> composite 1.0
        assert event.result.status == "halt"
        assert event.action == "halt_campaign"


class TestPayload:
    def test_payload_keys_and_rounding(self) -> None:
        event = dd.check_drift("alpha beta gamma", "alpha delta epsilon")
        assert set(event.payload) == {
            "status",
            "signal_a",
            "signal_b",
            "composite",
            "warn_threshold",
            "pause_threshold",
        }
        assert event.payload["status"] == event.result.status
        assert event.payload["signal_a"] == round(event.result.signal_a, 6)
        assert event.payload["signal_b"] == round(event.result.signal_b, 6)
        assert event.payload["composite"] == round(event.result.composite, 6)

    def test_payload_thresholds_default_when_none(self) -> None:
        event = dd.check_drift(INTENT, "totally different words entirely")
        assert event.payload["warn_threshold"] == round(DEFAULT_WARN_THRESHOLD, 6)
        assert event.payload["pause_threshold"] == round(DEFAULT_PAUSE_THRESHOLD, 6)

    def test_payload_explicit_thresholds_recorded(self) -> None:
        event = dd.check_drift(
            "alpha beta", "alpha gamma", warn_threshold=0.1, pause_threshold=0.8
        )
        assert event.payload["warn_threshold"] == 0.1
        assert event.payload["pause_threshold"] == 0.8


class TestDefaults:
    def test_none_thresholds_equal_explicit_defaults(self) -> None:
        implicit = dd.check_drift("alpha beta", "alpha gamma")
        explicit = dd.check_drift(
            "alpha beta",
            "alpha gamma",
            warn_threshold=DEFAULT_WARN_THRESHOLD,
            pause_threshold=DEFAULT_PAUSE_THRESHOLD,
        )
        assert implicit == explicit

    def test_result_is_reference_drift_result(self) -> None:
        event = dd.check_drift(INTENT, INTENT)
        assert isinstance(event, dd.DriftEvent)
        assert isinstance(event.result, DriftResult)
