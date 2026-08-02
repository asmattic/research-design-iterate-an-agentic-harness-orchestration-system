"""Behavior tests for harness_os.bs_detector (PRD §6.4.2)."""

from __future__ import annotations

from typing import Any

import os_ctx_testlib

bs = os_ctx_testlib.load_harness_os_module("bs_detector")


def _emission(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "agent_id": "budget-expert",
        "value": 42,
        "confidence": 0.5,
        "sources": ["docs/zoning.pdf"],
        "verifier_results": [],
    }
    base.update(overrides)
    return base


class TestOverConfident:
    def test_fires_alone(self) -> None:
        report = bs.inspect_emission(_emission(confidence=0.97))
        assert report.flags == ("over_confident",)
        assert len(report.reasons) == 1

    def test_boundary_fires_at_095(self) -> None:
        report = bs.inspect_emission(_emission(confidence=0.95))
        assert "over_confident" in report.flags

    def test_suppressed_by_verifier_pass(self) -> None:
        report = bs.inspect_emission(
            _emission(
                confidence=0.99,
                verifier_results=[{"verifier_id": "v1", "result": "pass"}],
            )
        )
        assert report.flags == ("clean",)

    def test_failing_verifier_does_not_suppress(self) -> None:
        report = bs.inspect_emission(
            _emission(
                confidence=0.99,
                verifier_results=[{"verifier_id": "v1", "result": "fail"}],
            )
        )
        assert "over_confident" in report.flags


class TestUnsupported:
    def test_fires_alone_on_empty_sources(self) -> None:
        report = bs.inspect_emission(_emission(sources=[]))
        assert report.flags == ("unsupported",)
        assert len(report.reasons) == 1

    def test_fires_on_missing_sources_key(self) -> None:
        emission = _emission()
        del emission["sources"]
        assert "unsupported" in bs.inspect_emission(emission).flags

    def test_suppressed_by_verifier_pass(self) -> None:
        report = bs.inspect_emission(
            _emission(
                sources=[],
                verifier_results=[{"verifier_id": "v1", "result": "pass"}],
            )
        )
        assert report.flags == ("clean",)

    def test_no_value_no_flag(self) -> None:
        emission = _emission(sources=[])
        del emission["value"]
        assert bs.inspect_emission(emission).flags == ("clean",)


class TestHallucinated:
    def test_scheme_garbage_source_fires(self) -> None:
        report = bs.inspect_emission(_emission(sources=["notaproto://???"]))
        assert report.flags == ("hallucinated",)
        assert len(report.reasons) == 1

    def test_bare_separator_fires(self) -> None:
        assert "hallucinated" in bs.inspect_emission(
            _emission(sources=["://garbage"])
        ).flags

    def test_http_without_netloc_fires(self) -> None:
        assert "hallucinated" in bs.inspect_emission(
            _emission(sources=["http://"])
        ).flags

    def test_plain_doc_reference_does_not_fire(self) -> None:
        report = bs.inspect_emission(_emission(sources=["docs/zoning.pdf"]))
        assert report.flags == ("clean",)

    def test_valid_https_url_does_not_fire(self) -> None:
        report = bs.inspect_emission(
            _emission(sources=["https://example.com/report"])
        )
        assert report.flags == ("clean",)

    def test_one_bad_source_among_good_fires(self) -> None:
        report = bs.inspect_emission(
            _emission(sources=["docs/ok.pdf", "junk://nope//"])
        )
        assert "hallucinated" in report.flags


class TestCombinationsAndInvariants:
    def test_over_confident_plus_unsupported(self) -> None:
        report = bs.inspect_emission(_emission(confidence=0.96, sources=[]))
        assert report.flags == ("over_confident", "unsupported")
        assert len(report.reasons) == 2
        assert "confiden" in report.reasons[0].lower()
        assert "source" in report.reasons[1].lower()

    def test_clean_appears_alone_with_no_reasons(self) -> None:
        report = bs.inspect_emission(_emission())
        assert report.flags == ("clean",)
        assert report.reasons == ()

    def test_empty_emission_is_clean(self) -> None:
        report = bs.inspect_emission({})
        assert report.flags == ("clean",)
        assert report.reasons == ()

    def test_reasons_parallel_non_clean_flags(self) -> None:
        cases = [
            _emission(confidence=0.98),
            _emission(sources=[]),
            _emission(confidence=0.99, sources=["bogus://x"]),
        ]
        for emission in cases:
            report = bs.inspect_emission(emission)
            non_clean = tuple(f for f in report.flags if f != "clean")
            assert len(report.reasons) == len(non_clean)

    def test_report_is_frozen(self) -> None:
        report = bs.inspect_emission(_emission())
        assert isinstance(report, bs.BSReport)
        try:
            report.flags = ()  # type: ignore[misc]
        except AttributeError:
            pass
        else:  # pragma: no cover
            raise AssertionError("BSReport must be frozen")
