"""The five built-in deterministic verifiers and their registry.

Every verifier exposes ``.name`` and ``.verify(claim) -> VerifierResult``.
The registry instances are network-free: the default citation_resolver has
``fetcher=None`` so tests and CI never touch the network. Callers wanting
live citation checks construct ``CitationResolver(fetcher=default_fetcher)``.
"""

from __future__ import annotations

import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping

import harness_protocol

from harness_verifier.results import VerifierResult

#: Canonical verifier names, in registry order.
VERIFIER_NAMES: tuple[str, ...] = (
    "code_test_runner",
    "schema_validator",
    "citation_resolver",
    "numeric_bound",
    "type_check",
)

_TAIL_CHARS = 800


def _is_number(value: Any) -> bool:
    """True for int/float but NOT bool (bool is an int subclass in Python)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class SchemaValidator:
    """Validate an instance against a named harness-protocol JSON Schema."""

    name = "schema_validator"

    def verify(self, claim: Mapping[str, Any]) -> VerifierResult:
        schema = claim.get("schema")
        if schema not in harness_protocol.SCHEMA_NAMES:
            return VerifierResult(
                self.name,
                "abstain",
                {
                    "reason": f"unknown schema {schema!r}",
                    "known_schemas": list(harness_protocol.SCHEMA_NAMES),
                },
            )
        errors = harness_protocol.iter_errors(schema, claim.get("instance"))
        if errors:
            return VerifierResult(self.name, "fail", {"errors": errors})
        return VerifierResult(self.name, "pass", {"schema": schema})


class NumericBound:
    """Check low <= value <= high for whichever bounds the claim provides."""

    name = "numeric_bound"

    def verify(self, claim: Mapping[str, Any]) -> VerifierResult:
        value = claim.get("value")
        if not _is_number(value):
            return VerifierResult(
                self.name,
                "abstain",
                {"reason": f"value is not numeric: {value!r}"},
            )
        low = claim.get("low")
        high = claim.get("high")
        if low is None and high is None:
            return VerifierResult(
                self.name, "abstain", {"reason": "no bounds provided"}
            )
        for bound_name, bound in (("low", low), ("high", high)):
            if bound is not None and not _is_number(bound):
                return VerifierResult(
                    self.name,
                    "abstain",
                    {"reason": f"{bound_name} bound is not numeric: {bound!r}"},
                )
        if low is not None and value < low:
            return VerifierResult(
                self.name,
                "fail",
                {"violated_bound": "low", "low": low, "value": value},
            )
        if high is not None and value > high:
            return VerifierResult(
                self.name,
                "fail",
                {"violated_bound": "high", "high": high, "value": value},
            )
        return VerifierResult(
            self.name, "pass", {"value": value, "low": low, "high": high}
        )


class TypeCheck:
    """Check a value's runtime type against a JSON-ish type name."""

    name = "type_check"

    _CHECKS: dict[str, Callable[[Any], bool]] = {
        "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "float": lambda v: isinstance(v, float),
        "number": _is_number,
        "str": lambda v: isinstance(v, str),
        "bool": lambda v: isinstance(v, bool),
        "list": lambda v: isinstance(v, list),
        "dict": lambda v: isinstance(v, dict),
        "null": lambda v: v is None,
    }

    @staticmethod
    def _actual_type(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "str"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "dict"
        return type(value).__name__

    def verify(self, claim: Mapping[str, Any]) -> VerifierResult:
        expected = claim.get("expected_type")
        check = self._CHECKS.get(expected)  # type: ignore[arg-type]
        if check is None:
            return VerifierResult(
                self.name,
                "abstain",
                {
                    "reason": f"unknown expected_type {expected!r}",
                    "known_types": sorted(self._CHECKS),
                },
            )
        value = claim.get("value")
        evidence = {"actual_type": self._actual_type(value), "expected_type": expected}
        return VerifierResult(
            self.name, "pass" if check(value) else "fail", evidence
        )


def default_fetcher(url: str, timeout_s: float = 5.0) -> int:
    """HTTP HEAD via urllib, returning the status code. Opt-in only —
    never wired into the registry instance, so tests/CI stay offline."""
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:  # 4xx/5xx still carry a status
        return int(exc.code)


class CitationResolver:
    """Check that a citation URL is well-formed and (with a fetcher) resolves.

    ``fetcher`` is injectable: a callable mapping url -> HTTP status. With no
    fetcher (the registry default) well-formed URLs abstain ("offline").
    """

    name = "citation_resolver"

    def __init__(self, fetcher: Callable[[str], int] | None = None) -> None:
        self.fetcher = fetcher

    @staticmethod
    def _is_well_formed(url: Any) -> bool:
        if not isinstance(url, str):
            return False
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    def verify(self, claim: Mapping[str, Any]) -> VerifierResult:
        url = claim.get("url")
        if not self._is_well_formed(url):
            return VerifierResult(
                self.name, "fail", {"error": "malformed url", "url": repr(url)}
            )
        if self.fetcher is None:
            return VerifierResult(self.name, "abstain", {"reason": "offline"})
        status = self.fetcher(url)
        if status < 400:
            return VerifierResult(self.name, "pass", {"status": status})
        return VerifierResult(self.name, "fail", {"status": status})


class CodeTestRunner:
    """Run pytest on one target path in a subprocess; the exit code decides."""

    name = "code_test_runner"

    def verify(self, claim: Mapping[str, Any]) -> VerifierResult:
        raw_target = claim.get("pytest_target")
        if not isinstance(raw_target, (str, Path)):
            return VerifierResult(
                self.name,
                "abstain",
                {"reason": f"pytest_target is not a path: {raw_target!r}"},
            )
        target = Path(raw_target)
        if not target.exists():
            return VerifierResult(
                self.name,
                "abstain",
                {"reason": f"target does not exist: {target}"},
            )
        timeout_s = claim.get("timeout_s", 60)
        command = [sys.executable, "-m", "pytest", str(target), "-q"]
        try:
            completed = subprocess.run(  # noqa: S603 — fixed argv, never shell=True
                command,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                cwd=target.parent,
            )
        except subprocess.TimeoutExpired:
            return VerifierResult(
                self.name, "fail", {"timeout": True, "timeout_s": timeout_s}
            )
        if completed.returncode == 0:
            return VerifierResult(self.name, "pass", {"exit_code": 0})
        output = (completed.stdout or "") + (completed.stderr or "")
        return VerifierResult(
            self.name,
            "fail",
            {"exit_code": completed.returncode, "tail": output[-_TAIL_CHARS:]},
        )


#: Registry of default (network-free) verifier instances, keyed by name.
_REGISTRY: dict[str, Any] = {
    verifier.name: verifier
    for verifier in (
        CodeTestRunner(),
        SchemaValidator(),
        CitationResolver(fetcher=None),
        NumericBound(),
        TypeCheck(),
    )
}

assert tuple(_REGISTRY) == VERIFIER_NAMES  # registry order == canonical order


def get_verifier(name: str) -> Any:
    """Return the registry verifier for *name*; KeyError lists known names."""
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"unknown verifier {name!r}; known verifiers: {', '.join(VERIFIER_NAMES)}"
        ) from None
