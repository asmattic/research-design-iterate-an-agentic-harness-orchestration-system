"""citation_resolver: offline abstain by default, injectable fetcher, malformed URLs fail.

No test in this file may touch the network: the registry instance has
fetcher=None and every fetching test injects a fake.
"""

from __future__ import annotations

import pytest

import verifier_testlib as tl  # noqa: F401

import harness_verifier
from harness_verifier import CitationResolver, get_verifier


def test_registry_instance_is_offline_and_abstains() -> None:
    result = get_verifier("citation_resolver").verify(
        {"url": "https://example.com/paper"}
    )
    assert result.verifier_id == "citation_resolver"
    assert result.result == "abstain"
    assert result.evidence == {"reason": "offline"}


def test_fake_fetcher_pass_below_400() -> None:
    seen: list[str] = []

    def fetcher(url: str) -> int:
        seen.append(url)
        return 200

    result = CitationResolver(fetcher=fetcher).verify({"url": "https://example.com/x"})
    assert result.result == "pass"
    assert seen == ["https://example.com/x"]


def test_fake_fetcher_boundary_399_passes_400_fails() -> None:
    assert (
        CitationResolver(fetcher=lambda url: 399)
        .verify({"url": "http://example.com/"})
        .result
        == "pass"
    )
    result = CitationResolver(fetcher=lambda url: 400).verify(
        {"url": "http://example.com/"}
    )
    assert result.result == "fail"
    assert result.evidence["status"] == 400


def test_fake_fetcher_404_fails_with_status_evidence() -> None:
    result = CitationResolver(fetcher=lambda url: 404).verify(
        {"url": "https://example.com/missing"}
    )
    assert result.result == "fail"
    assert result.evidence["status"] == 404


@pytest.mark.parametrize(
    "url",
    [
        "not a url",
        "ftp://example.com/file",  # wrong scheme
        "http://",  # no netloc
        "example.com/no-scheme",
        "",
        None,
        42,
    ],
)
def test_malformed_url_fails_even_with_fetcher(url) -> None:
    calls: list[str] = []

    def fetcher(u: str) -> int:
        calls.append(u)
        return 200

    result = CitationResolver(fetcher=fetcher).verify({"url": url})
    assert result.result == "fail"
    assert calls == []  # malformed URLs are never fetched


def test_missing_url_key_fails() -> None:
    assert CitationResolver(fetcher=lambda u: 200).verify({}).result == "fail"


def test_default_fetcher_exported_but_not_called_here() -> None:
    assert callable(harness_verifier.default_fetcher)
