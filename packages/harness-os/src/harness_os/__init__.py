"""harness-os: the Orchestrator System middleware (PRD §6.4).

Six sub-responsibilities that run on every expert emission before it reaches
the primary orchestrator: context manager, BS detector, validator/verifier
bridge, signal/noise attributor, weight tweaker, drift detector.

Round 2 ships deterministic cores; the LLM-judge layers (BS detection,
context summarization, drift's qualitative channel) are specified as
versioned prompt templates under ``prompts/`` and get wired to a model by
the adapter layer (§16).
"""

from __future__ import annotations

__version__ = "0.2.0"

from harness_os.bs_detector import BSReport, inspect_emission
from harness_os.context_manager import ContextBundle, assemble_context
from harness_os.drift_detector import DriftEvent, check_drift
from harness_os.signal_noise import DEFAULT_FACTOR_WEIGHTS, WeightedClaim, weigh
from harness_os.validator import attach_results, route_claims
from harness_os.weight_tweaker import apply_proposals

__all__ = [
    "__version__",
    "BSReport",
    "inspect_emission",
    "ContextBundle",
    "assemble_context",
    "DriftEvent",
    "check_drift",
    "DEFAULT_FACTOR_WEIGHTS",
    "WeightedClaim",
    "weigh",
    "attach_results",
    "route_claims",
    "apply_proposals",
]
