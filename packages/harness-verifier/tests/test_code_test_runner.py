"""code_test_runner: real pytest subprocess against tiny pass/fail files."""

from __future__ import annotations

import verifier_testlib as tl

from harness_verifier import get_verifier


def _verify(claim: dict):
    return get_verifier("code_test_runner").verify(claim)


def test_pass_on_passing_pytest_file(tmp_path) -> None:
    target = tl.write_passing_pytest_file(tmp_path)
    result = _verify({"pytest_target": str(target)})
    assert result.verifier_id == "code_test_runner"
    assert result.result == "pass"


def test_fail_on_failing_pytest_file_with_exit_code_and_tail(tmp_path) -> None:
    target = tl.write_failing_pytest_file(tmp_path)
    result = _verify({"pytest_target": str(target)})
    assert result.result == "fail"
    assert result.evidence["exit_code"] != 0
    tail = result.evidence["tail"]
    assert isinstance(tail, str)
    assert tail  # captured output present
    assert len(tail) <= 1000  # roughly the last ~800 chars, not the whole log


def test_abstain_when_target_does_not_exist(tmp_path) -> None:
    result = _verify({"pytest_target": str(tmp_path / "no_such_test.py")})
    assert result.result == "abstain"


def test_timeout_fails_with_timeout_evidence(tmp_path) -> None:
    target = tl.write_sleeping_pytest_file(tmp_path)
    result = _verify({"pytest_target": str(target), "timeout_s": 3})
    assert result.result == "fail"
    assert result.evidence["timeout"] is True
