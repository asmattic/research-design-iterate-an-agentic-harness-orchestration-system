"""Phase 2B acceptance suite for harness_reference.drift_check.

The lexical drift-check implementation has landed; these tests now run as
plain assertions (the strict-xfail markers from the contract phase are gone).
"""

from __future__ import annotations

import pytest

hr = pytest.importorskip("harness_reference", reason="stub lane not landed")
if not hasattr(hr, "__version__"):
    pytest.skip("harness_reference is a bare namespace package (stub lane not landed)",
                allow_module_level=True)
drift_mod = pytest.importorskip("harness_reference.drift_check")


def test_drift_identical_is_ok():
    text = "Underwrite the Tampa rental portfolio conservatively within budget."
    result = drift_mod.drift_check(text, text)
    assert result.composite == pytest.approx(0.0, abs=0.05)
    assert result.status == "ok"


def test_drift_disjoint_pauses():
    result = drift_mod.drift_check(
        "Underwrite the Tampa rental portfolio conservatively within budget.",
        "Compiling zsh plugins and benchmarking GPU shader kernels overnight.",
    )
    assert result.composite > drift_mod.DEFAULT_PAUSE_THRESHOLD
    assert result.status in ("pause", "halt")


def test_drift_threshold_monotonic():
    intent = "Plan the campaign roadmap."
    state = "Plan the campaign roadmap and also restructure the billing stack."
    strict = drift_mod.drift_check(intent, state,
                                   warn_threshold=0.0, pause_threshold=1.0)
    lax = drift_mod.drift_check(intent, state,
                                warn_threshold=0.99, pause_threshold=0.999)
    if strict.composite > 0.0:
        assert strict.status != "ok"
    if lax.composite <= 0.99:
        assert lax.status == "ok"
    assert strict.composite == pytest.approx(lax.composite)
