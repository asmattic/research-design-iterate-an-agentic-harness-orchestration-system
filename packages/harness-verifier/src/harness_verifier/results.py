"""The one result type every verifier returns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class VerifierResult:
    """Outcome of one deterministic verification.

    ``result`` semantics (PRD §6.7): "pass" and "fail" are authoritative —
    they win over any LLM opinion. "abstain" means the claim was not testable
    here (offline, unknown schema, wrong types, missing target, ...).
    """

    verifier_id: str
    result: Literal["pass", "fail", "abstain"]
    evidence: dict[str, Any] = field(default_factory=dict)
