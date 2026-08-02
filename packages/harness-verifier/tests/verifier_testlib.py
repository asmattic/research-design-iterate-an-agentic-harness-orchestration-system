"""Shared helpers for the harness-verifier test suite.

Deliberately NOT named conftest — module-level helpers live here so combined
pytest runs across suites never hit conftest name collisions.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
VERIFIER_PKG_DIR = TESTS_DIR.parent  # packages/harness-verifier
REPO_ROOT = VERIFIER_PKG_DIR.parent.parent
VERIFIER_SRC = VERIFIER_PKG_DIR / "src"
PROTOCOL_SRC = REPO_ROOT / "packages" / "harness-protocol-py" / "src"

for _src in (VERIFIER_SRC, PROTOCOL_SRC):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

EXPECTED_VERIFIER_NAMES = (
    "code_test_runner",
    "schema_validator",
    "citation_resolver",
    "numeric_bound",
    "type_check",
)

VALID_ENVELOPE_EXAMPLE = (
    REPO_ROOT
    / "packages"
    / "harness-protocol"
    / "examples"
    / "event-envelope"
    / "valid-agent-emission.json"
)


def load_valid_envelope() -> dict:
    """A protocol instance known to validate against event-envelope."""
    return json.loads(VALID_ENVELOPE_EXAMPLE.read_text(encoding="utf-8"))


def subprocess_env() -> dict[str, str]:
    """Environment for `python -m` subprocesses: both src trees on PYTHONPATH."""
    env = dict(os.environ)
    extra = os.pathsep.join([str(VERIFIER_SRC), str(PROTOCOL_SRC)])
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = extra + (os.pathsep + existing if existing else "")
    return env


def write_passing_pytest_file(directory: Path) -> Path:
    """A tiny real pytest file that passes."""
    target = directory / "test_tiny_pass.py"
    target.write_text(
        "def test_always_passes():\n    assert 1 + 1 == 2\n", encoding="utf-8"
    )
    return target


def write_failing_pytest_file(directory: Path) -> Path:
    """A tiny real pytest file that fails."""
    target = directory / "test_tiny_fail.py"
    target.write_text(
        "def test_always_fails():\n    assert 1 + 1 == 3\n", encoding="utf-8"
    )
    return target


def write_sleeping_pytest_file(directory: Path) -> Path:
    """A tiny real pytest file that sleeps far longer than any test timeout."""
    target = directory / "test_tiny_sleep.py"
    target.write_text(
        "import time\n\ndef test_sleeps():\n    time.sleep(60)\n", encoding="utf-8"
    )
    return target


def write_claims_file(directory: Path, claims: list[dict]) -> Path:
    path = directory / "claims.json"
    path.write_text(json.dumps(claims), encoding="utf-8")
    return path
