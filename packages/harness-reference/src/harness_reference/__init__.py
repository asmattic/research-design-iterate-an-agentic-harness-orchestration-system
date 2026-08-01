"""harness-reference: campaign templates plus five reference modules.

Phase 2A ships typed stubs; behavior lands in Phase 2B. Only
:func:`templates_dir` is fully implemented (asset resolution, not behavior).
"""

from __future__ import annotations

from harness_reference._assets import templates_dir
from harness_reference.consensus import DISSENT_FLOOR, aggregate
from harness_reference.drift_check import (
    DEFAULT_PAUSE_THRESHOLD,
    DEFAULT_WARN_THRESHOLD,
    DriftResult,
    drift_check,
)
from harness_reference.event_log import EventLog, validate_envelope
from harness_reference.memory_index import MemoryIndex
from harness_reference.retrospective import Proposal, retrospective

__version__ = "0.2.0"

__all__ = [
    "DEFAULT_PAUSE_THRESHOLD",
    "DEFAULT_WARN_THRESHOLD",
    "DISSENT_FLOOR",
    "DriftResult",
    "EventLog",
    "MemoryIndex",
    "Proposal",
    "aggregate",
    "drift_check",
    "retrospective",
    "templates_dir",
    "validate_envelope",
    "__version__",
]
