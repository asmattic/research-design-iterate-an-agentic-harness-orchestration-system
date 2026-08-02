"""Composite drift signal per PRD §11.

Round 2 is deliberately LEXICAL: vector/embedding signals are deferred to
Round 3 per the §22 kickoff question, so both sub-signals here are cheap
deterministic set distances over the raw text.

- ``signal_a`` — token-set Jaccard distance between the lowercased word
  sets of *intent_text* and *state_summary* (punctuation stripped).
- ``signal_b`` — character-bigram Jaccard distance over the
  whitespace-normalized lowercased text: a second, correlated-but-distinct
  lexical channel standing in for §11.2's semantic-distance signal until
  vectors land.
- ``composite`` — the mean of the two signals, clamped to [0, 1].

Upgrade path: Round 3 swaps ``signal_a`` for embedding cosine distance
(intent embedded once at campaign start, rolling state summary embedded at
each checkpoint) and ``signal_b`` for the LLM-judge qualitative score —
the shape of ``DriftResult`` and the threshold ladder stay unchanged.

Thresholds map the composite onto a status ladder:
ok < warn_threshold <= warn < pause_threshold <= pause < HALT margin
<= halt, where the HALT margin is ``max(pause_threshold, 0.9)``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

DEFAULT_WARN_THRESHOLD: float = 0.35
DEFAULT_PAUSE_THRESHOLD: float = 0.55

#: The halt band never starts below this composite, even with a low
#: pause_threshold — halting is reserved for near-total divergence.
_HALT_MARGIN_FLOOR: float = 0.9

_WORD_RE = re.compile(r"[a-z0-9']+")


@dataclass(frozen=True)
class DriftResult:
    """Outcome of a drift check: sub-signals, composite, and status."""

    signal_a: float
    signal_b: float
    composite: float
    status: Literal["ok", "warn", "pause", "halt"]


def _jaccard_distance(left: frozenset[str], right: frozenset[str]) -> float:
    """1 - |intersection| / |union|; defined as 0.0 when both sets are empty."""
    if not left and not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return 1.0 - len(left & right) / len(union)


def _word_set(text: str) -> frozenset[str]:
    """Lowercased word tokens with punctuation stripped."""
    return frozenset(_WORD_RE.findall(text.lower()))


def _bigram_set(text: str) -> frozenset[str]:
    """Character 2-grams of the whitespace-normalized lowercased text."""
    normalized = " ".join(text.lower().split())
    return frozenset(normalized[i : i + 2] for i in range(len(normalized) - 1))


def drift_check(
    intent_text: str,
    state_summary: str,
    *,
    warn_threshold: float = DEFAULT_WARN_THRESHOLD,
    pause_threshold: float = DEFAULT_PAUSE_THRESHOLD,
) -> DriftResult:
    """Compare *state_summary* against *intent_text* and return a DriftResult.

    Thresholds only affect the status ladder, never the composite.
    Raises ValueError unless ``0 <= warn_threshold <= pause_threshold <= 1``
    (the composite lives in [0, 1], so thresholds outside it would silently
    make parts of the status ladder unreachable).
    """
    if not (0.0 <= warn_threshold <= pause_threshold <= 1.0):
        raise ValueError(
            "thresholds must satisfy 0 <= warn_threshold <= pause_threshold <= 1 "
            f"(got warn={warn_threshold!r}, pause={pause_threshold!r})"
        )

    signal_a = _jaccard_distance(_word_set(intent_text), _word_set(state_summary))
    signal_b = _jaccard_distance(_bigram_set(intent_text), _bigram_set(state_summary))
    composite = max(0.0, min(1.0, (signal_a + signal_b) / 2.0))

    halt_margin = max(pause_threshold, _HALT_MARGIN_FLOOR)
    status: Literal["ok", "warn", "pause", "halt"]
    if composite < warn_threshold:
        status = "ok"
    elif composite < pause_threshold:
        status = "warn"
    elif composite < halt_margin:
        status = "pause"
    else:
        status = "halt"

    return DriftResult(
        signal_a=signal_a, signal_b=signal_b, composite=composite, status=status
    )
