"""Deterministic verifier layer (PRD §6.7): five built-in verifiers + runner.

Precedence principle: a deterministic pass/fail is authoritative over any LLM
opinion; abstain means "this claim was not testable here".
"""

from harness_verifier.results import VerifierResult
from harness_verifier.runner import run_claims
from harness_verifier.verifiers import (
    VERIFIER_NAMES,
    CitationResolver,
    default_fetcher,
    get_verifier,
)

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "VerifierResult",
    "VERIFIER_NAMES",
    "CitationResolver",
    "default_fetcher",
    "get_verifier",
    "run_claims",
]
