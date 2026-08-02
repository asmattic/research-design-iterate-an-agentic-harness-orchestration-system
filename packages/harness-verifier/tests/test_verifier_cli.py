"""harness-verify CLI: list, run over a claims file, exit codes, python -m entry."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import verifier_testlib as tl

from harness_verifier.cli import main


def test_list_exits_zero_and_names_all_verifiers(capsys) -> None:
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    for name in tl.EXPECTED_VERIFIER_NAMES:
        assert name in out


def test_run_mixed_claims_exits_one_with_json_lines(tmp_path, capsys) -> None:
    claims = [
        {"verifier": "type_check", "value": 3, "expected_type": "int"},  # pass
        {"verifier": "type_check", "value": 3, "expected_type": "str"},  # fail
        {"verifier": "citation_resolver", "url": "https://example.com/"},  # abstain
    ]
    path = tl.write_claims_file(tmp_path, claims)
    exit_code = main(["run", "--claims", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 1  # at least one fail

    lines = [line for line in captured.out.splitlines() if line.strip()]
    assert len(lines) == 3
    parsed = [json.loads(line) for line in lines]
    assert [p["result"] for p in parsed] == ["pass", "fail", "abstain"]
    for p in parsed:
        assert set(p) == {"verifier_id", "result", "evidence"}

    # summary goes to stderr, not stdout
    assert "1 fail" in captured.err
    assert "1 pass" in captured.err
    assert "1 abstain" in captured.err


def test_run_all_pass_exits_zero(tmp_path, capsys) -> None:
    claims = [{"verifier": "numeric_bound", "value": 5, "low": 0}]
    path = tl.write_claims_file(tmp_path, claims)
    assert main(["run", "--claims", str(path)]) == 0


def test_abstains_do_not_fail_the_run(tmp_path, capsys) -> None:
    claims = [
        {"verifier": "citation_resolver", "url": "https://example.com/"},
        {"verifier": "hallucinated_verifier"},
    ]
    path = tl.write_claims_file(tmp_path, claims)
    assert main(["run", "--claims", str(path)]) == 0


def test_usage_errors_exit_two(capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
    with pytest.raises(SystemExit) as excinfo:
        main(["run"])  # --claims is required
    assert excinfo.value.code == 2


def test_missing_claims_file_exits_two(tmp_path, capsys) -> None:
    exit_code = main(["run", "--claims", str(tmp_path / "absent.json")])
    assert exit_code == 2


def test_claims_file_not_an_array_exits_two(tmp_path, capsys) -> None:
    path = tmp_path / "claims.json"
    path.write_text('{"verifier": "type_check"}', encoding="utf-8")
    assert main(["run", "--claims", str(path)]) == 2


def test_python_dash_m_entrypoint(tmp_path) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "harness_verifier.cli", "list"],
        capture_output=True,
        text=True,
        env=tl.subprocess_env(),
        timeout=60,
    )
    assert proc.returncode == 0
    assert "code_test_runner" in proc.stdout
